"""Health-check routes for the FastAPI application."""

from fastapi import APIRouter

from backend.schemas.responses import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health():
    """Return a simple status response for uptime checks."""

    return {"status": "ok"}
