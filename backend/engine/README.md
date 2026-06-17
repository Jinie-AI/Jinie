# Backend Engine Module

The Engine is the intelligence center of the backend. It is the module that understands what the user is trying to build, maintains the project's memory, decides on the next processing task, and manages user feedback.

## Submodules

### 1. Engine Reframer (`reframer.py`)
Intercepts raw user input, handles corrections, disambiguates contradictory commands, and translates Urdu-English code-switching into a clean, canonical problem statement for the generators.

### 2. Customer Feedback (`feedback.py`)
Routes user corrections, ratings, and comments directly back to the active generation module, enabling iterative optimization of generated resources.

### 3. Current State (`state.py`)
Maintains a live, in-memory snapshot of all generated artifacts (requirements, design parameters, sitemap, source code files, and build/test logs). It serves as the single source of truth for the workspace.
