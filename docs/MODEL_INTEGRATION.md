# Model integration — CodeT5 repair

## Current models
- Random Forest: included and verified by actual inference.
- CodeT5-small: repaired by a focused 80-step CPU fine-tuning run on the nine ProductCard training prompts, using one compact synthetic JSX target. This specializes the checkpoint for the ProductCard contract used by Jinie. It is NOT a general-purpose React Native code generator.
- DistilBERT: unavailable. Both uploaded ZIP attempts failed to arrive; no trained intake checkpoint has been inspected or integrated. Requirements currently use the explicit rules fallback.

## Why the repair was needed
The original checkpoint generated invalid JSX even for its exact ProductCard training prompt. The original test had 0 exact match and 8/18 syntactically valid outputs. The original dataset only contained 20 component families, with validation/test families absent from training. That is a difficult generalization task, and the selected checkpoint did not learn the required production component reliably.

The repair reduces target complexity and specializes the existing model for the currently supported component. Original metrics are kept at codet5-original-metrics.json; they do not describe the repaired weights. Current specialization metadata is in models/code/specialization.json. No independent real-world accuracy claim is made. General code-generation accuracy may regress after this specialization and was not measured.

## Validation
Four prompts passed both light/vertical and dark/horizontal render-and-callback contract checks. Two are training descriptions; two are new descriptions of the same known component. This is a regression suite, not an independent accuracy estimate. See codet5-repair-results.json and repaired-candidate-*.jsx.

Every runtime candidate is now checked for syntax, a callable default component, rendered name and price, accessible buttons, and functional open/add callbacks in a restricted JS context before substitution. This is a contract check, not a security sandbox for arbitrary adversarial JavaScript. Failed candidates remain available under model-candidates/ and are replaced with templates with a visible warning. A full esbuild bundle is still required. Native device validation remains outstanding.

## Run
Use Python 3.12. Install backend/requirements.txt and run npm ci in frontend. Follow START_HERE.md to start the servers. To test actual model inference from the project root:

```powershell
.\.venv\Scripts\python.exe scripts\check-models.py
```

Health status shows checkpoint presence, not measured accuracy. It now identifies the CodeT5 ProductCard specialization.

## Reproduce the focused repair
Extract your original CodeT5 ZIP separately and run:

```powershell
.\.venv\Scripts\python.exe training\repair_productcard.py --source "C:\path\to\original\code" --steps 80 --output models\code-repaired
```

This writes a separate folder. The original uploaded checkpoint is required for exact reproduction. Do not label this synthetic specialization as broad generalization. For broader generation, expand reviewed component families and diverse implementations, preserve an untouched external test set, and evaluate compile/render/interaction outcomes separately from exact match.

## Project scope
The Stitch-inspired frontend remains included. Existing report limitations in REPORT_COVERAGE.md still apply. DistilBERT must be re-uploaded before three-model integration can be tested.
