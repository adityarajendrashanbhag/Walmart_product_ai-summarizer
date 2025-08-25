# shared/scraper.py  (new file or wherever you keep scrapers)
import os, json
from serpapi import GoogleSearch
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def fetch_walmart_reviews(product_id: str, pages: int = 5, sort: str = "helpful"):
    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY not set in environment")

    product_reviews = []
    for page in range(1, pages + 1):
        params = {
            "engine": "walmart_product_reviews",
            "product_id": product_id,     # <-- use the argument
            "sort": sort,
            "page": page,
            "api_key": SERPAPI_KEY,
        }
        response = GoogleSearch(params).get_dict()
        reviews_data = response.get("reviews", []) or []
        for r in reviews_data:
            r.pop("customer_type", None)
            r.pop("user_nickname", None)
        product_reviews.extend(reviews_data)

    return product_reviews
