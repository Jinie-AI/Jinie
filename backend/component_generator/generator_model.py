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
dependencies."""


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
    return (
        "Generate the React Native component for the following input:\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
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