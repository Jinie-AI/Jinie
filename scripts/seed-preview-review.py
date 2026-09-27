"""Create a deterministic local review fixture without paid model calls."""
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"backend"))
os.environ["JINIE_DATA_DIR"]=str(ROOT/"runtime/preview-parity")
os.environ["OPENAI_API_KEY"]=""
from studio import api, compiler, store
from studio.domain import extract, products
api.models.intake=extract
api.models.recommend=lambda *_:[{"id":"grid","source":"review fixture","score":None}]
compiler.code_candidate=lambda _:None
p=store.listing()[0] if store.listing() else api.create(api.Create(name="Preview Review",prompt="A clothing shop with home products detail cart checkout search settings profile",design=api.Design(primary="#ffffff")))
p["spec"].setdefault("products", products(p["spec"]["business"]))
for r in p["requirements"]:r["approved"]=True
p["design"]["primary"]="#ffffff"
p["screen_configs"]["home"].setdefault("title", "Good things. Great discoveries.")
compiler.compile_project(p)
compiler.bundle(p)
p["preview_directory"]=p.pop("_pending_preview")
p.update(status="ready",build_revision=p["revision"])
store.save(p)
print("Review fixture:",p["id"])
