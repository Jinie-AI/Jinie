"""
backend/shared/__init__.py

Generic infrastructure shared across every top-level module inside
backend/ (srs/, component_generator/, compiler/, deployment/, etc).

Note: Logger lives at the project root (../logger/, sibling to
backend/), not here — import it separately with `from logger import
Logger`. This file only bundles LLM/JSON helpers.
"""

from shared.llm_client import LLMClient, LLMAPIError
from shared.json_utils import strip_markdown_fences

__all__ = ["LLMClient", "LLMAPIError", "strip_markdown_fences"]