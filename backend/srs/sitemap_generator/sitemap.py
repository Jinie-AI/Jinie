"""
Stage 4: Generate a meaningful application sitemap.

The sitemap is based on:
1. The original application description.
2. Functional requirements.

The original application description is important because FR descriptions
may contain wording such as "The application shall support..." which should
NOT become screen names.
"""

from __future__ import annotations

import re
import time
from typing import Dict, List, Optional

from common.schemas import (
    FunctionalRequirement,
    FunctionalRequirementSet,
    NavigationEdge,
    ScreenType,
    Sitemap,
    SitemapNode,
)

from logger import Logger

from .sitemap_model import generate_sitemap_with_llm


# =========================================================
# HELPERS
# =========================================================

def _build_screen_id(index: int) -> str:
    return f"SCR-{index:03d}"


def _clean_screen_name(name: str, index: int) -> str:
    """
    Make sure screen names are valid PascalCase names ending with Screen.
    """

    if not name:
        return f"MainScreen{index}"

    # Remove anything that is not useful for a screen identifier
    cleaned = re.sub(r"[^A-Za-z0-9 ]+", " ", name)

    words = cleaned.split()

    # Remove common requirement-language words
    ignored = {
        "the",
        "application",
        "shall",
        "support",
        "should",
        "be",
        "able",
        "to",
        "allow",
        "allows",
        "user",
        "users",
        "system",
        "screen",
    }

    words = [
        word
        for word in words
        if word.lower() not in ignored
    ]

    if not words:
        return f"MainScreen{index}"

    result = "".join(
        word[:1].upper() + word[1:]
        for word in words[:4]
    )

    if not result.endswith("Screen"):
        result += "Screen"

    return result


def _route_from_name(name: str) -> str:
    """
    Convert PascalCase screen name into a route.
    """

    base = name.removesuffix("Screen")

    route = re.sub(
        r"(?<!^)([A-Z])",
        r"-\1",
        base,
    ).lower()

    return "/" + route.strip("-")


def _screen_type_from_text(text: str) -> ScreenType:
    """
    Determine a sensible screen type from screen/requirement text.
    """

    text = text.lower()

    if any(
        term in text
        for term in (
            "login",
            "log in",
            "sign in",
            "sign up",
            "signup",
            "register",
            "password",
            "authentication",
            "authenticate",
        )
    ):
        return ScreenType.AUTH

    if any(
        term in text
        for term in (
            "dashboard",
            "overview",
            "summary",
            "home",
        )
    ):
        return ScreenType.DASHBOARD

    if any(
        term in text
        for term in (
            "profile",
            "account",
        )
    ):
        return ScreenType.PROFILE

    if any(
        term in text
        for term in (
            "settings",
            "preferences",
            "configuration",
        )
    ):
        return ScreenType.SETTINGS

    if any(
        term in text
        for term in (
            "create",
            "add",
            "edit",
            "update",
            "submit",
            "register",
            "book",
            "request",
            "mark",
            "record",
        )
    ):
        return ScreenType.FORM

    if any(
        term in text
        for term in (
            "details",
            "detail",
            "view",
            "review",
        )
    ):
        return ScreenType.DETAIL

    if any(
        term in text
        for term in (
            "list",
            "search",
            "browse",
            "find",
            "history",
            "records",
            "directory",
            "results",
        )
    ):
        return ScreenType.LIST

    return ScreenType.GENERIC


# =========================================================
# RULE-BASED FALLBACK
# =========================================================

def _generate_via_rules(
    functional_set: FunctionalRequirementSet,
    trace_id: str,
    app_description: str = "",
) -> Sitemap:
    """
    Safe fallback when the LLM is unavailable.

    IMPORTANT:
    This fallback tries to create screens from the actual application
    description instead of blindly using the first words of an FR.
    """

    nodes: List[SitemapNode] = []

    # -----------------------------------------------------
    # If we have no requirements, create a simple main screen
    # -----------------------------------------------------

    if not functional_set.requirements:
        nodes.append(
            SitemapNode(
                screen_id=_build_screen_id(1),
                screen_name="MainScreen",
                route="/",
                screen_type=ScreenType.GENERIC,
                linked_fr_ids=[],
                is_entry_point=True,
            )
        )

        return Sitemap(
            trace_id=trace_id,
            nodes=nodes,
            edges=[],
        )

    # -----------------------------------------------------
    # Determine application context
    # -----------------------------------------------------

    app_text = app_description.lower()

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    if any(
        term in app_text
        for term in (
            "login",
            "log in",
            "sign in",
            "sign up",
            "register",
            "authentication",
        )
    ):
        nodes.append(
            SitemapNode(
                screen_id=_build_screen_id(len(nodes) + 1),
                screen_name="LoginScreen",
                route="/login",
                screen_type=ScreenType.AUTH,
                linked_fr_ids=[],
                is_entry_point=True,
            )
        )

    # -----------------------------------------------------
    # Main screen
    # -----------------------------------------------------

    nodes.append(
        SitemapNode(
            screen_id=_build_screen_id(len(nodes) + 1),
            screen_name="HomeScreen",
            route="/",
            screen_type=ScreenType.DASHBOARD,
            linked_fr_ids=[],
            is_entry_point=not bool(nodes),
        )
    )

    # -----------------------------------------------------
    # Create one sensible screen per distinct FR
    # -----------------------------------------------------

    used_names = {
        node.screen_name
        for node in nodes
    }

    for fr in functional_set.requirements:

        text = fr.description

        # Try to derive a meaningful name from nouns/actions
        words = re.findall(
            r"[A-Za-z][A-Za-z0-9]*",
            text,
        )

        ignored = {
            "the",
            "application",
            "shall",
            "support",
            "should",
            "be",
            "able",
            "to",
            "allow",
            "allows",
            "user",
            "users",
            "system",
            "with",
            "for",
            "from",
            "and",
        }

        useful_words = [
            word
            for word in words
            if word.lower() not in ignored
        ]

        if useful_words:
            candidate = "".join(
                word.title()
                for word in useful_words[:3]
            )
        else:
            candidate = "Feature"

        candidate = _clean_screen_name(
            candidate,
            len(nodes) + 1,
        )

        # Avoid duplicates
        if candidate in used_names:
            base = candidate.removesuffix("Screen")

            counter = 2

            while f"{base}{counter}Screen" in used_names:
                counter += 1

            candidate = f"{base}{counter}Screen"

        used_names.add(candidate)

        # Do not duplicate the home screen unnecessarily
        if candidate == "HomeScreen":
            continue

        nodes.append(
            SitemapNode(
                screen_id=_build_screen_id(len(nodes) + 1),
                screen_name=candidate,
                route=_route_from_name(candidate),
                screen_type=_screen_type_from_text(
                    f"{app_description} {text}"
                ),
                linked_fr_ids=[fr.fr_id],
                is_entry_point=False,
            )
        )

    # -----------------------------------------------------
    # Navigation edges
    # -----------------------------------------------------

    edges: List[NavigationEdge] = []

    for index in range(1, len(nodes)):
        edges.append(
            NavigationEdge(
                from_screen_id=nodes[index - 1].screen_id,
                to_screen_id=nodes[index].screen_id,
                trigger="navigate",
            )
        )

    return Sitemap(
        trace_id=trace_id,
        nodes=nodes,
        edges=edges,
    )


# =========================================================
# MAIN SITEMAP FUNCTION
# =========================================================

def generate_sitemap(
    functional_set: FunctionalRequirementSet,
    trace_id: str,
    app_description: str = "",
) -> Sitemap:

    start = time.perf_counter()

    audit = Logger(
        trace_id=trace_id
    )

    summaries = [
        {
            "fr_id": fr.fr_id,
            "description": fr.description,
        }
        for fr in functional_set.requirements
    ]

    # =====================================================
    # LLM GENERATION
    # =====================================================

    result = generate_sitemap_with_llm(
        fr_summaries=summaries,
        trace_id=trace_id,
        app_description=app_description,
    )

    # =====================================================
    # FALLBACK
    # =====================================================

    if result is None:

        audit.log_event(
            "sitemap.py",
            "LLM unavailable; used application-context fallback",
            level="WARNING",
        )

        return _generate_via_rules(
            functional_set=functional_set,
            trace_id=trace_id,
            app_description=app_description,
        )

    # =====================================================
    # BUILD PYDANTIC OBJECT
    # =====================================================

    names: Dict[str, str] = {}

    nodes: List[SitemapNode] = []

    for index, screen in enumerate(
        result["screens"],
        1,
    ):

        screen_name = _clean_screen_name(
            screen["screen_name"],
            index,
        )

        screen_id = _build_screen_id(index)

        names[
            screen["screen_name"]
        ] = screen_id

        names[
            screen_name
        ] = screen_id

        try:

            screen_type = ScreenType(
                screen["screen_type"]
            )

        except ValueError:

            screen_type = ScreenType.GENERIC

        nodes.append(
            SitemapNode(
                screen_id=screen_id,
                screen_name=screen_name,
                route=screen["route"],
                screen_type=screen_type,
                linked_fr_ids=screen["linked_fr_ids"],
                is_entry_point=screen["is_entry_point"],
            )
        )

    # =====================================================
    # GUARANTEE ENTRY POINT
    # =====================================================

    if nodes and not any(
        node.is_entry_point
        for node in nodes
    ):
        nodes[0].is_entry_point = True

    # =====================================================
    # BUILD EDGES
    # =====================================================

    edges: List[NavigationEdge] = []

    for edge in result["edges"]:

        from_id = names.get(
            edge["from_screen"]
        )

        to_id = names.get(
            edge["to_screen"]
        )

        if not from_id or not to_id:
            continue

        edges.append(
            NavigationEdge(
                from_screen_id=from_id,
                to_screen_id=to_id,
                trigger=edge["trigger"],
            )
        )

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    audit.log_event(
        "sitemap.py",
        (
            f"Stage complete | "
            f"screen_count={len(nodes)} "
            f"duration_ms={elapsed:.2f}"
        ),
    )

    return Sitemap(
        trace_id=trace_id,
        nodes=nodes,
        edges=edges,
    )