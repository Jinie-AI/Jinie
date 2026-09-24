"""
extract_components.py

Reads the REAL downloaded React Native Paper source files and extracts
structured component data: real prop names (via regex over TypeScript
Props types) and real descriptions (via JSDoc comments where present).

Run this LOCALLY on your machine, from backend/component_library/,
after the repo is cloned into raw_sources/react-native-paper/:

    cd backend/component_library
    python ingestion/extract_components.py

Writes: data/catalog.json
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional, TypedDict

# Paths relative to raw_sources/react-native-paper/src/components/,
# verified against the real cloned repo's actual folder structure.
COMPONENT_FILES: dict[str, str] = {
    # ---- Standalone files ----
    "ActivityIndicator": "ActivityIndicator.tsx",
    "Badge": "Badge.tsx",
    "Banner": "Banner.tsx",
    "Divider": "Divider.tsx",
    "Icon": "Icon.tsx",
    "Modal": "Modal.tsx",
    "ProgressBar": "ProgressBar.tsx",
    "Searchbar": "Searchbar.tsx",
    "Snackbar": "Snackbar.tsx",
    "Surface": "Surface.tsx",

    # ---- Folder-based components (main file matches folder name) ----
    "Appbar": "Appbar/Appbar.tsx",
    "AppbarAction": "Appbar/AppbarAction.tsx",
    "AppbarBackAction": "Appbar/AppbarBackAction.tsx",
    "AppbarContent": "Appbar/AppbarContent.tsx",
    "AppbarHeader": "Appbar/AppbarHeader.tsx",
    "Avatar": "Avatar/Avatar.tsx",
    "AvatarImage": "Avatar/AvatarImage.tsx",
    "AvatarText": "Avatar/AvatarText.tsx",
    "AvatarIcon": "Avatar/AvatarIcon.tsx",
    "BottomNavigation": "BottomNavigation/BottomNavigation.tsx",
    "Button": "Button/Button.tsx",
    "Card": "Card/Card.tsx",
    "CardActions": "Card/CardActions.tsx",
    "CardContent": "Card/CardContent.tsx",
    "CardCover": "Card/CardCover.tsx",
    "CardTitle": "Card/CardTitle.tsx",
    "Checkbox": "Checkbox/Checkbox.tsx",
    "CheckboxItem": "Checkbox/CheckboxItem.tsx",
    "Chip": "Chip/Chip.tsx",
    "DataTable": "DataTable/DataTable.tsx",
    "DataTableCell": "DataTable/DataTableCell.tsx",
    "DataTableHeader": "DataTable/DataTableHeader.tsx",
    "DataTableRow": "DataTable/DataTableRow.tsx",
    "Dialog": "Dialog/Dialog.tsx",
    "DialogActions": "Dialog/DialogActions.tsx",
    "DialogContent": "Dialog/DialogContent.tsx",
    "DialogTitle": "Dialog/DialogTitle.tsx",
    "Drawer": "Drawer/Drawer.tsx",
    "DrawerItem": "Drawer/DrawerItem.tsx",
    "DrawerSection": "Drawer/DrawerSection.tsx",
    "FAB": "FAB/FAB.tsx",
    "AnimatedFAB": "FAB/AnimatedFAB.tsx",
    "HelperText": "HelperText/HelperText.tsx",
    "IconButton": "IconButton/IconButton.tsx",
    "List": "List/List.tsx",
    "ListItem": "List/ListItem.tsx",
    "ListIcon": "List/ListIcon.tsx",
    "ListImage": "List/ListImage.tsx",
    "ListSection": "List/ListSection.tsx",
    "ListSubheader": "List/ListSubheader.tsx",
    "ListAccordion": "List/ListAccordion.tsx",
    "Menu": "Menu/Menu.tsx",
    "MenuItem": "Menu/MenuItem.tsx",
    "RadioButton": "RadioButton/RadioButton.tsx",
    "RadioButtonGroup": "RadioButton/RadioButtonGroup.tsx",
    "RadioButtonItem": "RadioButton/RadioButtonItem.tsx",
    "SegmentedButtons": "SegmentedButtons/SegmentedButtons.tsx",
    "Switch": "Switch/Switch.tsx",
    "TextInput": "TextInput/TextInput.tsx",
    "ToggleButton": "ToggleButton/ToggleButton.tsx",
    "Tooltip": "Tooltip/Tooltip.tsx",
    "TouchableRipple": "TouchableRipple/TouchableRipple.tsx",
    "Text": "Typography/Text.tsx",
}

# Organizational grouping only (not fabricated technical facts — just
# which bucket each real component belongs to, for the taxonomy tree).
CATEGORY_MAP: dict[str, str] = {
    "ActivityIndicator": "Feedback", "ProgressBar": "Feedback", "Snackbar": "Feedback", "Banner": "Feedback",
    "Badge": "Display", "Avatar": "Display", "AvatarImage": "Display", "AvatarText": "Display", "AvatarIcon": "Display",
    "Card": "Display", "CardActions": "Display", "CardContent": "Display", "CardCover": "Display", "CardTitle": "Display",
    "List": "Display", "ListItem": "Display", "ListIcon": "Display", "ListImage": "Display", "ListSection": "Display",
    "ListSubheader": "Display", "ListAccordion": "Display", "DataTable": "Display", "DataTableCell": "Display",
    "DataTableHeader": "Display", "DataTableRow": "Display", "Surface": "Display", "Divider": "Display",
    "Icon": "Display", "Text": "Display", "Chip": "Display",
    "TextInput": "Inputs", "Searchbar": "Inputs", "Checkbox": "Inputs", "CheckboxItem": "Inputs",
    "RadioButton": "Inputs", "RadioButtonGroup": "Inputs", "RadioButtonItem": "Inputs", "Switch": "Inputs",
    "SegmentedButtons": "Inputs", "HelperText": "Inputs",
    "Button": "Buttons", "IconButton": "Buttons", "FAB": "Buttons", "AnimatedFAB": "Buttons", "ToggleButton": "Buttons",
    "Appbar": "Navigation", "AppbarAction": "Navigation", "AppbarBackAction": "Navigation",
    "AppbarContent": "Navigation", "AppbarHeader": "Navigation", "BottomNavigation": "Navigation",
    "Drawer": "Navigation", "DrawerItem": "Navigation", "DrawerSection": "Navigation", "Menu": "Navigation",
    "MenuItem": "Navigation", "Tooltip": "Navigation",
    "Modal": "Overlay", "Dialog": "Overlay", "DialogActions": "Overlay", "DialogContent": "Overlay", "DialogTitle": "Overlay",
    "TouchableRipple": "Interaction",
}

_PROPS_TYPE_PATTERN = re.compile(
    r"(?:export\s+)?(?:type|interface)\s+\w*Props\w*[^{]*\{(.*?)\n\}",
    re.DOTALL,
)
_PROP_NAME_PATTERN = re.compile(r"^\s*\/?\*?\s*(\w+)\??\s*:", re.MULTILINE)
_JSDOC_PATTERN = re.compile(r"/\*\*(.*?)\*/", re.DOTALL)


class ComponentEntry(TypedDict):
    name: str
    category: str
    props: list[str]
    description: str
    import_path: str
    source_file: str


def _extract_props(source: str) -> list[str]:
    match = _PROPS_TYPE_PATTERN.search(source)
    if not match:
        return []
    body = match.group(1)
    # Strip inline comments so prop-name regex doesn't pick up comment words
    body = re.sub(r"//.*", "", body)
    names = _PROP_NAME_PATTERN.findall(body)
    # De-duplicate while preserving order
    seen = set()
    result = []
    for name in names:
        if name not in seen and name.isidentifier():
            seen.add(name)
            result.append(name)
    return result


def _extract_description(source: str) -> str:
    matches = _JSDOC_PATTERN.findall(source)
    for block in matches:
        lines = [
            line.strip().lstrip("*").strip()
            for line in block.splitlines()
            if line.strip().lstrip("*").strip() and not line.strip().startswith("@")
        ]
        if lines:
            return " ".join(lines)[:300]
    return ""


def extract_catalog(paper_src_root: Path) -> list[ComponentEntry]:
    components_dir = paper_src_root / "src" / "components"
    entries: list[ComponentEntry] = []

    for name, relative_path in COMPONENT_FILES.items():
        file_path = components_dir / relative_path
        if not file_path.exists():
            print(f"  SKIP (file not found): {name} -> {relative_path}")
            continue

        source = file_path.read_text(encoding="utf-8", errors="ignore")
        props = _extract_props(source)
        description = _extract_description(source) or f"React Native Paper {name} component."
        category = CATEGORY_MAP.get(name, "Other")

        entries.append({
            "name": name,
            "category": category,
            "props": props,
            "description": description,
            "import_path": "react-native-paper",
            "source_file": relative_path,
        })
        print(f"  OK: {name} ({len(props)} props found)")

    return entries


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent  # backend/component_library/
    paper_root = project_root / "raw_sources" / "react-native-paper"
    output_path = project_root / "data" / "catalog.json"

    if not paper_root.exists():
        raise SystemExit(f"ERROR: {paper_root} not found. Clone the repo into raw_sources/ first.")

    print(f"Extracting components from {paper_root} ...")
    catalog = extract_catalog(paper_root)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")

    print(f"\nDone. Extracted {len(catalog)}/{len(COMPONENT_FILES)} components.")
    print(f"Written to {output_path}")