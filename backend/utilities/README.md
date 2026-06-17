# Backend Utilities Module

The Utilities module is the shared service floor that all other modules build on. It is a collection of independently callable tools for file I/O, code editing, format conversion, style enforcement, environment setup, and quality checking.

## Submodules

### 1. File Handler (`file_handler.py`)
Responsible for every read, write, move, copy, and delete operation on files in the workspace. No direct filesystem access is allowed from other modules; all file operations go through this submodule to maintain auditability.

### 2. Code Editor (`code_editor.py`)
Handles programmatic changes to source files (inserting new lines, deleting blocks, replacing tokens, and applying formatting rules) without opening a visual editor.

### 3. MD Converter (`md_converter.py`)
Translates between Markdown and other formats (such as HTML or plain text) for requirements documents import/export.

### 4. Reformatter (`reformatter.py`)
Applies consistent style (indentation, line length limits, naming conventions, and whitespace rules) to generated code.

### 5. Environment Setup Manager (`env_setup.py`)
Installs the correct package versions, creates configuration files, sets environment variables, and scaffolds folder structures for the technology stack.

### 6. Verification & Validation (`vv.py`)
Acts as a quality gate checking that artifacts are built correctly according to specification (Verification) and satisfy user requirements (Validation).
