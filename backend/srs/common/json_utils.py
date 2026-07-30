"""
json_utils.py

Small shared utility used by every *_model.py file that parses LLM
responses expected to be JSON. Kept separate so requirement_model.py,
functional_model.py, non_functional_model.py, etc. don't import
private helpers from one another.
"""

import re


def strip_markdown_fences(raw: str) -> str:
    """
    Defensive cleanup in case the model wraps JSON in ```json fences
    despite being instructed not to.
    """
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned