"""
backend/srs/models/__init__.py

Public interface for model integrations used by the srs/ pipeline.
Currently exposes the Groq-based (free tier) requirement extractor.
Add future model integrations (e.g. a local component-generation
model) as sibling files in this folder and export them here.
"""

from models.requirement_model import extract_with_llm, ExtractedFeatures
from models.llm_client import LLMClient, LLMAPIError

__all__ = ["extract_with_llm", "ExtractedFeatures", "LLMClient", "LLMAPIError"]