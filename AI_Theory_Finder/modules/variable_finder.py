"""Variable recommendation module for AI Theory Finder."""

from __future__ import annotations

from dataclasses import dataclass

from config import (
    EvidenceStatus,
    TheoryRecommendation,
    TopicProfile,
    VariableCandidate,
    VariableMap,
    VariableRole,
)


@dataclass(frozen=True)
class VariableTemplate:
    """Curated variable candidate used for transparent recommendation."""

    name: str
    role: VariableRole
    rationale: str
    keywords: tuple[str, ...] = ()
    domains: tuple[str, ...] = ()
    linked_theories: tuple[str, ...] = ()
    priority: int = 50


class VariableFinder:
    """Generate a structured variable map from topic and theory signals."""

    def __init__(self, templates: tuple[VariableTemplate, ...] | None = None) -> None:
        self._templates = templates or self._default_templates()

    def recommend(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
        max_per_role: int = 6,
    ) -> VariableMap:
        """Return candidate independent, dependent, mediator, moderator, and control variables."""
        if max_per_role < 1:
            msg = "max_per_role must be at least 1"
            raise ValueError(msg)

        theory_names = tuple(theory.name for theory in theories)
        selected = self._select_templates(profile, theory_names)
        selected = self._add_theory_common_variables(selected, theories)

        return VariableMap(
            independent_variables=self._build_candidates(
                selected,
                VariableRole.INDEPENDENT,
                max_per_role,
            ),
            dependent_variables=self._build_candidates(
                selected,
                VariableRole.DEPENDENT,
                max_per_role,
            ),
            mediators=self._build_candidates(selected, VariableRole.MEDIATOR, max_per_role),
            moderators=self._build_candidates(selected, VariableRole.MODERATOR, max_per_role),
            controls=self._build_candidates(selected, VariableRole.CONTROL, max_per_role),
        )

    def _select_templates(
        self,
        profile: TopicProfile,
        theory_names: tuple[str, ...],
    ) -> list[VariableTemplate]:
        topic_terms = set(profile.terms) | set(profile.focal_constructs) | set(profile.outcome_constructs)
        topic_domains = set(profile.domains)
        topic_text = profile.normalized_topic
        selected: list[VariableTemplate] = []

        for template in self._templates:
            keyword_hit = any(keyword in topic_terms or keyword in topic_text for keyword in template.keywords)
            domain_hit = bool(topic_domains.intersection(template.domains))
            theory_hit = bool(set(theory_names).intersection(template.linked_theories))
            if keyword_hit or domain_hit or theory_hit:
                selected.append(template)

        return sorted(selected, key=lambda item: (-item.priority, item.name))

    def _add_theory_common_variables(
        self,
        selected: list[VariableTemplate],
        theories: list[TheoryRecommendation],
    ) -> list[VariableTemplate]:
        existing = {(item.role, item.name.lower()) for item in selected}
        additions: list[VariableTemplate] = []

        for theory in theories:
            for variable in theory.common_dependent_variables:
                self._append_theory_variable(
                    additions,
                    existing,
                    name=variable,
                    role=VariableRole.DEPENDENT,
                    theory=theory.name,
                )
            for variable in theory.common_mediators:
                self._append_theory_variable(
                    additions,
                    existing,
                    name=variable,
                    role=VariableRole.MEDIATOR,
                    theory=theory.name,
                )
            for variable in theory.common_moderators:
                self._append_theory_variable(
                    additions,
                    existing,
                    name=variable,
                    role=VariableRole.MODERATOR,
                    theory=theory.name,
                )

        return [*selected, *additions]

    def _append_theory_variable(
        self,
        additions: list[VariableTemplate],
        existing: set[tuple[VariableRole, str]],
        name: str,
        role: VariableRole,
        theory: str,
    ) -> None:
        key = (role, name.lower())
        if key in existing:
            return
        existing.add(key)
        additions.append(
            VariableTemplate(
                name=self._format_variable_name(name),
                role=role,
                rationale=f"Commonly appears as a {role.value.lower()} in models using {theory}.",
                linked_theories=(theory,),
                priority=35,
            )
        )

    def _build_candidates(
        self,
        templates: list[VariableTemplate],
        role: VariableRole,
        max_per_role: int,
    ) -> tuple[VariableCandidate, ...]:
        candidates: list[VariableCandidate] = []
        seen: set[str] = set()

        for template in templates:
            if template.role != role:
                continue
            key = template.name.lower()
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                VariableCandidate(
                    name=template.name,
                    role=template.role,
                    rationale=template.rationale,
                    linked_theories=template.linked_theories,
                    evidence_status=EvidenceStatus.CURATED,
                )
            )
            if len(candidates) >= max_per_role:
                break

        return tuple(candidates)

    def _format_variable_name(self, name: str) -> str:
        special_cases = {
            "ai adoption": "AI Adoption",
            "ai capability": "AI Capability",
            "roa": "ROA",
            "roe": "ROE",
            "tobin's q": "Tobin's Q",
        }
        normalized = name.strip().lower()
        if normalized in special_cases:
            return special_cases[normalized]
        return " ".join(word.capitalize() if word.lower() not in {"and", "of"} else word for word in name.split())

    def _default_templates(self) -> tuple[VariableTemplate, ...]:
        return (
            VariableTemplate(
                name="AI Capability",
                role=VariableRole.INDEPENDENT,
                rationale=(
                    "Captures the firm's ability to deploy AI resources, skills, data infrastructure, "
                    "and analytics routines."
                ),
                keywords=("artificial intelligence", "machine learning", "capability", "ai"),
                domains=("artificial intelligence", "strategic management", "information systems"),
                linked_theories=("Resource-Based View", "Dynamic Capability Theory", "Knowledge-Based View"),
                priority=98,
            ),
            VariableTemplate(
                name="AI Adoption",
                role=VariableRole.INDEPENDENT,
                rationale="Represents the extent to which the organization implements AI technologies in processes or decisions.",
                keywords=("artificial intelligence", "machine learning", "adoption", "technology adoption"),
                domains=("artificial intelligence", "information systems"),
                linked_theories=("TOE Framework", "Institutional Theory"),
                priority=94,
            ),
            VariableTemplate(
                name="Digital Readiness",
                role=VariableRole.INDEPENDENT,
                rationale="Reflects technological, organizational, and human readiness for digital initiatives.",
                keywords=("digital readiness", "digital transformation", "adoption", "technology adoption"),
                domains=("information systems", "artificial intelligence"),
                linked_theories=("TOE Framework", "Dynamic Capability Theory"),
                priority=88,
            ),
            VariableTemplate(
                name="Machine Learning Usage",
                role=VariableRole.INDEPENDENT,
                rationale="Operationalizes AI through the use of machine learning tools, models, or analytics applications.",
                keywords=("machine learning", "artificial intelligence", "analytics"),
                domains=("artificial intelligence", "information systems"),
                linked_theories=("Knowledge-Based View", "Dynamic Capability Theory"),
                priority=84,
            ),
            VariableTemplate(
                name="Corporate Governance Quality",
                role=VariableRole.INDEPENDENT,
                rationale="Represents board structure, oversight, transparency, and governance mechanisms.",
                keywords=("corporate governance", "governance", "board"),
                domains=("corporate governance", "finance and accounting"),
                linked_theories=("Agency Theory", "Stakeholder Theory", "Institutional Theory"),
                priority=90,
            ),
            VariableTemplate(
                name="Board Digital Expertise",
                role=VariableRole.INDEPENDENT,
                rationale="Captures whether board members have digital, analytics, technology, or AI-related expertise.",
                keywords=("board", "corporate governance", "digital expertise", "artificial intelligence"),
                domains=("corporate governance", "artificial intelligence"),
                linked_theories=("Agency Theory", "Dynamic Capability Theory"),
                priority=80,
            ),
            VariableTemplate(
                name="Firm Performance",
                role=VariableRole.DEPENDENT,
                rationale="Broad outcome for financial, operational, or market performance effects.",
                keywords=("firm performance", "performance", "financial performance"),
                domains=("strategic management", "finance and accounting"),
                linked_theories=(
                    "Resource-Based View",
                    "Dynamic Capability Theory",
                    "Agency Theory",
                    "Stakeholder Theory",
                ),
                priority=98,
            ),
            VariableTemplate(
                name="ROA",
                role=VariableRole.DEPENDENT,
                rationale="Accounting-based profitability measure often used to operationalize firm performance.",
                keywords=("return on assets", "roa", "profitability", "firm performance"),
                domains=("finance and accounting",),
                linked_theories=("Agency Theory", "Resource-Based View"),
                priority=92,
            ),
            VariableTemplate(
                name="ROE",
                role=VariableRole.DEPENDENT,
                rationale="Accounting-based shareholder return measure commonly used in governance and performance studies.",
                keywords=("return on equity", "roe", "profitability", "firm performance"),
                domains=("finance and accounting",),
                linked_theories=("Agency Theory", "Stakeholder Theory"),
                priority=90,
            ),
            VariableTemplate(
                name="Tobin's Q",
                role=VariableRole.DEPENDENT,
                rationale="Market-based firm value measure often used when governance or strategic assets may affect valuation.",
                keywords=("tobin's q", "firm value", "market value", "firm performance"),
                domains=("finance and accounting", "corporate governance"),
                linked_theories=("Agency Theory", "Stakeholder Theory"),
                priority=88,
            ),
            VariableTemplate(
                name="Innovation Performance",
                role=VariableRole.DEPENDENT,
                rationale="Useful when AI or knowledge resources are expected to improve new products, processes, or patents.",
                keywords=("innovation", "innovation performance", "artificial intelligence", "knowledge management"),
                domains=("innovation management", "artificial intelligence"),
                linked_theories=("Resource-Based View", "Dynamic Capability Theory", "Knowledge-Based View"),
                priority=84,
            ),
            VariableTemplate(
                name="Digital Transformation",
                role=VariableRole.MEDIATOR,
                rationale="Explains how AI resources may translate into organizational change and performance outcomes.",
                keywords=("digital transformation", "artificial intelligence", "digital readiness"),
                domains=("information systems", "artificial intelligence", "strategic management"),
                linked_theories=("Dynamic Capability Theory", "TOE Framework"),
                priority=96,
            ),
            VariableTemplate(
                name="Knowledge Management",
                role=VariableRole.MEDIATOR,
                rationale="Connects AI-enabled data processing and learning routines with innovation or performance.",
                keywords=("knowledge management", "knowledge", "artificial intelligence", "machine learning"),
                domains=("innovation management", "information systems"),
                linked_theories=("Knowledge-Based View", "Resource-Based View"),
                priority=90,
            ),
            VariableTemplate(
                name="Innovation Capability",
                role=VariableRole.MEDIATOR,
                rationale="Represents a mechanism through which AI and digital resources can improve performance.",
                keywords=("innovation capability", "innovation", "capability", "artificial intelligence"),
                domains=("innovation management", "strategic management"),
                linked_theories=("Resource-Based View", "Dynamic Capability Theory", "Knowledge-Based View"),
                priority=88,
            ),
            VariableTemplate(
                name="Corporate Governance Quality",
                role=VariableRole.MODERATOR,
                rationale="Can condition whether AI investment is monitored and converted into firm-level outcomes.",
                keywords=("corporate governance", "governance", "board", "artificial intelligence"),
                domains=("corporate governance", "artificial intelligence"),
                linked_theories=("Agency Theory", "Stakeholder Theory"),
                priority=92,
            ),
            VariableTemplate(
                name="Board Digital Expertise",
                role=VariableRole.MODERATOR,
                rationale="May strengthen the effect of AI capability by improving strategic oversight of digital initiatives.",
                keywords=("board", "digital expertise", "artificial intelligence", "corporate governance"),
                domains=("corporate governance", "artificial intelligence"),
                linked_theories=("Agency Theory", "Dynamic Capability Theory"),
                priority=96,
            ),
            VariableTemplate(
                name="Firm Size",
                role=VariableRole.MODERATOR,
                rationale="Larger firms may have more resources to absorb AI investments, while smaller firms may be more agile.",
                keywords=("firm size", "smes", "small and medium enterprises"),
                domains=("strategic management", "finance and accounting"),
                linked_theories=("Resource-Based View", "TOE Framework"),
                priority=82,
            ),
            VariableTemplate(
                name="Environmental Uncertainty",
                role=VariableRole.MODERATOR,
                rationale="Can change the value of AI capabilities and dynamic capabilities under turbulent conditions.",
                keywords=("environmental uncertainty", "market dynamism", "technological turbulence"),
                domains=("strategic management", "information systems"),
                linked_theories=("Dynamic Capability Theory", "TOE Framework", "Institutional Theory"),
                priority=80,
            ),
            VariableTemplate(
                name="Industry",
                role=VariableRole.CONTROL,
                rationale="Controls for sector-level differences in technology adoption, governance, and performance.",
                keywords=("industry", "manufacturing", "banking", "healthcare", "education"),
                domains=(
                    "artificial intelligence",
                    "corporate governance",
                    "strategic management",
                    "information systems",
                ),
                linked_theories=(),
                priority=70,
            ),
            VariableTemplate(
                name="Firm Age",
                role=VariableRole.CONTROL,
                rationale="Controls for maturity and accumulated organizational experience.",
                keywords=("firm age", "listed firms", "public firms"),
                domains=("strategic management", "finance and accounting"),
                linked_theories=(),
                priority=66,
            ),
        )
