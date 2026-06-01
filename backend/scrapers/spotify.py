"""Spotify podcasts via public RSS feeds (Spotify exposes RSS for shows)."""
import httpx
import feedparser
import re
from datetime import datetime


def _extract_show_id(url: str) -> str | None:
    match = re.search(r"spotify\.com/show/([A-Za-z0-9]+)", url)
    return match.group(1) if match else None


def _parse_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        if hasattr(entry, attr) and getattr(entry, attr):
            try:
                import time
                return datetime.fromtimestamp(time.mktime(getattr(entry, attr)))
            except Exception:
                pass
    return None


async def fetch_spotify_podcast(url: str, source_id: int) -> list[dict]:
    # Spotify shows have public RSS: https://feeds.megaphone.fm/ or direct RSS links
    # If user provides a direct RSS URL that's not spotify.com, use it directly
    rss_url = url
    if "spotify.com" in url:
        show_id = _extract_show_id(url)
        if not show_id:
            return []
        # Spotify's unofficial RSS endpoint
        rss_url = f"https://anchor.fm/s/{show_id}/podcast/rss"

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            headers = {"User-Agent": "NewsRadar/1.0 Podcast Client"}
            resp = await client.get(rss_url, headers=headers)
            resp.raise_for_status()
    except Exception:
        return []

    feed = feedparser.parse(resp.text)
    articles = []

    for entry in feed.entries[:20]:
        duration = None
        if hasattr(entry, "itunes_duration"):
            duration = entry.itunes_duration

        summary = re.sub(r"<[^>]+>", "", entry.get("summary", "")).strip()
        image = None
        if hasattr(entry, "image") and entry.image:
            image = entry.image.get("href")
        elif feed.feed.get("image"):
            image = feed.feed.image.get("href")

        articles.append({
            "source_id": source_id,
            "title": entry.get("title", "").strip(),
            "url": entry.get("link", url),
            "summary": summary[:500] or None,
            "image_url": image,
            "author": entry.get("author", feed.feed.get("author", None)),
            "published_at": _parse_date(entry),
            "is_paywalled": False,
            "tags": ["podcast", "spotify", *(["duration:" + duration] if duration else [])],
        })

    return articles
