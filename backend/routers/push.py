"""Web Push notifications (VAPID)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from db.database import get_db
from db.models import PushSubscription
import os
import json

router = APIRouter(prefix="/api/push", tags=["push"])

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_EMAIL = os.getenv("VAPID_EMAIL", "mailto:newsradar@example.com")


class SubscriptionData(BaseModel):
    endpoint: str
    keys: dict  # {p256dh, auth}


class PushPayload(BaseModel):
    title: str
    body: str
    url: str | None = None
    icon: str | None = None


@router.get("/vapid-key")
async def get_vapid_key():
    return {"publicKey": VAPID_PUBLIC_KEY}


@router.post("/subscribe", status_code=201)
async def subscribe(data: SubscriptionData, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(PushSubscription).where(PushSubscription.endpoint == data.endpoint))
    if existing.scalar_one_or_none():
        return {"ok": True, "message": "Already subscribed"}

    sub = PushSubscription(
        endpoint=data.endpoint,
        p256dh=data.keys.get("p256dh", ""),
        auth=data.keys.get("auth", ""),
    )
    db.add(sub)
    await db.commit()
    return {"ok": True}


@router.delete("/unsubscribe")
async def unsubscribe(endpoint: str, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(PushSubscription).where(PushSubscription.endpoint == endpoint))
    await db.commit()
    return {"ok": True}


@router.post("/send")
async def send_notification(payload: PushPayload, db: AsyncSession = Depends(get_db)):
    if not VAPID_PRIVATE_KEY:
        raise HTTPException(503, "VAPID keys not configured. Run: python generate_vapid.py")

    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        raise HTTPException(503, "pywebpush not installed")

    result = await db.execute(select(PushSubscription))
    subs = result.scalars().all()
    sent, failed = 0, 0

    notification_data = json.dumps({
        "title": payload.title,
        "body": payload.body,
        "url": payload.url or "/",
        "icon": payload.icon or "/icons/icon-192.png",
    })

    for sub in subs:
        try:
            webpush(
                subscription_info={"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}},
                data=notification_data,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_EMAIL},
            )
            sent += 1
        except Exception:
            failed += 1

    return {"sent": sent, "failed": failed}
