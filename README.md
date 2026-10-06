# Jinie

Jinie is a prompt-driven application design and generation workspace. Customers describe an application, review its requirements, customize its screens, build a working preview, inspect the generated source, and download a React Native project.

The authoring website uses React and TypeScript. Generated applications use React Native, Expo and React Native Web. The backend uses Python and FastAPI.

## Project workflow

1. Enter an application brief, optionally using browser dictation or an uploaded reference.
2. The Engine normalizes the brief and combines intake predictions, explicit screen requests, exclusions, component retrieval and optional architecture planning.
3. Review functional requirements and the shared Software Requirements Specification.
4. Accept the requirements and review the proposed screens in the Screens workspace.
5. Adjust colours, typography, navigation, layout, titles and supported screen options.
6. Accept the screens and build the application preview.
7. Test the generated application, inspect its code and traceability, and rebuild after changes.
8. Download the current build or deploy its web preview to configured Firebase Hosting.

Saved projects retain their configuration and generated artifacts. Changes to the generator apply to newly generated or rebuilt projects; an existing saved preview does not update automatically.

## Features

### Prompt and requirement processing

- Free-text application briefs with optional reference content.
- Browser speech recognition for dictation where the browser supports it.
- Local trained intake and layout checkpoints with rules-based fallbacks.
- Explicit screen inclusion and exclusion handling.
- Detection of named custom pages outside the trained screen labels.
- Stable requirement identifiers, editable descriptions and approval states.
- Optional architecture planning for richer screen configurations and compositions.

### Screens and appearance

- Home, Products, Product Details, Cart, Checkout, Search, Contact, About, Profile and Settings screens.
- Domain-specific catalogue aliases, including clothes and laptop models, map to the interactive Products screen.
- Custom information screens with separately scoped sections and labelled fields.
- Colour, theme, heading font, body font and navigation customization.
- Supported collection compositions include grids, cards, editorial layouts, rails and mosaics.
- Screen configuration is passed through to generated application source.
- Phone, tablet and desktop preview controls.
- Custom screen labels are displayed without internal `custom_` prefixes in the main review controls.

### Generated shopping interactions

- Product cards open product details when the Detail screen is available.
- Clearly labelled Add to cart controls when Cart is included.
- Cart quantity changes, removal and subtotal calculation.
- Search and category filtering.
- Local name/address validation and cash-on-delivery demonstration checkout.
- Local shopping and preference persistence through the generated storage adapters.

These are prototype interactions. Checkout does not process a real payment or fulfil an order.

### Software Requirements Specification

The website and PDF/Markdown exports share the same SRS source. It contains:

- Scope, revision and approval information.
- Functional requirements with traceability IDs and configuration-based acceptance checks.
- Non-functional requirements selected according to project scope.
- Component tree derived from the configured screens.
- Conceptual entities and relationships.
- Sitemap and supported navigation.
- Technology stack information.
- Traceability and release checks.

Quality targets and proposed acceptance checks are specifications, not evidence that performance, accessibility or security testing has passed.

### Source, evidence and export

- Generated source listing and editing with rebuild support.
- Component catalogue retrieval and reference associations per screen.
- Requirement-to-artifact traceability.
- Structural checks for generated files, routes, compositions and preview artifacts.
- Project event logs, build status, cancellation and feedback recording.
- Downloads named `<Customer Project Name>-jinie.zip`.
- ZIP exports include application source, the compiled web build and `SRS.md`.

### Workspace accounts

- Signup and login screens.
- Salted PBKDF2-HMAC-SHA256 password hashing and constant-time password comparison.
- In-memory session tokens with expiry.

The current project workspace is intended for local, single-user operation. Account functionality does not yet provide complete production-grade project isolation or a backend for generated customer applications.

## Models and component retrieval

| Resource | Role | Location |
| --- | --- | --- |
| DistilBERT | Predicts supported intake labels such as domain, style and screens; explicit prompt rules refine the result | `models/intake/` |
| Random Forest | Ranks supported layout options from domain, page and style | `models/layout.joblib` |
| CodeT5 | Produces specialized ProductCard candidates that undergo validation | `models/code/` |
| Component RAG | Retrieves relevant catalogue references using TF-IDF and cosine similarity | `backend/component_library/` and `backend/modules/component_generator/retrieval.py` |
| Architecture planner | Refines requirements, custom sections, design tokens and supported compositions when configured | `backend/modules/engine/` |

The compiler assembles the executable project from validated configuration and supported renderer components. Retrieved references guide planning; they are not automatically installed as third-party code. CodeT5 candidates are retained as inspectable artifacts after checks, while the accepted base screen component is preserved.

Checkpoint weights are loaded locally. Missing or unusable checkpoints activate the available fallback logic. Adding dataset rows does not update a model until training runs and the resulting checkpoint is installed.

## Backend modules

| Module | Directory | Responsibility |
| --- | --- | --- |
| 01 Utilities | `backend/modules/utilities/` | Project storage, accounts and performance helpers |
| 02 Engine | `backend/modules/engine/` | Brief normalization, intake, layout recommendations, planning and API orchestration |
| 03 Traceability Manager | `backend/modules/traceability_manager/` | Stable identifiers and requirement-to-artifact links |
| 04 SRS Generator | `backend/modules/srs_generator/` | Shared SRS generation and exports |
| 05 Component Generator | `backend/modules/component_generator/` | Catalogue, RAG retrieval, compositions and custom screen validation |
| 06 Compiler | `backend/modules/compiler/` | Application assembly and preview bundling |
| 07 Tester | `backend/modules/tester/` | Structural generated-artifact checks |
| 08 Logger | `backend/modules/logger/` | Project event recording |
| 09 Deployment Manager | `backend/modules/deployment_manager/` | Configured Firebase Hosting deployment |

The SRS module has separate requirement, FR, NFR, sitemap, component tree, entity and technology stack files, plus the shared document and PDF renderer.

Old Python compatibility files under `backend/studio/` and the old `backend/deployment/` wrapper were removed after updating their imports. `backend/studio/templates/` remains necessary: it contains the renderer templates used by compilation and verification scripts.

## Repository layout

```text
backend/
  main.py                   FastAPI entry point
  requirements.txt          Backend dependencies
  run_backend.ps1           Windows backend launcher
  modules/                  Active backend implementations
  component_library/        Retrieval catalogue and index resources
  studio/templates/         Generated React Native renderer templates
  data/                     Local account data
frontend/
  src/                      React/TypeScript authoring website
  public/                   Public assets
  dist/                     Built website
models/                     Local inference checkpoints
training/
  data/                     Training datasets and audit metadata
  01_DistilBERT.ipynb        Intake training notebook
  02_RandomForest.ipynb      Layout training notebook
  03_CodeT5.ipynb            Component training notebook
  train_intake.py            Intake training entry point
  train_layout.py            Layout training entry point
  train_code.py              Component training entry point
scripts/                    Build, validation and maintenance tools
tests/                      Regression tests
runtime/                    Saved projects and generated builds
tmp/                        Local backups and working artifacts
```

## Install and run

Run these commands from the repository root in PowerShell. Use the project virtual environment consistently; launching a different Python installation can cause missing dependencies or incompatible model-loading versions.

### Initial installation

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd frontend
npm install
cd ..
```

Use a Python version supported by the pinned transformer and scikit-learn packages. Node.js and npm are also required for the website and preview compiler. Keep scikit-learn at the project's pinned version when loading its existing Random Forest checkpoint.

### Backend

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Alternatively, from the repository root:

```powershell
.\backend\run_backend.ps1
```

Backend health: `http://127.0.0.1:8000/api/health`.
Interactive route documentation: `http://127.0.0.1:8000/docs`.

### Frontend

In a separate terminal, from the repository root:

```powershell
cd frontend
npm run dev
```

Open the address Vite prints, usually `http://localhost:5173`.

### Production website build

```powershell
cd frontend
npm run build
npm run preview
```

The build output is written to `frontend/dist/`.

## Configuration and storage

The backend reads its local `.env` file and existing shell environment. Keep private credentials outside tracked source files.

| Variable | Purpose |
| --- | --- |
| `JINIE_STORAGE=sqlite` | Explicitly select SQLite even if a MongoDB URI is present |
| `JINIE_DATA_DIR` | Override the project/artifact directory; defaults to `runtime/` |
| `JINIE_WARM_MODELS` | Set to `0` to skip background checkpoint warmup |
| `JINIE_ALLOWED_ORIGINS` | Configure the explicit frontend origins in the backend CORS settings |
| `MONGODB_URI` | Optional private MongoDB connection URI |
| `MONGODB_DATABASE` | Optional MongoDB database name; defaults to `jinie` |
| `JINIE_FIREBASE_PROJECT` | Firebase project used by Hosting deployment |

SQLite is the local default when no MongoDB URI is configured. MongoDB remains optional; a configured but unreachable database can prevent startup. For temporary local operation, set `JINIE_STORAGE=sqlite` in `backend/.env`.

`runtime/` holds saved project state and generated applications. Deleting it can remove projects and previews. Python bytecode caches and `.pytest_cache/` are disposable and regenerate automatically.

## Deployment

The Deployment Manager publishes the current web preview to Firebase Hosting when the backend machine has the CLI, credentials and project configured.

```powershell
npm install -g firebase-tools
firebase login
$env:JINIE_FIREBASE_PROJECT = "your-project-id"
```

Start the backend from that shell, build the current project revision, and use the Deploy page. Firebase Hosting deployment does not publish native applications to App Store or Google Play.

## Verification

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Frontend verification:

```powershell
cd frontend
npm run build
```

Regression tests cover prompt rules, exclusions, custom-screen field separation, component retrieval, planning contracts, SRS exports, storage and generated build/export workflows. Generated-artifact checks are structural checks; real-device interaction, performance and accessibility testing still require separate verification.

## Current limitations

- Custom information pages render labelled fields and sections. Arbitrary editable records, booking systems and remote integrations need additional implementation.
- Unprovided customer and patient values remain empty; the generator does not invent personal records.
- The current planner and renderer support a bounded screen contract and a maximum of ten screens per project.
- Catalogue imagery is drawn from available sample photography; the project does not generate arbitrary new product photographs.
- Local demonstration checkout does not process payments or submit orders to a fulfilment backend.
- Settings controls do not deliver push notifications.
- Native store publishing, production authorization, secure multi-user project ownership and comprehensive device testing remain additional work.
- Generated screens are constrained by available components, validated configurations and renderer support. Completely new functionality requires executable actions as well as a visual layout.

## Sample prompt

> Create a skincare shop with home, products, product details and cart. Add a doctor information page with fields: doctor name, specialization, clinic and contact number. Add a medical record page with fields: patient name, patient ID, patient condition and skin colour. Add a warranty page with fields: warranty number, coverage and expiry date. Keep each page's fields separate. Never invent patient information. Do not add settings.

The requested result is seven screens: Home, Products, Product Details, Cart, Doctor Information, Medical Record and Warranty. The custom pages are information displays, while the catalogue/detail/cart flow provides the supported shopping interactions.
