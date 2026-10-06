"""Retrieve training examples as planning references, never as executable code."""
import json
from functools import lru_cache
from modules.engine.domain import ROOT


@lru_cache(maxsize=1)
def layout_index():
    from sklearn.feature_extraction.text import TfidfVectorizer
    path = ROOT / "training/data/layouts.jsonl"
    rows, seen = [], set()
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("split") != "train":
            continue
        key = tuple(row.get(k, "") for k in ("business", "page", "style", "density", "template_id"))
        if key in seen:
            continue
        seen.add(key)
        rows.append({k: row.get(k) for k in ("id", "business", "page", "style", "density", "template_id", "components")})
    if not rows:
        return None
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([
        " ".join(str(row[k]) for k in ("business", "page", "style", "density", "template_id", "components"))
        for row in rows
    ])
    return rows, vectorizer, matrix


def retrieve_layout_examples(prompt, spec):
    index = layout_index()
    if index is None:
        return []
    rows, vectorizer, matrix = index
    examples = []
    for page in spec["pages"]:
        query = f"{spec['business']} {spec['style']} {page} {prompt}"
        scores = (matrix @ vectorizer.transform([query]).T).toarray().ravel()
        candidates = [i for i, row in enumerate(rows) if row["page"] == page]
        for i in sorted(candidates, key=lambda i: -scores[i])[:2]:
            examples.append({**rows[i], "score": round(float(scores[i]), 4)})
    return examples
