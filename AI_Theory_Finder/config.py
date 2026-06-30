"""Shared configuration and domain models for AI Theory Finder."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
DEFAULT_REPORT_NAME = "ai_theory_finder_report.md"


class EvidenceStatus(str, Enum):
    """Evidence verification state for any academic claim or citation."""

    VERIFIED = "Verified"
    CURATED = "Curated Knowledge Base"
    VERIFICATION_NEEDED = "Verification Needed"
    UNAVAILABLE = "Unavailable"


class VariableRole(str, Enum):
    """Common variable roles used in quantitative research models."""

    INDEPENDENT = "Independent Variable"
    DEPENDENT = "Dependent Variable"
    MEDIATOR = "Mediator"
    MODERATOR = "Moderator"
    CONTROL = "Control Variable"


@dataclass(frozen=True)
class SourceEvidence:
    """A traceable academic source or a placeholder requiring verification."""

    title: str
    authors: tuple[str, ...] = ()
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    url: str | None = None
    status: EvidenceStatus = EvidenceStatus.VERIFICATION_NEEDED
    note: str | None = None

    def display_label(self) -> str:
        """Return a compact citation label for reports."""
        author_label = ", ".join(self.authors) if self.authors else "Unknown author"
        year_label = str(self.year) if self.year else "n.d."
        suffix = "" if self.status != EvidenceStatus.VERIFICATION_NEEDED else " [Verification Needed]"
        return f"{author_label} ({year_label}). {self.title}.{suffix}"


@dataclass(frozen=True)
class TopicProfile:
    """Structured interpretation of a user-entered research topic."""

    raw_topic: str
    normalized_topic: str
    terms: tuple[str, ...]
    domains: tuple[str, ...]
    focal_constructs: tuple[str, ...]
    outcome_constructs: tuple[str, ...]
    context_terms: tuple[str, ...] = ()
    explanation: str = ""


@dataclass(frozen=True)
class TheoryRecommendation:
    """A ranked theory recommendation with usage patterns and evidence."""

    name: str
    relevance_score: int
    why_it_fits: str
    typical_use: str
    common_dependent_variables: tuple[str, ...] = ()
    common_mediators: tuple[str, ...] = ()
    common_moderators: tuple[str, ...] = ()
    evidence: tuple[SourceEvidence, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.relevance_score <= 100:
            msg = "relevance_score must be between 0 and 100"
            raise ValueError(msg)


@dataclass(frozen=True)
class VariableCandidate:
    """A candidate research variable with its model role and rationale."""

    name: str
    role: VariableRole
    rationale: str
    linked_theories: tuple[str, ...] = ()
    evidence_status: EvidenceStatus = EvidenceStatus.CURATED


@dataclass(frozen=True)
class VariableMap:
    """Grouped variables for conceptual model building."""

    independent_variables: tuple[VariableCandidate, ...] = ()
    dependent_variables: tuple[VariableCandidate, ...] = ()
    mediators: tuple[VariableCandidate, ...] = ()
    moderators: tuple[VariableCandidate, ...] = ()
    controls: tuple[VariableCandidate, ...] = ()

    def by_role(self) -> Mapping[VariableRole, Sequence[VariableCandidate]]:
        """Return variables grouped by formal role."""
        return {
            VariableRole.INDEPENDENT: self.independent_variables,
            VariableRole.DEPENDENT: self.dependent_variables,
            VariableRole.MEDIATOR: self.mediators,
            VariableRole.MODERATOR: self.moderators,
            VariableRole.CONTROL: self.controls,
        }


@dataclass(frozen=True)
class ConceptualFramework:
    """Textual conceptual framework and path relationships."""

    title: str
    narrative: str
    paths: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResearchGap:
    """Potential gap with a cautious explanation."""

    statement: str
    rationale: str
    evidence_status: EvidenceStatus = EvidenceStatus.VERIFICATION_NEEDED
    suggested_direction: str | None = None


@dataclass(frozen=True)
class Hypothesis:
    """A generated hypothesis template for researcher review."""

    label: str
    statement: str
    rationale: str
    evidence_status: EvidenceStatus = EvidenceStatus.CURATED


@dataclass(frozen=True)
class ReferenceRecommendation:
    """Reference suggestions associated with a theory."""

    theory_name: str
    seminal_sources: tuple[SourceEvidence, ...] = ()
    recent_sources: tuple[SourceEvidence, ...] = ()
    common_application: str = ""
    typical_models: tuple[str, ...] = ()


@dataclass
class ResearchReport:
    """Final report object assembled by the report generator."""

    topic_profile: TopicProfile
    theories: list[TheoryRecommendation] = field(default_factory=list)
    variable_map: VariableMap | None = None
    framework: ConceptualFramework | None = None
    gaps: list[ResearchGap] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    references: list[ReferenceRecommendation] = field(default_factory=list)
    directions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings."""

    max_theories: int = 5
    max_references_per_theory: int = 6
    enable_literature_search: bool = False
    literature_timeout_seconds: float = 12.0
    require_verified_recent_sources: bool = False
    output_dir: Path = OUTPUT_DIR
