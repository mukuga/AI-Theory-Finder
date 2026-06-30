"""Agent wrapper for conceptual framework generation."""

from __future__ import annotations

from config import ConceptualFramework, TheoryRecommendation, TopicProfile, VariableMap
from modules.framework_builder import FrameworkBuilder


class FrameworkAgent:
    """Agent facade for conceptual framework generation."""

    def __init__(self, builder: FrameworkBuilder | None = None) -> None:
        self.builder = builder or FrameworkBuilder()

    def run(
        self,
        profile: TopicProfile,
        theories: list[TheoryRecommendation],
        variable_map: VariableMap,
    ) -> ConceptualFramework:
        """Build a conceptual framework."""
        return self.builder.build(profile, theories, variable_map)
