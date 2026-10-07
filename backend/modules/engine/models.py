"""Optional local checkpoints. Never download weights during an API request."""

import json
from functools import lru_cache
from threading import RLock

from modules.engine.domain import FEATURES, PAGES, ROOT, extract
from modules.utilities.performance import memoized

MODEL_DIR = ROOT / "models"
INTAKE_LOCK = RLock()
CODE_LOCK = RLock()


def warmup():
    """Load request-critical checkpoints ahead of use; keep CodeT5 lazy to save RAM."""
    import logging

    for name, exists, loader, lock in (
        ("intake", MODEL_DIR / "intake/config.json", intake_model, INTAKE_LOCK),
        ("layout", MODEL_DIR / "layout.joblib", layout_model, INTAKE_LOCK),
    ):
        if exists.exists():
            try:
                with lock:
                    loader()
            except Exception as exc:
                logging.getLogger(__name__).warning("%s warmup unavailable: %s", name, type(exc).__name__)


def status():
    return {
        "intake": "DistilBERT (Trained Checkpoint)"
        if (MODEL_DIR / "intake/config.json").exists()
        else "Rules fallback (checkpoint unavailable)",
        "layout": "Synthetic-trained Random Forest"
        if (MODEL_DIR / "layout.joblib").exists()
        else "Rules fallback (checkpoint unavailable)",
        "code": (
            "CodeT5 ProductCard specialization + behavior checks"
            if (MODEL_DIR / "code/specialization.json").exists()
            else "CodeT5 candidate + validation"
        )
        if (MODEL_DIR / "code/config.json").exists()
        else "Template fallback (checkpoint unavailable)",
        "rag": "LocalComponentRAG (TF-IDF + Cosine Similarity over React Native UI Catalog)",
    }


@lru_cache(maxsize=1)
def intake_model():
    import torch

    torch.set_num_threads(min(torch.get_num_threads(), 4))
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    path = MODEL_DIR / "intake"
    return AutoTokenizer.from_pretrained(
        path, local_files_only=True
    ), AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True)


@memoized(maxsize=64)
# DistilBERT intake: classifies business, style, screens and features; explicit prompt rules reconcile the screen selection.
def intake(prompt):
    baseline = extract(prompt)
    if not (MODEL_DIR / "intake/config.json").exists():
        return baseline
    try:
        import torch

        with INTAKE_LOCK, torch.inference_mode():
            tok, model = intake_model()
            model.eval()
            # Overlapping windows retain requirements near the end of long briefs.
            encoded = tok(prompt, return_tensors="pt", truncation=True,
                          max_length=256, stride=48, padding=True,
                          return_overflowing_tokens=True)
            encoded.pop("overflow_to_sample_mapping", None)
            windows = []
            for start in range(0, encoded["input_ids"].shape[0], 4):
                batch = {key: value[start:start + 4] for key, value in encoded.items()}
                windows.append(torch.sigmoid(model(**batch).logits))
            predictions = torch.cat(windows)
            probs = predictions.amax(dim=0).tolist()
            category_probs = predictions.mean(dim=0).tolist()
        labels = json.loads(
            (MODEL_DIR / "intake/labels.json").read_text(encoding="utf-8")
        )
        threshold = (
            json.loads(
                (MODEL_DIR / "intake/thresholds.json").read_text(encoding="utf-8")
            )
            if (MODEL_DIR / "intake/thresholds.json").exists()
            else {"default": 0.5}
        )
        pairs = dict(zip(labels, probs))
        category_pairs = dict(zip(labels, category_probs))
        for kind, key in [("business", "business"), ("style", "style")]:
            candidates = {
                k.split(":")[1]: v for k, v in category_pairs.items() if k.startswith(kind + ":")
            }
            if candidates:
                ranked = sorted(candidates, key=candidates.get, reverse=True)
                winner = ranked[0]
                margin = candidates[winner] - (candidates[ranked[1]] if len(ranked) > 1 else 0)
                if candidates[winner] >= 0.5 and margin >= 0.1:
                    baseline[key] = winner
        selected = [
            k
            for k, v in pairs.items()
            if v >= threshold.get(k, threshold.get("default", 0.5))
        ]
        baseline["pages"] = [p for p in PAGES if "page:" + p in selected] or [
            "home",
            "products",
            "detail",
        ]
        if "checkout" in baseline["pages"] and "cart" not in baseline["pages"]:
            baseline["pages"].append("cart")
        baseline["features"] = [f for f in FEATURES if "feature:" + f in selected]
        baseline.update(source="DistilBERT", confidence=round(max(probs), 3))
    except Exception as exc:
        baseline["warnings"].append(
            f"Intake checkpoint could not run; using rules: {type(exc).__name__}"
        )
    from modules.component_generator.screen_contract import normalize_pages

    baseline["pages"] = normalize_pages(baseline["pages"], prompt)
    baseline["features"] = ["catalog"] + [p for p in baseline["pages"] if p in FEATURES]
    return baseline


@lru_cache(maxsize=1)
def layout_model():
    import joblib

    return joblib.load(
        MODEL_DIR / "layout.joblib"
    )  # trusted project-owned checkpoint only


@memoized(maxsize=128)
# Random Forest layout recommendation: ranks layouts from business/page/style inputs; rules are used if inference is unavailable.
def recommend(business, page, style):
    if (MODEL_DIR / "layout.joblib").exists():
        try:
            model = layout_model()
            probs = model.predict_proba(
                [
                    {
                        "business": business,
                        "page": page,
                        "style": style,
                        "density": "comfortable",
                    }
                ]
            )[0]
            return [
                {
                    "id": str(model.classes_[i]),
                    "score": round(float(probs[i]), 3),
                    "source": "synthetic-trained Random Forest",
                }
                for i in probs.argsort()[::-1][:3]
            ]
        except Exception:
            pass
    first = {"minimal": "grid", "luxury": "editorial", "playful": "cards"}.get(style, "grid")
    return [
        {"id": x, "score": None, "source": "rules"}
        for x in [first] + [v for v in ["grid", "editorial", "cards"] if v != first]
    ]


@lru_cache(maxsize=1)
def code_model():
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    torch.set_num_threads(min(torch.get_num_threads(), 4))
    p = MODEL_DIR / "code"
    return AutoTokenizer.from_pretrained(
        p, local_files_only=True
    ), AutoModelForSeq2SeqLM.from_pretrained(p, local_files_only=True)


@memoized(maxsize=8, ttl=3600)
# CodeT5 candidate: proposes component code for validation; the compiler preserves the accepted working component.
def code_candidate(description):
    if not (MODEL_DIR / "code/config.json").exists():
        return None
    import torch

    with CODE_LOCK, torch.inference_mode():
        tok, model = code_model()
        model.eval()
        output = model.generate(
            **tok(description, return_tensors="pt", truncation=True, max_length=256),
            max_new_tokens=1024,
            num_beams=4,
            max_time=25,
        )
    return tok.decode(output[0], skip_special_tokens=True)
