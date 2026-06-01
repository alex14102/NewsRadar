from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from db.database import get_db
from db.models import Source

router = APIRouter(prefix="/api/sources", tags=["sources"])

PRESET_SOURCES = [
    # NEWS — polskie wiadomości
    {"name": "Gazeta.pl",        "url": "https://rss.gazeta.pl/pub/rss/najnowsze_wyborcza_kraj.xml",                      "source_type": "rss",     "category": "news",        "color": "#e63946"},
    {"name": "Rzeczpospolita",   "url": "https://www.rp.pl/rss/1019406",                                                  "source_type": "rss",     "category": "news",        "color": "#c1121f"},
    {"name": "TVN24",            "url": "https://tvn24.pl/najnowsze.xml",                                                 "source_type": "rss",     "category": "news",        "color": "#e9c46a"},
    {"name": "WP Wiadomości",    "url": "https://wiadomosci.wp.pl/rss.xml",                                               "source_type": "rss",     "category": "news",        "color": "#2a9d8f"},
    {"name": "Onet Wiadomości",  "url": "https://wiadomosci.onet.pl/.feed",                                               "source_type": "rss",     "category": "news",        "color": "#e76f51"},
    {"name": "New York Times",   "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",                         "source_type": "rss",     "category": "news",        "color": "#1a1a1a"},
    # GEOPOLITYKA
    {"name": "Politico Europe",  "url": "https://www.politico.eu/feed/",                                                  "source_type": "rss",     "category": "geopolityka", "color": "#0057b8"},
    {"name": "Defence24",        "url": "https://defence24.pl/rss.xml",                                                   "source_type": "rss",     "category": "geopolityka", "color": "#4a6741"},
    {"name": "Al Jazeera",       "url": "https://www.aljazeera.com/xml/rss/all.xml",                                      "source_type": "rss",     "category": "geopolityka", "color": "#c8a951"},
    {"name": "Foreign Policy",   "url": "https://foreignpolicy.com/feed/",                                                "source_type": "rss",     "category": "geopolityka", "color": "#8b0000"},
    {"name": "The Economist",    "url": "https://www.economist.com/europe/rss.xml",                                       "source_type": "rss",     "category": "geopolityka", "color": "#e3120b"},
    # GOSPODARKA
    {"name": "Puls Biznesu",     "url": "https://www.pb.pl/rss/najnowsze.xml",                                            "source_type": "rss",     "category": "gospodarka",  "color": "#3a86ff"},
    {"name": "Money.pl",         "url": "https://www.money.pl/rss/gospodarka.xml",                                        "source_type": "rss",     "category": "gospodarka",  "color": "#00b4d8"},
    {"name": "Bloomberg",        "url": "https://feeds.bloomberg.com/markets/news.rss",                                   "source_type": "rss",     "category": "gospodarka",  "color": "#f4a261"},
    {"name": "WSJ Business",     "url": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",                                "source_type": "rss",     "category": "gospodarka",  "color": "#0074d9"},
    # BIZNES
    {"name": "Forbes Polska",    "url": "https://www.forbes.pl/feed/rss",                                                 "source_type": "rss",     "category": "biznes",      "color": "#1d6fa4"},
    {"name": "Forbes",           "url": "https://www.forbes.com/business/feed/",                                          "source_type": "rss",     "category": "biznes",      "color": "#c9a227"},
    {"name": "Business Insider", "url": "https://feeds.businessinsider.com/custom/all",                                   "source_type": "rss",     "category": "biznes",      "color": "#e63946"},
    {"name": "Inc.com",          "url": "https://www.inc.com/rss",                                                        "source_type": "rss",     "category": "biznes",      "color": "#2d6a4f"},
    # NAUKA
    {"name": "BBC Science",      "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",                  "source_type": "rss",     "category": "nauka",       "color": "#ff6b35"},
    {"name": "Science Daily",    "url": "https://www.sciencedaily.com/rss/top/science.xml",                               "source_type": "rss",     "category": "nauka",       "color": "#06d6a0"},
    {"name": "Nature",           "url": "https://www.nature.com/nature.rss",                                              "source_type": "rss",     "category": "nauka",       "color": "#003d5b"},
    {"name": "NASA",             "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss",                                 "source_type": "rss",     "category": "nauka",       "color": "#0b3d91"},
    {"name": "Phys.org",         "url": "https://phys.org/rss-feed/",                                                     "source_type": "rss",     "category": "nauka",       "color": "#48cae4"},
    # TECHNOLOGIA
    {"name": "SpiderWeb",        "url": "https://spidersweb.pl/feed",                                                     "source_type": "rss",     "category": "technologia", "color": "#7c3aed"},
    {"name": "AntyWeb",          "url": "https://antyweb.pl/feed",                                                        "source_type": "rss",     "category": "technologia", "color": "#4361ee"},
    {"name": "TechCrunch",       "url": "https://techcrunch.com/feed/",                                                   "source_type": "rss",     "category": "technologia", "color": "#0d9e16"},
    {"name": "Wired",            "url": "https://www.wired.com/feed/rss",                                                 "source_type": "rss",     "category": "technologia", "color": "#b5a642"},
    {"name": "Ars Technica",     "url": "https://feeds.arstechnica.com/arstechnica/index",                                "source_type": "rss",     "category": "technologia", "color": "#ff6600"},
    # VIDEO — YouTube
    {"name": "Damian Olszewski", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC9TWnOWxa6wdbPEZYYVpJTQ",  "source_type": "youtube", "category": "video",       "color": "#ff0000"},
    # SOCIAL — X (Twitter)
    {"name": "Donald Trump",     "url": "https://x.com/realDonaldTrump",                                                  "source_type": "x",       "category": "social",      "color": "#e4e4f0"},
]


class SourceCreate(BaseModel):
    name: str
    url: str
    source_type: str = "rss"
    category: str = "general"
    enabled: bool = True
    notify: bool = False
    color: str | None = None
    fetch_interval: int = 900


class SourceUpdate(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    notify: bool | None = None
    category: str | None = None
    color: str | None = None
    fetch_interval: int | None = None


@router.get("")
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).order_by(Source.created_at))
    return result.scalars().all()


@router.post("", status_code=201)
async def create_source(data: SourceCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Source).where(Source.url == data.url))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Source with this URL already exists")

    source = Source(**data.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.patch("/{source_id}")
async def update_source(source_id: int, data: SourceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(404, "Source not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(source, field, value)

    await db.commit()
    await db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Source).where(Source.id == source_id))
    await db.commit()


@router.post("/presets", status_code=201)
async def add_presets(db: AsyncSession = Depends(get_db)):
    added = []
    for preset in PRESET_SOURCES:
        existing = await db.execute(select(Source).where(Source.url == preset["url"]))
        if not existing.scalar_one_or_none():
            source = Source(**preset)
            db.add(source)
            added.append(preset["name"])
    await db.commit()
    return {"added": added}
