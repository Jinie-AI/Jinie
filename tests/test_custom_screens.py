import sys
from pathlib import Path
import pytest
from pydantic import ValidationError
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from modules.component_generator.screen_contract import normalize_pages, excluded_pages, requested_custom_pages
from modules.component_generator.custom_screens import complete_custom_screens
from modules.engine.openai_planner import ScreenConfig

def test_mixed_screen_list_does_not_turn_instructions_into_pages():
    prompt = "Create a skincare shop with home, products, product details and cart. Add a doctor information page with fields: doctor name, specialization, clinic and contact number. Add a medical record page with fields: patient name, patient ID, patient condition and skin colour. Add a warranty page with fields: warranty number, coverage and expiry date. Keep each page’s fields separate. Never invent patient information. Do not add settings."
    pages = normalize_pages(["home"], prompt)
    assert pages == ["home", "products", "detail", "cart", "custom_doctor_information", "custom_medical_record", "custom_warranty"]
    configs, requirements = {}, {}
    complete_custom_screens(prompt, pages, configs, requirements)
    assert len(pages) == 7
    assert "Contact number" in requirements["custom_doctor_information"]
    assert "Expiry date" in requirements["custom_warranty"]

PROMPT = "Create me a makeup application with homescreen, menu screen, user profile, and dont add settings. Give me a screen where there is a medical record that the doctor gave to the patient, it should include patient name, patient id, patient condition, skin colour"


@pytest.mark.parametrize("exclusion", ["dont add settings", "don't include settings", "do not show settings", "without settings"])
def test_exclusions(exclusion):
    assert "settings" in excluded_pages(exclusion)
    assert "settings" not in normalize_pages(["home", "settings"], exclusion)


def test_exact_customer_request_gets_fields_and_no_extra_commerce_pages():
    pages = normalize_pages(["home", "products", "cart", "checkout", "settings"], PROMPT)
    configs, requirements = {}, {}
    complete_custom_screens(PROMPT, pages, configs, requirements)
    assert set(pages) == {"home", "products", "detail", "profile", "custom_medical_record"}
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
    generated = {}
    complete_custom_screens("Show warranty", [page], generated, {})
    assert generated[page]["sections"]
    with pytest.raises(ValidationError):
        ScreenConfig(page="../../escape")


def test_unknown_requested_screens_are_discovered_and_configured():
    prompt = (
        "Create a laptop shop with homepage screen, laptop models screen, "
        "and a warranty page. Do not add settings."
    )
    assert requested_custom_pages(prompt) == ["custom_warranty"]
    pages = normalize_pages(["home", "products", "settings"], prompt)
    configs, requirements = {}, {}
    complete_custom_screens(prompt, pages, configs, requirements)
    assert pages == ["home", "products", "detail", "custom_warranty", "cart"]
    assert "Warranty number" in requirements["custom_warranty"]
    assert "custom_laptop_models" not in configs


def test_single_unknown_screen_uses_explicit_requested_fields():
    prompt = "Add a doctor information page that should include doctor name, clinic, phone number and availability."
    pages = normalize_pages(["home"], prompt)
    configs, requirements = {}, {}
    complete_custom_screens(prompt, pages, configs, requirements)
    fields = [field["label"] for section in configs["custom_doctor_information"]["sections"] for field in section["fields"]]
    assert fields == ["Doctor name", "Clinic", "Phone number", "Availability"]
    assert "Doctor name" in requirements["custom_doctor_information"]


def test_shopping_actions_survive_top_level_screen_list():
    pages = normalize_pages(["home"], "Build a shop with home screen and clothes screen. Include cart and checkout.")
    assert {"products", "detail", "cart", "checkout"} <= set(pages)
    excluded = normalize_pages(["home"], "Build a shop with home screen and clothes screen without cart.")
    assert "cart" not in excluded
    assert "checkout" not in excluded


def test_custom_fields_stay_with_their_screen():
    prompt = "Add a warranty page with fields: serial number, expiry date. Add an invoice page with fields: invoice number, total."
    pages = requested_custom_pages(prompt)
    configs = {}
    complete_custom_screens(prompt, pages, configs, {})
    warranty = [f["label"] for s in configs["custom_warranty"]["sections"] for f in s["fields"]]
    invoice = [f["label"] for s in configs["custom_invoice"]["sections"] for f in s["fields"]]
    assert warranty == ["Serial number", "Expiry date"]
    assert invoice == ["Invoice number", "Total"]
