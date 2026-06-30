# AI Theory Finder

AI Theory Finder helps researchers identify suitable theories, variables, conceptual frameworks, research gaps, hypotheses, and reference directions for a research topic.

The application is designed to avoid fabricated claims. Any citation or paper that cannot be verified by the configured evidence source must be marked as `[Verification Needed]`.

## Architecture First

The system is organized as a modular, object-oriented Python application that can run locally or in Google Colab.

```text
AI_Theory_Finder/
  app.py
  config.py
  requirements.txt
  README.md
  data/
  output/
  modules/
    topic_parser.py
    theory_finder.py
    variable_finder.py
    framework_builder.py
    gap_analyzer.py
    hypothesis_generator.py
    reference_recommender.py
    report_generator.py
  agents/
    theory_agent.py
    variable_agent.py
    framework_agent.py
    gap_agent.py
    hypothesis_agent.py
    reference_agent.py
```

## Design Principles

- Evidence first: recommendations must be traceable to known theory knowledge, local curated data, or verified literature search results.
- No fabricated citations: unverified sources are explicitly marked as `[Verification Needed]`.
- Modular responsibilities: each module owns one research task and exposes a small typed interface.
- Agent orchestration: agents coordinate modules and add reasoning explanations without hiding evidence quality.
- Colab compatible: the app uses standard Python files, simple dependencies, and file-based input/output.
- Maintainability over speed: clear domain models, type hints, and readable reports are preferred over premature optimization.

## Core Data Flow

```text
Research topic
  -> TopicParser
  -> TheoryFinder
  -> VariableFinder
  -> FrameworkBuilder
  -> GapAnalyzer
  -> HypothesisGenerator
  -> ReferenceRecommender
  -> ReportGenerator
  -> Final report
```

## Main Components

### `TopicParser`

Normalizes user input into a structured topic profile:

- topic terms
- likely domain
- focal constructs
- possible performance outcomes
- governance or context terms

### `TheoryFinder`

Ranks candidate theories using:

- keyword/topic fit
- domain fit
- known construct associations
- evidence availability
- prior-study usage patterns

Output includes theory name, relevance score, explanation, common dependent variables, mediators, moderators, and evidence status.

### `VariableFinder`

Builds a structured variable map:

- independent variables
- dependent variables
- mediators
- moderators
- controls, when useful

### `FrameworkBuilder`

Turns recommended theories and variables into a textual conceptual framework.

### `GapAnalyzer`

Identifies plausible research gaps by comparing:

- topic emphasis
- theory usage
- variable coverage
- context gaps
- methods or setting gaps

### `HypothesisGenerator`

Generates example hypotheses from the conceptual framework. Hypotheses are templates for researcher review, not claims of proven causal truth.

### `ReferenceRecommender`

Provides seminal and recent reference suggestions per theory. Sources must include verification metadata.

### `ReportGenerator`

Builds the final report with:

- topic analysis
- recommended theories
- variable map
- conceptual framework
- research gaps
- example hypotheses
- suggested references
- research direction recommendations

## Evidence Strategy

The first production version uses a curated local theory knowledge base for stable theory metadata. Recent papers from 2023-2026 should be collected through a verifiable search layer when enabled. If that layer is unavailable, recent-paper entries must be marked `[Verification Needed]` instead of invented.

## How To Run

From the project folder:

```bash
python app.py --topic "Artificial Intelligence, Corporate Governance, Firm Performance"
```

With a custom output path:

```bash
python app.py --topic "AI Capability and Firm Performance" --output output/my_report.md
```

With optional recent-source metadata search:

```bash
python app.py --topic "AI Capability and Firm Performance" --enable-literature-search
```

The search option tries OpenAlex and Crossref for 2023-2026 metadata. If no source metadata is returned, the report keeps `[Verification Needed]` placeholders instead of inventing citations.

Interactive mode:

```bash
python app.py
```

## Google Colab Usage

Upload the `AI_Theory_Finder` folder to Colab, then run:

```python
import sys
sys.path.insert(0, "/content/AI_Theory_Finder")

from app import AITheoryFinder

finder = AITheoryFinder()
report = finder.analyze("Artificial Intelligence, Corporate Governance, Firm Performance")
markdown = finder.report_generator.render_markdown(report)
print(markdown)
```

## Planned Implementation Order

1. Shared config and data models.
2. Topic parser.
3. Theory finder.
4. Variable finder.
5. Framework builder.
6. Gap analyzer.
7. Hypothesis generator.
8. Reference recommender.
9. Report generator.
10. App orchestration and Colab usage notes.

## Current Status

Implemented:

- typed domain models
- topic parser
- theory finder
- variable finder
- conceptual framework builder
- research gap analyzer
- hypothesis generator
- reference recommender
- Markdown report generator
- command-line app orchestration
- agent facades
- optional OpenAlex/Crossref recent-source metadata adapters
