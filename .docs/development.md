# Development & Setup Guide

This guide details how to set up your local development environment for the Jinie Desktop Application.

## Prerequisites

Ensure you have the following installed on your machine:
- **Node.js** (v18.0.0 or higher) & **npm**
- **Python** (v3.10 or higher) & **pip**
- **Git**

## Project Setup

Clone the repository and follow the steps below to configure your workspace.

### 1. Repository Layout
```text
jinie-desktop/
├── .docs/            # Project documentation files
├── backend/          # Python backend services
└── frontend/         # Frontend web application / desktop shell
```

---

### 2. Backend Setup (`backend/`)

The backend requires a Python virtual environment to manage package dependencies.

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment:**
   * **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Backend Service:**
   ```bash
   python main.py
   ```

---

### 3. Frontend Setup (`frontend/`)

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Package Dependencies:**
   ```bash
   npm install
   ```

3. **Start Frontend in Development Mode:**
   ```bash
   npm run dev
   ```

---

## Workspace Settings

To ensure consistent code styling and validation, configure your editor with:
- **Python Formatting:** Ruff or Black.
- **JavaScript Formatting:** Prettier.
- **Git Hooks:** Pre-commit hooks if configured.
