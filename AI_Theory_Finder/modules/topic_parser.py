"""Topic parsing module for AI Theory Finder."""

from __future__ import annotations

import re
from collections import Counter

from config import TopicProfile


class TopicParser:
    """Convert free-form research topics into a structured topic profile."""

    _STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "based",
        "between",
        "by",
        "for",
        "from",
        "in",
        "into",
        "of",
        "on",
        "or",
        "study",
        "the",
        "to",
        "using",
        "with",
    }

    _PHRASE_ALIASES = {
        "ai": "artificial intelligence",
        "ml": "machine learning",
        "roa": "return on assets",
        "roe": "return on equity",
        "tobin q": "tobin's q",
        "tobins q": "tobin's q",
        "esg": "environmental social governance",
        "smes": "small and medium enterprises",
        "sme": "small and medium enterprises",
    }

    _DOMAIN_KEYWORDS = {
        "artificial intelligence": {
            "ai",
            "artificial intelligence",
            "machine learning",
            "algorithm",
            "analytics",
            "automation",
            "deep learning",
        },
        "corporate governance": {
            "board",
            "board digital expertise",
            "corporate governance",
            "governance",
            "ownership",
            "directors",
            "audit committee",
        },
        "strategic management": {
            "capability",
            "competitive advantage",
            "dynamic capability",
            "firm performance",
            "resource",
            "strategy",
        },
        "information systems": {
            "adoption",
            "digital readiness",
            "digital transformation",
            "information system",
            "technology adoption",
            "toe",
        },
        "innovation management": {
            "innovation",
            "innovation capability",
            "knowledge management",
            "r&d",
            "research and development",
        },
        "finance and accounting": {
            "financial performance",
            "firm value",
            "return on assets",
            "return on equity",
            "roa",
            "roe",
            "tobin's q",
        },
        "sustainability": {
            "environmental social governance",
            "esg",
            "sustainability",
            "green innovation",
            "csr",
        },
    }

    _OUTCOME_KEYWORDS = {
        "firm performance": {
            "firm performance",
            "performance",
            "financial performance",
            "organizational performance",
        },
        "firm value": {"firm value", "market value", "tobin's q"},
        "profitability": {"profitability", "return on assets", "return on equity", "roa", "roe"},
        "innovation performance": {"innovation", "innovation performance", "patent", "r&d"},
        "sustainability performance": {"sustainability performance", "esg performance", "csr performance"},
    }

    _CONTEXT_KEYWORDS = {
        "developed countries",
        "developing countries",
        "emerging markets",
        "public firms",
        "listed firms",
        "smes",
        "small and medium enterprises",
        "manufacturing",
        "banking",
        "healthcare",
        "education",
        "indonesia",
        "asia",
        "europe",
        "united states",
    }

    def parse(self, topic: str) -> TopicProfile:
        """Parse a user topic into domains, constructs, outcomes, and context."""
        if not topic or not topic.strip():
            msg = "Research topic cannot be empty."
            raise ValueError(msg)

        normalized = self._normalize(topic)
        expanded = self._expand_aliases(normalized)
        terms = self._extract_terms(expanded)
        domains = self._detect_domains(expanded, terms)
        outcomes = self._detect_outcomes(expanded, terms)
        context_terms = self._detect_context(expanded)
        constructs = self._detect_constructs(expanded, terms, outcomes, context_terms)
        explanation = self._build_explanation(domains, constructs, outcomes, context_terms)

        return TopicProfile(
            raw_topic=topic.strip(),
            normalized_topic=expanded,
            terms=tuple(terms),
            domains=tuple(domains),
            focal_constructs=tuple(constructs),
            outcome_constructs=tuple(outcomes),
            context_terms=tuple(context_terms),
            explanation=explanation,
        )

    def _normalize(self, topic: str) -> str:
        text = topic.strip().lower()
        text = text.replace("&", " and ")
        text = re.sub(r"[^a-z0-9'\s-]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _expand_aliases(self, text: str) -> str:
        words = text.split()
        expanded_words = [self._PHRASE_ALIASES.get(word, word) for word in words]
        expanded = " ".join(expanded_words)
        for source, replacement in self._PHRASE_ALIASES.items():
            expanded = re.sub(rf"\b{re.escape(source)}\b", replacement, expanded)
        return re.sub(r"\s+", " ", expanded).strip()

    def _extract_terms(self, text: str) -> list[str]:
        words = [word for word in text.split() if word not in self._STOPWORDS and len(word) > 1]
        phrases = self._known_phrases_found(text)
        counts = Counter(words)
        ranked_words = [word for word, _ in counts.most_common()]
        return self._dedupe_preserving_order([*phrases, *ranked_words])

    def _detect_domains(self, text: str, terms: list[str]) -> list[str]:
        term_set = set(terms)
        scores: dict[str, int] = {}
        for domain, keywords in self._DOMAIN_KEYWORDS.items():
            score = sum(1 for keyword in keywords if self._contains_keyword(text, term_set, keyword))
            if score:
                scores[domain] = score
        ranked = sorted(scores, key=lambda domain: (-scores[domain], domain))
        return ranked or ["general management"]

    def _detect_outcomes(self, text: str, terms: list[str]) -> list[str]:
        term_set = set(terms)
        outcomes: list[str] = []
        for outcome, keywords in self._OUTCOME_KEYWORDS.items():
            if any(self._contains_keyword(text, term_set, keyword) for keyword in keywords):
                outcomes.append(outcome)
        return outcomes

    def _detect_context(self, text: str) -> list[str]:
        return [
            keyword
            for keyword in sorted(self._CONTEXT_KEYWORDS)
            if re.search(rf"\b{re.escape(keyword)}\b", text)
        ]

    def _detect_constructs(
        self,
        text: str,
        terms: list[str],
        outcomes: list[str],
        context_terms: list[str],
    ) -> list[str]:
        phrases = self._known_phrases_found(text)
        excluded = set(outcomes) | set(context_terms)
        constructs = [phrase for phrase in phrases if phrase not in excluded]
        if not constructs:
            constructs = [term for term in terms if term not in excluded][:5]
        return self._dedupe_preserving_order(constructs)

    def _known_phrases_found(self, text: str) -> list[str]:
        phrases: set[str] = set()
        for keyword_group in (*self._DOMAIN_KEYWORDS.values(), *self._OUTCOME_KEYWORDS.values()):
            phrases.update(keyword for keyword in keyword_group if " " in keyword)
        phrases.update(self._CONTEXT_KEYWORDS)
        phrases.update(self._PHRASE_ALIASES.values())
        return [
            phrase
            for phrase in sorted(phrases, key=lambda item: (-len(item), item))
            if re.search(rf"\b{re.escape(phrase)}\b", text)
        ]

    def _contains_keyword(self, text: str, term_set: set[str], keyword: str) -> bool:
        if " " in keyword or "'" in keyword:
            return bool(re.search(rf"\b{re.escape(keyword)}\b", text))
        return keyword in term_set

    def _build_explanation(
        self,
        domains: list[str],
        constructs: list[str],
        outcomes: list[str],
        context_terms: list[str],
    ) -> str:
        domain_text = ", ".join(domains[:3])
        construct_text = ", ".join(constructs[:4]) if constructs else "the supplied topic terms"
        outcome_text = ", ".join(outcomes) if outcomes else "no explicit outcome variable"
        context_text = ", ".join(context_terms) if context_terms else "no explicit study context"
        return (
            f"The topic appears to sit in {domain_text}. "
            f"Key constructs detected: {construct_text}. "
            f"Outcome focus: {outcome_text}. Context: {context_text}."
        )

    def _dedupe_preserving_order(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for value in values:
            if value and value not in seen:
                seen.add(value)
                deduped.append(value)
        return deduped
