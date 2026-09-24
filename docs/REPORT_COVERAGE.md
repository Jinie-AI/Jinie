> CodeT5 repair update: the included checkpoint was specialized for ProductCard and now passes the known-component regression checks. See docs/MODEL_INTEGRATION.md (MODEL_INTEGRATION.md from this folder) for scope and evidence. DistilBERT is still missing. Historical verification below may refer to earlier weights.

# Report-to-delivery coverage

Source: the supplied 20-page approved FYP-1 report. Flutter requirements are translated to React Native. “Implemented” describes available code; separate verification evidence describes what actually ran. This is not a claim that every promise in the report is finished.

| Report module | Active implementation | Coverage and limits |
|---|---|---|
| 1 Utilities | studio/store.py, compiler.py, existing utilities/, source editor | Guarded file access, JSON validation, source edits with before/after history, Markdown SRS export, project scaffold. Existing conversion/reformatter utilities remain. Full semantic V&V and automatic environment installation for arbitrary stacks are not implemented. |
| 2 Engine | studio/api.py, models.py, store.py; engine/reframer.py | Normalized prompts, optional local DistilBERT, fallback, persistent SQLite state, feedback and stage checkpoints. No trained intake checkpoint supplied; no general contradiction resolver. Feedback requires review rather than automatic interpretation. |
| 3 Traceability | requirement/component/test IDs, traceability.json, Evidence view | Project-scoped IDs link screens, shared source and structural checks. Generic dependency traversal implemented in traceability/id_assigner.py. Links are coarse at shared App.jsx level; automatic fine-grained dependency regeneration is not complete. |
| 4 SRS | project creation/review + SRS export | Functional screen requirements, quality requirements, page list/sitemap, stack identification and trained synthetic RF ranking. Dataset is not externally curated; real-world recommendation quality unmeasured. |
| 5 Component generator | studio/catalog.py, templates/, models.py | Twenty reusable React Native component templates exported; isolated previews. ProductCard is directly used by the app. Other components are individually usable and inspectable; many app controls are currently implemented inline. |
| 6 Compiler | studio/compiler.py + build-preview.mjs | Native Expo scaffold, hooks/state, local storage, sample data, themes, layouts, actual browser bundle, ZIP. Optional CodeT5 ProductCard inference with fallback. Fine-tuned weights absent; arbitrary business logic from natural language is not implemented. |
| 7 Tester | API structural checks, tests/test_studio.py, scripts/browser-smoke.mjs | Automated approval, path/validation, export/edit/rebuild, compilation and browser commerce checks. Device testing and exhaustive semantic satisfaction of every editable requirement remain manual. |
| 8 Logger | persisted event records, events endpoint, activity panel | Actual stage/error logs with timestamps, polling UI, SSE endpoint. No fabricated percent timer. |
| 9 Deployment | API /deploy + deployment/firebase_helper.py | Real Firebase CLI invocation, failures and successful URL/build metadata. Requires your CLI login/project. No deployment performed here; no automatic Auth-provider provisioning or Firestore-backed commerce. |
| 10 Input | Studio Overview + /references | English/Urdu text accepted, template briefs, PDF/text/JSON context, optional image OCR, browser dictation. OCR is not vision; formal Urdu extraction remains unvalidated. |
| 11 Design preferences | Design panel + generated config | Primary/secondary/accent colors, separate system heading/body font choices, grid/editorial/cards, light/dark/system, and bottom/top/sidebar navigation. |
| 12 Progress/status | pipeline bar + activity panel | Actual stages, error messages, cancellation between stages, retry. Retry regenerates from saved approved state rather than resuming arbitrary partial component execution. |
| 13 SRS editor | Requirements panel | Editable requirement descriptions, per-requirement approvals, export, ID links. Page/control edits drive behavior; free-form prose changes alone do not create new capabilities. Regeneration is whole-project, not dependency-minimal. |
| 14 Live review | Preview panel | Actual compiled React Native Web source in sandboxed iframe, isolated components, mobile/tablet/desktop frames, 3D view, requirement-linked feedback. Alt-click element selection captures a screen-linked note; automatic targeted component rewriting remains incomplete. |
| 15 Code explorer | Code panel | Source file browser, JSX/JSON highlighting, editable source, rebuild, download ZIP and traceability matrix. Collapsible folders and JSX/JSON syntax highlighting are implemented. |

## Architecture choices changed from the report

- React remains the browser builder; React Native/Expo replaces Flutter output.
- SQLite replaces MongoDB for local builder project state. This reduces setup burden for a one-week FYP demo.
- Native generated apps use AsyncStorage for local cart/order persistence. No cloud backend or real payment processor is implied.
- Firebase Hosting can host the web build. It cannot host/install an Android or iOS binary. Native delivery is through exported source/emulator/development builds.
- New default generation needs no Groq key. The original Groq-based source and legacy main remain for reference and are not the active pipeline.

## Before calling the full report complete

Train/evaluate DistilBERT and CodeT5; replace synthetic layout records with documented curated examples; validate native builds; connect/configure Firebase on your account; address the explicitly partial features above or agree a reduced scope with your supervisor. Do not claim a full intelligent implementation merely because the demo can compile a template shop.
