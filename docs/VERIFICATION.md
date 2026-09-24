## Current repair verification

Actual model inference passed for Random Forest and CodeT5. Four ProductCard prompt cases passed the behavioral validator. Five validator regression checks passed. All 15 browser checks passed, including confirmation that the generated CodeT5 component was used, and 3 backend tests passed. DistilBERT and native device execution remain untested.

> CodeT5 repair update: the included checkpoint was specialized for ProductCard and now passes the known-component regression checks. See docs/MODEL_INTEGRATION.md (MODEL_INTEGRATION.md from this folder) for scope and evidence. DistilBERT is still missing. Historical verification below may refer to earlier weights.

# Verification evidence

## Executed checks

- Frontend TypeScript check and Vite production build: passed.
- API regression: approval gate, generation, compilation, ZIP contents, edited-source rebuild, stale-download prevention, feedback unapproval, preservation of the last successful preview after a failed build, path traversal rejection, upload validation and dataset group separation. Three test functions passed; these cover multiple assertions and complete generation/rebuild requests.
- Chromium browser: real UI creation/approval/generation, compiled iframe, add-to-cart, checkout validation, order submission, empty search, isolated component callback, Evidence view narrow viewport, syntax-editor save/rebuild, edited configuration in preview, and sidebar navigation. `browser-test-results.json` lists the final executed checks.
- All 180 React Native code training targets parse with esbuild's JSX parser. Parsing alone is not functional verification.
- Dataset audit: 720 intake / 400 layout / 180 code rows; no exact cross-split duplicates; no shared group IDs across train/validation/test. `training/data/audit.json` records the dataset hashes. Near-duplicate meaning still requires human curation.
- Random Forest training and held-out synthetic evaluation executed. `models/layout_metrics.json` contains results and the fitted model is included.
- Exported example: `npm install` and `npm run build:web` passed using Expo/Metro, producing a 195-module browser bundle. This validates the Expo project scaffold beyond the custom builder preview.

## Not executed / not proven

- DistilBERT or CodeT5 training; scripts/notebooks are supplied, pretrained/fine-tuned weights are not.
- Android/iOS compilation, installation, device accessibility or native persistence tests.
- Actual Firebase deployment (no configured account/project).
- Browser speech recognition and Tesseract installation on the user's Windows machine.
- Accuracy on independently collected real-world briefs/designs.
- Semantic correctness of arbitrary manually edited requirements or generated model code.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_studio.py -q
npm --prefix frontend run build
.\.venv\Scripts\python.exe training\audit_data.py
```

For browser checks, install Playwright in `frontend`, install its Chromium browser and set the Python executable if necessary:

```powershell
cd frontend
npm install --save-dev playwright
npx playwright install chromium
cd ..
$env:PYTHON=(Resolve-Path .\.venv\Scripts\python.exe).Path
node scripts\browser-smoke.mjs
```

The browser script starts isolated test servers on ports 8011/5181, writes test data to runtime-browser-test, and captures screenshots. Keep these test servers local.

## Appearance update

Frontend production build passed. Eight Chromium appearance checks passed: dark theme, persistence, pointer tilt, motion pause, light theme, mobile width, system appearance and reduced motion. API calls were mocked for these visual checks; existing backend regression results above describe the prior unchanged pipeline. Desktop and mobile screenshots were inspected.
