import feedparser
import httpx
from datetime import datetime
import re
import time as _time


PAYWALL_DOMAINS = [
    "rzeczpospolita.pl", "rp.pl", "wyborcza.pl", "polityka.pl",
    "newsweek.pl", "tygodnikpowszechny.pl", "puls-biznesu.pl",
]


def _detect_paywall(url: str) -> bool:
    domain = url.split("/")[2] if url.startswith("http") else ""
    return any(d in domain for d in PAYWALL_DOMAINS)


def _parse_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime.fromtimestamp(_time.mktime(val))
            except Exception:
                pass
    return None


def _extract_image(entry) -> str | None:
    # YouTube / media:thumbnail (highest priority)
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")
    # media:content
    if hasattr(entry, "media_content") and entry.media_content:
        for m in entry.media_content:
            if m.get("medium") == "image" or m.get("type", "").startswith("image"):
                return m.get("url")
    # enclosures
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image"):
                return enc.get("href") or enc.get("url")
    # img in summary
    if hasattr(entry, "summary"):
        m = re.search(r'<img[^>]+src=["\']([^"\']{10,})["\']', entry.summary or "")
        if m:
            return m.group(1)
    return None


def _is_youtube_feed(url: str) -> bool:
    return "youtube.com/feeds" in url or "youtube.com/feeds/videos.xml" in url


def _youtube_video_url(entry) -> str:
    """Return canonical youtube.com/watch URL from a feed entry."""
    link = entry.get("link", "")
    if "youtube.com/watch" in link:
        return link
    yt_id = getattr(entry, "yt_videoid", None) or getattr(entry, "videoid", None)
    if yt_id:
        return f"https://www.youtube.com/watch?v={yt_id}"
    return link


def _youtube_thumbnail(entry) -> str | None:
    img = _extract_image(entry)
    if img:
        return img
    # fallback: construct from video ID
    yt_id = getattr(entry, "yt_videoid", None)
    if yt_id:
        return f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
    return None


async def fetch_rss(url: str, source_id: int) -> list[dict]:
    headers = {"User-Agent": "NewsRadar/1.0 feed-reader"}
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            content = resp.text
        except Exception:
            return []

    feed = feedparser.parse(content)
    is_yt = _is_youtube_feed(url)
    articles = []

    for entry in feed.entries[:30]:
        article_url = _youtube_video_url(entry) if is_yt else entry.get("link", "")
        if not article_url:
            continue

        summary = entry.get("summary", "") or entry.get("description", "")
        summary = re.sub(r"<[^>]+>", "", summary).strip()[:600]

        image = _youtube_thumbnail(entry) if is_yt else _extract_image(entry)

        articles.append({
            "source_id": source_id,
            "title": entry.get("title", "Bez tytułu").strip(),
            "url": article_url,
            "summary": summary or None,
            "image_url": image,
            "author": entry.get("author", None),
            "published_at": _parse_date(entry),
            "is_paywalled": False if is_yt else _detect_paywall(article_url),
            "tags": [t.get("term") for t in entry.get("tags", []) if t.get("term")][:5],
        })

    return articles
