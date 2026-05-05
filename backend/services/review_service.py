"""Service layer for review scraping and cache-aware retrieval."""

from backend.clients.s3_client import S3Repository
from backend.clients.serpapi_client import SerpAPIClient


class ReviewService:
    """Coordinates review scraping with S3-backed cache checks."""

    def __init__(
        self,
        scraper_client: SerpAPIClient | None = None,
        s3_repository: S3Repository | None = None,
    ):
        """Initialize the service with scraper and storage dependencies."""

        self.scraper_client = scraper_client or SerpAPIClient()
        self.s3_repository = s3_repository or S3Repository()

    def scrape_reviews(self, product_id: str, pages: int = 5, sort: str = "helpful") -> dict:
        """Return cached metadata or scrape raw reviews for a product."""

        s3_key = self.s3_repository.build_product_key(product_id)
        if self.s3_repository.file_exists(s3_key):
            return {
                "status": "cached",
                "message": f"File already exists in S3: {s3_key}",
                "s3_uri": self.s3_repository.uri_for_key(s3_key),
            }

        reviews = self.scraper_client.fetch_walmart_reviews(
            product_id=product_id,
            pages=pages,
            sort=sort,
        )
        return {"rows": reviews, "count": len(reviews)}
