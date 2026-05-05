from typing import Any

from pydantic import BaseModel


class URLIn(BaseModel):
    url: str


class ScrapeIn(BaseModel):
    product_id: str
    pages: int = 5
    sort: str = "helpful"


class CleanIn(BaseModel):
    product_id: str
    json_result: list[dict[str, Any]]


class SummarizeIn(BaseModel):
    bucket: str
    key: str
