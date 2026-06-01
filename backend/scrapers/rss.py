import feedparser
import httpx
from datetime import datetime
from email.utils import parsedate_to_datetime
import re


PAYWALL_DOMAINS = [
    "rzeczpospolita.pl", "rp.pl", "wyborcza.pl", "polityka.pl",
    "newsweek.pl", "tygodnikpowszechny.pl", "puls-biznesu.pl",
]


def _detect_paywall(url: str, content: str = "") -> bool:
    domain = url.split("/")[2] if url.startswith("http") else ""
    return any(d in domain for d in PAYWALL_DOMAINS)


def _parse_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        if hasattr(entry, attr) and getattr(entry, attr):
            try:
                import time
                return datetime.fromtimestamp(time.mktime(getattr(entry, attr)))
            except Exception:
                pass
    return None


def _extract_image(entry) -> str | None:
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")
    if hasattr(entry, "media_content") and entry.media_content:
        return entry.media_content[0].get("url")
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image"):
                return enc.get("href") or enc.get("url")
    if hasattr(entry, "summary"):
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.summary or "")
        if match:
            return match.group(1)
    return None


async def fetch_rss(url: str, source_id: int) -> list[dict]:
    headers = {"User-Agent": "NewsRadar/1.0 (+https://github.com/newsradar)"}
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            content = resp.text
        except Exception:
            return []

    feed = feedparser.parse(content)
    articles = []

    for entry in feed.entries[:30]:
        article_url = entry.get("link", "")
        if not article_url:
            continue

        summary = entry.get("summary", "") or entry.get("description", "")
        summary = re.sub(r"<[^>]+>", "", summary).strip()[:800]

        articles.append({
            "source_id": source_id,
            "title": entry.get("title", "Bez tytułu").strip(),
            "url": article_url,
            "summary": summary or None,
            "image_url": _extract_image(entry),
            "author": entry.get("author", None),
            "published_at": _parse_date(entry),
            "is_paywalled": _detect_paywall(article_url),
            "tags": [t.get("term") for t in entry.get("tags", []) if t.get("term")][:5],
        })

    return articles
