# Jinie Desktop Backend Services

The backend handles natural language parsing, Software Requirements Specification (SRS) generation, layout assembly, widget compilation, testing, and cloud deployment. 

The backend architecture consists of **9 specialized pipeline modules**, each designed as an importable Python package:

```text
backend/
├── main.py               # Main service entry point
├── requirements.txt      # Python dependencies
├── utilities/            # Module 01: Low-level file actions, linter styling, & verification
├── engine/               # Module 02: Orchestration state, prompt reframing & feedback
├── traceability/         # Module 03: Assigns hierarchical trace IDs to artifacts
├── srs/                  # Module 04: Produces SRS document, Sitemap, & Stack configs
├── component_generator/  # Module 05: Generates isolated UI widgets from token inputs
├── compiler/             # Module 06: Compiles widget trees into full Flutter folders
├── tester/               # Module 07: Exercises compiled apps against requirements
├── logger/               # Module 08: Pipeline logger & preflight boot validation
└── deployment/           # Module 09: Handles Firebase hosting deployments
```

---

## 🛠️ Pipeline Flow Overview

1. **Intake & Reframing**: The user uploads prompts or assets to the **Input Interface**. The backend **Engine** parses inputs and reframes Urdu/English commands into structured problem specs.
2. **Matrix Init**: **Traceability** maps the initial goal to root tracking nodes.
3. **SRS Generation**: The **SRS Generator** creates functional requirements, sitemap hierarchies, styling rules, and stack recommendations.
4. **Interactive Checkpoint**: The user approves/edits requirements in the frontend.
5. **Component Synthesis**: **Component Generator** curates visual widget code blocks.
6. **Compilation**: **Compiler** structures widgets into an executable Flutter workspace folder.
7. **Quality Gates**: **Tester** runs automated validation tracks, and **Logger** runs boot/login check sweeps to confirm correct execution.
8. **Deployment**: **Deployment Manager** publishes the finalized workspace to Google Firebase.
