# Jinie — AI-Driven UI to Flutter Application Generation

Welcome to the **Jinie** codebase! Jinie is an AI-assisted system designed to bridge visual application design and mobile engineering by automatically converting natural language requirements into fully executable Flutter application projects.

---

## 🎯 Project Objectives & Scope

### Objectives
- **NLP Requirement Intake**: Extract structured application specifications from natural language inputs (supporting English, Urdu, and English-Urdu code-switching) using a fine-tuned **DistilBERT** model.
- **UI Layout Recommendation**: Curate e-commerce layout structures and train a **Random Forest** recommender to choose optimized interfaces.
- **Component-to-Code Curation**: Translate specifications into modular Flutter widgets using a fine-tuned **CodeT5-small** model.
- **Scaffolding and Compiler**: Compile individual generated widgets into complete, structured Flutter project directories.
- **Traceability Gate**: Map generated code blocks, components, and tests back to originating requirements using a dynamic Traceability Matrix.
- **One-Click Deploy**: Publish compiled projects to Google Firebase Hosting automatically.

### Scope & Constraints
- **Target Domain**: E-commerce mobile applications for small local businesses (clothing, food, electronics, accessories, beauty, services).
- **Supported Screens**: Home, Product Listing, Product Detail, Shopping Cart, Checkout, Contact Us, About, and Search (up to 8 screens).
- **Exclusions**: Web and desktop compilation outputs are not target outputs. Complex animations and custom state engines are out of scope.

---

## 🏗️ Repository Architecture

This codebase is organized as a monorepo containing:

```text
jinie-desktop/
├── .docs/              # Architectural specs, API references, and model documentation
├── backend/            # Python local services & pipeline modules
└── frontend/           # Vite React TypeScript desktop client interface
```

For specific details, please see:
* **[Documentation Index](.docs/README.md)**
* **[Backend Service Overview](backend/README.md)** (Contains 9 Pipeline Modules)
* **[Frontend Application Overview](frontend/README.md)** (Contains 6 Component Interfaces)
