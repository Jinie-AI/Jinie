# Jinie Desktop Frontend Client

The frontend is a Vite + React + TypeScript web desktop client shell designed for user interaction throughout the application generation cycle. It is structured into **6 major interface components**:

```text
frontend/src/components/
├── InputInterface/       # Module 10: Prompts field, speech captures, and file attachment uploader
├── DesignPreferences/    # Module 11: Color, font, navigation style, and dark/light configuration swatches
├── ProgressStatus/       # Module 12: Real-time stepper indicator, logs terminal, and error indicators
├── SRSViewer/            # Module 13: Requirements tables with direct inline editing and item approval controls
├── LiveReview/           # Module 14: Simulated device frames showcasing full interactions and feedback forms
└── CodeExplorer/         # Module 15: File-tree views, syntax highlighter viewer, and ZIP download triggers
```

---

## 🚀 Development Quickstart

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Run Dev Client**:
   ```bash
   npm run dev
   ```

The application will run locally at `http://localhost:5173/` by default.
