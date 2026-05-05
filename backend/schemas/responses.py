from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ProductIdResponse(BaseModel):
    product_id: str


class SummaryResponse(BaseModel):
    summary: Any
