"""Hypothesis generation module for AI Theory Finder."""

from __future__ import annotations

from config import ConceptualFramework, EvidenceStatus, Hypothesis, VariableCandidate, VariableMap


class HypothesisGenerator:
    """Generate example hypothesis templates from a conceptual framework."""

    def generate(
        self,
        variable_map: VariableMap,
        framework: ConceptualFramework,
        max_hypotheses: int = 6,
    ) -> list[Hypothesis]:
        """Return ordered hypothesis templates for researcher review."""
        if max_hypotheses < 1:
            msg = "max_hypotheses must be at least 1"
            raise ValueError(msg)

        primary_iv = self._first(variable_map.independent_variables)
        primary_dv = self._first(variable_map.dependent_variables)
        primary_mediator = self._first(variable_map.mediators)
        primary_moderator = self._first(variable_map.moderators)
        hypotheses: list[Hypothesis] = []

        if primary_iv and primary_dv:
            hypotheses.append(self._direct_effect("H1", primary_iv, primary_dv))

        if primary_iv and primary_mediator:
            hypotheses.append(self._antecedent_to_mediator("H2", primary_iv, primary_mediator))

        if primary_mediator and primary_dv:
            hypotheses.append(self._mediator_to_outcome("H3", primary_mediator, primary_dv))

        if primary_iv and primary_mediator and primary_dv:
            hypotheses.append(self._mediation("H4", primary_iv, primary_mediator, primary_dv))

        if primary_iv and primary_dv and primary_moderator:
            hypotheses.append(self._moderation("H5", primary_moderator, primary_iv, primary_dv))

        secondary_iv = self._second(variable_map.independent_variables)
        if secondary_iv and primary_dv:
            label = f"H{len(hypotheses) + 1}"
            hypotheses.append(self._direct_effect(label, secondary_iv, primary_dv))

        return self._renumber(hypotheses[:max_hypotheses])

    def _direct_effect(
        self,
        label: str,
        independent: VariableCandidate,
        dependent: VariableCandidate,
    ) -> Hypothesis:
        return Hypothesis(
            label=label,
            statement=f"{independent.name} positively affects {dependent.name}.",
            rationale=(
                f"{independent.name} is positioned as an explanatory construct and {dependent.name} as the main "
                "outcome. The expected positive direction should be confirmed with verified theory-specific studies."
            ),
            evidence_status=EvidenceStatus.CURATED,
        )

    def _antecedent_to_mediator(
        self,
        label: str,
        independent: VariableCandidate,
        mediator: VariableCandidate,
    ) -> Hypothesis:
        return Hypothesis(
            label=label,
            statement=f"{independent.name} positively affects {mediator.name}.",
            rationale=(
                f"The conceptual framework treats {mediator.name} as a mechanism through which "
                f"{independent.name} may create organizational change."
            ),
            evidence_status=EvidenceStatus.CURATED,
        )

    def _mediator_to_outcome(
        self,
        label: str,
        mediator: VariableCandidate,
        dependent: VariableCandidate,
    ) -> Hypothesis:
        return Hypothesis(
            label=label,
            statement=f"{mediator.name} positively affects {dependent.name}.",
            rationale=(
                f"If {mediator.name} captures a meaningful organizational mechanism, it should help explain "
                f"variation in {dependent.name}."
            ),
            evidence_status=EvidenceStatus.CURATED,
        )

    def _mediation(
        self,
        label: str,
        independent: VariableCandidate,
        mediator: VariableCandidate,
        dependent: VariableCandidate,
    ) -> Hypothesis:
        return Hypothesis(
            label=label,
            statement=(
                f"{mediator.name} mediates the relationship between {independent.name} and {dependent.name}."
            ),
            rationale=(
                f"This follows the framework path {independent.name} -> {mediator.name} -> {dependent.name}."
            ),
            evidence_status=EvidenceStatus.CURATED,
        )

    def _moderation(
        self,
        label: str,
        moderator: VariableCandidate,
        independent: VariableCandidate,
        dependent: VariableCandidate,
    ) -> Hypothesis:
        return Hypothesis(
            label=label,
            statement=(
                f"{moderator.name} strengthens the positive relationship between "
                f"{independent.name} and {dependent.name}."
            ),
            rationale=(
                f"{moderator.name} is modeled as a boundary condition. The direction of strengthening should be "
                "checked against verified empirical literature and the study context."
            ),
            evidence_status=EvidenceStatus.CURATED,
        )

    def _renumber(self, hypotheses: list[Hypothesis]) -> list[Hypothesis]:
        return [
            Hypothesis(
                label=f"H{index}",
                statement=hypothesis.statement,
                rationale=hypothesis.rationale,
                evidence_status=hypothesis.evidence_status,
            )
            for index, hypothesis in enumerate(hypotheses, start=1)
        ]

    def _first(self, values: tuple[VariableCandidate, ...]) -> VariableCandidate | None:
        return values[0] if values else None

    def _second(self, values: tuple[VariableCandidate, ...]) -> VariableCandidate | None:
        return values[1] if len(values) > 1 else None
