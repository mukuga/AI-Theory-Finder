"""Agent wrapper for variable recommendation."""

from __future__ import annotations

from config import TheoryRecommendation, TopicProfile, VariableMap
from modules.variable_finder import VariableFinder


class VariableAgent:
    """Agent facade for variable recommendation."""

    def __init__(self, finder: VariableFinder | None = None) -> None:
        self.finder = finder or VariableFinder()

    def run(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
        max_per_role: int = 6,
    ) -> VariableMap:
        """Build a variable map."""
        return self.finder.recommend(profile, theories, max_per_role=max_per_role)
