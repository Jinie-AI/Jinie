import sys
from pathlib import Path
import pytest
from pydantic import ValidationError
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from studio.screen_contract import normalize_pages, excluded_pages
from studio.custom_screens import complete_custom_screens
from studio.openai_planner import ScreenConfig

PROMPT = "Create me a makeup application with homescreen, menu screen, user profile, and dont add settings. Give me a screen where there is a medical record that the doctor gave to the patient, it should include patient name, patient id, patient condition, skin colour"


@pytest.mark.parametrize("exclusion", ["dont add settings", "don't include settings", "do not show settings", "without settings"])
def test_exclusions(exclusion):
    assert "settings" in excluded_pages(exclusion)
    assert "settings" not in normalize_pages(["home", "settings"], exclusion)


def test_exact_customer_request_gets_fields_and_no_extra_commerce_pages():
    pages = normalize_pages(["home", "products", "cart", "checkout", "settings"], PROMPT)
    configs, requirements = {}, {}
    complete_custom_screens(PROMPT, pages, configs, requirements)
    assert set(pages) == {"home", "products", "profile", "custom_medical_record"}
    screen = ScreenConfig.model_validate(configs["custom_medical_record"])
    assert {f.label for s in screen.sections for f in s.fields} == {"Patient name", "Patient ID", "Patient condition", "Skin colour"}
    assert all(f.value == "" for s in screen.sections for f in s.fields)
    assert "Patient ID" in requirements[screen.page]


def test_arbitrary_information_screen_and_missing_structure():
    page = "custom_warranty"
    config = ScreenConfig(page=page, title="Warranty", sections=[{"title": "Coverage", "fields": [{"label": "Expiry date"}]}])
    requirements = {}
    complete_custom_screens("Show warranty information", [page], {page: config.model_dump()}, requirements)
    assert "Expiry date" in requirements[page]
    with pytest.raises(ValueError):
        complete_custom_screens("Show warranty", [page], {}, {})
    with pytest.raises(ValidationError):
        ScreenConfig(page="../../escape")
