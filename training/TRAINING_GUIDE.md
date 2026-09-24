# Train Jinie's three models properly

## What is already trained

`models/layout.joblib` is a real fitted scikit-learn Random Forest pipeline. Its 400-row synthetic dataset uses 320 training, 40 validation and 40 test records. Training-only group cross-validation selected hyperparameters. The held-out synthetic test scored 1.0 accuracy; this is expected because the labels follow a simple rule. It is NOT evidence of 100% real design accuracy. Full metrics, dataset SHA-256, versions and confusion matrix are in `models/layout_metrics.json`.

No fine-tuned DistilBERT or CodeT5 weights are supplied. This environment did not have their GPU/runtime/checkpoints available for a defensible training run. The training code is prepared, but the transformer training jobs have not been executed or validated here. The backend uses explicit rules/templates until you install the resulting local checkpoints.

## Why “100% output” is the wrong target

There are different outcomes: correct business classification, correct page/feature extraction, useful layout ranking, syntactically valid code, behavior that meets requirements and a successful native build. One accuracy number cannot cover them all. Perfect training scores often indicate memorization. Near-duplicate descriptions or repeated code targets across train/test can make a weak model look excellent.

For your one-week deadline, keep the constrained generator and approval step as the reliable demo path. Train models to improve suggestions, then evaluate them separately. Do not hide fallback use or change test labels to improve a score. These datasets are STARTERS; see DATASET_CARD.md.

## Files for each model

| Model | Dataset | Training code | Notebook | Output |
|---|---|---|---|---|
| Multilingual DistilBERT | data/intake.jsonl + labels.json | train_intake.py | 01_DistilBERT.ipynb | models/intake/ |
| Random Forest | data/layouts.jsonl | train_layout.py | 02_RandomForest.ipynb | models/layout.joblib |
| CodeT5-small | data/code.jsonl | train_code.py | 03_CodeT5.ipynb | models/code/ |

Use a multilingual DistilBERT checkpoint because the application must handle English/Urdu input. Roman Urdu still requires representative labeled examples. An English-only tokenizer is not a substitute for this data. CodeT5-small is a pretrained code model; this project fine-tunes it on JSX, not Flutter.

## Step 1 — curate before running long training

Keep a backup of training/data. Each row has id, group_id, split, provenance and reviewed. Follow the dataset card. For NLP, preserve the label vocabulary unless you also update `backend/studio/domain.py`, the inference schema and compiler support. A classifier cannot make the compiler implement an unsupported feature just by predicting its label.

An NLP row looks like:

```json
{"id":"real-001","group_id":"business-brief-001","split":"train","text":"Meri kapron ki dukaan ke liye products, cart aur checkout chahiye","business_type":"clothing","pages":["home","products","detail","cart","checkout"],"features":["catalog","cart","checkout"],"style":"minimal","labels":["business:clothing","style:minimal","page:home","page:products","page:detail","page:cart","page:checkout","feature:catalog","feature:cart","feature:checkout"],"language":"roman_ur","provenance":"human_collected","reviewed":true}
```

Only mark that provenance when a human actually supplied the brief. Include about/contact/search only when requested or documented as an explicit default. Label negative requests carefully. Reserve 10% of independent briefs as a test set before paraphrasing. Keep all translations/paraphrases of a source brief in its group.

For layouts, model features are business, page, style, density; target is template_id. Source designs should be grouped together. Use grid/editorial/cards to match the implemented compiler. If you introduce more labels, implement those layouts as well. Human ranking tests (top-1/top-2 preference) are more informative than recovering a synthetic rule.

For code, inputs are description and outputs are complete self-contained JSX modules. Test imports, default export, props, callbacks, empty states and accessibility. Keep repeated implementation targets in one group. The starter's family-held-out test is intentionally difficult; report that split definition rather than quietly moving those families into training.

## Step 2 — use Google Colab for the transformer models

1. Open the appropriate `.ipynb` notebook from this folder in Colab.
2. Runtime > Change runtime type > GPU (a T4 is sufficient for the supplied batch sizes; availability is not guaranteed).
3. Upload the enhanced project ZIP when the notebook asks. Its extraction cell finds the project root automatically.
4. Run the dependency cell and verify `torch.cuda.is_available()` is True.
5. Run the training cell. It explicitly sets --allow-synthetic for a bootstrap trial; REMOVE that flag after you have reviewed the dataset.
6. Download the trained checkpoint ZIP from the final cell immediately. Colab storage is temporary.

Free GPU sessions vary. Do not base your final-day schedule on guaranteed availability. If GPU memory is exhausted, reduce --batch-size from 8 to 4 (DistilBERT) or 2 to 1 (CodeT5). Gradient accumulation remains enabled. Do not reduce target lengths by silently truncating valid code.

Local equivalent, using the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r training\requirements.txt
.\.venv\Scripts\python.exe training\train_intake.py --epochs 8 --batch-size 8 --allow-synthetic
.\.venv\Scripts\python.exe training\train_code.py --epochs 20 --batch-size 2 --allow-synthetic
```

GPU training duration is deliberately not promised. Model downloads need internet; inference uses only local files and does not call Groq or Hugging Face APIs.

## Step 3 — train/retrain Random Forest on your laptop

```powershell
.\.venv\Scripts\python.exe training\train_layout.py
```

The saved pipeline includes vectorization, so inference uses the same encoding as training. Hyperparameter search uses only training folds. The validation and test sets are evaluated separately and never used to fit the checkpoint. Retrain after replacing synthetic rows with curated data.

## Step 4 — examine evaluation, not just loss

DistilBERT writes validation-selected thresholds and held-out test metrics: micro-F1, macro-F1, exact label-set match, Hamming loss and per-label precision/recall/F1. Inspect minority labels and compare English, Roman Urdu and Urdu-script subsets. A label omitted in every prediction can look fine under overall accuracy but fail recall completely. Also check exclusive business/style decisions and screen dependencies at the application level.

CodeT5 writes test predictions and normalized exact match. Exact match can reject two equivalent programs; low exact match alone is not proof of failure. Conversely, plausible-looking code can be broken. Run:

```powershell
node scripts\check-code-predictions.mjs models\code\predictions.json
```

Then compile representative predictions with their actual dependencies and test their props and interactions in the isolated preview and on a device. Syntax pass rate is not semantic correctness. Save invalid predictions as evidence and document your fallback strategy. The current compiler attempts the trained ProductCard candidate, checks its basic contract and bundle, then falls back on build failure. A compilable candidate can still contain runtime/behavior defects; you must inspect it before an examiner demo.

## Step 5 — install trained checkpoints

Extract the downloaded model directories directly under the project root:

```text
models/intake/config.json
models/intake/model.safetensors
models/intake/tokenizer.json
models/intake/labels.json
models/intake/thresholds.json
models/code/config.json
models/code/model.safetensors
models/code/tokenizer.json
models/layout.joblib
```

Other tokenizer files created by save_pretrained must also remain in the folders. Do not copy just model.safetensors. Install training/requirements.txt in the backend's virtual environment, restart the backend, and check `/api/health`. Its model status should show trained checkpoint/local CodeT5. The UI records provenance; do not relabel a fallback as AI inference.

## One-week schedule

| Day | Concrete outcome |
|---|---|
| 1 | Run the delivered demo locally; verify export and Android emulator; read coverage gaps with teammates. Freeze the supported commerce scope. |
| 2 | Divide NLP labeling, layout curation and code review among the team. Freeze independent test groups. Record data provenance. |
| 3 | Train DistilBERT and RF. Inspect per-label failures, adjust training data using training/validation only. |
| 4 | Fine-tune CodeT5. Inspect syntax/build failures and callback behavior. Retain the template fallback. |
| 5 | Integrate checkpoints, run the regression scripts and manually test 10 unseen briefs; finish Firebase account setup. |
| 6 | Test on a phone/emulator; record a backup demo video; export a known-good app; document honest model scores and limitations. |
| 7 | Freeze dependencies/code, prepare slides and rehearse the exact demonstration. Avoid major architecture changes. |

## Sources used for implementation choices

- Expo SDK 54 compatibility table: https://docs.expo.dev/versions/v54.0.0/ (React Native 0.81 / React 19.1).
- Multilingual DistilBERT model card: https://huggingface.co/distilbert/distilbert-base-multilingual-cased
- CodeT5-small model card: https://huggingface.co/Salesforce/codet5-small
- Pinned Transformers Trainer API: https://huggingface.co/docs/transformers/v4.57.1/en/main_classes/trainer

The report's architecture has been adapted to React Native at your request. The scope statement should also explain that Firebase Hosting and browser preview use the React Native Web build, while the exported mobile project uses Expo.
