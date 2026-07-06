"""
backend/utilities/file_handler/file_handler.py
===============================================
Concrete implementation of IFileHandler for the Jinie project.

Sprint 1  :  read, write, append, delete, move, copy, exists, list_dir
Sprint 2  :  binary support for uploaded images/PDFs, richer mime detection

Where this sits in the Jinie pipeline
--------------------------------------
  [User uploads wireframe / Compiler saves Dart file]
                    │
                    ▼
          FileHandler.read(path)
                    │
                    ▼   FilePayload
          CodeEditor.load_file(payload)   ← next submodule
"""

import os
import uuid
import shutil
import mimetypes
from datetime import datetime, timezone
from pathlib import Path

from backend.utilities.file_handler.file_handler_contract import (
    IFileHandler,
    FilePayload,
    WriteReceipt,
    FileInfo,
    FileHandlerError,
)


# ── private helpers ───────────────────────────────────────────────────────────

def _make_trace_id() -> str:
    """Every operation gets a unique ID registered in Traceability Matrix."""
    return f"FH-{uuid.uuid4()}"


def _resolve(path: str) -> str:
    """Return absolute, normalised path string."""
    return str(Path(path).resolve())


def _validate(path: str) -> None:
    """Raise INVALID_PATH if path is empty or blank."""
    if not path or not path.strip():
        raise FileHandlerError(
            "INVALID_PATH",
            "path must be a non-empty string.",
            path,
        )


def _log_entry(op: str, path: str, tid: str,
               extra: dict | None = None) -> dict:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": op,
        "path":      path,
        "trace_id":  tid,
    }
    if extra:
        entry.update(extra)
    return entry


# ── implementation ────────────────────────────────────────────────────────────

class FileHandler(IFileHandler):
    """
    The only class in Jinie that is allowed to touch the filesystem.

    Quick usage
    -----------
        fh = FileHandler()

        # Engine reads a user-uploaded reference file
        payload = fh.read("/uploads/wireframe.txt")

        # Compiler saves a generated Dart widget
        fh.write("/project/lib/widgets/product_card.dart", dart_code)

        # Hand payload to CodeEditor for edits
        code_payload = CodeEditor().load_file(payload).get_payload()
    """

    def __init__(self) -> None:
        # Logger (Module 08) reads this via get_log()
        self._log: list[dict] = []

    # ── read ──────────────────────────────────────────────────────────────────

    def read(self, path: str) -> FilePayload:
        """
        Read a UTF-8 text file and return a FilePayload.

        In Jinie this is called for:
          • User-uploaded reference files (text/wireframe descriptions)
          • Generated Dart files from the Compiler before CodeEditor edits
          • pubspec.yaml, firebase.json, .env config files

        OUTPUT → FilePayload → CodeEditor.load_file(payload)
        """
        _validate(path)
        absp = _resolve(path)
        tid  = _make_trace_id()

        # file must exist
        if not os.path.isfile(absp):
            raise FileHandlerError("FILE_NOT_FOUND",
                                   "File does not exist.", absp)

        # read raw bytes
        try:
            raw_bytes = Path(absp).read_bytes()
        except PermissionError:
            raise FileHandlerError("PERMISSION_ERROR",
                                   "Read permission denied.", absp)

        # decode — Jinie works only with UTF-8 text files
        try:
            raw_content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise FileHandlerError(
                "ENCODING_ERROR",
                "File is not valid UTF-8. "
                "Binary files (images, compiled PDFs) are Sprint 2.",
                absp,
            )

        ext       = Path(absp).suffix.lower()
        mime, _   = mimetypes.guess_type(absp)
        size      = len(raw_bytes)

        payload = FilePayload(
            path        = absp,
            raw_content = raw_content,
            encoding    = "utf-8",
            size_bytes  = size,
            extension   = ext,
            trace_id    = tid,
            mime_type   = mime or "",
        )

        self._log.append(_log_entry("READ", absp, tid,
                                    {"size_bytes": size,
                                     "extension":  ext}))
        return payload

    # ── write ─────────────────────────────────────────────────────────────────

    def write(self, path: str, content: str,
              overwrite: bool = True) -> WriteReceipt:
        """
        Write content to path. Creates parent directories automatically.

        In Jinie this is called for:
          • Saving CodeT5-generated Dart widget code
          • Writing main.dart, pubspec.yaml, firebase.json
          • Saving the SRS document as a .md file
        """
        _validate(path)
        absp = _resolve(path)
        tid  = _make_trace_id()

        if not overwrite and os.path.exists(absp):
            raise FileHandlerError(
                "DESTINATION_EXISTS",
                "File already exists. Pass overwrite=True to replace it.",
                absp,
            )

        overwritten = os.path.exists(absp)
        Path(absp).parent.mkdir(parents=True, exist_ok=True)

        try:
            encoded = content.encode("utf-8")
            Path(absp).write_bytes(encoded)
        except PermissionError:
            raise FileHandlerError("PERMISSION_ERROR",
                                   "Write permission denied.", absp)
        except OSError as exc:
            if "No space left" in str(exc):
                raise FileHandlerError("DISK_FULL",
                                       "No space left on device.", absp)
            raise FileHandlerError("PERMISSION_ERROR", str(exc), absp)

        receipt = WriteReceipt(
            success       = True,
            path          = absp,
            bytes_written = len(encoded),
            trace_id      = tid,
            overwritten   = overwritten,
        )
        self._log.append(_log_entry("WRITE", absp, tid, {
            "bytes_written": len(encoded),
            "overwritten":   overwritten,
        }))
        return receipt

    # ── append ────────────────────────────────────────────────────────────────

    def append(self, path: str, content: str) -> WriteReceipt:
        """
        Append content to path. Creates the file if it does not exist.

        In Jinie this is called for:
          • Adding new widget blocks to an existing Dart file
          • Logger appending audit events to a log file
        """
        _validate(path)
        absp = _resolve(path)
        tid  = _make_trace_id()

        Path(absp).parent.mkdir(parents=True, exist_ok=True)

        try:
            encoded = content.encode("utf-8")
            with open(absp, "ab") as f:
                f.write(encoded)
        except PermissionError:
            raise FileHandlerError("PERMISSION_ERROR",
                                   "Append permission denied.", absp)

        receipt = WriteReceipt(
            success       = True,
            path          = absp,
            bytes_written = len(encoded),
            trace_id      = tid,
            overwritten   = False,
        )
        self._log.append(_log_entry("APPEND", absp, tid,
                                    {"bytes_written": len(encoded)}))
        return receipt

    # ── delete ────────────────────────────────────────────────────────────────

    def delete(self, path: str) -> bool:
        """
        Delete a file.
        Returns True if deleted, False if it was already gone.

        In Jinie this is called for:
          • Cleaning up temp build files after compilation
          • Removing failed Dart files before regeneration
        """
        _validate(path)
        absp = _resolve(path)
        tid  = _make_trace_id()

        if not os.path.exists(absp):
            self._log.append(_log_entry("DELETE_SKIP", absp, tid,
                                        {"reason": "file not found"}))
            return False

        try:
            os.remove(absp)
        except PermissionError:
            raise FileHandlerError("PERMISSION_ERROR",
                                   "Delete permission denied.", absp)

        self._log.append(_log_entry("DELETE", absp, tid))
        return True

    # ── move ──────────────────────────────────────────────────────────────────

    def move(self, src: str, dst: str,
             create_parents: bool = False) -> str:
        """
        Move src to dst. Returns absolute dst path.

        In Jinie this is called for:
          • Moving compiled files into the final Flutter project folder
        """
        _validate(src)
        _validate(dst)
        abs_src = _resolve(src)
        abs_dst = _resolve(dst)
        tid     = _make_trace_id()

        if not os.path.exists(abs_src):
            raise FileHandlerError("FILE_NOT_FOUND",
                                   "Source does not exist.", abs_src)

        if create_parents:
            Path(abs_dst).parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(abs_src, abs_dst)
        except PermissionError:
            raise FileHandlerError("PERMISSION_ERROR",
                                   "Move permission denied.", abs_src)

        self._log.append(_log_entry("MOVE", abs_src, tid,
                                    {"destination": abs_dst}))
        return abs_dst

    # ── copy ──────────────────────────────────────────────────────────────────

    def copy(self, src: str, dst: str,
             create_parents: bool = False) -> str:
        """
        Copy src to dst. Returns absolute dst path.

        In Jinie this is called for:
          • Copying template Dart files before CodeEditor applies edits
        """
        _validate(src)
        _validate(dst)
        abs_src = _resolve(src)
        abs_dst = _resolve(dst)
        tid     = _make_trace_id()

        if not os.path.exists(abs_src):
            raise FileHandlerError("FILE_NOT_FOUND",
                                   "Source does not exist.", abs_src)

        if create_parents:
            Path(abs_dst).parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(abs_src, abs_dst)
        except PermissionError:
            raise FileHandlerError("PERMISSION_ERROR",
                                   "Copy permission denied.", abs_src)

        self._log.append(_log_entry("COPY", abs_src, tid,
                                    {"destination": abs_dst}))
        return abs_dst

    # ── exists ────────────────────────────────────────────────────────────────

    def exists(self, path: str) -> bool:
        """Return True if path exists (file or directory)."""
        _validate(path)
        return os.path.exists(_resolve(path))

    # ── list_dir ──────────────────────────────────────────────────────────────

    def list_dir(self, path: str) -> list[FileInfo]:
        """
        List directory contents sorted A→Z by name.

        In Jinie this is called for:
          • Code Explorer (Module 15) building the file tree view
          • Deployment Manager packaging all files for Firebase
        """
        _validate(path)
        absp = _resolve(path)

        if not os.path.isdir(absp):
            raise FileHandlerError("DIRECTORY_NOT_FOUND",
                                   "Path is not a directory.", absp)

        entries: list[FileInfo] = []
        for e in sorted(os.scandir(absp), key=lambda x: x.name.lower()):
            st = e.stat()
            entries.append(FileInfo(
                name         = e.name,
                path         = str(Path(e.path).resolve()),
                size_bytes   = st.st_size if e.is_file() else 0,
                extension    = Path(e.name).suffix.lower() if e.is_file() else "",
                is_directory = e.is_dir(),
            ))
        return entries

    # ── log ───────────────────────────────────────────────────────────────────

    def get_log(self) -> list[dict]:
        """
        Return snapshot of the internal log.
        Module 08 (Logger) reads this for audit and preflight checks.
        """
        return list(self._log)