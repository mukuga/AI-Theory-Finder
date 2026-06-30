"""Agent wrapper for research gap analysis."""

from __future__ import annotations

from config import ResearchGap, TheoryRecommendation, TopicProfile, VariableMap
from modules.gap_analyzer import GapAnalyzer


class GapAgent:
    """Agent facade for research gap analysis."""

    def __init__(self, analyzer: GapAnalyzer | None = None) -> None:
        self.analyzer = analyzer or GapAnalyzer()

    def run(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
        variable_map: VariableMap,
        max_gaps: int = 6,
    ) -> list[ResearchGap]:
        """Identify potential research gaps."""
        return self.analyzer.analyze(profile, theories, variable_map, max_gaps=max_gaps)
