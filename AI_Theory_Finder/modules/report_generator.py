"""Report generation module for AI Theory Finder."""

from __future__ import annotations

from pathlib import Path

from config import (
    DEFAULT_REPORT_NAME,
    EvidenceStatus,
    ReferenceRecommendation,
    ResearchReport,
    SourceEvidence,
    VariableCandidate,
    VariableMap,
)


class ReportGenerator:
    """Render research recommendations into a Markdown report."""

    def render_markdown(self, report: ResearchReport) -> str:
        """Return a complete Markdown report."""
        sections = [
            self._title(report),
            self._topic_analysis(report),
            self._theory_section(report),
            self._variable_section(report.variable_map),
            self._framework_section(report),
            self._gap_section(report),
            self._hypothesis_section(report),
            self._reference_section(report.references),
            self._direction_section(report),
            self._evidence_note(),
        ]
        return "\n\n".join(section for section in sections if section).strip() + "\n"

    def save_markdown(
        self,
        report: ResearchReport,
        output_dir: Path,
        filename: str = DEFAULT_REPORT_NAME,
    ) -> Path:
        """Render and save a Markdown report."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        output_path.write_text(self.render_markdown(report), encoding="utf-8")
        return output_path

    def _title(self, report: ResearchReport) -> str:
        return f"# AI Theory Finder Report\n\n**Research Topic:** {report.topic_profile.raw_topic}"

    def _topic_analysis(self, report: ResearchReport) -> str:
        profile = report.topic_profile
        return "\n".join(
            [
                "## 1. Topic Analysis",
                "",
                profile.explanation,
                "",
                f"- Normalized topic: `{profile.normalized_topic}`",
                f"- Detected domains: {self._join(profile.domains)}",
                f"- Focal constructs: {self._join(profile.focal_constructs)}",
                f"- Outcome constructs: {self._join(profile.outcome_constructs)}",
                f"- Context terms: {self._join(profile.context_terms)}",
            ]
        )

    def _theory_section(self, report: ResearchReport) -> str:
        lines = ["## 2. Top Recommended Theories"]
        for theory in report.theories:
            evidence_status = self._evidence_status(theory.evidence)
            lines.extend(
                [
                    "",
                    f"### {theory.name} ({theory.relevance_score}/100)",
                    "",
                    f"**Evidence status:** {evidence_status}",
                    "",
                    f"**Why it fits:** {theory.why_it_fits}",
                    "",
                    f"**Typical use:** {theory.typical_use}",
                    "",
                    f"- Common dependent variables: {self._join(theory.common_dependent_variables)}",
                    f"- Common mediators: {self._join(theory.common_mediators)}",
                    f"- Common moderators: {self._join(theory.common_moderators)}",
                ]
            )
        return "\n".join(lines)

    def _variable_section(self, variable_map: VariableMap | None) -> str:
        if variable_map is None:
            return ""

        return "\n\n".join(
            [
                "## 3. Variable Map",
                self._variable_group("Independent Variables", variable_map.independent_variables),
                self._variable_group("Dependent Variables", variable_map.dependent_variables),
                self._variable_group("Mediators", variable_map.mediators),
                self._variable_group("Moderators", variable_map.moderators),
                self._variable_group("Control Variables", variable_map.controls),
            ]
        )

    def _variable_group(self, title: str, variables: tuple[VariableCandidate, ...]) -> str:
        lines = [f"### {title}"]
        if not variables:
            lines.append("- No candidates generated.")
            return "\n".join(lines)

        for variable in variables:
            theories = self._join(variable.linked_theories)
            lines.append(f"- **{variable.name}**: {variable.rationale} Linked theories: {theories}.")
        return "\n".join(lines)

    def _framework_section(self, report: ResearchReport) -> str:
        if report.framework is None:
            return ""

        lines = [
            "## 4. Conceptual Framework",
            "",
            f"### {report.framework.title}",
            "",
            report.framework.narrative,
            "",
            "**Proposed paths:**",
            *[f"- {path}" for path in report.framework.paths],
            "",
            "**Assumptions:**",
            *[f"- {assumption}" for assumption in report.framework.assumptions],
        ]
        return "\n".join(lines)

    def _gap_section(self, report: ResearchReport) -> str:
        lines = ["## 5. Potential Research Gaps"]
        for gap in report.gaps:
            lines.extend(
                [
                    "",
                    f"### {gap.statement}",
                    "",
                    f"**Evidence status:** {gap.evidence_status.value}",
                    "",
                    f"**Rationale:** {gap.rationale}",
                ]
            )
            if gap.suggested_direction:
                lines.append(f"**Suggested direction:** {gap.suggested_direction}")
        return "\n".join(lines)

    def _hypothesis_section(self, report: ResearchReport) -> str:
        lines = ["## 6. Example Hypotheses"]
        for hypothesis in report.hypotheses:
            lines.extend(
                [
                    "",
                    f"- **{hypothesis.label}:** {hypothesis.statement}",
                    f"  Rationale: {hypothesis.rationale}",
                ]
            )
        return "\n".join(lines)

    def _reference_section(self, references: list[ReferenceRecommendation]) -> str:
        lines = ["## 7. Suggested References"]
        for reference in references:
            lines.extend(
                [
                    "",
                    f"### {reference.theory_name}",
                    "",
                    "**Seminal sources:**",
                    *self._source_lines(reference.seminal_sources),
                    "",
                    "**Recent sources, 2023-2026:**",
                    *self._source_lines(reference.recent_sources),
                    "",
                    f"**Common application:** {reference.common_application}",
                    "",
                    "**Typical research models:**",
                    *[f"- {model}" for model in reference.typical_models],
                ]
            )
        return "\n".join(lines)

    def _direction_section(self, report: ResearchReport) -> str:
        lines = ["## 8. Research Direction Recommendations"]
        directions = report.directions or self._default_directions(report)
        lines.extend(f"- {direction}" for direction in directions)
        return "\n".join(lines)

    def _default_directions(self, report: ResearchReport) -> list[str]:
        topic = report.topic_profile.raw_topic
        return [
            f"Use the generated framework for '{topic}' as a starting model, then verify each path with recent literature.",
            "Prioritize constructs with clear measurement scales and available data.",
            "Define country, industry, period, and sample before finalizing hypotheses.",
            "Treat all `[Verification Needed]` entries as search tasks before manuscript writing.",
        ]

    def _evidence_note(self) -> str:
        return (
            "## Evidence Caution\n\n"
            "This report is a research-assistance artifact. Curated theory metadata is not a substitute for a "
            "systematic literature review. Any item marked `[Verification Needed]` must be checked in verified "
            "academic databases before citation or manuscript use."
        )

    def _source_lines(self, sources: tuple[SourceEvidence, ...]) -> list[str]:
        if not sources:
            return ["- No source available. [Verification Needed]"]

        lines: list[str] = []
        for source in sources:
            suffix = ""
            if source.status == EvidenceStatus.VERIFICATION_NEEDED:
                suffix = " [Verification Needed]"
            detail = source.display_label()
            if source.venue:
                detail += f" {source.venue}."
            if source.doi:
                detail += f" DOI: {source.doi}."
            if source.url:
                detail += f" URL: {source.url}."
            if source.note:
                detail += f" Note: {source.note}"
            lines.append(f"- {detail}{suffix if suffix not in detail else ''}")
        return lines

    def _join(self, values: tuple[str, ...] | list[str]) -> str:
        return ", ".join(values) if values else "Not specified"

    def _evidence_status(self, sources: tuple[SourceEvidence, ...]) -> str:
        if not sources:
            return EvidenceStatus.VERIFICATION_NEEDED.value
        statuses = {source.status for source in sources}
        if EvidenceStatus.VERIFICATION_NEEDED in statuses:
            return EvidenceStatus.VERIFICATION_NEEDED.value
        if EvidenceStatus.VERIFIED in statuses:
            return EvidenceStatus.VERIFIED.value
        return EvidenceStatus.CURATED.value
