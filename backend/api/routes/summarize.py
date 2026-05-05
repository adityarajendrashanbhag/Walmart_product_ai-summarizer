"""Summarization HTTP routes."""

from fastapi import APIRouter, HTTPException

from backend.schemas.requests import SummarizeIn
from backend.schemas.responses import SummaryResponse
from backend.services.summarization_service import SummarizationService

router = APIRouter(tags=["summarize"])
summarization_service = SummarizationService()


@router.post("/summarize", response_model=SummaryResponse)
def summarize(payload: SummarizeIn):
    """Generate an AI summary from a cleaned review file stored in S3."""

    try:
        return summarization_service.summarize_reviews(
            bucket=payload.bucket,
            key=payload.key,
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {error}",
        ) from error
