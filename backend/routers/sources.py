from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from db.database import get_db
from db.models import Source

router = APIRouter(prefix="/api/sources", tags=["sources"])

PRESET_SOURCES = [
    {"name": "Gazeta.pl", "url": "https://rss.gazeta.pl/pub/rss/najnowsze_wyborcza_kraj.xml", "source_type": "rss", "category": "news", "color": "#e63946"},
    {"name": "Rzeczpospolita", "url": "https://www.rp.pl/rss/1019406", "source_type": "rss", "category": "news", "color": "#457b9d"},
    {"name": "TVN24", "url": "https://tvn24.pl/najnowsze.xml", "source_type": "rss", "category": "news", "color": "#e9c46a"},
    {"name": "WP Wiadomości", "url": "https://wiadomosci.wp.pl/rss.xml", "source_type": "rss", "category": "news", "color": "#2a9d8f"},
    {"name": "Onet Wiadomości", "url": "https://wiadomosci.onet.pl/.feed", "source_type": "rss", "category": "news", "color": "#e76f51"},
    {"name": "Puls Biznesu", "url": "https://www.pb.pl/rss/najnowsze.xml", "source_type": "rss", "category": "business", "color": "#264653"},
    {"name": "SpiderWeb", "url": "https://spidersweb.pl/feed", "source_type": "rss", "category": "tech", "color": "#7209b7"},
    {"name": "AntyWeb", "url": "https://antyweb.pl/feed", "source_type": "rss", "category": "tech", "color": "#4361ee"},
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
