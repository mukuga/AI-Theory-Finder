"""Agent wrapper for hypothesis generation."""

from __future__ import annotations

from config import ConceptualFramework, Hypothesis, VariableMap
from modules.hypothesis_generator import HypothesisGenerator


class HypothesisAgent:
    """Agent facade for hypothesis generation."""

    def __init__(self, generator: HypothesisGenerator | None = None) -> None:
        self.generator = generator or HypothesisGenerator()

    def run(
        self,
        variable_map: VariableMap,
        framework: ConceptualFramework,
        max_hypotheses: int = 6,
    ) -> list[Hypothesis]:
        """Generate hypothesis templates."""
        return self.generator.generate(variable_map, framework, max_hypotheses=max_hypotheses)
