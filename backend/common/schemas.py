"""
schemas.py

Pydantic V2 data structures shared across every stage of the SRS
generation pipeline (backend/srs/). Every submodule (requirement,
functional, non_functional, sitemap, entities, component_tree,
stack_identifier, pipeline) imports its input/output shapes from here
so the whole pipeline stays strictly typed end-to-end.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


# =====================================================================
# Shared enums
# =====================================================================

class SupportedLanguage(str, Enum):
    ENGLISH = "english"
    URDU = "urdu"
    ROMAN_URDU = "roman_urdu"
    UNKNOWN = "unknown"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NFRCategory(str, Enum):
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    RELIABILITY = "reliability"
    SCALABILITY = "scalability"
    ACCESSIBILITY = "accessibility"


class ScreenType(str, Enum):
    AUTH = "auth"
    FEED = "feed"
    DETAIL = "detail"
    FORM = "form"
    PROFILE = "profile"
    SETTINGS = "settings"
    LIST = "list"
    DASHBOARD = "dashboard"
    GENERIC = "generic"


class RelationshipType(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"


class AttributeType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    ARRAY = "array"
    OBJECT = "object"
    REFERENCE = "reference"


# =====================================================================
# Stage 1 — Raw requirement extraction
# =====================================================================

class RawRequirementFeatures(BaseModel):
    """Output of requirement.py — unstructured-to-semi-structured pass."""

    model_config = ConfigDict(extra="forbid")

    trace_id: str = Field(..., description="Pipeline-wide trace identifier")
    original_prompt: str = Field(..., description="Verbatim user input")
    detected_language: SupportedLanguage = Field(default=SupportedLanguage.UNKNOWN)
    normalized_text: str = Field(..., description="Cleaned/translated working text")
    extracted_keywords: List[str] = Field(default_factory=list)
    intent_tags: List[str] = Field(
        default_factory=list,
        description="Coarse intents, e.g. ['auth', 'social_feed', 'ecommerce']",
    )
    candidate_entities: List[str] = Field(
        default_factory=list, description="Nouns likely to become data entities"
    )
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


# =====================================================================
# Stage 2 — Functional requirements
# =====================================================================

class FunctionalRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fr_id: str = Field(..., description="Stable identifier, e.g. FR-001")
    description: str
    actors: List[str] = Field(default_factory=list)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    priority: Priority = Field(default=Priority.MEDIUM)
    source_keywords: List[str] = Field(default_factory=list)


class FunctionalRequirementSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    requirements: List[FunctionalRequirement] = Field(default_factory=list)


# =====================================================================
# Stage 3 — Non-functional requirements
# =====================================================================

class NonFunctionalRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nfr_id: str = Field(..., description="Stable identifier, e.g. NFR-001")
    category: NFRCategory
    constraint: str = Field(..., description="Human-readable constraint statement")
    linked_fr_id: Optional[str] = Field(
        default=None, description="FR node this constraint attaches to, if any"
    )
    threshold_value: Optional[float] = Field(default=None)
    threshold_unit: Optional[str] = Field(default=None, description="e.g. 'ms', '%'")


class NonFunctionalRequirementSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    requirements: List[NonFunctionalRequirement] = Field(default_factory=list)


# =====================================================================
# Stage 4 — Sitemap / navigation topology
# =====================================================================

class SitemapNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    screen_id: str = Field(..., description="Stable identifier, e.g. SCR-001")
    screen_name: str = Field(..., description="e.g. 'AuthScreen', 'MainFeed'")
    route: str = Field(..., description="e.g. '/auth', '/feed'")
    screen_type: ScreenType = Field(default=ScreenType.GENERIC)
    linked_fr_ids: List[str] = Field(default_factory=list)
    is_entry_point: bool = Field(default=False)


class NavigationEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_screen_id: str
    to_screen_id: str
    trigger: str = Field(default="navigate", description="e.g. 'on_login_success'")


class Sitemap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    nodes: List[SitemapNode] = Field(default_factory=list)
    edges: List[NavigationEdge] = Field(default_factory=list)


# =====================================================================
# Stage 5 — Entities
# =====================================================================

class EntityAttribute(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: AttributeType
    required: bool = Field(default=True)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class EntityRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_entity: str
    to_entity: str
    relationship_type: RelationshipType


class Entity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_id: str = Field(..., description="Stable identifier, e.g. ENT-001")
    name: str
    attributes: List[EntityAttribute] = Field(default_factory=list)
    relationships: List[EntityRelationship] = Field(default_factory=list)
    source_fr_ids: List[str] = Field(default_factory=list)


class EntitySet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    entities: List[Entity] = Field(default_factory=list)


# =====================================================================
# Stage 6 — Component tree
# =====================================================================

class ComponentNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component_id: str
    component_type: str = Field(..., description="e.g. 'SafeAreaView', 'FlatList'")
    props: Dict[str, Any] = Field(default_factory=dict)
    design_tokens: Dict[str, str] = Field(default_factory=dict)
    children: List["ComponentNode"] = Field(default_factory=list)


ComponentNode.model_rebuild()


class ComponentTree(BaseModel):
    model_config = ConfigDict(extra="forbid")

    screen_id: str
    screen_name: str
    root: ComponentNode


class ComponentTreeSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    trees: List[ComponentTree] = Field(default_factory=list)


# =====================================================================
# Stage 7 — Tech stack targets
# =====================================================================

class TechStackSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framework: str = Field(default="React Native (Expo)")
    state_management: str = Field(default="Zustand")
    ui_library: str = Field(default="Tamagui")
    navigation_library: str = Field(default="React Navigation")
    backend_service: str = Field(default="Firebase / Firestore")
    reasoning: List[str] = Field(default_factory=list)


# =====================================================================
# Final aggregate output
# =====================================================================

class PipelineTiming(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage_name: str
    duration_ms: float


class FullSRSOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    raw_features: RawRequirementFeatures
    functional_requirements: FunctionalRequirementSet
    non_functional_requirements: NonFunctionalRequirementSet
    sitemap: Sitemap
    entities: EntitySet
    component_trees: ComponentTreeSet
    tech_stack: TechStackSelection
    stage_timings: List[PipelineTiming] = Field(default_factory=list)
    total_duration_ms: float = Field(default=0.0)