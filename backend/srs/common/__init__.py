"""
backend/srs/common/__init__.py

Public interface for the shared foundation used by every generator
(requirements_generator, fr_generator, nfr_generator, sitemap_generator,
entities_generator, component_tree_generator, stack_identifier_generator).

Exposes:
    - LLMClient            : Groq (free-tier) chat completion client
    - LLMAPIError           : raised when the Groq API call fails
    - strip_markdown_fences : JSON-cleanup helper for LLM responses
    - all Pydantic schemas  : the shared data contracts (see schemas.py)

Logger lives in its own logger/ folder, not here — import it via
`from logger import Logger` instead.
"""

from common.llm_client import LLMClient, LLMAPIError
from common.json_utils import strip_markdown_fences
from common.schemas import (
    FullSRSOutput,
    RawRequirementFeatures,
    FunctionalRequirement,
    FunctionalRequirementSet,
    NonFunctionalRequirement,
    NonFunctionalRequirementSet,
    Sitemap,
    SitemapNode,
    NavigationEdge,
    Entity,
    EntitySet,
    EntityAttribute,
    EntityRelationship,
    ComponentNode,
    ComponentTree,
    ComponentTreeSet,
    TechStackSelection,
    PipelineTiming,
    SupportedLanguage,
    Priority,
    NFRCategory,
    ScreenType,
    RelationshipType,
    AttributeType,
)

__all__ = [
    "LLMClient",
    "LLMAPIError",
    "strip_markdown_fences",
    "FullSRSOutput",
    "RawRequirementFeatures",
    "FunctionalRequirement",
    "FunctionalRequirementSet",
    "NonFunctionalRequirement",
    "NonFunctionalRequirementSet",
    "Sitemap",
    "SitemapNode",
    "NavigationEdge",
    "Entity",
    "EntitySet",
    "EntityAttribute",
    "EntityRelationship",
    "ComponentNode",
    "ComponentTree",
    "ComponentTreeSet",
    "TechStackSelection",
    "PipelineTiming",
    "SupportedLanguage",
    "Priority",
    "NFRCategory",
    "ScreenType",
    "RelationshipType",
    "AttributeType",
]