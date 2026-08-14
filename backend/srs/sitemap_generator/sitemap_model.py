"""
LLM model for Stage 4 — Sitemap generation.

The important difference from the old version is that the model receives
the ORIGINAL application description as well as the functional requirements.

This prevents bad screen names such as:

    BuildAModernScreen
    ShouldBeAbleScreen
    IncludeAnUpcomingScreen

Instead, the LLM must understand the actual application domain.
"""

from __future__ import annotations

import json
import logging
from typing import Optional, TypedDict, List

from shared.llm_client import (
    LLMAPIError,
    LLMClient,
)

from shared.json_utils import (
    strip_markdown_fences,
)


logger = logging.getLogger(__name__)

_client = LLMClient()


# =========================================================
# VALID SCREEN TYPES
# =========================================================

_VALID_SCREEN_TYPES = {
    "auth",
    "detail",
    "form",
    "profile",
    "settings",
    "list",
    "dashboard",
    "generic",
}


# =========================================================
# TYPES
# =========================================================

class ExtractedScreen(TypedDict):
    screen_name: str
    route: str
    screen_type: str
    linked_fr_ids: List[str]
    is_entry_point: bool


class ExtractedEdge(TypedDict):
    from_screen: str
    to_screen: str
    trigger: str


class ExtractedSitemap(TypedDict):
    screens: List[ExtractedScreen]
    edges: List[ExtractedEdge]


# =========================================================
# SYSTEM PROMPT
# =========================================================

_SYSTEM_PROMPT = """
You are the sitemap and navigation designer for a software application.

Your job is to understand the ACTUAL APPLICATION described by the user.

You will receive:

1. The original application request.
2. Functional requirements generated from that request.

IMPORTANT:

The original application request is the source of truth for the application's
domain.

DO NOT create screen names from requirement grammar.

NEVER create names like:

- BuildAModernScreen
- ShouldBeAbleScreen
- ShouldBeAble2Screen
- IncludeAnUpcomingScreen
- TheApplicationScreen
- SupportUsersScreen

Those are BAD names.

Instead, identify the actual features of the application.

For example:

If the application request is:

"Create a student attendance management system"

Good screens could be:

- DashboardScreen
- StudentsScreen
- AttendanceScreen
- ClassesScreen
- ReportsScreen
- SettingsScreen

If the application request is:

"Create an online bakery ordering application"

Good screens could be:

- HomeScreen
- MenuScreen
- ProductDetailsScreen
- CartScreen
- CheckoutScreen
- OrdersScreen
- ProfileScreen

If the application request is:

"Create a doctor appointment booking system"

Good screens could be:

- HomeScreen
- DoctorsScreen
- DoctorDetailsScreen
- AppointmentScreen
- MyAppointmentsScreen
- ProfileScreen

Do NOT blindly use these examples.
Only use screens that are actually appropriate for the user's request.

SCREEN NAMING RULES:

- Use meaningful PascalCase.
- Every screen name must end with "Screen".
- Use nouns/features, not requirement sentences.
- Maximum approximately 4 words before "Screen".
- Do not include words such as:
  "shall", "should", "able", "support", "application", "system",
  unless they are genuinely part of a domain name.
- Keep the number of screens reasonable.
- Group related functional requirements onto the same screen.
- Do not create one screen for every FR automatically.

ROUTES:

Routes must be lowercase.

Examples:

DashboardScreen -> /dashboard
StudentsScreen -> /students
AttendanceScreen -> /attendance
ProductDetailsScreen -> /product-details

SCREEN TYPES:

Use one of:

auth
detail
form
profile
settings
list
dashboard
generic

ENTRY POINT:

Usually there should be exactly one entry point.

NAVIGATION:

Create logical navigation between screens.

Return ONLY valid JSON.

Do not return markdown.
Do not return explanations.

Required format:

{
  "screens": [
    {
      "screen_name": "DashboardScreen",
      "route": "/dashboard",
      "screen_type": "dashboard",
      "linked_fr_ids": ["FR-001"],
      "is_entry_point": true
    }
  ],
  "edges": [
    {
      "from_screen": "DashboardScreen",
      "to_screen": "StudentsScreen",
      "trigger": "open_students"
    }
  ]
}
"""


# =========================================================
# USER PROMPT
# =========================================================

def _build_user_prompt(
    fr_summaries: List[dict],
    app_description: str,
) -> str:

    requirements = "\n".join(
        f"- {fr['fr_id']}: {fr['description']}"
        for fr in fr_summaries
    )

    return f"""
ORIGINAL APPLICATION REQUEST:

{app_description}


FUNCTIONAL REQUIREMENTS:

{requirements}


TASK:

Design the sitemap for THIS application.

First understand what the application is.

Then identify its meaningful user-facing areas.

Do not convert the first words of the functional requirements into screen names.

The screen names must represent actual application features.

Return only JSON.
"""


# =========================================================
# MAIN FUNCTION
# =========================================================

def generate_sitemap_with_llm(
    fr_summaries: List[dict],
    trace_id: str,
    app_description: str = "",
) -> Optional[ExtractedSitemap]:

    if not fr_summaries and not app_description:

        logger.debug(
            "trace_id=%s | sitemap_model.py | "
            "no application description or FRs provided",
            trace_id,
        )

        return None

    messages = [
        {
            "role": "system",
            "content": _SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": _build_user_prompt(
                fr_summaries,
                app_description,
            ),
        },
    ]

    # =====================================================
    # CALL LLM
    # =====================================================

    try:

        raw_response = _client.chat_completion(
            messages=messages,
            trace_id=trace_id,
            temperature=0.1,
            max_tokens=1600,
        )

    except LLMAPIError as exc:

        logger.warning(
            "trace_id=%s | sitemap_model.py | "
            "LLM call failed | error=%s",
            trace_id,
            str(exc),
        )

        return None

    # =====================================================
    # CLEAN RESPONSE
    # =====================================================

    cleaned = strip_markdown_fences(
        raw_response
    )

    # =====================================================
    # PARSE JSON
    # =====================================================

    try:

        parsed = json.loads(
            cleaned
        )

        if not isinstance(
            parsed,
            dict,
        ):
            raise ValueError(
                "Expected JSON object"
            )

        if "screens" not in parsed:
            raise ValueError(
                "Missing screens"
            )

    except (
        json.JSONDecodeError,
        ValueError,
    ) as exc:

        logger.warning(
            "trace_id=%s | sitemap_model.py | "
            "invalid LLM JSON | error=%s | raw=%s",
            trace_id,
            str(exc),
            cleaned[:500],
        )

        return None

    # =====================================================
    # VALID FR IDS
    # =====================================================

    valid_fr_ids = {
        fr["fr_id"]
        for fr in fr_summaries
    }

    # =====================================================
    # PROCESS SCREENS
    # =====================================================

    screens: List[ExtractedScreen] = []

    screen_names_seen = set()

    for index, item in enumerate(
        parsed.get("screens", [])
    ):

        try:

            if not isinstance(
                item,
                dict,
            ):
                continue

            screen_name = str(
                item.get(
                    "screen_name",
                    "",
                )
            ).strip()

            if not screen_name:
                continue

            # ---------------------------------------------
            # Screen type
            # ---------------------------------------------

            screen_type = str(
                item.get(
                    "screen_type",
                    "generic",
                )
            ).lower()

            if (
                screen_type
                not in _VALID_SCREEN_TYPES
            ):
                screen_type = "generic"

            # ---------------------------------------------
            # Linked FRs
            # ---------------------------------------------

            linked_ids = [
                fid
                for fid in item.get(
                    "linked_fr_ids",
                    [],
                )
                if fid in valid_fr_ids
            ]

            # ---------------------------------------------
            # Route
            # ---------------------------------------------

            route = str(
                item.get(
                    "route",
                    "",
                )
            ).strip()

            if not route:
                route = (
                    "/"
                    + screen_name
                    .removesuffix("Screen")
                    .lower()
                    .replace(" ", "-")
                )

            # ---------------------------------------------
            # Duplicate screen names
            # ---------------------------------------------

            original_name = screen_name

            counter = 2

            while screen_name in screen_names_seen:

                screen_name = (
                    f"{original_name.removesuffix('Screen')}"
                    f"{counter}Screen"
                )

                counter += 1

            screen_names_seen.add(
                screen_name
            )

            screens.append(
                {
                    "screen_name": screen_name,
                    "route": route,
                    "screen_type": screen_type,
                    "linked_fr_ids": linked_ids,
                    "is_entry_point": bool(
                        item.get(
                            "is_entry_point",
                            False,
                        )
                    ),
                }
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:

            logger.warning(
                "trace_id=%s | sitemap_model.py | "
                "skipping malformed screen index=%d | error=%s",
                trace_id,
                index,
                str(exc),
            )

    # =====================================================
    # NO SCREENS
    # =====================================================

    if not screens:

        logger.warning(
            "trace_id=%s | sitemap_model.py | "
            "LLM returned zero usable screens",
            trace_id,
        )

        return None

    # =====================================================
    # GUARANTEE ENTRY POINT
    # =====================================================

    entry_points = [
        screen
        for screen in screens
        if screen["is_entry_point"]
    ]

    if not entry_points:

        screens[0]["is_entry_point"] = True

    elif len(entry_points) > 1:

        # Keep only the first one as entry point
        first = True

        for screen in screens:

            if screen["is_entry_point"]:

                if first:
                    first = False
                else:
                    screen["is_entry_point"] = False

    # =====================================================
    # PROCESS EDGES
    # =====================================================

    edges: List[ExtractedEdge] = []

    for index, item in enumerate(
        parsed.get("edges", [])
    ):

        try:

            if not isinstance(
                item,
                dict,
            ):
                continue

            from_screen = str(
                item.get(
                    "from_screen",
                    "",
                )
            )

            to_screen = str(
                item.get(
                    "to_screen",
                    "",
                )
            )

            if (
                from_screen
                not in screen_names_seen
                or
                to_screen
                not in screen_names_seen
            ):
                continue

            edges.append(
                {
                    "from_screen": from_screen,
                    "to_screen": to_screen,
                    "trigger": str(
                        item.get(
                            "trigger",
                            "navigate",
                        )
                    ),
                }
            )

        except (
            KeyError,
            TypeError,
        ) as exc:

            logger.warning(
                "trace_id=%s | sitemap_model.py | "
                "skipping malformed edge index=%d | error=%s",
                trace_id,
                index,
                str(exc),
            )

    # =====================================================
    # LOG
    # =====================================================

    logger.info(
        "trace_id=%s | sitemap_model.py | "
        "generated %d screens and %d edges",
        trace_id,
        len(screens),
        len(edges),
    )

    return {
        "screens": screens,
        "edges": edges,
    }