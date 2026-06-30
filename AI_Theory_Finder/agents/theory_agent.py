"""Agent wrapper for theory recommendation."""

from __future__ import annotations

from config import TheoryRecommendation, TopicProfile
from modules.theory_finder import TheoryFinder


class TheoryAgent:
    """Agent facade for theory recommendation."""

    def __init__(self, finder: TheoryFinder | None = None) -> None:
        self.finder = finder or TheoryFinder()

    def run(self, profile: TopicProfile, limit: int = 5) -> list[TheoryRecommendation]:
        """Recommend theories for a parsed topic."""
        return self.finder.recommend(profile, limit=limit)
