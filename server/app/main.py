# server/app/main.py  (run this with uvicorn)
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shared.walmart.scraper import fetch_walmart_reviews
import pandas as pd
import unicodedata

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

@app.post("/data_clean")
def data_clean(payload: dict):  # payload already contains `json_result`
    try:
        def clean_text(text: str) -> str:
            if not isinstance(text, str):
                return ""

            # Normalize unicode characters (é → e, curly quotes → ')
            text = unicodedata.normalize("NFKD", text)

            # Remove emojis and non-ASCII symbols
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)

            # Keep words, numbers, apostrophes
            text = re.sub(r"[^A-Za-z0-9' ]+", " ", text)

            # Remove stray apostrophes (not inside words)
            text = re.sub(r"\B'|'(?!\w)", "", text)

            # Collapse multiple spaces
            text = re.sub(r"\s+", " ", text).strip()

            return text
        # Step 1: Load reviews into DataFrame
        reviews_df = pd.DataFrame(payload["json_result"])

        # Step 2: Transform into clean format
        reviews_df = (
            reviews_df.drop(columns=["negative_feedback", "positive_feedback", "title"])
            .rename(
                columns={
                    "position": "customer_id",
                    "rating": "customer_rating",
                    "review_submission_time": "review_date",
                    "text": "review_text",
                }
            )
        )
        reviews_df["customer_id"] = "C" + reviews_df["customer_id"].astype(str)
        reviews_df["review_date"] = pd.to_datetime(reviews_df["review_date"])
        reviews_df["review_text"] = reviews_df["review_text"].astype(str).str.lower()
        reviews_df["review_text"] = reviews_df["review_text"].apply(clean_text)

        # ✅ Prevent NaN -> JSON error
        reviews_df = reviews_df.where(pd.notnull(reviews_df), None)

        return reviews_df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(500, f"Data cleaning failed: {e}")
