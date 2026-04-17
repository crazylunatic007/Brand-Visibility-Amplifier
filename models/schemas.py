from pydantic import BaseModel
from enum import Enum
from typing import Optional


class QueryIntent(str, Enum):
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial_investigation"


class QueryType(str, Enum):
    EQUIVALENT = "equivalent"
    FOLLOW_UP = "follow_up"
    GENERALIZATION = "generalization"
    SPECIFICATION = "specification"
    CANONICALIZATION = "canonicalization"
    LANGUAGE_TRANSLATION = "language_translation"
    ENTAILMENT = "entailment"
    CLARIFICATION = "clarification"


class GeneratedQuery(BaseModel):
    query_text: str
    intent: QueryIntent
    query_type: QueryType
    rationale: str
    selected: bool = False
    search_volume: Optional[int] = None
    keyword_difficulty: Optional[float] = None
    semrush_validated: bool = False


class ContentSection(BaseModel):
    heading: str
    heading_level: int
    body_text: str
    word_count: int
    section_index: int


class QueryPlacement(BaseModel):
    query: GeneratedQuery
    target_section: ContentSection
    placement_type: str  # "new_subsection" | "expand_existing" | "new_paragraph"
    reasoning: str
    suggested_heading: Optional[str] = None
    content_brief: str


class ParsedContent(BaseModel):
    url: str
    title: str
    sections: list[ContentSection]
    full_text: str
    meta_description: Optional[str] = None
