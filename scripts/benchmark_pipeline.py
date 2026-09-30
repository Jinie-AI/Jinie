"""Local cold/repeated inference timings; no paid calls or project database writes."""
import json
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from studio import models
from studio.retrieval import retrieve_for_screens


def main():
    prompt = "A minimal flower shop with products, cart, checkout and contact. No profile."
    report = {}
    for label in ("first", "repeated"):
        started = perf_counter()
        spec = models.intake(prompt)
        intake_end = perf_counter()
        layouts = models.recommend(spec["business"], "home", spec["style"])
        layout_end = perf_counter()
        refs = retrieve_for_screens(prompt, spec["pages"])
        end = perf_counter()
        report[label] = {
            "intake_ms": round((intake_end - started) * 1000, 2),
            "layout_ms": round((layout_end - intake_end) * 1000, 2),
            "retrieval_ms": round((end - layout_end) * 1000, 2),
            "intake_source": spec.get("source"),
            "layout_source": layouts[0]["source"],
            "pages": spec["pages"],
            "reference_count": len(refs),
        }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
