"""Module 07 adapter for Jinie's structural build checks."""

from pathlib import Path

from modules.tester.build_checks import check_artifacts


# Build testing: verifies generated artifacts and structural coverage; full device and user-flow acceptance still require testing.
class Tester:
    def generate_tests(self, functional_specs: list[dict]) -> list[dict]:
        return [
            {
                "id": f"TEST-{index:03}",
                "requirement": item.get("id"),
                "page": item.get("page"),
                "name": f"Verify {item.get('page', 'screen')} requirement",
                "kind": "structural",
            }
            for index, item in enumerate(functional_specs, 1)
        ]

    def run_tests(self, source_path, preview_path, config: dict) -> list[dict]:
        return check_artifacts(Path(source_path), Path(preview_path), config)
