"""Service layer for transforming and persisting scraped review data."""

import pandas as pd

from backend.clients.s3_client import S3Repository
from backend.domain.review_cleaner import clean_review_text


class CleaningService:
    """Transforms raw review payloads into analysis-ready stored data."""

    def __init__(self, s3_repository: S3Repository | None = None):
        """Initialize the service with an S3-backed review repository."""

        self.s3_repository = s3_repository or S3Repository()

    def clean_and_store_reviews(self, product_id: str, raw_reviews: list[dict]) -> dict:
        """Clean scraped reviews, upload them to S3, and return storage metadata."""

        s3_key = self.s3_repository.build_product_key(product_id)
        if self.s3_repository.file_exists(s3_key):
            return {
                "status": "cached",
                "message": f"File already exists in S3: {s3_key}",
                "s3_uri": self.s3_repository.uri_for_key(s3_key),
            }

        reviews_df = pd.DataFrame(raw_reviews)
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
        reviews_df["review_text"] = reviews_df["review_text"].apply(clean_review_text)
        reviews_df = reviews_df.where(pd.notnull(reviews_df), None)

        s3_uri = self.s3_repository.upload_df(reviews_df, s3_key)
        return {
            "status": "uploaded",
            "s3_uri": s3_uri,
            "count": len(reviews_df),
        }
