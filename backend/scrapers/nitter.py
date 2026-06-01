"""X/Twitter profiles via public RSS (Nitter instances or direct RSS bridges)."""
import httpx
import feedparser
import re
from datetime import datetime


NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.1d4.us",
]


def _extract_x_username(url: str) -> str | None:
    match = re.search(r"(?:twitter\.com|x\.com)/([A-Za-z0-9_]+)", url)
    return match.group(1) if match else None


async def fetch_x_profile(url: str, source_id: int) -> list[dict]:
    username = _extract_x_username(url)
    if not username:
        return []

    for instance in NITTER_INSTANCES:
        rss_url = f"{instance}/{username}/rss"
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                headers = {"User-Agent": "NewsRadar/1.0"}
                resp = await client.get(rss_url, headers=headers)
                if resp.status_code != 200:
                    continue

            feed = feedparser.parse(resp.text)
            articles = []
            for entry in feed.entries[:20]:
                summary = re.sub(r"<[^>]+>", "", entry.get("summary", "")).strip()
                articles.append({
                    "source_id": source_id,
                    "title": summary[:120] + "..." if len(summary) > 120 else summary,
                    "url": entry.get("link", "").replace(instance, "https://twitter.com"),
                    "summary": summary[:500],
                    "image_url": None,
                    "author": f"@{username}",
                    "published_at": _parse_date(entry),
                    "is_paywalled": False,
                    "tags": ["x", "social"],
                })
            return articles
        except Exception:
            continue

    return []


def _parse_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        if hasattr(entry, attr) and getattr(entry, attr):
            try:
                import time
                return datetime.fromtimestamp(time.mktime(getattr(entry, attr)))
            except Exception:
                pass
    return None
