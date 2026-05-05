"""SerpAPI client wrapper for Walmart review scraping."""

import os

from dotenv import find_dotenv, load_dotenv
from serpapi import GoogleSearch

load_dotenv(find_dotenv())


class SerpAPIClient:
    """Encapsulates Walmart review retrieval through SerpAPI."""

    def __init__(self, api_key: str | None = None):
        """Initialize the client with an explicit or environment-provided API key."""

        self.api_key = api_key or os.getenv("SERPAPI_KEY")

    def fetch_walmart_reviews(
        self,
        product_id: str,
        pages: int = 5,
        sort: str = "helpful",
    ) -> list[dict]:
        """Fetch review pages for a Walmart product and trim unused fields."""

        if not self.api_key:
            raise RuntimeError("SERPAPI_KEY not set in environment")

        product_reviews = []
        for page in range(1, pages + 1):
            params = {
                "engine": "walmart_product_reviews",
                "product_id": product_id,
                "sort": sort,
                "page": page,
                "api_key": self.api_key,
            }
            response = GoogleSearch(params).get_dict()
            reviews_data = response.get("reviews", []) or []
            for review in reviews_data:
                review.pop("customer_type", None)
                review.pop("user_nickname", None)
            product_reviews.extend(reviews_data)

        return product_reviews
