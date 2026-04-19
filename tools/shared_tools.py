import os
import re
from functools import lru_cache

from firecrawl import FirecrawlApp, ScrapeOptions
from langchain_core.tools import tool

_MAX_RESULT_CHARS = 4000
_MD_LINK_RE = re.compile(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+")
_WS_RE = re.compile(r"[ \t]+")
_NEWLINE_RE = re.compile(r"\n{3,}")


@lru_cache(maxsize=1)
def _firecrawl_client() -> FirecrawlApp:
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise RuntimeError("FIRECRAWL_API_KEY is not set")
    return FirecrawlApp(api_key=api_key)


def _clean_markdown(md: str) -> str:
    md = _MD_LINK_RE.sub("", md)
    md = _WS_RE.sub(" ", md)
    md = _NEWLINE_RE.sub("\n\n", md).strip()
    if len(md) > _MAX_RESULT_CHARS:
        md = md[:_MAX_RESULT_CHARS] + " …[truncated]"
    return md


@tool
def web_search_tool(query: str) -> list[dict] | str:
    """Search the web and return cleaned markdown snippets for the top results.

    Args:
        query: The search query.

    Returns:
        A list of {title, url, markdown} dicts, or an error string on failure.
    """
    try:
        client = _firecrawl_client()
        response = client.search(
            query=query,
            limit=5,
            scrape_options=ScrapeOptions(formats=["markdown"]),
        )
    except Exception as exc:
        return f"Web search failed: {exc}"

    if not getattr(response, "success", False):
        return "Web search failed: upstream returned no success flag."

    results: list[dict] = []
    for item in response.data or []:
        md = item.get("markdown") or ""
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "markdown": _clean_markdown(md),
            }
        )
    return results
