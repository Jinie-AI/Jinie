import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
import zipfile
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel, Field

from . import models, openai_planner, store
from .compiler import bundle, compile_project
from .domain import products
from .retrieval import retrieve_for_screens
from .composition import default_composition
from .build_checks import check_artifacts
from .srs_document import build_srs, srs_markdown
from .screen_contract import (
    CAPABILITIES,
    BusinessId,
    PageId,
    excluded_pages,
    normalize_pages,
)

try:
    from component_library.retrieverRAG import get_rag_components
except ImportError:
    try:
        from ..component_library.retrieverRAG import get_rag_components
    except ImportError:

        def get_rag_components(query: str, top_k: int = 5):
            return []


from . import auth

router = APIRouter(prefix="/api")
router.include_router(auth.router)
# Mobile router already includes the /api prefix; registered by main.py.
JOBS = {}


def now():
    return datetime.now(timezone.utc).isoformat()


def fetch(pid):
    try:
        p = store.get(pid)
        p["spec"].setdefault("products", products(p["spec"]["business"]))
        return p
    except KeyError:
        raise HTTPException(404, "Project not found")


def log(p, stage, message):
    p["events"].append(
        {"id": len(p["events"]) + 1, "time": now(), "stage": stage, "message": message}
    )
    p["updated_at"] = now()
    store.save(p)


def mutable(pid):
    p = fetch(pid)
    if p["status"] in ["building", "deploying"]:
        raise HTTPException(409, "Wait for or cancel the active build first.")
    return p


class Design(BaseModel):
    primary: str = Field("#7c5ce0", pattern=r"^#[0-9a-fA-F]{6}$")
    secondary: str = Field("#ede5f7", pattern=r"^#[0-9a-fA-F]{6}$")
    accent: str = Field("#b98849", pattern=r"^#[0-9a-fA-F]{6}$")
    bodyFont: Literal["sans", "serif"] = "sans"
    navigation: Literal["bottom", "top", "sidebar"] = "bottom"
    theme: Literal["light", "dark", "system"] = "light"
    font: Literal["sans", "serif"] = "sans"
    layout: Literal["grid", "editorial", "cards"] = "grid"


class Create(BaseModel):
    use_openai: bool = False
    prompt: str = Field(min_length=8, max_length=12000)
    name: str = Field("My collection", min_length=1, max_length=60)
    reference_text: str = Field("", max_length=24000)
    design: Design = Field(default_factory=Design)


class Requirement(BaseModel):
    id: str
    page: PageId
    text: str = Field(min_length=5, max_length=1000)
    approved: bool = True


class Review(BaseModel):
    requirements: list[Requirement] = Field(min_length=1, max_length=10)
    design: Design
    business: BusinessId = "clothing"
    screen_configs: dict[str, dict] = Field(default_factory=dict)


class Edit(BaseModel):
    content: str = Field(max_length=200000)


class Feedback(BaseModel):
    requirement_id: str
    text: str = Field(min_length=3, max_length=3000)
    rating: int = Field(3, ge=1, le=5)


DESCRIPTIONS = {
    "home": "Show a branded home screen and featured products.",
    "products": "Browse the sample catalog and filter by category.",
    "detail": "Open a product to inspect its description and price.",
    "cart": "Add products to a bag and change quantities.",
    "checkout": "Validate name/address and save a cash-on-delivery demo order locally.",
    "contact": "Display editable business contact details.",
    "about": "Present the business story.",
    "search": "Filter products by a typed search query.",
}


@router.get("/health")
def health():
    return {
        "status": "ok",
        "models": models.status(),
        "engine": openai_planner.configuration(),
        "deployment_configured": bool(os.getenv("JINIE_FIREBASE_PROJECT")),
        "mode": "local single-user workspace",
    }


@router.get("/components/rag")
def rag_search(query: str = "", top_k: int = 5):
    if not query.strip():
        raise HTTPException(400, "Query parameter is required")
    results = get_rag_components(query, top_k)
    return {"query": query, "count": len(results), "results": results}


@router.get("/projects")
def projects():
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "status": p["status"],
            "updated_at": p["updated_at"],
        }
        for p in store.listing()
    ]


@router.post("/projects", status_code=201)
def create(req: Create):
    if not req.prompt.strip():
        raise HTTPException(422, "Describe your app first.")
    from .brief import normalize_brief

    canonical = normalize_brief(req.prompt)
    spec = models.intake(canonical + "\n" + req.reference_text)
    spec["pages"] = normalize_pages(spec["pages"], canonical)
    spec["page_requirements"] = {page: CAPABILITIES[page] for page in spec["pages"]}
    recommendations = models.recommend(spec["business"], "home", spec["style"])
    spec["layout_recommendations"] = recommendations
    rag_comps = retrieve_for_screens(canonical, spec["pages"])
    spec["rag_components"] = rag_comps
    api_plan = None
    if openai_planner.configuration()["configured"]:
        try:
            spec, api_plan = openai_planner.plan_requirements(
                canonical, req.reference_text, spec, rag_components=rag_comps
            )
        except openai_planner.PlannerError as exc:
            raise HTTPException(502, str(exc))
    # Associate only actual selected screens; never claim catalog references are executable imports.
    for item in rag_comps:
        item["screens"] = [
            page
            for page in spec["pages"]
            if page in item.get("screens", [])
            or item["name"]
            in spec.get("screen_configs", {})
            .get(page, {})
            .get("reference_components", [])
        ]
    spec["rag_components"] = rag_comps
    if api_plan:
        api_plan["rag_components"] = rag_comps
    spec.setdefault("products", products(spec["business"]))
    pid = uuid.uuid4().hex
    custom_reqs = spec.get("page_requirements", {})
    req_list = [
        {
            "id": f"REQ-{i + 1:03}",
            "page": page,
            "text": custom_reqs.get(page)
            or CAPABILITIES.get(page)
            or f"Provide the {page} screen.",
            "approved": False,
        }
        for i, page in enumerate(spec["pages"])
    ]
    design_tokens = req.design.model_dump()
    design_tokens["layout"] = recommendations[0]["id"]
    if spec.get("design"):
        design_tokens.update({k: v for k, v in spec["design"].items() if v})
    screen_cfgs = spec.get("screen_configs") or {}
    excluded = excluded_pages(canonical)
    for page in spec["pages"]:
        screen_cfgs.setdefault(
            page,
            {
                "page": page,
                "title": "",
                "subtitle": "",
                "layout": design_tokens["layout"],
                "show_hero": page == "home",
                "show_search": page in ["home", "products", "search"]
                and "search" not in excluded,
                "show_badges": True,
            },
        )
    for page, screen in screen_cfgs.items():
        if page in ("home", "products") and not screen.get("composition"):
            screen["composition"] = default_composition(spec["business"], page, screen.get("layout", design_tokens["layout"]))
    default_nfr = [
        {
            "id": "NFR-001",
            "category": "Performance",
            "text": "Initial render time shall be < 1,500ms; screen transitions and list animations must maintain consistent 60 FPS.",
        },
        {
            "id": "NFR-002",
            "category": "Accessibility",
            "text": "All interactive components, buttons, and inputs expose accessible labels (WCAG 2.1 AA) with >= 44x44 dp targets.",
        },
        {
            "id": "NFR-003",
            "category": "Security & Privacy",
            "text": "Client-side sandboxed runtime; no real payment credentials or plain-text secrets are stored.",
        },
        {
            "id": "NFR-004",
            "category": "Offline Persistence",
            "text": "Shopping bag items, order state, and user preferences persist locally across app sessions via AsyncStorage.",
        },
        {
            "id": "NFR-005",
            "category": "Responsiveness",
            "text": "Adaptive layout dynamically conforms across smartphone viewports (375-430px), tablets (600-800px), and desktop web.",
        },
    ]
    p = {
        "id": pid,
        "name": req.name,
        "prompt": req.prompt,
        "canonical_prompt": canonical,
        "reference_text": req.reference_text,
        "spec": spec,
        "screen_configs": screen_cfgs,
        "design": design_tokens,
        "requirements": req_list,
        "rag_components": rag_comps,
        "nfr": default_nfr,
        "stack": [
            "React Native",
            "Expo SDK 54",
            "React Context / hooks",
            "AsyncStorage",
            "React Native Web preview",
        ],
        "status": "review",
        "stage": "requirements",
        "events": [],
        "traceability": [],
        "components": [],
        "tests": [],
        "feedback": [],
        "model_warnings": [],
        "models": models.status(),
        "created_at": now(),
        "updated_at": now(),
        "revision": 1,
        "build_revision": None,
        "deployment": None,
    }
    p["api_plan"] = api_plan
    if api_plan:
        p["models"]["planner"] = "Jinie Architecture Engine (" + api_plan["model"] + ")"
        p["model_warnings"] += spec["warnings"]
    if rag_comps:
        p["models"]["rag"] = (
            f"Jinie Component Catalog (Indexed {len(rag_comps)} UI components)"
        )
    p["recommendations"] = models.recommend(spec["business"], "home", spec["style"])
    if not spec.get("design", {}).get("layout"):
        p["design"]["layout"] = p["recommendations"][0]["id"]
    log(
        p,
        "requirements",
        "Screen plan and component references are ready. Review the details and build your application.",
    )
    return p


class RefineDesign(BaseModel):
    instructions: str = Field(min_length=8, max_length=4000)


@router.post("/projects/{pid}/refine-design")
def refine_design(pid: str, req: RefineDesign):
    with store.LOCK:
        p = mutable(pid)
        revision = p["revision"]
    if not openai_planner.configuration()["configured"]:
        raise HTTPException(
            503,
            "Text-based design refinement is unavailable. Use the design controls instead.",
        )
    local_spec = {**p["spec"], "design": p["design"], "screen_configs": p.get("screen_configs", {})}
    prompt = (
        p["prompt"]
        + "\nCurrent appearance: "
        + json.dumps(p["design"])
        + "\nRefine appearance and screen copy only. Keep the existing screens and product catalog. "
        "The following design change takes priority over the earlier appearance: "
        + req.instructions
    )
    try:
        spec, plan = openai_planner.plan_requirements(
            prompt,
            p.get("reference_text", ""),
            local_spec,
            rag_components=p.get("rag_components", []),
        )
    except openai_planner.PlannerError as exc:
        raise HTTPException(502, str(exc)) from exc
    with store.LOCK:
        p = mutable(pid)
        if p["revision"] != revision:
            raise HTTPException(
                409,
                "The project changed during refinement. Retry with the latest version.",
            )
        p["design"].update(spec["design"])
        for page in p["spec"]["pages"]:
            if page in spec.get("screen_configs", {}):
                p.setdefault("screen_configs", {})[page] = spec["screen_configs"][page]
        p["spec"]["screen_configs"] = p["screen_configs"]
        p["spec"]["design"] = p["design"]
        p["api_plan"] = plan
        p["model_warnings"] = spec.get("warnings", [])
        p["revision"] += 1
        p.update(status="review", stage="requirements", tests=[], deployment=None)
        log(
            p,
            "design",
            "Design refinement applied. Rebuild to update the generated app.",
        )
        return p


@router.get("/projects/{pid}")
def get_project(pid: str):
    return fetch(pid)


@router.get("/projects/{pid}/srs.pdf")
@router.get("/projects/{pid}/srs")
def get_srs_pdf(pid: str):
    p = fetch(pid)
    from .srs_pdf import generate_srs_pdf

    pdf_bytes = generate_srs_pdf(p)
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", p.get("name", "App"))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="SRS_{safe_name}.pdf"'},
    )


@router.put("/projects/{pid}/review")
def review(pid: str, req: Review):
    with store.LOCK:
        p = mutable(pid)
        ids = [r.id for r in req.requirements]
        pages = [r.page for r in req.requirements]
        if len(ids) != len(set(ids)) or len(pages) != len(set(pages)):
            raise HTTPException(422, "Requirement IDs and pages must be unique.")
        if not all(re.fullmatch(r"REQ-\d{3}", i) for i in ids):
            raise HTTPException(422, "Requirement IDs must use REQ-001 format.")
        if "checkout" in pages and "cart" not in pages:
            raise HTTPException(422, "Checkout requires a cart page.")
        reqs = [r.model_dump() for r in req.requirements]
        p.update(
            requirements=reqs,
            design=req.design.model_dump(),
            status="review",
            stage="requirements",
            tests=[],
            deployment=None,
        )
        if req.screen_configs:
            from .openai_planner import ScreenConfig

            try:
                p["screen_configs"] = {
                    page: ScreenConfig.model_validate(
                        {
                            **req.screen_configs.get(
                                page, p.get("screen_configs", {}).get(page, {})
                            ),
                            "page": page,
                        }
                    ).model_dump()
                    for page in pages
                }
            except ValueError as exc:
                raise HTTPException(422, "Invalid screen configuration.") from exc
        if p["spec"]["business"] != req.business:
            p["spec"].pop("products", None)
            p["spec"].pop("business_label", None)
        p["spec"]["business"] = req.business
        p["spec"]["pages"] = pages
        p["spec"]["features"] = ["catalog"] + [
            x
            for x in pages
            if x
            in ["cart", "checkout", "search", "contact", "about", "settings", "profile"]
        ]
        p["revision"] += 1
        log(p, "requirements", "Screen customization and review saved.")
        return p


def run_job(pid, cancel, rebuild_only=False):
    try:
        p = fetch(pid)
        if not rebuild_only:
            if cancel.is_set():
                raise InterruptedError()
            p["stage"] = "components"
            log(
                p,
                "components",
                "Assembling React Native components and requirement trace links.",
            )
            p = compile_project(p)
            store.save(p)
        if cancel.is_set():
            raise InterruptedError()
        p["stage"] = "compilation"
        log(
            p,
            "compilation",
            "Bundling actual React Native source for the browser preview.",
        )
        bundle(p)
        if cancel.is_set():
            raise InterruptedError()
        p["stage"] = "testing"
        log(
            p, "testing", "Checking approved screens, source files and compiled bundle."
        )
        source = store.folder(pid) / "source"
        config = json.loads((source / "src/config.json").read_text(encoding="utf-8"))
        p["tests"] = [
            {
                "id": f"TEST-{i + 1:03}",
                "requirement": r["id"],
                "name": r["page"] + " is present in compiled configuration",
                "status": "passed" if r["page"] in config["pages"] else "failed",
                "kind": "structural",
            }
            for i, r in enumerate(p["requirements"])
        ]
        p["tests"] += [
            {
                "id": "BUILD-001",
                "requirement": None,
                "name": "React Native Web source bundles successfully",
                "status": "passed",
                "kind": "compilation",
            },
            {
                "id": "NATIVE-001",
                "requirement": None,
                "name": "Android/iOS device acceptance testing",
                "status": "not_run",
                "kind": "manual",
            },
        ]
        p["tests"] += check_artifacts(source, store.folder(pid) / p["_pending_preview"], config)
        store.write(pid, "test-results.json", json.dumps(p["tests"], indent=2))
        store.save(p)
        if any(t["status"] == "failed" for t in p["tests"]):
            raise RuntimeError(
                "Build validation failed: " + "; ".join(t["name"] for t in p["tests"] if t["status"] == "failed")
            )
        p.update(
            status="ready",
            stage="ready",
            build_revision=p["revision"],
            preview_directory=p.pop("_pending_preview"),
            error=None,
            models=models.status(),
        )
        if p.get("api_plan"):
            p["models"]["planner"] = (
                "Jinie Intelligence (" + p["api_plan"]["model"] + ")"
            )
        store.write(pid, "test-results.json", json.dumps(p["tests"], indent=2))
        log(
            p,
            "ready",
            "Build ready. Browser preview uses the generated source; native tests remain separate.",
        )
    except InterruptedError:
        p = fetch(pid)
        p.update(status="cancelled", stage="cancelled")
        log(p, "cancelled", "Build cancelled at a safe checkpoint. You can retry.")
    except Exception as exc:
        p = fetch(pid)
        p.update(status="failed", error=str(exc))
        log(p, "error", str(exc))
    finally:
        with store.LOCK:
            if JOBS.get(pid) is cancel:
                JOBS.pop(pid, None)


def launch(pid, rebuild_only=False):
    with store.LOCK:
        p = mutable(pid)
        if not all(r["approved"] for r in p["requirements"]):
            raise HTTPException(
                409, "Accept the requirements and screens before building."
            )
        if rebuild_only and not (store.folder(pid) / "source/App.jsx").exists():
            raise HTTPException(409, "Generate the source first.")
        p.update(
            status="building",
            stage="components" if not rebuild_only else "compilation",
            error=None,
            tests=[],
            deployment=None,
        )
        log(
            p,
            p["stage"],
            "Build started." if not rebuild_only else "Rebuilding edited source.",
        )
        cancel = threading.Event()
        JOBS[pid] = cancel
        threading.Thread(
            target=run_job, args=(pid, cancel, rebuild_only), daemon=True
        ).start()
        return p


@router.post("/projects/{pid}/build")
def build(pid: str):
    return launch(pid)


@router.post("/projects/{pid}/rebuild")
def rebuild(pid: str):
    return launch(pid, True)


@router.post("/projects/{pid}/cancel")
def cancel(pid: str):
    fetch(pid)
    if pid in JOBS:
        JOBS[pid].set()
    return {
        "message": "Cancellation requested; active compiler step will finish before stopping."
    }


@router.get("/projects/{pid}/events")
def events(pid: str, after: int = 0):
    fetch(pid)

    def stream():
        cursor = after
        for _ in range(600):
            p = fetch(pid)
            for e in p["events"]:
                if e["id"] > cursor:
                    yield "data: " + json.dumps(e) + "\n\n"
                    cursor = e["id"]
            if p["status"] not in ["building", "deploying"]:
                break
            time.sleep(0.25)

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.get("/projects/{pid}/files")
def files(pid: str):
    fetch(pid)
    base = store.folder(pid) / "source"
    return sorted(
        str(f.relative_to(base)).replace("\\", "/")
        for f in base.rglob("*")
        if f.is_file()
    )


@router.get("/projects/{pid}/file")
def read_file(pid: str, path: str):
    fetch(pid)
    try:
        f = store.safe_file(pid, path)
    except ValueError:
        raise HTTPException(400, "Invalid path")
    if not f.is_file():
        raise HTTPException(404, "File not found")
    return {"path": path, "content": f.read_text(encoding="utf-8")}


@router.put("/projects/{pid}/file")
def edit_file(pid: str, path: str, req: Edit):
    with store.LOCK:
        p = mutable(pid)
        try:
            f = store.safe_file(pid, path)
        except ValueError:
            raise HTTPException(400, "Invalid path")
        if not f.is_file() or f.suffix not in [".jsx", ".js", ".json", ".md", ".rules"]:
            raise HTTPException(400, "Choose an existing editable source file.")
        if f.suffix == ".json":
            try:
                json.loads(req.content)
            except ValueError:
                raise HTTPException(422, "JSON is invalid.")
        previous = f.read_text(encoding="utf-8")
        store.write(pid, path, req.content)
        affected = [t["requirement"] for t in p.get("traceability", []) if path in t.get("files", [])]
        p.setdefault("edits", []).append(
            {"file": path, "time": now(), "before": previous, "after": req.content, "affected_requirements": affected}
        )
        p.update(status="edited", deployment=None)
        p["revision"] += 1
        log(p, "editor", "Saved " + path + "; rebuild to update preview." + (" Affected requirements: " + ", ".join(affected) if affected else ""))
        return p


@router.get("/projects/{pid}/preview/{asset:path}")
def preview(pid: str, asset: str):
    p = fetch(pid)
    if p["build_revision"] is None:
        raise HTTPException(409, "Build the project first.")
    base = (store.folder(pid) / p.get("preview_directory", "preview")).resolve()
    path = (base / asset).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise HTTPException(404, "Preview asset not found")
    return FileResponse(
        path,
        media_type={
            ".js": "application/javascript",
            ".html": "text/html",
            ".css": "text/css",
        }.get(path.suffix),
        headers={
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: https://images.unsplash.com; connect-src 'none'; font-src data:;",
        },
    )


@router.get("/projects/{pid}/download")
def download(pid: str):
    p = fetch(pid)
    if p["status"] != "ready" or p["build_revision"] != p["revision"]:
        raise HTTPException(409, "Build the current revision before downloading.")
    # Keep customer names, but remove unsafe filename/path characters.
    customer_name = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f]', "-", p["name"])
    customer_name = re.sub(r"\s+", " ", customer_name).strip(" .-")[:100].rstrip(" .") or "App"
    archive_name = f"{customer_name}-jinie"
    ascii_name = archive_name.encode("ascii", "ignore").decode().strip(" .-") or "app-jinie"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in (store.folder(pid) / "source").rglob("*"):
            if f.is_file():
                z.write(
                    f, archive_name + "/" + f.relative_to(store.folder(pid) / "source").as_posix()
                )
        preview_dir = store.folder(pid) / p.get("preview_directory", "preview")
        if preview_dir.exists():
            for f in preview_dir.rglob("*"):
                if f.is_file():
                    z.write(f, archive_name + "/web-build/" + f.relative_to(preview_dir).as_posix())
        z.writestr(archive_name + "/SRS.md", srs_markdown(p))
    return Response(
        buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{ascii_name}.zip"; filename*=UTF-8\'\'{quote(archive_name + ".zip", safe="")}'},
    )


@router.get("/projects/{pid}/srs.json")
def srs_data(pid: str):
    return build_srs(fetch(pid))


@router.get("/projects/{pid}/srs.md")
def srs(pid: str):
    return Response(
        srs_markdown(fetch(pid)),
        media_type="text/markdown",
        headers={"Content-Disposition": 'attachment; filename="SRS.md"'},
    )


@router.post("/projects/{pid}/feedback")
def feedback(pid: str, req: Feedback):
    with store.LOCK:
        p = mutable(pid)
        if req.requirement_id not in [r["id"] for r in p["requirements"]]:
            raise HTTPException(422, "Choose a requirement ID from this project.")
        p["feedback"].append(
            dict(id="FB-" + uuid.uuid4().hex[:8], time=now(), **req.model_dump())
        )
        for r in p["requirements"]:
            if r["id"] == req.requirement_id:
                r["approved"] = False
        p.update(status="review", deployment=None)
        p["revision"] += 1
        log(
            p,
            "feedback",
            "Feedback linked to "
            + req.requirement_id
            + ". Review that requirement and rebuild.",
        )
        return p


@router.post("/references")
async def references(file: UploadFile = File(...)):
    data = await file.read(2_000_001)
    if len(data) > 2_000_000:
        raise HTTPException(413, "Reference limit is 2 MB.")
    suffix = (file.filename or "").rsplit(".", 1)[-1].lower()
    if suffix == "pdf":
        from pypdf import PdfReader

        try:
            text = "\n".join(
                p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages[:30]
            )
        except Exception:
            raise HTTPException(
                422,
                "Could not read this PDF. Upload a text-based PDF or paste its text.",
            )
    elif suffix in ["txt", "md", "json"]:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(422, "Use UTF-8 text.")
    elif suffix in ["png", "jpg", "jpeg", "webp"]:
        cli = shutil.which("tesseract")
        if not cli:
            raise HTTPException(
                409,
                "Image text extraction needs Tesseract installed on the backend. Install it or paste a description. This is OCR, not visual layout recognition.",
            )
        with tempfile.TemporaryDirectory() as tmp:
            path = __import__("pathlib").Path(tmp) / ("reference." + suffix)
            path.write_bytes(data)
            result = subprocess.run(
                [cli, str(path), "stdout", "-l", "eng"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode:
                raise HTTPException(
                    422,
                    "Could not extract text from the image. Paste a written description instead.",
                )
            text = result.stdout
        if not text.strip():
            raise HTTPException(
                422, "No readable text found. Describe the layout in your prompt."
            )
    else:
        raise HTTPException(
            415, "Supported references: PDF, TXT, Markdown, JSON, PNG, JPEG and WebP."
        )
    return {"name": file.filename, "text": text[:24000], "truncated": len(text) > 24000}


@router.post("/projects/{pid}/deploy")
def deploy(pid: str):
    with store.LOCK:
        p = mutable(pid)
        project = os.getenv("JINIE_FIREBASE_PROJECT", "")
        if not re.fullmatch(
            r"[a-z][a-z0-9-]{4,28}[a-z0-9]", project
        ) or not shutil.which("firebase"):
            raise HTTPException(
                409,
                "Configure JINIE_FIREBASE_PROJECT, install firebase-tools and run firebase login on the backend machine first.",
            )
        if p["status"] != "ready" or p["build_revision"] != p["revision"]:
            raise HTTPException(409, "Build the current revision before deployment.")
        p.update(status="deploying")
        log(
            p,
            "deployment",
            "Deploying browser build to configured Firebase Hosting project.",
        )

    def work():
        try:
            base = store.folder(pid)
            (base / "firebase.json").write_text(
                json.dumps(
                    {
                        "hosting": {
                            "public": p.get("preview_directory", "preview"),
                            "ignore": ["**/.*"],
                            "rewrites": [
                                {"source": "**", "destination": "/index.html"}
                            ],
                        }
                    }
                )
            )
            result = subprocess.run(
                [
                    shutil.which("firebase"),
                    "deploy",
                    "--only",
                    "hosting",
                    "--project",
                    project,
                    "--non-interactive",
                    "--json",
                ],
                cwd=base,
                capture_output=True,
                text=True,
                timeout=240,
            )
            if result.returncode:
                raise RuntimeError(result.stderr[-2000:] or result.stdout[-2000:])
            response = json.loads(result.stdout)
            if response.get("status") != "success":
                raise RuntimeError("Firebase did not report a successful deployment.")
            p["deployment"] = {
                "url": "https://" + project + ".web.app",
                "time": now(),
                "revision": p["revision"],
                "build_id": pid + "-" + str(p["build_revision"]),
            }
            p["status"] = "ready"
            log(p, "deployment", "Firebase Hosting deployment succeeded.")
        except Exception as e:
            p["status"] = "ready"
            p["error"] = str(e)
            log(p, "error", "Deployment failed: " + str(e))

    threading.Thread(target=work, daemon=True).start()
    return p
