"""
Full-page text fetcher for when Tavily snippets aren't enough.
Used optionally by the Searcher to enrich thin results.
"""
import re
from html.parser import HTMLParser

import httpx
from loguru import logger


class _TextExtractor(HTMLParser):
    """Extracts visible text from HTML using stdlib only — no BeautifulSoup dep."""

    _SKIP = {"script", "style", "head", "meta", "link", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skipping = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag.lower() in self._SKIP:
            self._skipping = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._SKIP:
            self._skipping = False

    def handle_data(self, data: str) -> None:
        if not self._skipping:
            chunk = data.strip()
            if chunk:
                self._chunks.append(chunk)

    def get_text(self) -> str:
        raw = " ".join(self._chunks)
        return re.sub(r"\s+", " ", raw).strip()


async def fetch_page_text(url: str, max_chars: int = 4_000) -> str:
    """
    Fetches a URL and returns its plain-text content truncated to max_chars.
    Returns an empty string on any error (network, non-200, parse).
    """
    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={"User-Agent": "ResearchAssistant/1.0"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        extractor = _TextExtractor()
        extractor.feed(response.text)
        text = extractor.get_text()

        logger.debug("[web_reader] {} chars fetched from {}", len(text), url)
        return text[:max_chars]

    except Exception as exc:
        logger.warning("[web_reader] Failed to fetch {}: {}", url, exc)
        return ""