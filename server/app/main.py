# server/app/main.py  (run this with uvicorn)
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shared.walmart.scraper import fetch_walmart_reviews

app = FastAPI(title="Walmart API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten for prod
    allow_methods=["*"],
    allow_headers=["*"],
)

WALMART_ID = re.compile(r"/ip/[^/]+/(\d+)")

class URLIn(BaseModel):
    url: str

class ScrapeIn(BaseModel):
    product_id: str
    pages: int = 5
    sort: str = "helpful"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/extract_id")
def extract_id(payload: URLIn):
    m = WALMART_ID.search(payload.url or "")
    if not m:
        raise HTTPException(400, "Could not extract product ID")
    return {"product_id": m.group(1)}

@app.post("/scrape")
def scrape(payload: ScrapeIn):
    try:
        reviews = fetch_walmart_reviews(
            product_id=payload.product_id,
            pages=payload.pages,
            sort=payload.sort,
        )
        return {"rows": reviews, "count": len(reviews)}
    except Exception as e:
        # Surface a friendly error to the UI
        raise HTTPException(500, f"Scrape failed: {e}")
