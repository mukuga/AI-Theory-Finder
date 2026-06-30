"""Theory recommendation module for AI Theory Finder."""

from __future__ import annotations

from dataclasses import dataclass

from config import EvidenceStatus, SourceEvidence, TheoryRecommendation, TopicProfile


@dataclass(frozen=True)
class TheoryKnowledge:
    """Curated theory metadata used for transparent scoring."""

    name: str
    domains: tuple[str, ...]
    keywords: tuple[str, ...]
    typical_use: str
    common_dependent_variables: tuple[str, ...]
    common_mediators: tuple[str, ...]
    common_moderators: tuple[str, ...]
    evidence: tuple[SourceEvidence, ...]


class TheoryFinder:
    """Rank relevant theories for a parsed research topic."""

    def __init__(self, knowledge_base: tuple[TheoryKnowledge, ...] | None = None) -> None:
        self._knowledge_base = knowledge_base or self._default_knowledge_base()

    def recommend(self, profile: TopicProfile, limit: int = 5) -> list[TheoryRecommendation]:
        """Return ranked theory recommendations for a topic profile."""
        if limit < 1:
            msg = "limit must be at least 1"
            raise ValueError(msg)

        ranked = sorted(
            (self._score_theory(theory, profile) for theory in self._knowledge_base),
            key=lambda item: item.relevance_score,
            reverse=True,
        )
        return ranked[:limit]

    def _score_theory(self, theory: TheoryKnowledge, profile: TopicProfile) -> TheoryRecommendation:
        topic_text = profile.normalized_topic
        profile_domains = set(profile.domains)
        profile_terms = set(profile.terms)
        profile_constructs = set(profile.focal_constructs)
        profile_outcomes = set(profile.outcome_constructs)

        domain_hits = profile_domains.intersection(theory.domains)
        outcome_terms = profile_outcomes.intersection(set(profile.terms) | set(profile.outcome_constructs))
        keyword_hits = {
            keyword
            for keyword in theory.keywords
            if keyword not in outcome_terms
            and (
                keyword in profile_constructs
                or keyword in profile_terms
                or ((" " in keyword or "'" in keyword) and keyword in topic_text)
            )
        }
        outcome_hits = profile_outcomes.intersection(theory.common_dependent_variables)
        explicit_name_hit = theory.name.lower() in topic_text
        ai_topic = "artificial intelligence" in profile_constructs or "machine learning" in profile_constructs
        ai_theory_fit = any(
            keyword in theory.keywords
            for keyword in (
                "artificial intelligence",
                "machine learning",
                "digital transformation",
                "technology adoption",
            )
        )

        score = 15
        score += min(24, 12 * len(domain_hits))
        score += 10 * len(keyword_hits)
        score += 4 * len(outcome_hits)
        score += 25 if explicit_name_hit else 0
        score += 8 if ai_topic and ai_theory_fit else 0
        score += 5 if theory.evidence else 0
        score = min(score, 100)

        why_it_fits = self._build_rationale(
            theory=theory,
            profile=profile,
            domain_hits=tuple(sorted(domain_hits)),
            keyword_hits=tuple(sorted(keyword_hits)),
            outcome_hits=tuple(sorted(outcome_hits)),
        )

        return TheoryRecommendation(
            name=theory.name,
            relevance_score=score,
            why_it_fits=why_it_fits,
            typical_use=theory.typical_use,
            common_dependent_variables=theory.common_dependent_variables,
            common_mediators=theory.common_mediators,
            common_moderators=theory.common_moderators,
            evidence=theory.evidence,
        )

    def _build_rationale(
        self,
        theory: TheoryKnowledge,
        profile: TopicProfile,
        domain_hits: tuple[str, ...],
        keyword_hits: tuple[str, ...],
        outcome_hits: tuple[str, ...],
    ) -> str:
        rationale_parts: list[str] = []
        if domain_hits:
            rationale_parts.append(f"domain fit with {', '.join(domain_hits)}")
        if keyword_hits:
            rationale_parts.append(f"construct fit through {', '.join(keyword_hits[:5])}")
        if outcome_hits:
            rationale_parts.append(f"outcome fit with {', '.join(outcome_hits)}")

        if not rationale_parts:
            return (
                f"{theory.name} has a weaker direct match to '{profile.raw_topic}', "
                "but may still be useful as a complementary lens if the study needs its assumptions."
            )

        return (
            f"{theory.name} fits '{profile.raw_topic}' because it shows "
            f"{'; '.join(rationale_parts)}. This recommendation is based on curated theory metadata, "
            "not an automated claim that every listed source studied this exact topic."
        )

    def _default_knowledge_base(self) -> tuple[TheoryKnowledge, ...]:
        return (
            TheoryKnowledge(
                name="Resource-Based View",
                domains=("strategic management", "innovation management"),
                keywords=(
                    "capability",
                    "competitive advantage",
                    "resource",
                    "artificial intelligence",
                    "knowledge management",
                    "innovation capability",
                    "firm performance",
                ),
                typical_use=(
                    "Explains how valuable, rare, inimitable, and organizationally embedded resources "
                    "can support sustained competitive advantage and performance differences."
                ),
                common_dependent_variables=(
                    "firm performance",
                    "firm value",
                    "innovation performance",
                    "competitive advantage",
                ),
                common_mediators=("innovation capability", "knowledge management", "digital transformation"),
                common_moderators=("environmental uncertainty", "firm size", "market dynamism"),
                evidence=(
                    SourceEvidence(
                        title="Firm Resources and Sustained Competitive Advantage",
                        authors=("Barney",),
                        year=1991,
                        venue="Journal of Management",
                        status=EvidenceStatus.CURATED,
                    ),
                ),
            ),
            TheoryKnowledge(
                name="Dynamic Capability Theory",
                domains=("strategic management", "innovation management", "information systems"),
                keywords=(
                    "dynamic capability",
                    "digital transformation",
                    "artificial intelligence",
                    "machine learning",
                    "adaptation",
                    "sensing",
                    "seizing",
                    "reconfiguring",
                    "innovation capability",
                ),
                typical_use=(
                    "Explains how firms sense technological opportunities, seize them, and reconfigure "
                    "resources under changing environments."
                ),
                common_dependent_variables=(
                    "firm performance",
                    "innovation performance",
                    "competitive advantage",
                    "digital transformation performance",
                ),
                common_mediators=("digital transformation", "innovation capability", "organizational agility"),
                common_moderators=("environmental uncertainty", "technological turbulence", "firm size"),
                evidence=(
                    SourceEvidence(
                        title="Dynamic Capabilities and Strategic Management",
                        authors=("Teece", "Pisano", "Shuen"),
                        year=1997,
                        venue="Strategic Management Journal",
                        status=EvidenceStatus.CURATED,
                    ),
                ),
            ),
            TheoryKnowledge(
                name="Agency Theory",
                domains=("corporate governance", "finance and accounting"),
                keywords=(
                    "board",
                    "corporate governance",
                    "governance",
                    "ownership",
                    "directors",
                    "audit committee",
                    "firm performance",
                    "firm value",
                ),
                typical_use=(
                    "Explains how monitoring, incentives, ownership, and board structures address conflicts "
                    "between principals and agents."
                ),
                common_dependent_variables=("firm performance", "firm value", "profitability"),
                common_mediators=("monitoring effectiveness", "risk disclosure", "managerial discipline"),
                common_moderators=("board independence", "ownership concentration", "firm size"),
                evidence=(
                    SourceEvidence(
                        title="Theory of the Firm: Managerial Behavior, Agency Costs and Ownership Structure",
                        authors=("Jensen", "Meckling"),
                        year=1976,
                        venue="Journal of Financial Economics",
                        status=EvidenceStatus.CURATED,
                    ),
                ),
            ),
            TheoryKnowledge(
                name="Stakeholder Theory",
                domains=("corporate governance", "sustainability"),
                keywords=(
                    "stakeholder",
                    "corporate governance",
                    "environmental social governance",
                    "sustainability",
                    "csr",
                    "firm performance",
                ),
                typical_use=(
                    "Explains how firms create value by managing relationships with shareholders, employees, "
                    "customers, communities, regulators, and other stakeholders."
                ),
                common_dependent_variables=(
                    "firm performance",
                    "sustainability performance",
                    "firm value",
                    "reputation",
                ),
                common_mediators=("stakeholder engagement", "csr performance", "reputation"),
                common_moderators=("industry sensitivity", "regulatory pressure", "ownership structure"),
                evidence=(
                    SourceEvidence(
                        title="Strategic Management: A Stakeholder Approach",
                        authors=("Freeman",),
                        year=1984,
                        venue="Pitman",
                        status=EvidenceStatus.CURATED,
                    ),
                    SourceEvidence(
                        title="The Stakeholder Theory of the Corporation: Concepts, Evidence, and Implications",
                        authors=("Donaldson", "Preston"),
                        year=1995,
                        venue="Academy of Management Review",
                        status=EvidenceStatus.CURATED,
                    ),
                ),
            ),
            TheoryKnowledge(
                name="Institutional Theory",
                domains=("corporate governance", "information systems", "sustainability"),
                keywords=(
                    "institutional",
                    "regulation",
                    "legitimacy",
                    "governance",
                    "adoption",
                    "developing countries",
                    "emerging markets",
                    "environmental social governance",
                ),
                typical_use=(
                    "Explains how coercive, normative, and mimetic pressures shape organizational choices, "
                    "technology adoption, governance practices, and legitimacy-seeking behavior."
                ),
                common_dependent_variables=(
                    "technology adoption",
                    "governance quality",
                    "sustainability performance",
                    "firm performance",
                ),
                common_mediators=("legitimacy", "governance quality", "compliance capability"),
                common_moderators=("regulatory pressure", "national institutions", "industry norms"),
                evidence=(
                    SourceEvidence(
                        title="The Iron Cage Revisited: Institutional Isomorphism and Collective Rationality in Organizational Fields",
                        authors=("DiMaggio", "Powell"),
                        year=1983,
                        venue="American Sociological Review",
                        status=EvidenceStatus.CURATED,
                    ),
                ),
            ),
            TheoryKnowledge(
                name="Knowledge-Based View",
                domains=("strategic management", "innovation management", "information systems"),
                keywords=(
                    "knowledge",
                    "knowledge management",
                    "artificial intelligence",
                    "machine learning",
                    "innovation",
                    "capability",
                    "digital transformation",
                ),
                typical_use=(
                    "Explains the firm as an institution for integrating, creating, and applying knowledge, "
                    "especially when knowledge assets influence innovation and performance."
                ),
                common_dependent_variables=("innovation performance", "firm performance", "competitive advantage"),
                common_mediators=("knowledge management", "absorptive capacity", "innovation capability"),
                common_moderators=("knowledge intensity", "organizational learning culture", "firm size"),
                evidence=(
                    SourceEvidence(
                        title="Toward a Knowledge-Based Theory of the Firm",
                        authors=("Grant",),
                        year=1996,
                        venue="Strategic Management Journal",
                        status=EvidenceStatus.CURATED,
                    ),
                ),
            ),
            TheoryKnowledge(
                name="TOE Framework",
                domains=("information systems", "innovation management"),
                keywords=(
                    "technology adoption",
                    "adoption",
                    "digital readiness",
                    "artificial intelligence",
                    "machine learning",
                    "technology",
                    "organization",
                    "environment",
                    "toe",
                ),
                typical_use=(
                    "Explains technology adoption through technological, organizational, and environmental "
                    "conditions."
                ),
                common_dependent_variables=("technology adoption", "ai adoption", "digital transformation"),
                common_mediators=("digital readiness", "adoption intention", "implementation capability"),
                common_moderators=("environmental uncertainty", "competitive pressure", "firm size"),
                evidence=(
                    SourceEvidence(
                        title="The Processes of Technological Innovation",
                        authors=("Tornatzky", "Fleischer"),
                        year=1990,
                        venue="Lexington Books",
                        status=EvidenceStatus.CURATED,
                    ),
                ),
            ),
        )
