# Dataset provenance and research limits

Expanded on 4 October 2026. These are programmatically generated SYNTHETIC STARTER DATASETS, not independently collected human examples. All 6,000 records remain reviewed=false. Existing trained checkpoints were not modified or retrained.

| File | Records | Train / validation / test | Actual diversity |
|---|---:|---|---|
| data/intake.jsonl | 2,000 | 1,600 / 191 / 209 | 1,229 semantic groups; original multilingual briefs plus varied English and Roman Urdu prompts and explicit exclusions |
| data/layouts.jsonl | 2,000 | 1,618 / 183 / 199 | 480 unique model-input combinations; 1,520 repeated rows explicitly marked with replica_of |
| data/code.jsonl | 2,000 | 1,600 / 200 / 200 | 20 component families; original examples plus spacing, typography and colour variants |

The current layout label vocabulary permits only 480 distinct business/page/style/density combinations. Repeated rows meet the requested record count but do not create new design knowledge or independent evaluation evidence. Human-rated layouts and richer model input features are needed for meaningful further expansion. The target remains a simple synthetic rule.

Intake retains the existing labels.json vocabulary to remain compatible with existing checkpoints. It does not add arbitrary custom-screen classes, profile/settings classes, or new business classes. Mixed Urdu-script examples still contain English domain/page words. Roman Urdu wording is synthetic and has not been linguistically reviewed.

Code variants retain the same props and component structure. They increase visual variation, not behavioural capability. All variants of a component family stay in its original split. JSX transformation checks syntax only, not runtime behaviour, accessibility, or training token-length suitability. The short-code training limit should be reviewed before training on longer components.

Original records are preserved. Backups are in tmp/dataset-backup-before-2000. Run python training/expand_datasets.py to reproduce expansion from the original data; rerunning on expanded data makes no further additions. Run python training/audit_data.py to check labels, exclusions, grouped splits and exact cross-split duplicates. Near-duplicate phrasing still exists and independent real-world evaluation remains necessary.

## Before a defensible final experiment

1. Replace or substantially rewrite briefs with 500–800 independently collected descriptions, balanced across the ten categories. Have a fluent Urdu speaker review language. Include missing features, explicit exclusions, typos, synonyms, vague requests, and unsupported domains.
2. Annotate business_type, pages, features and style from the actual request. Regenerate labels from those fields. Two team members should label a subset independently, discuss disagreements and document agreement.
3. Collect 300–500 actual layout records with the source URL, design author, access date, permitted use/license, screenshot reference and human template label. Do not scrape or redistribute copyrighted designs without permission. Several records from one design must share group_id.
4. Expand code targets into real, tested implementations with props and acceptance tests. Variations of the same implementation must remain in one split. Do not put a renamed copy of a test component into training.
5. Freeze splits before training; commit a dataset hash. Check near-duplicates across splits. Tune only on validation. Evaluate test once after choices are fixed.
6. Keep synthetic and reviewed-real evaluations separate. Store provenance as synthetic_template, AI_seed_reviewed, or human_collected as appropriate; marking reviewed does not change how a row was produced.

`make_datasets.py` overwrites the starter files. Back up curated work before running it. `train_intake.py` and `train_code.py` intentionally refuse unreviewed data unless --allow-synthetic is explicitly supplied.
