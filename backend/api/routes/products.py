"""Product-related HTTP routes."""

from fastapi import APIRouter, HTTPException

from backend.schemas.requests import URLIn
from backend.schemas.responses import ProductIdResponse
from backend.services.product_service import ProductService

router = APIRouter(tags=["products"])
product_service = ProductService()


@router.post("/extract_id", response_model=ProductIdResponse)
def extract_id(payload: URLIn):
    """Extract a Walmart product ID from the submitted product URL."""

    try:
        return {"product_id": product_service.extract_product_id(payload.url)}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
