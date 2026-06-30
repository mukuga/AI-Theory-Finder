"""Application entry point for AI Theory Finder."""

from __future__ import annotations

import argparse
from pathlib import Path

from config import AppConfig, ResearchReport
from modules.framework_builder import FrameworkBuilder
from modules.gap_analyzer import GapAnalyzer
from modules.hypothesis_generator import HypothesisGenerator
from modules.literature_search import (
    CrossrefSearchProvider,
    LiteratureSearchConfig,
    LiteratureSearchService,
    OpenAlexSearchProvider,
)
from modules.reference_recommender import ReferenceRecommender
from modules.report_generator import ReportGenerator
from modules.theory_finder import TheoryFinder
from modules.topic_parser import TopicParser
from modules.variable_finder import VariableFinder


class AITheoryFinder:
    """Coordinate the complete research recommendation workflow."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()
        self.topic_parser = TopicParser()
        self.theory_finder = TheoryFinder()
        self.variable_finder = VariableFinder()
        self.framework_builder = FrameworkBuilder()
        self.gap_analyzer = GapAnalyzer()
        self.hypothesis_generator = HypothesisGenerator()
        self.reference_recommender = ReferenceRecommender(self._literature_provider())
        self.report_generator = ReportGenerator()

    def analyze(self, topic: str) -> ResearchReport:
        """Run the full analysis workflow and return a report object."""
        topic_profile = self.topic_parser.parse(topic)
        theories = self.theory_finder.recommend(topic_profile, limit=self.config.max_theories)
        variable_map = self.variable_finder.recommend(topic_profile, theories)
        framework = self.framework_builder.build(topic_profile, theories, variable_map)
        gaps = self.gap_analyzer.analyze(topic_profile, theories, variable_map)
        hypotheses = self.hypothesis_generator.generate(variable_map, framework)
        references = self.reference_recommender.recommend(
            topic_profile,
            theories,
            max_recent_sources=self.config.max_references_per_theory,
        )
        directions = self._research_directions(topic_profile.raw_topic)

        return ResearchReport(
            topic_profile=topic_profile,
            theories=theories,
            variable_map=variable_map,
            framework=framework,
            gaps=gaps,
            hypotheses=hypotheses,
            references=references,
            directions=directions,
        )

    def run(self, topic: str, output_path: Path | None = None) -> Path:
        """Analyze a topic and save the Markdown report."""
        report = self.analyze(topic)
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(self.report_generator.render_markdown(report), encoding="utf-8")
            return output_path
        return self.report_generator.save_markdown(report, self.config.output_dir)

    def _research_directions(self, topic: str) -> list[str]:
        return [
            f"Use '{topic}' to define a focused model with one primary antecedent, one outcome, and one mechanism.",
            "Verify recent 2023-2026 literature before claiming novelty or underuse.",
            "Test mediation and moderation separately to avoid overloading the empirical model.",
            "Report whether each citation is verified, curated background, or still pending verification.",
        ]

    def _literature_provider(self) -> LiteratureSearchService | None:
        if not self.config.enable_literature_search:
            return None

        provider_config = LiteratureSearchConfig(timeout_seconds=self.config.literature_timeout_seconds)
        return LiteratureSearchService(
            providers=(
                OpenAlexSearchProvider(provider_config),
                CrossrefSearchProvider(provider_config),
            )
        )


def build_parser() -> argparse.ArgumentParser:
    """Create command-line parser."""
    parser = argparse.ArgumentParser(description="AI Theory Finder")
    parser.add_argument("--topic", type=str, help="Research topic to analyze.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional Markdown output path. Defaults to output/ai_theory_finder_report.md.",
    )
    parser.add_argument("--max-theories", type=int, default=5, help="Maximum number of theories to recommend.")
    parser.add_argument(
        "--max-references",
        type=int,
        default=6,
        help="Maximum number of recent references per theory when literature search is enabled.",
    )
    parser.add_argument(
        "--enable-literature-search",
        action="store_true",
        help="Try OpenAlex and Crossref for recent 2023-2026 metadata. Requires internet access.",
    )
    parser.add_argument(
        "--literature-timeout",
        type=float,
        default=12.0,
        help="Timeout in seconds for each literature-search provider.",
    )
    return parser


def main() -> None:
    """Run the AI Theory Finder command-line flow."""
    parser = build_parser()
    args = parser.parse_args()
    topic = args.topic or input("Enter your research topic: ").strip()

    app = AITheoryFinder(
        config=AppConfig(
            max_theories=args.max_theories,
            max_references_per_theory=args.max_references,
            enable_literature_search=args.enable_literature_search,
            literature_timeout_seconds=args.literature_timeout,
        )
    )
    output_path = app.run(topic=topic, output_path=args.output)
    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    main()
