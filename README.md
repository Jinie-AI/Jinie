# <div align="center">🧞 Jinie</div>

<p align="center">
  <img src=".docs/assets/logo-banner.png" alt="Jinie Logo Banner" width="100%" />
</p>

## <div align="center">AI-Driven UI to React Native Application Generation</div>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](#)
[![Node Version](https://img.shields.io/badge/node-18%2B-green.svg)](#)
[![Vite](https://img.shields.io/badge/vite-8.x-indigo.svg)](#)
[![React Native Compatibility](https://img.shields.io/badge/react--native-Expo%20CLI-cyan.svg)](#)
[![Developers](https://img.shields.io/badge/Developers-Team%20Jinie-orange.svg)](#)

</div>

---

### <div align="center">"Bridging the space between imagination and production-ready mobile code."</div>

Jinie is an intelligent, localized desktop pipeline engineered by **Ahmad Hassan (B-Ted)**, **Ansa Anwaar**, **Kaneez Zehra**, and **Chaudry Ali Sher**. It transforms plain text descriptions-supporting English, Urdu, and code-mixed Urdu-English (Roman Urdu)-into complete, runnable, and Firebase-hosted React Native (with Expo) applications.

Rather than wrapping public third-party APIs, Jinie utilizes self-trained, specialized machine learning models to classify requirements, recommend screen layouts, and generate component hierarchies. This architectural choice secures speed, reproducibility, and full local execution capability.

---

## 🧭 Architecture Overview

Jinie relies on a decoupled, client-server desktop model. The frontend desktop client hosts the interface controls, and the Python service layer handles NLP requirement processing, code compilation, and preflight testing.

```mermaid
graph TB
    subgraph Frontend_Container [Frontend Desktop Client]
        10[Module 10: Input UI]
        11[Module 11: Design Panel]
        12[Module 12: Progress Stepper]
        13[Module 13: Requirements Editor]
        14[Module 14: Live Sandbox Review]
        15[Module 15: Code Explorer]
    end

    subgraph Backend_Service [Local Python Backend Service]
        M02[Module 02: Engine Coordinator]
        M01[Module 01: Utilities System]
        M03[Module 03: Traceability Matrix]
        M04[Module 04: SRS Requirements Generator]
        M05[Module 05: UI Component Synthesizer]
        M06[Module 06: Project Scaffolder & Compiler]
        M07[Module 07: Automated Use-case Tester]
        M08[Module 08: Preflight Boot Check & Logger]
        M09[Module 09: Firebase Deployment Manager]
    end

    %% Communication
    Frontend_Container <==>|Localhost REST & WebSockets| Backend_Service

    %% Engine routing
    10 -.->|Raw Prompts| M02
    11 -.->|Visual Tokens| M05
    M02 ===> M04
    M04 -.->|Sitemap & IDs| M03
    M04 ===> M05
    M05 ===> M06
    M06 ===> M07
    M07 ===> M08
    M08 ===> M09

    %% Output feeds
    M04 ---->|Interactive Specs| 13
    M06 ---->|Rendering Source| 14
    M06 ---->|Workspace Tree| 15
    M09 ---->|Hosting URL & Stepper Events| 12
```

---

## ⚡ System Workflow

The generation pipeline moves through seven distinct checkpoints:

```mermaid
stateDiagram-v2
    [*] --> Prompt_Intake : 1. Freeform English / Urdu prompt
    Prompt_Intake --> SRS_Generation : 2. DistilBERT extracts requirements & sitemap
    SRS_Generation --> Design_Tokens : 3. User chooses colors, fonts, and layouts
    Design_Tokens --> User_Approval : 4. User reviews and approves functional specs
    User_Approval --> Compilation : 5. CodeT5-small generates React Native component files
    Compilation --> Verification_Testing : 6. Simulator boot checks & integration tests
    Verification_Testing --> Live_Deployment : 7. Firebase helper publishes app
    Live_Deployment --> [*]
```

---

## 📦 Internal Module Structure

### Backend Modules (`backend/`)

| Module                      | Submodule / File                                                                | Responsibility                                                                            |
| :-------------------------- | :------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------- |
| **01. Utilities**           | `file_handler`, `code_editor`, `md_converter`, `reformatter`, `env_setup`, `vv` | File operations, formatting, markdown parses, environment setup, and verification checks. |
| **02. Engine**              | `reframer`, `feedback`, `state`                                                 | Maintains state snapshots, rewrites inputs, routes user reviews.                          |
| **03. Traceability**        | `id_assigner`                                                                   | Allocates unique hierarchical trace identifiers to elements.                              |
| **04. SRS Generator**       | `requirement`, `sitemap`, `functional`, `non_functional`, `stack_identifier`    | Requirement classifiers, sitemap builders, stack identifiers.                             |
| **05. Component Generator** | `generator`                                                                     | Selects layouts using design tokens; curates React Native component code.                 |
| **06. Compiler**            | `compiler`                                                                      | Links components, styles, and scaffold configs.                                           |
| **07. Tester**              | `tester`                                                                        | Generates and executes test suites on compiled code.                                      |
| **08. Logger**              | `logger`                                                                        | Tracks operations; performs preflight checks and login validation.                        |
| **09. Deployment**          | `firebase_helper`                                                               | Configures and deploys build assets to Firebase Hosting.                                  |

### Frontend UI Components (`frontend/src/components/`)

| Component Folder      | Module    | Subcomponents                                                             | Key Responsibility                                             |
| :-------------------- | :-------- | :------------------------------------------------------------------------ | :------------------------------------------------------------- |
| **InputInterface**    | Module 10 | `PromptInputBox`, `FileUploader`                                          | Freeform text intake area and attachments coordinator.         |
| **DesignPreferences** | Module 11 | `ColorPalette`, `Typography`, `LayoutMode`, `ThemeToggle`                 | Dynamic styling configuration swatches.                        |
| **ProgressStatus**    | Module 12 | `StageTracker`, `LiveLogStream`, `ErrorAlerts`, `Controls`                | Progress monitor, real-time log terminal, build controls.      |
| **SRSViewer**         | Module 13 | `RequirementListView`, `InlineEditor`, `ApprovalToggle`, `IDBadgeDisplay` | Requirement verification grid, inline editors, and check-offs. |
| **LiveReview**        | Module 14 | `ComponentPreview`, `FullAppPreview`, `DeviceToggle`, `FeedbackCapture`   | Sandboxed simulator displaying preview components.             |
| **CodeExplorer**      | Module 15 | `FileTreeView`, `SyntaxEditor`, `DownloadZIP`, `TraceabilityLink`         | File browser and ZIP packaging bundle triggers.                |

---

## 🔄 Data Flow

The flow of inputs and outputs through the self-trained ML model endpoints is structured as follows:

```mermaid
flowchart LR
    UserInput([Raw Text / Attachments]) -->|Engine Reframer| ProblemSpec[Structured Goal Object]
    ProblemSpec -->|DistilBERT NLP Intake| SRS[SRS Document & Sitemap]
    SRS -->|Random Forest Layout Recommender| ScreenTemplates[Component Layout Mapping]
    ScreenTemplates -->|CodeT5-small Generator| TSXCode[React Native Component TSX Code]
    TSXCode -->|Compiler Assembly| RNApp[Executable Project Bundle]
    RNApp -->|Preflight Diagnostics| TestedApp[Verified React Native Package]
    TestedApp -->|Firebase Hosting Deploy| ProductionURL([Active Web Preview URL])
```

---

## 🛠️ Request Lifecycle & Build Pipeline

<details>
<summary>🔍 View Detailed Request Lifecycle</summary>

1. **Intake**: A text prompt (e.g. Roman Urdu text outlining product pages) is submitted through the `PromptInputBox`.
2. **Reframing**: The `EngineReframer` translates colloquialisms and prepares a standardized problem target.
3. **Extraction**: `RequirementGenerator` triggers the local `DistilBERT` classifier to list required categories and screens.
4. **Site Scaffolding**: `SitemapGenerator` configures navigation paths.
5. **Interactive Checkpoint**: The client app renders the specification list. Execution pauses until requirements are checked and approved.
6. **Component Compilation**: Once approved, the `ComponentGenerator` reads styling tokens and triggers `CodeT5-small` iterations, building React Native component TSX code.
7. **Scaffolding Integration**: The `Compiler` packages the code, inserting imports, package.json dependencies, and Expo configurations.
8. **Automated Verification**: `Tester` triggers Jest/Expo component check suites.
9. **Boot Safety Check**: The `Logger` verifies the application boots cleanly, executing authentication endpoints.
10. **Cloud Deploy**: `FirebaseHelper` packages the assets and pushes them live.
</details>

---

## 📂 Repository Structure

```text
jinie-desktop/
├── .docs/                  # Conceptual & technical documentation index
│   ├── README.md           # Documentation guide
│   ├── api.md              # REST & WebSockets contracts
│   ├── architecture.md     # Module connections and architecture diagrams
│   ├── ai_models.md        # Dataset specifications & model training summaries
│   └── development.md      # Workspace prerequisites & environment details
├── backend/                # Local Python Service Layer
│   ├── main.py             # Entry server loop
│   ├── requirements.txt    # Python packaging dependencies
│   ├── utilities/          # Shared filesystem handlers, formatters, & V&V gates
│   ├── engine/             # State trackers & prompt parsers
│   ├── traceability/       # Traceability Matrix index systems
│   ├── srs/                # Requirements & sitemap compiler
│   ├── component_generator/# Layout generators
│   ├── compiler/           # Project assembly controllers
│   ├── tester/             # Unit & integration testing modules
│   ├── logger/             # Activity diagnostics & preflight checks
│   └── deployment/         # Firebase hosting deployment scripts
└── frontend/               # User Interface Client Shell
    ├── package.json        # Node scripts & dependencies
    ├── vite.config.ts      # Vite compilation configurations
    ├── src/
    │   ├── main.tsx        # UI entry hook
    │   ├── App.tsx         # Layout controller
    │   └── components/     # UI panel directories (Input, Design, Progress, SRS, Preview)
```

---

## 💻 Development Workflow

### Prerequisites

- **Node.js** (v18.0.0 or higher)
- **Python** (v3.10 or higher)
- **Expo CLI** (for testing compiled React Native output)

### Setup & Local Development

1. **Backend Configuration**:

   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   python main.py
   ```

2. **Frontend Configuration**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Verification Checks

Before contributing code updates, the local workspace can be validated using the build and import scripts:

```bash
# Verify Python modules load cleanly
python -c "import utilities, engine, traceability, srs, component_generator, compiler, tester, logger, deployment"

# Validate Frontend React compilation outputs
cd frontend
npm run build
```
