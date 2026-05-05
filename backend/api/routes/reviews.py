"""Review scraping and cleaning HTTP routes."""

from fastapi import APIRouter, HTTPException

from backend.schemas.requests import CleanIn, ScrapeIn
from backend.services.cleaning_service import CleaningService
from backend.services.review_service import ReviewService

router = APIRouter(tags=["reviews"])
review_service = ReviewService()
cleaning_service = CleaningService()


@router.post("/scrape")
def scrape(payload: ScrapeIn):
    """Scrape raw Walmart reviews or return cached review-file metadata."""

    try:
        return review_service.scrape_reviews(
            product_id=payload.product_id,
            pages=payload.pages,
            sort=payload.sort,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Scrape failed: {error}") from error


@router.post("/data_clean")
def data_clean(payload: CleanIn):
    """Clean scraped review data and persist the normalized CSV to S3."""

    try:
        return cleaning_service.clean_and_store_reviews(
            product_id=payload.product_id,
            raw_reviews=payload.json_result,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Data cleaning failed: {error}",
        ) from error
