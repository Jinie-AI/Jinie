"""
backend/srs/__init__.py

Public package interface for the entire srs/ module. External callers
(e.g. backend/engine/, the Engine Coordinator) should import from this
package root rather than reaching into individual generator folders
directly — this keeps the internal stage breakdown (requirements_generator,
fr_generator, nfr_generator, sitemap_generator, entities_generator,
component_tree_generator, stack_identifier_generator) an implementation
detail that can be reorganized without breaking external callers.

Usage:
    from srs import run_srs_pipeline, FullSRSOutput

    result: FullSRSOutput = run_srs_pipeline("Build me a social feed app")
"""

from pipeline import run_srs_pipeline, SRSPipelineError
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
    "run_srs_pipeline",
    "SRSPipelineError",
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

__version__ = "0.2.0"