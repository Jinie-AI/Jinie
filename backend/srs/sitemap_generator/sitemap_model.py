"""
sitemap_model.py

Domain-specific LLM layer for Stage 4 (Sitemap / navigation topology).
Given the FR list, asks the LLM to design screens and navigation edges
directly, instead of relying only on the fixed keyword-lookup table in
sitemap.py.
"""

from __future__ import annotations

import json
import logging
from typing import Optional, TypedDict, List

from common.llm_client import LLMClient, LLMAPIError
from common.json_utils import strip_markdown_fences

logger = logging.getLogger(__name__)

_client = LLMClient()

_VALID_SCREEN_TYPES = {
    "auth", "feed", "detail", "form", "profile", "settings", "list", "dashboard", "generic",
}


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


_SYSTEM_PROMPT = """You are a navigation/sitemap design engine for a mobile \
app generation pipeline. Given a list of Functional Requirements (each \
with an fr_id and description), design the set of app screens/routes \
needed and how navigation flows between them.

Respond with ONLY a single valid JSON object, no markdown fences, no \
preamble, no explanation, with exactly these keys:

{
  "screens": [
    {
      "screen_name": "PascalCase name ending in 'Screen' or a common \
name like 'MainFeed'",
      "route": "lowercase path, e.g. '/auth'",
      "screen_type": "auth" | "feed" | "detail" | "form" | "profile" | \
"settings" | "list" | "dashboard" | "generic",
      "linked_fr_ids": [fr_id strings this screen serves],
      "is_entry_point": true only for the screen(s) the app opens on
    }
  ],
  "edges": [
    {"from_screen": "screen_name", "to_screen": "screen_name", "trigger": \
"short description like 'on_login_success' or 'navigate'"}
  ]
}

Group related FRs onto the same screen where it makes sense (e.g. login \
and register both belong on an auth screen). Only reference fr_ids that \
were given to you. Keep the screen count reasonable (roughly one screen \
per distinct user-facing area, not one per FR)."""


def _build_user_prompt(fr_summaries: List[dict]) -> str:
    lines = [f"- {fr['fr_id']}: {fr['description']}" for fr in fr_summaries]
    return "Functional Requirements:\n" + "\n".join(lines)


def generate_sitemap_with_llm(fr_summaries: List[dict], trace_id: str) -> Optional[ExtractedSitemap]:
    """
    Calls the LLM to design screens + navigation edges from the given
    FR summaries. Returns None (never raises) on any failure — caller
    falls back to the keyword-lookup table in sitemap.py.
    """
    if not fr_summaries:
        logger.debug("trace_id=%s | sitemap_model.py | no FRs provided, skipping LLM call", trace_id)
        return None

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(fr_summaries)},
    ]

    try:
        raw_response = _client.chat_completion(messages=messages, trace_id=trace_id, temperature=0.3, max_tokens=1200)
    except LLMAPIError as exc:
        logger.warning(
            "trace_id=%s | sitemap_model.py | LLM call failed, caller should fall back | error=%s",
            trace_id, str(exc),
        )
        return None

    cleaned = strip_markdown_fences(raw_response)

    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict) or "screens" not in parsed:
            raise ValueError("Expected a JSON object with a 'screens' key")
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "trace_id=%s | sitemap_model.py | LLM response was not valid JSON | error=%s | raw=%s",
            trace_id, str(exc), cleaned[:300],
        )
        return None

    valid_fr_ids = {fr["fr_id"] for fr in fr_summaries}
    screens: List[ExtractedScreen] = []
    screen_names_seen = set()

    for index, item in enumerate(parsed.get("screens", [])):
        try:
            screen_type = str(item.get("screen_type", "generic")).lower()
            if screen_type not in _VALID_SCREEN_TYPES:
                screen_type = "generic"

            linked_ids = [fid for fid in item.get("linked_fr_ids", []) if fid in valid_fr_ids]

            screen: ExtractedScreen = {
                "screen_name": str(item["screen_name"]),
                "route": str(item.get("route", f"/{str(item['screen_name']).lower()}")),
                "screen_type": screen_type,
                "linked_fr_ids": linked_ids,
                "is_entry_point": bool(item.get("is_entry_point", False)),
            }
            screens.append(screen)
            screen_names_seen.add(screen["screen_name"])
        except (KeyError, TypeError) as exc:
            logger.warning(
                "trace_id=%s | sitemap_model.py | skipping malformed screen item at index=%d | error=%s",
                trace_id, index, str(exc),
            )
            continue

    if not screens:
        logger.warning("trace_id=%s | sitemap_model.py | LLM returned zero usable screens", trace_id)
        return None

    edges: List[ExtractedEdge] = []
    for index, item in enumerate(parsed.get("edges", [])):
        try:
            from_screen = str(item["from_screen"])
            to_screen = str(item["to_screen"])
            if from_screen not in screen_names_seen or to_screen not in screen_names_seen:
                logger.debug(
                    "trace_id=%s | sitemap_model.py | skipping edge referencing unknown screen at index=%d",
                    trace_id, index,
                )
                continue
            edges.append({
                "from_screen": from_screen,
                "to_screen": to_screen,
                "trigger": str(item.get("trigger", "navigate")),
            })
        except (KeyError, TypeError) as exc:
            logger.warning(
                "trace_id=%s | sitemap_model.py | skipping malformed edge item at index=%d | error=%s",
                trace_id, index, str(exc),
            )
            continue

    logger.info(
        "trace_id=%s | sitemap_model.py | LLM generated %d screens and %d edges",
        trace_id, len(screens), len(edges),
    )
    return {"screens": screens, "edges": edges}