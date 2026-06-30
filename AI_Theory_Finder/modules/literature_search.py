"""Optional literature search adapters for verified recent-source metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from config import EvidenceStatus, SourceEvidence


class LiteratureSearchProvider(Protocol):
    """Provider interface for recent academic metadata search."""

    def search_recent(
        self,
        query: str,
        from_year: int = 2023,
        to_year: int = 2026,
        limit: int = 5,
    ) -> tuple[SourceEvidence, ...]:
        """Search recent academic metadata."""


@dataclass(frozen=True)
class LiteratureSearchConfig:
    """Network settings for literature search providers."""

    timeout_seconds: float = 12.0
    user_agent: str = "AI-Theory-Finder/1.0 (mailto:researcher@example.com)"


class OpenAlexSearchProvider:
    """OpenAlex metadata search provider."""

    base_url = "https://api.openalex.org/works"

    def __init__(self, config: LiteratureSearchConfig | None = None) -> None:
        self.config = config or LiteratureSearchConfig()

    def search_recent(
        self,
        query: str,
        from_year: int = 2023,
        to_year: int = 2026,
        limit: int = 5,
    ) -> tuple[SourceEvidence, ...]:
        params = {
            "search": query,
            "filter": f"from_publication_date:{from_year}-01-01,to_publication_date:{to_year}-12-31",
            "per-page": str(limit),
            "sort": "relevance_score:desc",
        }
        data = self._get_json(f"{self.base_url}?{urlencode(params)}")
        results = data.get("results", []) if isinstance(data, dict) else []
        return tuple(self._parse_work(item) for item in results if isinstance(item, dict))[:limit]

    def _parse_work(self, item: dict[str, Any]) -> SourceEvidence:
        title = self._clean_text(str(item.get("title") or item.get("display_name") or "Untitled work"))
        year = self._safe_int(item.get("publication_year"))
        doi = self._normalize_doi(item.get("doi"))
        source = item.get("primary_location", {}).get("source") if isinstance(item.get("primary_location"), dict) else None
        venue = source.get("display_name") if isinstance(source, dict) else None
        authors = self._parse_openalex_authors(item.get("authorships"))
        url = item.get("landing_page_url") or item.get("id")

        return SourceEvidence(
            title=title,
            authors=authors,
            year=year,
            venue=venue,
            doi=doi,
            url=str(url) if url else None,
            status=EvidenceStatus.VERIFIED,
            note="Metadata returned by OpenAlex. Verify suitability by reading the source before citation.",
        )

    def _parse_openalex_authors(self, authorships: Any) -> tuple[str, ...]:
        if not isinstance(authorships, list):
            return ()
        authors: list[str] = []
        for authorship in authorships[:6]:
            author = authorship.get("author") if isinstance(authorship, dict) else None
            name = author.get("display_name") if isinstance(author, dict) else None
            if name:
                authors.append(str(name))
        return tuple(authors)

    def _get_json(self, url: str) -> dict[str, Any]:
        request = Request(url, headers={"User-Agent": self.config.user_agent})
        with urlopen(request, timeout=self.config.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
        data = json.loads(payload)
        return data if isinstance(data, dict) else {}

    def _normalize_doi(self, value: Any) -> str | None:
        if not value:
            return None
        doi = str(value).replace("https://doi.org/", "").strip()
        return doi or None

    def _safe_int(self, value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _clean_text(self, value: str) -> str:
        return " ".join(value.split())


class CrossrefSearchProvider:
    """Crossref metadata search provider."""

    base_url = "https://api.crossref.org/works"

    def __init__(self, config: LiteratureSearchConfig | None = None) -> None:
        self.config = config or LiteratureSearchConfig()

    def search_recent(
        self,
        query: str,
        from_year: int = 2023,
        to_year: int = 2026,
        limit: int = 5,
    ) -> tuple[SourceEvidence, ...]:
        params = {
            "query.bibliographic": query,
            "filter": f"from-pub-date:{from_year}-01-01,until-pub-date:{to_year}-12-31,type:journal-article",
            "rows": str(limit),
            "sort": "relevance",
        }
        data = self._get_json(f"{self.base_url}?{urlencode(params)}")
        message = data.get("message", {}) if isinstance(data, dict) else {}
        items = message.get("items", []) if isinstance(message, dict) else []
        return tuple(self._parse_work(item) for item in items if isinstance(item, dict))[:limit]

    def _parse_work(self, item: dict[str, Any]) -> SourceEvidence:
        title_values = item.get("title") if isinstance(item.get("title"), list) else []
        title = self._clean_text(str(title_values[0])) if title_values else "Untitled work"
        year = self._parse_crossref_year(item)
        authors = self._parse_crossref_authors(item.get("author"))
        container = item.get("container-title") if isinstance(item.get("container-title"), list) else []

        return SourceEvidence(
            title=title,
            authors=authors,
            year=year,
            venue=str(container[0]) if container else None,
            doi=str(item.get("DOI")) if item.get("DOI") else None,
            url=str(item.get("URL")) if item.get("URL") else None,
            status=EvidenceStatus.VERIFIED,
            note="Metadata returned by Crossref. Verify suitability by reading the source before citation.",
        )

    def _parse_crossref_year(self, item: dict[str, Any]) -> int | None:
        issued = item.get("published-print") or item.get("published-online") or item.get("issued")
        if not isinstance(issued, dict):
            return None
        date_parts = issued.get("date-parts")
        if not isinstance(date_parts, list) or not date_parts:
            return None
        first_date = date_parts[0]
        if not isinstance(first_date, list) or not first_date:
            return None
        try:
            return int(first_date[0])
        except (TypeError, ValueError):
            return None

    def _parse_crossref_authors(self, authors: Any) -> tuple[str, ...]:
        if not isinstance(authors, list):
            return ()
        parsed: list[str] = []
        for author in authors[:6]:
            if not isinstance(author, dict):
                continue
            given = str(author.get("given") or "").strip()
            family = str(author.get("family") or "").strip()
            name = " ".join(part for part in (given, family) if part)
            if name:
                parsed.append(name)
        return tuple(parsed)

    def _get_json(self, url: str) -> dict[str, Any]:
        request = Request(url, headers={"User-Agent": self.config.user_agent})
        with urlopen(request, timeout=self.config.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
        data = json.loads(payload)
        return data if isinstance(data, dict) else {}

    def _clean_text(self, value: str) -> str:
        return " ".join(value.split())


class LiteratureSearchService:
    """Try multiple providers and return only provider-supplied metadata."""

    def __init__(self, providers: tuple[LiteratureSearchProvider, ...] | None = None) -> None:
        self.providers = providers or (
            OpenAlexSearchProvider(),
            CrossrefSearchProvider(),
        )

    def search_recent(
        self,
        query: str,
        from_year: int = 2023,
        to_year: int = 2026,
        limit: int = 5,
    ) -> tuple[SourceEvidence, ...]:
        """Search providers in order and return de-duplicated verified metadata."""
        collected: list[SourceEvidence] = []
        for provider in self.providers:
            try:
                collected.extend(provider.search_recent(query, from_year=from_year, to_year=to_year, limit=limit))
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError):
                continue
            if len(collected) >= limit:
                break
        return tuple(self._dedupe(collected))[:limit]

    def _dedupe(self, sources: list[SourceEvidence]) -> list[SourceEvidence]:
        seen: set[str] = set()
        deduped: list[SourceEvidence] = []
        for source in sources:
            key = (source.doi or source.url or source.title).lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(source)
        return deduped
