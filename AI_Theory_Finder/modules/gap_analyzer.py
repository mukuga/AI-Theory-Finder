"""Research gap analysis module for AI Theory Finder."""

from __future__ import annotations

from config import (
    EvidenceStatus,
    ResearchGap,
    TheoryRecommendation,
    TopicProfile,
    VariableCandidate,
    VariableMap,
)


class GapAnalyzer:
    """Identify cautious, explainable potential research gaps."""

    def analyze(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
        variable_map: VariableMap,
        max_gaps: int = 6,
    ) -> list[ResearchGap]:
        """Return potential research gaps for researcher review."""
        if max_gaps < 1:
            msg = "max_gaps must be at least 1"
            raise ValueError(msg)

        gaps = [
            *self._topic_specific_gaps(profile, theories, variable_map),
            *self._theory_coverage_gaps(profile, theories),
            *self._variable_role_gaps(variable_map),
            *self._context_gaps(profile),
        ]
        return self._dedupe_gaps(gaps)[:max_gaps]

    def _topic_specific_gaps(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
        variable_map: VariableMap,
    ) -> list[ResearchGap]:
        text = profile.normalized_topic
        theory_names = {theory.name for theory in theories}
        moderator_names = self._names(variable_map.moderators)
        gaps: list[ResearchGap] = []

        if "artificial intelligence" in text and "corporate governance" in text:
            gaps.append(
                ResearchGap(
                    statement="AI governance mechanisms remain weakly connected to firm performance models.",
                    rationale=(
                        "The topic combines AI, governance, and performance. This suggests an opportunity to "
                        "study whether governance quality, oversight routines, or board expertise explain how AI "
                        "investments become performance outcomes."
                    ),
                    evidence_status=EvidenceStatus.VERIFICATION_NEEDED,
                    suggested_direction=(
                        "Test AI capability with governance quality or board digital expertise as moderator or mediator."
                    ),
                )
            )

        if "Board Digital Expertise" in moderator_names or "Board Digital Expertise" in self._names(
            variable_map.independent_variables
        ):
            gaps.append(
                ResearchGap(
                    statement="Board digital expertise may be underexamined as a boundary condition.",
                    rationale=(
                        "The variable map identifies board digital expertise as relevant, but this construct is more "
                        "specialized than traditional board independence, board size, or ownership variables."
                    ),
                    evidence_status=EvidenceStatus.VERIFICATION_NEEDED,
                    suggested_direction=(
                        "Compare board digital expertise with traditional corporate governance variables in AI adoption studies."
                    ),
                )
            )

        if "Institutional Theory" not in theory_names and (
            "adoption" in text or "governance" in text or "developing countries" in profile.context_terms
        ):
            gaps.append(
                ResearchGap(
                    statement="Institutional Theory may be underutilized for this topic.",
                    rationale=(
                        "The topic includes adoption, governance, or country context signals where regulatory, normative, "
                        "and legitimacy pressures may matter."
                    ),
                    evidence_status=EvidenceStatus.VERIFICATION_NEEDED,
                    suggested_direction=(
                        "Use Institutional Theory to examine regulatory pressure, legitimacy, or national governance context."
                    ),
                )
            )

        return gaps

    def _theory_coverage_gaps(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
    ) -> list[ResearchGap]:
        theory_names = {theory.name for theory in theories}
        gaps: list[ResearchGap] = []
        text = profile.normalized_topic

        if "artificial intelligence" in text and "TOE Framework" not in theory_names:
            gaps.append(
                ResearchGap(
                    statement="Technology adoption conditions could be modeled more explicitly.",
                    rationale=(
                        "AI studies often need to distinguish technological, organizational, and environmental readiness. "
                        "If TOE is not among the top theories, adoption conditions may be hidden inside broad capability terms."
                    ),
                    evidence_status=EvidenceStatus.VERIFICATION_NEEDED,
                    suggested_direction="Add TOE variables such as technological readiness, organizational readiness, and competitive pressure.",
                )
            )

        if "corporate governance" in text and "Stakeholder Theory" not in theory_names:
            gaps.append(
                ResearchGap(
                    statement="Stakeholder-oriented governance outcomes may be less visible in the model.",
                    rationale=(
                        "Governance-performance studies can focus narrowly on shareholder monitoring. Stakeholder Theory "
                        "may broaden the model toward legitimacy, sustainability, and stakeholder value."
                    ),
                    evidence_status=EvidenceStatus.VERIFICATION_NEEDED,
                    suggested_direction="Consider stakeholder engagement, ESG performance, or reputation as additional outcomes or mediators.",
                )
            )

        return gaps

    def _variable_role_gaps(self, variable_map: VariableMap) -> list[ResearchGap]:
        gaps: list[ResearchGap] = []
        mediator_names = self._names(variable_map.mediators)
        moderator_names = self._names(variable_map.moderators)

        if "Digital Transformation" in mediator_names:
            gaps.append(
                ResearchGap(
                    statement="Digital transformation can be tested as a mechanism rather than a background condition.",
                    rationale=(
                        "The variable map positions digital transformation as a mediator. This creates a more precise "
                        "research model than treating digitalization as general context."
                    ),
                    evidence_status=EvidenceStatus.VERIFICATION_NEEDED,
                    suggested_direction="Measure digital transformation as a mediating construct between AI capability and firm outcomes.",
                )
            )

        if "Environmental Uncertainty" in moderator_names:
            gaps.append(
                ResearchGap(
                    statement="Environmental uncertainty may explain inconsistent AI-performance findings.",
                    rationale=(
                        "If AI effects differ across stable and turbulent environments, direct-effect models may miss "
                        "important boundary conditions."
                    ),
                    evidence_status=EvidenceStatus.VERIFICATION_NEEDED,
                    suggested_direction="Test interaction effects between AI capability and environmental uncertainty.",
                )
            )

        return gaps

    def _context_gaps(self, profile: TopicProfile) -> list[ResearchGap]:
        if profile.context_terms:
            context = ", ".join(profile.context_terms)
            return [
                ResearchGap(
                    statement=f"The study context is explicit but may need stronger theoretical justification: {context}.",
                    rationale=(
                        "Context terms are present in the topic. The report should explain why this setting matters "
                        "for theory, measurement, and generalizability."
                    ),
                    evidence_status=EvidenceStatus.VERIFICATION_NEEDED,
                    suggested_direction="Compare findings across context groups or justify the selected country, industry, or firm type.",
                )
            ]

        return [
            ResearchGap(
                statement="Most proposed models need clearer country, industry, or institutional context.",
                rationale=(
                    "The topic does not specify study setting. Without context, it is harder to identify whether findings "
                    "apply to developed countries, developing countries, specific industries, listed firms, or SMEs."
                ),
                evidence_status=EvidenceStatus.VERIFICATION_NEEDED,
                suggested_direction="Define a study context such as emerging markets, listed firms, SMEs, or a specific industry.",
            )
        ]

    def _names(self, variables: tuple[VariableCandidate, ...]) -> set[str]:
        return {variable.name for variable in variables}

    def _dedupe_gaps(self, gaps: list[ResearchGap]) -> list[ResearchGap]:
        seen: set[str] = set()
        unique: list[ResearchGap] = []
        for gap in gaps:
            key = gap.statement.lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(gap)
        return unique
