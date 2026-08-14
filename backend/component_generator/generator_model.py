"""
generator_model.py

Domain-specific layer on top of shared/llm_client.py. Knows nothing
about validation, fallback logic, or JSX rendering rules — it only
knows: what prompt to send the LLM for React Native component
generation, and how to clean up the model's raw text reply.

Uses Groq's free API (llama-3.3-70b-versatile by default) via the
same LLMClient every srs/*_model.py file already uses. This is the
file you'd edit if you ever change *what* you ask the model to
generate (e.g. add Flutter support, change the prompt's style rules)
without touching the HTTP/auth plumbing in shared/llm_client.py.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from shared.llm_client import LLMClient, LLMAPIError
from shared.json_utils import strip_markdown_fences

logger = logging.getLogger(__name__)

_client = LLMClient()  # single shared client instance for this module


_SYSTEM_PROMPT = """You are a React Native code generation engine for a \
mobile app generation pipeline. You are given a Component Tree (JSON) \
that was already designed by an earlier pipeline stage, plus design \
tokens and the target tech stack. Your job is ONLY to render that \
existing tree into real React Native component code — you must NOT \
invent new structure, add screens, or change the hierarchy.

Respond with ONLY the raw React Native component source code. No \
markdown fences, no preamble, no explanation, no commentary before or \
after the code. The output must:
- Start with the necessary `import` statements (React, and any \
react-native primitives actually used).
- Define a single functional component matching the given component name.
- Use a `StyleSheet.create(...)` block for styling, driven by the \
provided design tokens.
- End with a default export of the component.
- Use only components implied by the Component Tree's node types \
(e.g. View, Text, TouchableOpacity, TextInput, Image, ScrollView).
- Respect the given tech stack (e.g. state management / UI library) \
only where the tree actually calls for it — do not add unrelated \
dependencies.

Color fidelity: if `design_tokens.isCustomColor` is true, the colors \
in `design_tokens.colors` were explicitly hand-picked by the end user \
as their final, non-negotiable choice — not a starting palette for \
you to interpret or adjust. In that case you MUST use those exact hex \
values verbatim everywhere a themed color applies (backgrounds, \
buttons, accents, text-on-color, etc.) — do not substitute a similar \
shade, do not add your own accent colors, and do not lighten/darken \
them for "better contrast" unless the tree or props explicitly call \
for a computed variant (e.g. a pressed/disabled state). If \
`isCustomColor` is false or absent, treat the given colors as a \
sensible default palette you may adapt tastefully.

Visual polish: within the existing tree structure (never add or remove \
nodes to achieve this), make reasonable styling choices that avoid a \
flat, generic look:
- Spacing: use a consistent scale (4, 8, 12, 16, 24) for padding and \
margins rather than one flat value everywhere — group related items \
with smaller gaps, separate distinct sections with larger ones.
- Depth: give elevated surfaces like Cards, buttons, and modals a \
subtle shadow or elevation (e.g. `shadowColor`, `shadowOpacity`, \
`shadowRadius`, `shadowOffset` on iOS and `elevation` on Android) \
instead of a flat, borderless block — keep it subtle, not heavy.
- Typography: give headings and titles a visibly larger `fontSize` \
and heavier `fontWeight` than body or label text, so there's a clear \
visual hierarchy instead of every piece of text looking the same size.
- Borders/radius: prefer soft, rounded corners (roughly 8–16) on \
cards, buttons, and inputs over sharp corners, unless the design \
tokens specify otherwise."""


def _build_user_prompt(
    component_name: str,
    component_tree: dict,
    design_tokens: dict,
    tech_stack: Optional[dict] = None,
) -> str:
    payload = {
        "component_name": component_name,
        "component_tree": component_tree,
        "design_tokens": design_tokens,
        "tech_stack": tech_stack or {},
    }
    color_instruction = ""
    if design_tokens.get("isCustomColor"):
        colors = design_tokens.get("colors", {})
        color_instruction = (
            "\n\nIMPORTANT: The user explicitly chose these exact colors "
            f"themselves: primary={colors.get('primary')}, "
            f"secondary={colors.get('secondary')}, accent={colors.get('accent')}. "
            "Use these literal hex values verbatim — do not substitute, "
            "adjust, or invent alternate shades."
        )
    return (
        "Generate the React Native component for the following input:\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
        f"{color_instruction}"
    )


def generate_component_with_llm(
    component_name: str,
    component_tree: dict,
    design_tokens: dict,
    trace_id: str,
    tech_stack: Optional[dict] = None,
) -> Optional[str]:
    """
    Calls the LLM (Groq, free tier) to render `component_tree` into
    React Native component source code. Returns None (never raises)
    if the call fails or the response is empty — the caller
    (generator.py) is responsible for falling back to the rule-based
    renderer in that case.
    """
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": _build_user_prompt(component_name, component_tree, design_tokens, tech_stack),
        },
    ]

    try:
        raw_response = _client.chat_completion(messages=messages, trace_id=trace_id, temperature=0.2, max_tokens=1500)
    except LLMAPIError as exc:
        logger.warning(
            "trace_id=%s | generator_model.py | LLM call failed, caller should fall back | error=%s",
            trace_id, str(exc),
        )
        return None

    cleaned = strip_markdown_fences(raw_response)

    if not cleaned or not cleaned.strip():
        logger.warning(
            "trace_id=%s | generator_model.py | LLM returned empty content, caller should fall back",
            trace_id,
        )
        return None

    logger.info(
        "trace_id=%s | generator_model.py | LLM generation succeeded | component=%s length=%d",
        trace_id, component_name, len(cleaned),
    )
    return cleaned