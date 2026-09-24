> CodeT5 repair update: the included checkpoint was specialized for ProductCard and now passes the known-component regression checks. See docs/MODEL_INTEGRATION.md (MODEL_INTEGRATION.md from this folder) for scope and evidence. DistilBERT is still missing. Historical verification below may refer to earlier weights.

# Jinie Studio

React web workspace → traceable React Native / Expo commerce application.

**Read [START_HERE.md](START_HERE.md) first.** It includes Windows setup, a demo walkthrough, model status and remaining work.

- [Model training guide](training/TRAINING_GUIDE.md)
- [Dataset provenance](training/DATASET_CARD.md)
- [Report requirement coverage](docs/REPORT_COVERAGE.md)
- [Verification evidence](docs/VERIFICATION.md)

The active app runs through `backend/main.py`, `backend/studio/` and `frontend/src/pages/StudioPage.tsx`. Older modules and `.docs/` are retained as historical source; their earlier capability claims may not describe the active implementation.
