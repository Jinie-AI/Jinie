# Backend SRS Generator Module

The SRS (Software Requirements Specification) Generator takes the structured engine state and translates it into a detailed, formal specification layout detailing how the system should function. Downstream modules use this specification as their primary source of scope.

## Submodules

### 1. Requirement Generator (`requirement.py`)
Reads parsed user goals and translates them into list items describing functional and constraints boundaries, assigning each a unique trace ID.

### 2. Sitemap Generator (`sitemap.py`)
Produces a structured navigation layout mapping all pages, layouts, and route transitions (e.g. Home, Product Detail, Cart).

### 3. Functional Requirement Generator (`functional.py`)
Enumerates specific operations and data handling rules mapping directly to each screen element or transaction.

### 4. Non-Functional Requirement Generator (`non_functional.py`)
Fills out constraint metrics (response speed limits, accessibility settings, standard layout conventions).

### 5. Technology Stack Identifier (`stack_identifier.py`)
Matches constraints and sitemap requirements to recommend libraries, databases, and dependencies compatible with the project goal.
