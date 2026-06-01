"""Paywall bypass via 12ft.io and archive.ph proxies."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup

router = APIRouter(prefix="/api/paywall", tags=["paywall"])

BYPASS_SERVICES = [
    ("12ft", "https://12ft.io/proxy?q={}"),
    ("archive", "https://archive.ph/newest/{}"),
]


class BypassRequest(BaseModel):
    url: str


@router.post("/bypass")
async def bypass_paywall(req: BypassRequest):
    """Returns redirect URL to bypass paywall via 12ft.io or archive.ph."""
    # Return the proxy URLs so frontend can open them
    return {
        "original_url": req.url,
        "bypass_urls": [
            {"service": name, "url": template.format(req.url)}
            for name, template in BYPASS_SERVICES
        ],
    }


@router.get("/fetch")
async def fetch_article(url: str):
    """Fetch article content through 12ft.io and return clean text."""
    proxy_url = f"https://12ft.io/proxy?q={url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(proxy_url, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(502, "Bypass service unavailable")

        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "form"]):
            tag.decompose()

        article_tag = soup.find("article") or soup.find(class_=lambda c: c and "article" in c.lower()) or soup.body
        text = article_tag.get_text(separator="\n", strip=True) if article_tag else ""
        paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 60]

        return {"url": url, "content": "\n\n".join(paragraphs[:80]), "via": "12ft.io"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch article: {str(e)}")
