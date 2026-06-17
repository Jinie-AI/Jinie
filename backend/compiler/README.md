# Backend Compiler Module

The Compiler takes generated components (from Module 5), functional requirements/sitemap (from Module 4), and compiles them into a single coherent application project folder.

## Submodules

### 1. Compiler Engine (`compiler.py`)
Wires up page navigation, integrates state managers, injects static data, and generates the entry points (`App.tsx`, `package.json`, `app.json`, navigation routes) of the React Native (with Expo) project.
