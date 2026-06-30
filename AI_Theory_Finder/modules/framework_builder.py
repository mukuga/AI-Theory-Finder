"""Conceptual framework builder module for AI Theory Finder."""

from __future__ import annotations

from config import ConceptualFramework, TheoryRecommendation, TopicProfile, VariableCandidate, VariableMap


class FrameworkBuilder:
    """Build a textual conceptual framework from theories and variables."""

    def build(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
        variable_map: VariableMap,
    ) -> ConceptualFramework:
        """Create a framework narrative, relationship paths, and assumptions."""
        primary_iv = self._first(variable_map.independent_variables)
        primary_dv = self._first(variable_map.dependent_variables)
        primary_mediator = self._first(variable_map.mediators)
        primary_moderator = self._first(variable_map.moderators)
        theory_names = [theory.name for theory in theories[:3]]

        title = self._build_title(profile, primary_iv, primary_dv)
        paths = self._build_paths(primary_iv, primary_dv, primary_mediator, primary_moderator)
        narrative = self._build_narrative(
            profile=profile,
            theory_names=theory_names,
            primary_iv=primary_iv,
            primary_dv=primary_dv,
            primary_mediator=primary_mediator,
            primary_moderator=primary_moderator,
            paths=paths,
        )
        assumptions = self._build_assumptions(primary_iv, primary_dv, primary_mediator, primary_moderator)

        return ConceptualFramework(
            title=title,
            narrative=narrative,
            paths=paths,
            assumptions=assumptions,
        )

    def _build_title(
        self,
        profile: TopicProfile,
        primary_iv: VariableCandidate | None,
        primary_dv: VariableCandidate | None,
    ) -> str:
        if primary_iv and primary_dv:
            return f"Conceptual Framework: {primary_iv.name} and {primary_dv.name}"
        return f"Conceptual Framework: {profile.raw_topic}"

    def _build_paths(
        self,
        primary_iv: VariableCandidate | None,
        primary_dv: VariableCandidate | None,
        primary_mediator: VariableCandidate | None,
        primary_moderator: VariableCandidate | None,
    ) -> tuple[str, ...]:
        if not primary_iv or not primary_dv:
            return ("Insufficient variables to define a directional framework.",)

        paths = [f"{primary_iv.name} -> {primary_dv.name}"]

        if primary_mediator:
            paths.append(f"{primary_iv.name} -> {primary_mediator.name} -> {primary_dv.name}")

        if primary_moderator:
            paths.append(f"{primary_moderator.name} moderates {primary_iv.name} -> {primary_dv.name}")
            if primary_mediator:
                paths.append(
                    f"{primary_moderator.name} may also condition {primary_iv.name} -> {primary_mediator.name}"
                )

        return tuple(paths)

    def _build_narrative(
        self,
        profile: TopicProfile,
        theory_names: list[str],
        primary_iv: VariableCandidate | None,
        primary_dv: VariableCandidate | None,
        primary_mediator: VariableCandidate | None,
        primary_moderator: VariableCandidate | None,
        paths: tuple[str, ...],
    ) -> str:
        theory_text = ", ".join(theory_names) if theory_names else "the selected theoretical lenses"

        if not primary_iv or not primary_dv:
            return (
                f"For the topic '{profile.raw_topic}', the available variable evidence is not yet sufficient "
                "to define a complete conceptual framework. Add at least one independent variable and one "
                "dependent variable before formulating directional paths."
            )

        mediator_text = (
            f" {primary_mediator.name} is positioned as a mediating mechanism that explains how "
            f"{primary_iv.name} may translate into {primary_dv.name}."
            if primary_mediator
            else ""
        )
        moderator_text = (
            f" {primary_moderator.name} is positioned as a boundary condition that may strengthen, weaken, "
            f"or redirect the relationship between {primary_iv.name} and {primary_dv.name}."
            if primary_moderator
            else ""
        )
        path_text = "; ".join(paths)

        return (
            f"The proposed framework for '{profile.raw_topic}' treats {primary_iv.name} as the main explanatory "
            f"construct and {primary_dv.name} as the principal outcome. The framework is informed by "
            f"{theory_text}, which helps justify why resources, governance mechanisms, institutional conditions, "
            f"or knowledge processes may influence the outcome.{mediator_text}{moderator_text} "
            f"The core path structure is: {path_text}."
        )

    def _build_assumptions(
        self,
        primary_iv: VariableCandidate | None,
        primary_dv: VariableCandidate | None,
        primary_mediator: VariableCandidate | None,
        primary_moderator: VariableCandidate | None,
    ) -> tuple[str, ...]:
        assumptions: list[str] = []
        if primary_iv and primary_dv:
            assumptions.append(
                f"{primary_iv.name} is theoretically prior to {primary_dv.name}; empirical design should confirm timing."
            )
        if primary_mediator:
            assumptions.append(
                f"{primary_mediator.name} should be measured separately from both antecedent and outcome variables."
            )
        if primary_moderator:
            assumptions.append(
                f"{primary_moderator.name} should be tested with an interaction term or multi-group design."
            )
        assumptions.append(
            "The framework is a recommendation template; final causal claims require verified literature and empirical testing."
        )
        return tuple(assumptions)

    def _first(self, values: tuple[VariableCandidate, ...]) -> VariableCandidate | None:
        return values[0] if values else None
