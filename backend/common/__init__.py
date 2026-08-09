"""
backend/srs/common/__init__.py

Public interface for the SRS-specific shared foundation. Unlike
backend/shared/ (generic infra reused by every top-level module), this
common/ only holds schemas.py — the Pydantic data contracts specific
to the 7 SRS pipeline stages (FRs, NFRs, Sitemap, Entities, etc).

For generic infra (LLMClient, Logger, JSON helpers), import from
backend/shared/ instead — every generator here already does.
"""

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