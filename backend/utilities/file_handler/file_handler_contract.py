"""
================================================================
CONTRACT  :  FileHandler
MODULE    :  backend/utilities/file_handler
VERSION   :  1.0.0   |   Sprint 1
================================================================

WHO USES THIS IN JINIE
-----------------------
Every backend module that needs to touch a file goes through
FileHandler.  Nobody else touches the filesystem.

  Module 10 (Input Interface)
      User uploads a PDF wireframe or image
              │
              ▼
      FileHandler.read(path)   ← reads the uploaded file
              │  FilePayload
              ▼
      Engine (Module 02)       ← gets raw_content for NLP

  Module 06 (Compiler)
      CodeT5 generates a Flutter/Dart file
              │
              ▼
      FileHandler.write(path, dart_code)
              │  WriteReceipt
              ▼
      CodeEditor.load_file(payload)   ← next submodule edits it

  Module 09 (Deployment Manager)
      Firebase Helper needs pubspec.yaml, main.dart, etc.
              │
              ▼
      FileHandler.read(path)  for each file in the project

WHAT FileHandler GUARANTEES
----------------------------
read()
    → FilePayload
        .path          str   absolute path on disk
        .raw_content   str   exact UTF-8 decoded text
        .encoding      str   "utf-8"
        .size_bytes    int   byte count
        .extension     str   lowercase e.g. ".dart" ".pdf" ".png"
        .trace_id      str   "FH-<uuid4>"  logged in Traceability Matrix
        .mime_type     str   e.g. "text/x-dart"  (empty if unknown)

write(path, content)
    → WriteReceipt
        .success       bool
        .path          str
        .bytes_written int
        .trace_id      str   "FH-<uuid4>"
        .overwritten   bool

append(path, content)  → WriteReceipt
delete(path)           → bool   True=deleted  False=was already gone
move(src, dst)         → str    new absolute path
copy(src, dst)         → str    destination absolute path
exists(path)           → bool
list_dir(path)         → list[FileInfo]   sorted A→Z

CONTRACT RULES
--------------
PRE  (caller must guarantee)
  1. path is always a non-empty string
  2. content for write/append is always str, never None
  3. For move/copy destination parent exists OR create_parents=True

POST (FileHandler guarantees)
  1. Never raises raw OSError — always wraps in FileHandlerError
  2. Never modifies content — pure I/O only
  3. Every operation adds a structured entry to the internal log
  4. trace_id is always UUID4 prefixed "FH-"

ERROR CODES
-----------
  FILE_NOT_FOUND      read/delete on missing file
  PERMISSION_ERROR    OS denied the operation
  ENCODING_ERROR      file is not valid UTF-8
  DISK_FULL           no space left on device
  INVALID_PATH        path is empty or blank
  DIRECTORY_NOT_FOUND list_dir on non-directory
  DESTINATION_EXISTS  write(overwrite=False) on existing file

DOWNSTREAM (what CodeEditor.load_file expects)
  CodeEditor receives FilePayload and uses:
    .raw_content  → split into lines for editing
    .extension    → detect language (dart/py/json etc)
    .trace_id     → stored as source_trace_id in CodePayload
                    so Traceability Manager can walk the chain

AGILE ROADMAP
  Sprint 1  read, write, append, exists, list_dir, delete, move, copy
  Sprint 2  richer mime detection, binary file support for images/PDFs
================================================================
"""

from dataclasses import dataclass


# ── data types ────────────────────────────────────────────────────────────────

@dataclass
class FilePayload:
    """
    Output of FileHandler.read().
    Direct input of CodeEditor.load_file().

    Treat as immutable — nothing downstream should alter it.
    """
    path:        str    # absolute normalised path
    raw_content: str    # exact UTF-8 text — CodeEditor works with this
    encoding:    str    # "utf-8"
    size_bytes:  int    # byte count on disk
    extension:   str    # lowercase e.g. ".dart"  ".py"  ".json"
    trace_id:    str    # "FH-<uuid4>" registered in Traceability Matrix
    mime_type:   str = ""  # e.g. "text/x-dart" — empty if undetectable


@dataclass
class WriteReceipt:
    """Output of FileHandler.write() and FileHandler.append()."""
    success:       bool
    path:          str
    bytes_written: int
    trace_id:      str    # "FH-<uuid4>"
    overwritten:   bool = False


@dataclass
class FileInfo:
    """One item in the list returned by FileHandler.list_dir()."""
    name:         str
    path:         str   # absolute path
    size_bytes:   int   # 0 for directories
    extension:    str   # lowercase; "" for directories
    is_directory: bool


# ── error type ────────────────────────────────────────────────────────────────

class FileHandlerError(Exception):
    """
    Raised by FileHandler for every failure.
    Never raises raw OSError to callers.

    Usage:
        except FileHandlerError as e:
            if e.code == "FILE_NOT_FOUND":
                ...
    """
    CODES = frozenset({
        "FILE_NOT_FOUND",
        "PERMISSION_ERROR",
        "ENCODING_ERROR",
        "DISK_FULL",
        "INVALID_PATH",
        "DIRECTORY_NOT_FOUND",
        "DESTINATION_EXISTS",
    })

    def __init__(self, code: str, message: str, path: str = "") -> None:
        if code not in self.CODES:
            raise ValueError(f"Unknown FileHandlerError code: {code!r}")
        self.code = code
        self.path = path
        super().__init__(f"[FileHandler/{code}] {message}  (path={path!r})")


# ── abstract interface ────────────────────────────────────────────────────────

class IFileHandler:
    """
    Abstract contract.
    Every other module imports IFileHandler, not the concrete class.
    This lets us swap implementations each sprint without breaking callers.
    """

    def read(self, path: str) -> FilePayload:
        """
        Read a UTF-8 file and return a FilePayload.

        Jinie uses this for:
          • User uploaded reference PDFs / wireframes (text layer)
          • Generated Flutter/Dart files from the Compiler
          • Config files: pubspec.yaml, firebase.json, .env

        PRE  path non-empty; file exists; content is valid UTF-8
        POST FilePayload returned; READ entry added to internal log
        ERR  FileHandlerError(FILE_NOT_FOUND | ENCODING_ERROR | PERMISSION_ERROR)
        """
        raise NotImplementedError

    def write(self, path: str, content: str,
              overwrite: bool = True) -> WriteReceipt:
        """
        Write content to path. Parent dirs created automatically.

        Jinie uses this for:
          • Saving CodeT5-generated Dart widget files
          • Writing pubspec.yaml, main.dart, firebase.json
          • Saving the SRS document as markdown

        PRE  content is str; overwrite=False raises if file exists
        POST file on disk == content; WriteReceipt returned
        ERR  FileHandlerError(DESTINATION_EXISTS | PERMISSION_ERROR | DISK_FULL)
        """
        raise NotImplementedError

    def append(self, path: str, content: str) -> WriteReceipt:
        """
        Append content to path. Creates the file if it does not exist.

        Jinie uses this for:
          • Adding new widget code blocks to an existing Dart file
          • Appending log entries to the Logger's log file

        POST file = original bytes + new content bytes
        ERR  FileHandlerError(PERMISSION_ERROR)
        """
        raise NotImplementedError

    def delete(self, path: str) -> bool:
        """
        Delete a file.

        Jinie uses this for:
          • Cleaning up temp files after compilation
          • Removing failed build artifacts before retry

        POST  file does not exist on disk
        RETURNS True if deleted; False if already gone
        ERR   FileHandlerError(PERMISSION_ERROR)
        """
        raise NotImplementedError

    def move(self, src: str, dst: str,
             create_parents: bool = False) -> str:
        """
        Move src to dst.

        Jinie uses this for:
          • Moving compiled files into the final Flutter project folder

        POST  file at dst; src gone
        RETURNS absolute dst path
        ERR   FileHandlerError(FILE_NOT_FOUND | PERMISSION_ERROR)
        """
        raise NotImplementedError

    def copy(self, src: str, dst: str,
             create_parents: bool = False) -> str:
        """
        Copy src to dst.

        Jinie uses this for:
          • Duplicating template files before applying CodeEditor edits

        POST  identical file at dst; src unchanged
        RETURNS absolute dst path
        ERR   FileHandlerError(FILE_NOT_FOUND | PERMISSION_ERROR)
        """
        raise NotImplementedError

    def exists(self, path: str) -> bool:
        """Return True if path exists (file or directory)."""
        raise NotImplementedError

    def list_dir(self, path: str) -> list:
        """
        List directory contents sorted A→Z.

        Jinie uses this for:
          • Code Explorer (Module 15) building the file tree view
          • Deployment Manager packaging all files for Firebase upload

        POST  list[FileInfo] sorted case-insensitively by name
        ERR   FileHandlerError(DIRECTORY_NOT_FOUND)
        """
        raise NotImplementedError

    def get_log(self) -> list:
        """
        Return snapshot of the internal operation log (list[dict]).
        Logger module (Module 08) reads this for audit events.
        """
        raise NotImplementedError