import json
import os
import re
from threading import Lock
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_GLOBAL_RAG = None
_RAG_LOCK = Lock()

# Search descriptions supplement the imported API docs, which mostly describe props.
PATTERN_DESCRIPTIONS = {
    "ActivityIndicator": (
        "Show an indeterminate loading spinner while content or an operation is pending. "
        "Indicate waiting without displaying a numeric completion percentage."
    ),
    "Badge": (
        "Highlight a promotional label or item count beside related content. "
        "Display a compact sale marker or shopping bag quantity indicator."
    ),
    "Banner": (
        "Show a prominent inline message with supporting text and optional actions. "
        "Introduce a collection or explain a screen-level notice."
    ),
    "Divider": (
        "Separate order totals and related groups of information with a thin line. "
        "Create visual boundaries between rows, sections and summary content."
    ),
    "Icon": (
        "Display a small symbolic image for a category, status or action. "
        "Support visual recognition alongside a readable label."
    ),
    "Modal": (
        "Display content in an overlay above the current screen. "
        "Present focused information with application-controlled visibility and dismissal."
    ),
    "ProgressBar": (
        "Display horizontal progress for an ongoing operation. "
        "Show a supplied completion fraction or an indeterminate waiting state."
    ),
    "Searchbar": (
        "Search and filter a product catalog by name, category or description. "
        "Provide a search text field with a search icon and clear action."
    ),
    "Snackbar": (
        "Confirm an action with a brief message, such as an item added to the shopping bag. "
        "Show temporary feedback with an optional follow-up action."
    ),
    "Surface": (
        "Provide a themed background container with elevation and shadow. "
        "Group related content on a visually distinct panel."
    ),
    "Appbar": (
        "Show the app name, current screen and navigation actions in a toolbar. "
        "Group title content, back navigation and contextual action icons."
    ),
    "AppbarAction": (
        "Place a contextual icon action inside an application toolbar. "
        "Expose a supplied callback for a toolbar command."
    ),
    "AppbarBackAction": (
        "Show a back arrow action inside an application toolbar. "
        "Let a supplied navigation callback return to the previous screen."
    ),
    "AppbarContent": (
        "Display the current screen title and optional subtitle inside a toolbar. "
        "Identify the page without adding a separate navigation control."
    ),
    "AppbarHeader": (
        "Arrange a top application header containing toolbar content and actions. "
        "Provide the header container for screen titles and back controls."
    ),
    "Avatar": (
        "Represent a customer on a local profile screen with a compact avatar. "
        "Use a profile image, initials or symbolic account icon."
    ),
    "AvatarImage": (
        "Display a supplied profile photograph inside a circular avatar. "
        "Represent a customer or contact using an image source."
    ),
    "AvatarText": (
        "Display customer initials or a short label inside a circular avatar. "
        "Provide a text-based profile representation when a photo is absent."
    ),
    "AvatarIcon": (
        "Display a symbolic account or category icon inside a circular avatar. "
        "Provide an icon-based profile representation."
    ),
    "BottomNavigation": (
        "Switch between primary app screens using bottom tabs. "
        "Display route labels, icons and the currently selected destination."
    ),
    "Button": (
        "Trigger an action such as add to cart or confirm an order. "
        "Provide a labelled press control with application-supplied behavior."
    ),
    "Card": (
        "Group product imagery, title, price and actions in a catalog card. "
        "Present a contained item in a collection grid or content list."
    ),
    "CardActions": (
        "Arrange action controls at the bottom of a content card. "
        "Group supplied buttons for opening an item or adding it to a bag."
    ),
    "CardContent": (
        "Contain descriptive text and supporting information inside a card. "
        "Group an item description, price or other readable details."
    ),
    "CardCover": (
        "Display a product photograph above its catalog details. "
        "Provide a prominent cover image for a visual content card."
    ),
    "CardTitle": (
        "Display a card heading with an optional subtitle and side elements. "
        "Identify the product or content item within a card."
    ),
    "Checkbox": (
        "Represent an independent option as checked, unchecked or indeterminate. "
        "Allow several options to be selected when the application supplies state."
    ),
    "CheckboxItem": (
        "Combine a checkbox with a readable label in a pressable row. "
        "Present an independently selectable form or preference option."
    ),
    "Chip": (
        "Filter products by category using compact selectable labels. "
        "Represent a category, tag or active filter in a small pill-shaped control."
    ),
    "DataTable": (
        "Arrange structured records into a table with rows and columns. "
        "Present supplied values for comparison in a compact tabular view."
    ),
    "DataTableCell": (
        "Display one text or numeric value inside a table row. "
        "Align a record field with the corresponding column heading."
    ),
    "DataTableHeader": (
        "Group column headings above structured table records. "
        "Describe the meaning of values in each table column."
    ),
    "DataTableRow": (
        "Group cells belonging to one structured record in a table. "
        "Align related field values horizontally under column headings."
    ),
    "Dialog": (
        "Present a focused dialog overlay for a decision or short message. "
        "Group a title, explanatory content and confirmation or cancellation actions."
    ),
    "DialogActions": (
        "Arrange confirmation and cancellation buttons within a dialog. "
        "Expose supplied callbacks for responding to the dialog."
    ),
    "DialogContent": (
        "Contain explanatory text or input controls inside a dialog. "
        "Present the details needed before a user makes a decision."
    ),
    "DialogTitle": (
        "Display the heading of a focused dialog. "
        "Identify the decision or message above the dialog content."
    ),
    "Drawer": (
        "Group navigation destinations in a side drawer. "
        "Organize screen links into a vertical navigation panel."
    ),
    "DrawerItem": (
        "Display one labelled destination inside a navigation drawer. "
        "Show its active state and invoke a supplied navigation callback."
    ),
    "DrawerSection": (
        "Group related drawer destinations under a section heading. "
        "Organize a side navigation panel into readable categories."
    ),
    "FAB": (
        "Expose a prominent primary action using a floating action button. "
        "Display an icon and optional label for an application-defined command."
    ),
    "AnimatedFAB": (
        "Display a floating action button with animated extended label visibility. "
        "Keep a primary action prominent while its presentation changes."
    ),
    "HelperText": (
        "Explain a form field or show a validation error. "
        "Provide a short hint beneath a customer name or delivery address input."
    ),
    "IconButton": (
        "Provide a compact action for quantity increase, decrease or removal. "
        "Use a pressable icon to invoke an application-supplied callback."
    ),
    "List": (
        "Organize related information into vertically arranged list content. "
        "Group rows, section headings and expandable information."
    ),
    "ListItem": (
        "Present a contact detail, preference or order summary row. "
        "Combine a title, description and optional leading or trailing element."
    ),
    "ListIcon": (
        "Display a leading or trailing icon alongside a list row. "
        "Identify the type of information shown in the adjacent label."
    ),
    "ListImage": (
        "Display a thumbnail image alongside a list row. "
        "Provide a visual reference for the item described by the row."
    ),
    "ListSection": (
        "Group related list rows into a titled section. "
        "Separate contact details or preference groups within a long list."
    ),
    "ListSubheader": (
        "Display a supporting heading above a group of list rows. "
        "Describe the next information group without adding an action."
    ),
    "ListAccordion": (
        "Expand or collapse a group of related list rows. "
        "Reveal supporting information beneath a selectable section heading."
    ),
    "Menu": (
        "Display a contextual popup menu anchored to a control. "
        "Group secondary actions while keeping them out of the main content area."
    ),
    "MenuItem": (
        "Display one labelled command inside a popup menu. "
        "Invoke a supplied callback when the menu option is selected."
    ),
    "RadioButton": (
        "Represent one option within a mutually exclusive selection. "
        "Show whether its value is the currently selected choice."
    ),
    "RadioButtonGroup": (
        "Coordinate radio options around one selected value. "
        "Notify the application when a mutually exclusive choice changes."
    ),
    "RadioButtonItem": (
        "Combine a radio control and readable label in a selectable row. "
        "Present one choice in a mutually exclusive option list."
    ),
    "SegmentedButtons": (
        "Arrange related choices in a compact horizontal segmented control. "
        "Display selected values for application-defined view or preference options."
    ),
    "Switch": (
        "Toggle a local settings preference on or off. "
        "Represent a boolean option using application-controlled state."
    ),
    "TextInput": (
        "Collect customer name, delivery address or search text. "
        "Provide a labelled text field with optional input hints and error styling."
    ),
    "ToggleButton": (
        "Represent an action or option with a selectable icon button. "
        "Display checked state for an application-controlled toggle."
    ),
    "Tooltip": (
        "Show a brief explanatory label associated with a control. "
        "Describe an icon or action when its tooltip is displayed."
    ),
    "TouchableRipple": (
        "Wrap interactive content with press handling and visual ripple feedback. "
        "Provide touch feedback for a supplied application action."
    ),
    "Text": (
        "Render readable headings, body copy, field labels and captions. "
        "Apply themed typography to descriptive information."
    ),
}


# Retrieval index: TF-IDF represents catalogue text; cosine similarity ranks components against the search query.
class LocalComponentRAG:
    def __init__(self, catalog_path=None):
        if not catalog_path or not os.path.exists(catalog_path):
            catalog_path = Path(__file__).resolve().parent / "data" / "catalog.json"

        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

        self.vectorizer = TfidfVectorizer(
            stop_words="english", token_pattern=r"(?u)\b\w+\b"
        )
        self.corpus = [self._get_searchable_text(c) for c in self.catalog]
        self.matrix = self.vectorizer.fit_transform(self.corpus)

    def _get_searchable_text(self, comp):
        name = comp.get("name", "")
        split_name = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
        if "Searchbar" in name:
            split_name += " search bar"
        category = comp.get("category", "")
        description = PATTERN_DESCRIPTIONS.get(name, comp.get("description", ""))
        props = " ".join(comp.get("props", []))
        return f"{name} {split_name} {name} {category} {category} {description} {props}"

    def retrieve_components(self, query: str, top_k: int = 5):
        if not query or not query.strip() or top_k <= 0:
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = scores.argsort()[::-1][: min(top_k, 20)]

        results = []
        for idx in top_indices:
            score_val = float(scores[idx])
            if score_val <= 0.01:
                continue
            comp = self.catalog[idx]
            results.append(
                {
                    "name": comp.get("name"),
                    "category": comp.get("category"),
                    "score": score_val,
                    "description": PATTERN_DESCRIPTIONS.get(
                        comp.get("name"), comp.get("description", "")
                    ),
                    "props": comp.get("props", [])[:8],
                    "import_path": comp.get("import_path", "react-native-paper"),
                }
            )
        return results


def get_rag_components(query: str, top_k: int = 4):
    global _GLOBAL_RAG
    with _RAG_LOCK:
        if _GLOBAL_RAG is None:
            _GLOBAL_RAG = LocalComponentRAG()
    return _GLOBAL_RAG.retrieve_components(query, top_k)
