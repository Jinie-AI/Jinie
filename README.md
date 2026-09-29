# Jinie

### From a commerce application brief to a reviewable React Native project

Jinie is a browser-based workspace for creating, reviewing, customising and exporting commerce applications. Customers describe their idea, approve requirements, personalise screens and build an Expo/React Native project. The workspace brings together requirements documentation, design review, source editing, build checks and project persistence.

Developed by **Ahmad Hassan (B-Ted)**, **Ansa Anwaar**, **Kaneez Zehra**, and **Chaudry Ali Sher**.

> This README describes the updated Jinie implementation. Older downloaded snapshots may have a different folder structure. Use the matching updated source before following the commands below.

## Current workflow

**Prompt → Requirements → Screens → Build → Preview → Code / Evidence → Download or configured web hosting**

1. Enter a project name and describe the application.
2. Review, edit and accept the requirements.
3. Customise screen content, appearance and supported layouts.
4. Accept the screens and build the project.
5. Inspect the design, device sizes and available component previews.
6. Review source files and recorded checks, or return to Screens to make changes.
7. Download the current successful build or publish its browser output through configured hosting.

## Features

### Project input and management

- Named projects with saved requirements, design settings and revisions.
- English, Urdu and Roman Urdu text input; multilingual accuracy still requires evaluation.
- Supported reference uploads: PDF, text, Markdown, JSON and selected image formats, up to 2 MB.
- Browser-dependent dictation and optional local image-text extraction.
- Recent-project navigation and MongoDB-backed project persistence when configured.

### Requirements and documentation

- Editable screen-level functional requirements with identifiers and approval state.
- Five default quality targets covering performance, accessibility, security/privacy, persistence and responsiveness.
- A shared SRS structure used by the website, PDF export and exported Markdown.
- SRS sections: scope, FRs, NFRs, component tree, entities and relationships, sitemap, technology stack, traceability and release checks.
- Quality targets are requirements to verify, not measured compliance results.

### Screens and design

- Supported pages: Home, Catalogue, Product Details, Cart, Checkout, Search, Contact, About, Settings and Profile.
- Screen titles, subtitles, colours, typography choices, themes and navigation settings.
- Configurable Home/Catalogue compositions using hero, search, categories, collection, spotlight and statement blocks.
- Variations in section order, hero treatment, card style, image proportions, spacing and corners.
- Design controls integrated into the Screens workspace.
- Saved compositions validated before use.

### Preview and generated applications

- Shared accepted-design preview in Screens and the default Preview view.
- Mobile, tablet and desktop preview sizes.
- Isolated compiled component previews.
- Hidden scrollbar tracks inside application previews while scrolling remains available.
- Generated React Native behaviour for supported catalogue, search, product details, cart and demonstration checkout flows.
- Local storage adapters for supported application state.

**Preview distinction:** The default full-app view currently uses the design renderer. Selecting an individual component uses the compiled preview. The former full working-app toggle, perspective control and annotation feedback panel have been removed. The compiled application remains part of the generated output; design inspection alone does not verify its full behaviour.

### Source, evidence and exports

- Collapsible source-file explorer and highlighted source editing.
- Save and rebuild generated source.
- Requirement-to-screen, source-file and check relationships.
- Clickable source links in Evidence and requirement links in Code.
- Edit records identify linked requirements potentially affected by a source change.
- Checks for required files, preview artifacts, supported/unique page IDs, checkout dependencies, composition validity and package metadata.
- Stage logs, error reporting, cancellation at safe checkpoints and retry.
- Current-revision checks prevent stale project downloads.
- ZIP filename and enclosing folder use the customer project name followed by **-jinie**.

## Architecture

| Layer | Current responsibility |
|---|---|
| React / TypeScript website | Input, review, screen controls, preview, code browsing and evidence |
| Python / FastAPI backend | Validation, workflow coordination, source assembly, exports and build status |
| MongoDB | Project records when configured |
| SQLite | Local storage mode when MongoDB is unconfigured |
| Local runtime directory | Generated source files and compiled preview artifacts |
| React Native / Expo | Exported application project |
| React Native Web / esbuild | Browser compilation and preview output |
| ReportLab | Requirements PDF formatting |

The implementation uses **React Native and Expo rather than Flutter and Dart**. Project accounts currently use separate local account storage; MongoDB project storage does not automatically migrate accounts or provide a backend for generated customer applications.

## Module coverage

These are implementation areas, not a claim that every item in the original proposal is fully complete.

| Module | Delivered scope | Remaining boundary |
|---|---|---|
| 01 Utilities | Guarded files, source edits, exports and scaffolding | Universal formatting and environment automation |
| 02 Engine | Brief processing, saved state, review and build coordination | General contradiction handling and targeted regeneration |
| 03 Traceability | Requirement/file/check links and edit-impact records | Fine-grained dependency graph |
| 04 SRS Generator | Website, PDF and Markdown specifications | Prompt-specific NFR generation and atomic acceptance criteria |
| 05 Component Generator | Reusable components and validated compositions | Arbitrary component and screen types |
| 06 Compiler | Expo/React Native project and browser bundle | Verified signed native releases |
| 07 Tester | Structural checks and regression tests | Exhaustive behavioural, accessibility and device testing |
| 08 Logger | Timestamped stages, failures and edit records | Full release-health verification |
| 09 Deployment | Configured Firebase Hosting workflow | Automatic cloud-service provisioning |
| 10 Input Interface | Project brief, supported uploads and dictation control | Broad language, voice and image-input verification |
| 11 Design Preferences | Supported colours, fonts, themes, navigation and layouts | Unrestricted visual editing |
| 12 Progress and Status | Stages, logs, cancellation and retry | Resume from arbitrary checkpoints |
| 13 SRS Viewer and Editor | Requirement editing, approvals and complete document viewer | Selective downstream regeneration |
| 14 Live Review | Design/device review and isolated compiled components | Direct full-runtime review in the default view |
| 15 Code Explorer | File tree, edits, rebuild, trace links and ZIP export | Component-level dependency-aware editing |

## Active repository structure

```text
Jinie-main/
  backend/
    main.py
    requirements.txt
    .env.example
    studio/
      api.py                 # Project lifecycle and operations
      auth.py                # Local accounts and sessions
      store.py               # Project storage and guarded file paths
      screen_contract.py     # Supported pages and dependency rules
      composition.py         # Validated layout definitions
      compiler.py            # Project generation and bundling
      build_checks.py        # Build-artifact validation
      srs_document.py        # Shared specification content
      srs_pdf.py             # PDF export
      templates/             # React Native renderers
    component_library/       # Component reference catalogue
  frontend/
    src/
      pages/StudioPage.tsx    # Main workspace
      pages/AuthPage.tsx
      components/preview/
      components/studio/
      styles/
    package.json
    vite.config.ts
  scripts/                   # Startup, build, migration and validation tools
  tests/                     # Automated regression checks
  models/                    # Local processing assets
  training/                  # Training and evaluation assets
  runtime/                   # Generated projects; do not delete to clean up docs
```

Historical documentation and examples folders have been removed from the updated working project. Installed dependencies and runtime artifacts are not substitutes for source-controlled application files.

## Setup on Windows

Use a current Node.js 22 release (22.12 or later) or Node.js 24, and a Python version compatible with the pinned backend dependencies. The existing development environment has run with Python 3.14. Git is required only for version control; Firebase tooling is optional for hosting.

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm --prefix frontend install
```

Review backend/.env.example and create backend/.env for your local configuration. Keep credentials private and outside version control. Model files and environment-dependent integrations must be available where configured; startup does not provision all services automatically.

### Run the backend

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

If the terminal is already inside backend:

```powershell
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Run the frontend

Open a second terminal in the project root:

```powershell
cd frontend
npm run dev
```

Open http://localhost:5173, or the address printed by Vite if that port is busy. Keep both terminals running.

## MongoDB project storage

Set these privately in backend/.env:

```env
MONGODB_URI=your_actual_connection_string
MONGODB_DATABASE=jinie
```

Allow the backend computer's address in the database network settings. Stop the backend before migrating, then run from the project root:

```powershell
.\.venv\Scripts\python.exe scripts/mongodb_setup.py --migrate
```

This verifies the connection and copies SQLite project records without overwriting matching MongoDB records. Original SQLite data remains available. Restart the backend afterward.

An empty connection setting retains SQLite mode. A configured but unreachable MongoDB connection fails explicitly rather than silently saving into another database.

**Keep runtime:** MongoDB stores project records, but generated files and preview bundles still live on the host computer. Deleting runtime breaks access to those existing outputs.

## Verification

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
npm --prefix frontend run build
npm --prefix frontend run lint
node scripts/test-native-renderer.mjs
node scripts/test-product-card-validation.mjs
```

Tests cover workflow rules, composition validation, documentation, storage and build-related behaviour. The regression fixture disables the live MongoDB setting for isolated testing.

A successful bundle or page-presence check does not prove every customer requirement. Native startup checks are not physical-device acceptance tests. Review failed and not-run checks in Evidence before presenting a build as verified.

## Hosting and export

ZIP export is available after a successful build of the current revision. It contains generated source, available browser output and SRS Markdown.

Firebase Hosting requires installed Firebase tools, a logged-in account and JINIE_FIREBASE_PROJECT configured on the backend. The active deployment handler publishes the browser build only. It does not automatically configure customer authentication, database rules or storage services.

App Store and Play Store publication are currently disabled. React Native source export is not a signed mobile release.

## Current limitations

- Supported commerce screens and block types define the generation scope.
- The design renderer and generated renderer are separate; pixel equivalence is not guaranteed.
- NFRs are default targets rather than measured results for each project.
- Checkout creates local demonstration orders without charging real payments.
- Login exists, but project ownership enforcement and production session management remain incomplete.
- Source regeneration can overwrite generated files; selective merging is not implemented.
- Real-device, accessibility, performance, backup/recovery and public deployment checks remain necessary.
- The project should not be treated as a fully verified public multi-user production service.

## Repository hygiene

Keep environment files, database credentials, runtime data, virtual environments and dependency folders out of commits. Temporary files and Python caches can be removed; runtime, model assets and active build scripts should be retained. Save exported documents separately if they are not needed in the repository.
