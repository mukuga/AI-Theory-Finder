"""Agent wrapper for reference recommendation."""

from __future__ import annotations

from config import ReferenceRecommendation, TheoryRecommendation, TopicProfile
from modules.reference_recommender import ReferenceRecommender


class ReferenceAgent:
    """Agent facade for reference recommendation."""

    def __init__(self, recommender: ReferenceRecommender | None = None) -> None:
        self.recommender = recommender or ReferenceRecommender()

    def run(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
        max_recent_sources: int = 5,
    ) -> list[ReferenceRecommendation]:
        """Recommend references for selected theories."""
        return self.recommender.recommend(profile, theories, max_recent_sources=max_recent_sources)
