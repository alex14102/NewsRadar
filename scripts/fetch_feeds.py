#!/usr/bin/env python3
"""Fetch all RSS feeds and output articles.json for static GitHub Pages hosting."""
import feedparser
import json
import hashlib
import re
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

SOURCES = [
    # NEWS
    {"name": "Gazeta.pl",        "url": "https://rss.gazeta.pl/pub/rss/najnowsze_wyborcza_kraj.xml",                     "source_type": "rss", "category": "news",        "color": "#e63946"},
    {"name": "Rzeczpospolita",   "url": "https://www.rp.pl/rss/1019406",                                                 "source_type": "rss", "category": "news",        "color": "#c1121f"},
    {"name": "TVN24",            "url": "https://tvn24.pl/najnowsze.xml",                                                "source_type": "rss", "category": "news",        "color": "#e9c46a"},
    {"name": "WP Wiadomości",    "url": "https://wiadomosci.wp.pl/rss.xml",                                              "source_type": "rss", "category": "news",        "color": "#2a9d8f"},
    {"name": "Onet Wiadomości",  "url": "https://wiadomosci.onet.pl/.feed",                                              "source_type": "rss", "category": "news",        "color": "#e76f51"},
    {"name": "Do Rzeczy",        "url": "https://dorzeczy.pl/feed",                                                      "source_type": "rss", "category": "news",        "color": "#8b2c2c"},
    {"name": "New York Times",   "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",                        "source_type": "rss", "category": "news",        "color": "#1a1a1a"},
    # GEOPOLITYKA
    {"name": "Politico Europe",  "url": "https://www.politico.eu/feed/",                                                 "source_type": "rss", "category": "geopolityka", "color": "#0057b8"},
    {"name": "Defence24",        "url": "https://defence24.pl/rss.xml",                                                  "source_type": "rss", "category": "geopolityka", "color": "#4a6741"},
    {"name": "Al Jazeera",       "url": "https://www.aljazeera.com/xml/rss/all.xml",                                     "source_type": "rss", "category": "geopolityka", "color": "#c8a951"},
    {"name": "Foreign Policy",   "url": "https://foreignpolicy.com/feed/",                                               "source_type": "rss", "category": "geopolityka", "color": "#8b0000"},
    {"name": "The Economist",    "url": "https://www.economist.com/europe/rss.xml",                                      "source_type": "rss", "category": "geopolityka", "color": "#e3120b"},
    # GOSPODARKA
    {"name": "Puls Biznesu",     "url": "https://www.pb.pl/rss/najnowsze.xml",                                           "source_type": "rss", "category": "gospodarka",  "color": "#3a86ff"},
    {"name": "Money.pl",         "url": "https://www.money.pl/rss/gospodarka.xml",                                       "source_type": "rss", "category": "gospodarka",  "color": "#00b4d8"},
    {"name": "Bloomberg",        "url": "https://feeds.bloomberg.com/markets/news.rss",                                  "source_type": "rss", "category": "gospodarka",  "color": "#f4a261"},
    {"name": "WSJ Business",     "url": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",                               "source_type": "rss", "category": "gospodarka",  "color": "#0074d9"},
    # BIZNES
    {"name": "Forbes Polska",    "url": "https://www.forbes.pl/feed/rss",                                                "source_type": "rss", "category": "biznes",      "color": "#1d6fa4"},
    {"name": "Forbes",           "url": "https://www.forbes.com/business/feed/",                                         "source_type": "rss", "category": "biznes",      "color": "#c9a227"},
    {"name": "Business Insider", "url": "https://feeds.businessinsider.com/custom/all",                                  "source_type": "rss", "category": "biznes",      "color": "#e63946"},
    {"name": "Inc.com",          "url": "https://www.inc.com/rss",                                                       "source_type": "rss", "category": "biznes",      "color": "#2d6a4f"},
    # NAUKA
    {"name": "BBC Science",      "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",                 "source_type": "rss", "category": "nauka",       "color": "#ff6b35"},
    {"name": "Science Daily",    "url": "https://www.sciencedaily.com/rss/top/science.xml",                              "source_type": "rss", "category": "nauka",       "color": "#06d6a0"},
    {"name": "Nature",           "url": "https://www.nature.com/nature.rss",                                             "source_type": "rss", "category": "nauka",       "color": "#003d5b"},
    {"name": "NASA",             "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss",                                "source_type": "rss", "category": "nauka",       "color": "#0b3d91"},
    {"name": "Phys.org",         "url": "https://phys.org/rss-feed/",                                                    "source_type": "rss", "category": "nauka",       "color": "#48cae4"},
    # TECHNOLOGIA
    {"name": "SpiderWeb",        "url": "https://spidersweb.pl/feed",                                                    "source_type": "rss", "category": "technologia", "color": "#7c3aed"},
    {"name": "AntyWeb",          "url": "https://antyweb.pl/feed",                                                       "source_type": "rss", "category": "technologia", "color": "#4361ee"},
    {"name": "TechCrunch",       "url": "https://techcrunch.com/feed/",                                                  "source_type": "rss", "category": "technologia", "color": "#0d9e16"},
    {"name": "Wired",            "url": "https://www.wired.com/feed/rss",                                                "source_type": "rss", "category": "technologia", "color": "#b5a642"},
    {"name": "Ars Technica",     "url": "https://feeds.arstechnica.com/arstechnica/index",                               "source_type": "rss", "category": "technologia", "color": "#ff6600"},
]


def _parse_date(entry) -> str | None:
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc).isoformat()
            except Exception:
                pass
    for field in ("published", "updated"):
        val = getattr(entry, field, None)
        if val:
            try:
                return parsedate_to_datetime(val).isoformat()
            except Exception:
                pass
    return None


def _extract_image(entry) -> str | None:
    # media:thumbnail
    for m in getattr(entry, "media_thumbnail", []):
        if url := m.get("url"):
            return url
    # media:content image
    for m in getattr(entry, "media_content", []):
        if m.get("medium") == "image" and (url := m.get("url")):
            return url
    # enclosure
    for enc in getattr(entry, "enclosures", []):
        if enc.get("type", "").startswith("image/") and (url := enc.get("href") or enc.get("url")):
            return url
    # og:image in content
    content = (getattr(entry, "summary", "") or "") + (getattr(entry, "content", [{}])[0].get("value", "") if hasattr(entry, "content") else "")
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    if m:
        return m.group(1)
    return None


def _clean_summary(text: str | None) -> str | None:
    if not text:
        return None
    clean = re.sub(r"<[^>]+>", "", text).strip()
    return clean[:500] if clean else None


def stable_id(url: str) -> int:
    return int(hashlib.md5(url.encode()).hexdigest()[:8], 16)


def fetch_all() -> list[dict]:
    articles = []
    now = datetime.now(timezone.utc).isoformat()

    for src_id, source in enumerate(SOURCES, start=1):
        print(f"  Fetching {source['name']}...", file=sys.stderr)
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:30]:
                url = entry.get("link", "")
                if not url:
                    continue
                articles.append({
                    "id": stable_id(url),
                    "source_id": src_id,
                    "source_name": source["name"],
                    "source_color": source["color"],
                    "source_type": source["source_type"],
                    "category": source["category"],
                    "title": entry.get("title", "").strip(),
                    "url": url,
                    "summary": _clean_summary(entry.get("summary")),
                    "full_content": None,
                    "image_url": _extract_image(entry),
                    "author": entry.get("author", None),
                    "published_at": _parse_date(entry),
                    "fetched_at": now,
                    "is_read": False,
                    "is_bookmarked": False,
                    "is_paywalled": False,
                    "tags": [],
                })
        except Exception as e:
            print(f"  ERROR {source['name']}: {e}", file=sys.stderr)

    # Sort by published_at descending, fall back to fetched_at
    articles.sort(
        key=lambda a: a.get("published_at") or a["fetched_at"],
        reverse=True,
    )
    # Deduplicate by id
    seen = set()
    unique = []
    for a in articles:
        if a["id"] not in seen:
            seen.add(a["id"])
            unique.append(a)

    print(f"  Total: {len(unique)} articles from {len(SOURCES)} sources", file=sys.stderr)
    return unique


if __name__ == "__main__":
    import os
    out_path = sys.argv[1] if len(sys.argv) > 1 else "articles.json"
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    data = fetch_all()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Saved {len(data)} articles to {out_path}", file=sys.stderr)
