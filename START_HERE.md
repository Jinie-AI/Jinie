# Updated model package

Read `docs/MODEL_INTEGRATION.md` first. Repaired CodeT5 ProductCard specialization and Random Forest are included. DistilBERT uploads failed and must be retried. Generated candidates now pass behavior checks before use; failures are visible.

# Jinie Studio — start here

This delivery adds a working local React web builder that generates React Native + Expo projects. Flutter is not used by the new pipeline. The original source remains available for reference, but the active frontend is `frontend/src/pages/StudioPage.tsx` and active backend is `backend/studio/`.

## What is ready

- Redesigned responsive workspace, 3D phone composition and optional 3D live preview.
- Saved projects, brief normalization, English/Roman Urdu keyword fallback, model inference hooks.
- Trained Random Forest checkpoint (synthetic bootstrap, NOT validated real-world intelligence).
- Editable SRS with per-page approvals; three colors, heading/body typography, navigation, theme and three layouts.
- Twenty exported React Native components with isolated previews.
- React Native shop generation: catalog, product details, categories, search, cart quantities, local demo COD checkout, about/contact.
- Actual generated JSX compiled through React Native Web in a sandboxed iframe.
- Persistent SQLite project state, build logs, cancellation at stage boundaries and retry.
- Collapsible source tree, syntax-highlighted editing, rebuild, traceability matrix, SRS export and project ZIP.
- Alt-click an app element to attach feedback to its screen.
- Firebase Hosting deployment command flow with real success/failure handling, after you supply/configure your own account.
- Starter datasets, training scripts, three Colab notebooks, evaluation tools and one-week plan.

## Important remaining work

DistilBERT and CodeT5 weights are NOT trained or included. Rules/templates keep the demo usable until checkpoints are added. The RF is trained only on synthetic labels. Android/iOS device tests, actual Firebase deployment and browser speech recognition on your machine require your environment. This is a single-user local FYP workspace, not a secure public SaaS. The report's broader promises (arbitrary natural-language code changes, automatic targeted regeneration, full Urdu understanding, cloud Auth/Firestore integration and semantic testing of every requirement) are not all fulfilled. Read `docs/REPORT_COVERAGE.md` before presenting completion claims.

## Windows setup (your VS Code / PowerShell)

Install Python 3.11 or 3.12 and Node.js 22 LTS. Extract this ZIP to a normal writable folder, for example `D:\Jinie-Enhanced`. Do not run commands inside the ZIP preview.

Open a terminal in the extracted `Jinie-main` folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd frontend
npm ci
cd ..
```

Terminal 1:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Terminal 2, from the project root:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1
```

Open http://127.0.0.1:5173. API docs: http://127.0.0.1:8000/docs.

Alternatively run `powershell -ExecutionPolicy Bypass -File scripts\start.ps1` for this trusted project script. It installs dependencies and opens the two terminals. No activation of the Python environment is needed.

Mac/Linux: `bash scripts/start.sh` (Python 3 and Node required).

A generated sample is included in `examples/EverydayEdit/`; its Expo browser export was built successfully during verification.

## Workspace appearance

Use the top-right Light / Dark / System selector to change the builder theme. The setting persists across reloads. Motion toggles floating phones, orbital particles and entrance animations. Pointer movement tilts the decorative 3D phone; mobile screens use a scaled composition. OS reduced-motion preferences override animation. Generated-app themes are still controlled separately in Design.

## First demonstration

1. Choose The Everyday Edit and Create my app.
2. Read the requirements, edit the page set, approve each one.
3. Open Design. Select a color, layout and light/dark mode. Generate app.
4. Preview: add a product, open Bag, change quantity, search, then place a demo order using a name and address. No payment is charged.
5. Switch viewport and 3D perspective. Select an isolated component.
6. Evidence: inspect requirement IDs, generated files and checks. Show the model provenance honestly.
7. Code: edit `src/config.json` name, Save file, Rebuild source; observe the same source in preview.
8. Download ZIP and open the generated app in another VS Code window.

## Run the exported React Native app

```powershell
npm install
npx expo install --fix
npm run web
```

For Android, start an Android Studio emulator and run `npm run android`. For a phone, use an Expo Go version compatible with SDK 54, or create a matching development build. A currently installed Expo Go version may target a newer SDK. Run `npx expo-doctor` and follow its version guidance. iOS native builds require Apple's tooling or an EAS build account. No APK or signed iOS build is included.

Native cart and orders use AsyncStorage; full-page browser output uses localStorage. Sandboxed builder previews use in-memory state when storage is blocked. Orders are device-local demo records, not a server order system.

## References, voice and deployment

Text-based PDF, TXT, Markdown and JSON references contribute extracted text to intake. PNG/JPEG/WebP can contribute OCR text if Tesseract is installed and on PATH. This does not reconstruct a visual layout. Dictate uses your browser's speech-recognition support and may use its online speech service.

To enable Firebase Hosting:

```powershell
npm install -g firebase-tools
firebase login
$env:JINIE_FIREBASE_PROJECT="your-real-project-id"
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Restart the backend in that terminal after setting the variable. Deploy publishes the current compiled browser build to this configured Firebase project's default Hosting site; it can replace that site's existing deployment. Use a dedicated demo Firebase project. It does not create Firestore databases or Auth providers. The generated `firestore.rules` denies all access until you intentionally design your backend. Never put service-account private keys in frontend files.

## Common issues

- Backend offline: confirm terminal 1 is running. If port 8000 differs, copy `frontend/.env.example` to `.env`, change VITE_API_URL and restart Vite.
- Build says esbuild missing: run `npm ci` inside `frontend` and ensure Node is on PATH for the backend process.
- Build blocked: approve all requirements. Feedback unapproves its target deliberately.
- Preview is stale: Save and Rebuild source; regenerating from requirements overwrites generated source edits.
- RF cannot load: use the pinned scikit-learn version or rerun `python training/train_layout.py` using your installed version.
- Model says fallback: no checkpoint is loaded. Follow `training/TRAINING_GUIDE.md`; restart backend after copying weights.
- Syntax error after editing: fix source and rebuild; the UI reports compiler errors.

Saved local projects live in `runtime/`. Back up that folder. Do not expose the backend publicly: there is no multi-user authentication or tenant isolation.
