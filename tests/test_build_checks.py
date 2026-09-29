import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from studio.build_checks import check_artifacts

def test_missing_files_and_invalid_navigation_are_reported(tmp_path):
    results = check_artifacts(tmp_path, tmp_path, {"pages": ["checkout"]})
    assert next(r for r in results if r["id"] == "FILES-001")["status"] == "failed"
    assert next(r for r in results if r["id"] == "ROUTES-001")["status"] == "failed"
    assert next(r for r in results if r["id"] == "PREVIEW-001")["status"] == "failed"

def test_composition_needs_renderer_and_valid_schema(tmp_path):
    config = {"pages": ["home"], "screen_configs": {"home": {"composition": {"blocks": [{"kind": "hero"}]}}}}
    result = lambda: next(r for r in check_artifacts(tmp_path, tmp_path, config) if r["id"] == "LAYOUT-001")["status"]
    assert result() == "failed"
    path = tmp_path / "src/components/PlannedCommerce.jsx"
    path.parent.mkdir(parents=True)
    path.write_text("export default () => null")
    assert result() == "passed"
    config["screen_configs"]["home"]["composition"]["blocks"][0]["kind"] = "unknown"
    assert result() == "failed"
