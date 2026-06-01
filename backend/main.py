from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db.database import init_db, SessionLocal
from db.models import Source
from sqlalchemy import select
import asyncio

from routers import sources, feed, push, paywall, settings


scheduler = AsyncIOScheduler()


async def scheduled_refresh():
    from routers.feed import _ingest_source
    async with SessionLocal() as db:
        result = await db.execute(select(Source).where(Source.enabled == True))
        active_sources = result.scalars().all()
        for source in active_sources:
            try:
                await _ingest_source(source, db)
            except Exception as e:
                print(f"[Scheduler] Error ingesting {source.name}: {e}")


async def seed_presets():
    from routers.sources import PRESET_SOURCES
    async with SessionLocal() as db:
        result = await db.execute(select(Source))
        if result.scalars().first() is None:
            for preset in PRESET_SOURCES:
                source = Source(**preset)
                db.add(source)
            await db.commit()
            print("[Startup] Seeded preset sources")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_presets()
    scheduler.add_job(scheduled_refresh, "interval", minutes=15, id="auto_refresh")
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="NewsRadar API",
    description="News aggregator with notifications and paywall bypass",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://alex14102.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router)
app.include_router(feed.router)
app.include_router(push.router)
app.include_router(paywall.router)
app.include_router(settings.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "NewsRadar"}
