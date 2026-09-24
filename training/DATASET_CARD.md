# Dataset provenance and research limits

These are AI-authored, programmatically expanded SYNTHETIC STARTER DATASETS. They are not 720 human-written briefs, 400 inspected Figma designs, or 180 manually verified components. Do not describe them that way in your report.

| File | Records | Unit / split grouping | Labels |
|---|---:|---|---|
| data/intake.jsonl | 720 | 240 base briefs, each in English, Roman Urdu, and mixed Urdu-script; translations stay together | business type, pages, features, style |
| data/layouts.jsonl | 400 | unique business / page / style / density combinations | one of 3 layout IDs |
| data/code.jsonl | 180 | 20 implementation families, 9 descriptions each; families stay together | React Native JSX target |

Splits are train/validation/test at 80/10/10 by group (576/72/72 NLP, 320/40/40 layout, 144/18/18 code). All rows start with reviewed=false. NLP wording and language coverage are narrow. Urdu-script examples retain English domain/page words; they do NOT establish formal Urdu fluency. Code test holds out two entire component families, so small-data results can be poor. Layout targets come from a simple style/page rule. A high or perfect layout score therefore measures recovery of that rule, not human design quality.

## Before a defensible final experiment

1. Replace or substantially rewrite briefs with 500–800 independently collected descriptions, balanced across the ten categories. Have a fluent Urdu speaker review language. Include missing features, explicit exclusions, typos, synonyms, vague requests, and unsupported domains.
2. Annotate business_type, pages, features and style from the actual request. Regenerate labels from those fields. Two team members should label a subset independently, discuss disagreements and document agreement.
3. Collect 300–500 actual layout records with the source URL, design author, access date, permitted use/license, screenshot reference and human template label. Do not scrape or redistribute copyrighted designs without permission. Several records from one design must share group_id.
4. Expand code targets into real, tested implementations with props and acceptance tests. Variations of the same implementation must remain in one split. Do not put a renamed copy of a test component into training.
5. Freeze splits before training; commit a dataset hash. Check near-duplicates across splits. Tune only on validation. Evaluate test once after choices are fixed.
6. Keep synthetic and reviewed-real evaluations separate. Store provenance as synthetic_template, AI_seed_reviewed, or human_collected as appropriate; marking reviewed does not change how a row was produced.

`make_datasets.py` overwrites the starter files. Back up curated work before running it. `train_intake.py` and `train_code.py` intentionally refuse unreviewed data unless --allow-synthetic is explicitly supplied.
