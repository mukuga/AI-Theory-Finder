"""Reference recommendation module for AI Theory Finder."""

from __future__ import annotations

from config import EvidenceStatus, ReferenceRecommendation, SourceEvidence, TheoryRecommendation, TopicProfile
from modules.literature_search import LiteratureSearchProvider


class ReferenceRecommender:
    """Recommend traceable references without fabricating recent citations."""

    def __init__(self, literature_provider: LiteratureSearchProvider | None = None) -> None:
        self.literature_provider = literature_provider

    def recommend(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
        max_recent_sources: int = 5,
    ) -> list[ReferenceRecommendation]:
        """Return reference suggestions for each recommended theory."""
        return [self._build_reference_recommendation(profile, theory, max_recent_sources) for theory in theories]

    def _build_reference_recommendation(
        self,
        profile: TopicProfile,
        theory: TheoryRecommendation,
        max_recent_sources: int,
    ) -> ReferenceRecommendation:
        recent_sources = self._recent_sources(profile, theory, max_recent_sources)
        return ReferenceRecommendation(
            theory_name=theory.name,
            seminal_sources=theory.evidence,
            recent_sources=recent_sources,
            common_application=self._common_application(theory, profile),
            typical_models=self._typical_models(theory),
        )

    def _recent_sources(
        self,
        profile: TopicProfile,
        theory: TheoryRecommendation,
        max_recent_sources: int,
    ) -> tuple[SourceEvidence, ...]:
        if not self.literature_provider:
            return self._recent_search_placeholders(profile, theory)

        query = self._recent_query(profile, theory)
        sources = self.literature_provider.search_recent(query, from_year=2023, to_year=2026, limit=max_recent_sources)
        if sources:
            return sources
        return self._recent_search_placeholders(profile, theory)

    def _recent_search_placeholders(
        self,
        profile: TopicProfile,
        theory: TheoryRecommendation,
    ) -> tuple[SourceEvidence, ...]:
        topic_terms = ", ".join(profile.focal_constructs[:3]) or profile.normalized_topic
        outcome_terms = ", ".join(profile.outcome_constructs) or "research outcome"
        return (
            SourceEvidence(
                title=f"Recent 2023-2026 papers applying {theory.name} to {topic_terms}",
                authors=(),
                year=None,
                venue=None,
                status=EvidenceStatus.VERIFICATION_NEEDED,
                note=(
                    "No verified recent-source metadata was returned by the configured local workflow. "
                    f"Search Google Scholar, Scopus, Web of Science, Crossref, Semantic Scholar, or OpenAlex for: "
                    f'"{self._recent_query(profile, theory)}" 2023..2026.'
                ),
            ),
        )

    def _recent_query(self, profile: TopicProfile, theory: TheoryRecommendation) -> str:
        topic_terms = " ".join(profile.focal_constructs[:3]) or profile.normalized_topic
        outcome_terms = " ".join(profile.outcome_constructs) or "research outcome"
        return f"{theory.name} {topic_terms} {outcome_terms}"

    def _common_application(self, theory: TheoryRecommendation, profile: TopicProfile) -> str:
        constructs = ", ".join(profile.focal_constructs[:3]) or profile.raw_topic
        outcomes = ", ".join(profile.outcome_constructs) or "the selected dependent variables"
        return (
            f"{theory.name} is commonly applied by linking {constructs} to {outcomes}, "
            f"then explaining the relationship through mechanisms such as "
            f"{self._join_or_default(theory.common_mediators, 'mediating processes')} and boundary conditions such as "
            f"{self._join_or_default(theory.common_moderators, 'contextual moderators')}."
        )

    def _typical_models(self, theory: TheoryRecommendation) -> tuple[str, ...]:
        dependent = self._first_or_default(theory.common_dependent_variables, "Outcome Variable")
        mediator = self._first_or_default(theory.common_mediators, "Mediating Mechanism")
        moderator = self._first_or_default(theory.common_moderators, "Boundary Condition")
        return (
            f"Core effect model: Explanatory Construct -> {dependent}",
            f"Mediation model: Explanatory Construct -> {mediator} -> {dependent}",
            f"Moderation model: {moderator} moderates Explanatory Construct -> {dependent}",
        )

    def _join_or_default(self, values: tuple[str, ...], default: str) -> str:
        return ", ".join(values[:3]) if values else default

    def _first_or_default(self, values: tuple[str, ...], default: str) -> str:
        return values[0] if values else default
