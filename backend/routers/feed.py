from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func
from pydantic import BaseModel
from datetime import datetime, timedelta
from db.database import get_db
from db.models import Article, Source
from scrapers.rss import fetch_rss
from scrapers.nitter import fetch_x_profile
from scrapers.spotify import fetch_spotify_podcast

router = APIRouter(prefix="/api/feed", tags=["feed"])

SCRAPER_MAP = {
    "rss": fetch_rss,
    "x": fetch_x_profile,
    "spotify": fetch_spotify_podcast,
    "youtube": fetch_rss,  # YouTube exposes RSS feeds
}


async def _ingest_source(source: Source, db: AsyncSession) -> int:
    scraper = SCRAPER_MAP.get(source.source_type, fetch_rss)
    articles = await scraper(source.url, source.id)
    new_count = 0

    for art_data in articles:
        existing = await db.execute(select(Article).where(Article.url == art_data["url"]))
        if existing.scalar_one_or_none():
            continue
        article = Article(**art_data)
        db.add(article)
        new_count += 1

    source.last_fetched = datetime.utcnow()
    await db.commit()
    return new_count


@router.get("")
async def get_feed(
    category: str | None = None,
    source_id: int | None = None,
    unread_only: bool = False,
    bookmarked: bool = False,
    search: str | None = None,
    page: int = 1,
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Article, Source.name.label("source_name"), Source.color.label("source_color"), Source.source_type).join(
        Source, Article.source_id == Source.id
    ).where(Source.enabled == True)

    if category and category != "all":
        stmt = stmt.where(Source.category == category)
    if source_id:
        stmt = stmt.where(Article.source_id == source_id)
    if unread_only:
        stmt = stmt.where(Article.is_read == False)
    if bookmarked:
        stmt = stmt.where(Article.is_bookmarked == True)
    if search:
        stmt = stmt.where(Article.title.ilike(f"%{search}%"))

    stmt = stmt.order_by(desc(Article.published_at)).offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            **{c.key: getattr(row.Article, c.key) for c in Article.__table__.columns},
            "source_name": row.source_name,
            "source_color": row.source_color,
            "source_type": row.source_type,
            "published_at": row.Article.published_at.isoformat() if row.Article.published_at else None,
            "fetched_at": row.Article.fetched_at.isoformat(),
        }
        for row in rows
    ]


@router.post("/refresh")
async def refresh_feed(background_tasks: BackgroundTasks, source_id: int | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Source).where(Source.enabled == True)
    if source_id:
        stmt = stmt.where(Source.id == source_id)
    result = await db.execute(stmt)
    sources = result.scalars().all()

    total_new = 0
    for source in sources:
        new_count = await _ingest_source(source, db)
        total_new += new_count

    return {"refreshed": len(sources), "new_articles": total_new}


@router.patch("/{article_id}/read")
async def mark_read(article_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(update(Article).where(Article.id == article_id).values(is_read=True))
    await db.commit()
    return {"ok": True}


@router.patch("/{article_id}/bookmark")
async def toggle_bookmark(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        return {"ok": False}
    article.is_bookmarked = not article.is_bookmarked
    await db.commit()
    return {"bookmarked": article.is_bookmarked}


@router.post("/mark-all-read")
async def mark_all_read(source_id: int | None = None, db: AsyncSession = Depends(get_db)):
    stmt = update(Article).values(is_read=True)
    if source_id:
        stmt = stmt.where(Article.source_id == source_id)
    await db.execute(stmt)
    await db.commit()
    return {"ok": True}


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total = await db.execute(select(func.count(Article.id)))
    unread = await db.execute(select(func.count(Article.id)).where(Article.is_read == False))
    bookmarked = await db.execute(select(func.count(Article.id)).where(Article.is_bookmarked == True))
    return {
        "total": total.scalar(),
        "unread": unread.scalar(),
        "bookmarked": bookmarked.scalar(),
    }
