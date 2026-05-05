"""Service layer for loading stored reviews and generating summaries."""

from backend.clients.bedrock_client import BedrockClient
from backend.clients.s3_client import S3Repository


class SummarizationService:
    """Coordinates S3 review retrieval and Bedrock summarization."""

    def __init__(
        self,
        s3_repository: S3Repository | None = None,
        bedrock_client: BedrockClient | None = None,
    ):
        """Initialize the service with storage and model dependencies."""

        self.s3_repository = s3_repository or S3Repository()
        self.bedrock_client = bedrock_client or BedrockClient()

    def summarize_reviews(self, bucket: str, key: str) -> dict:
        """Load stored reviews from S3 and return an LLM-generated summary."""

        repository = self.s3_repository
        if bucket != repository.bucket:
            repository = S3Repository(bucket=bucket)

        df = repository.load_reviews_df(key)
        reviews_text = "\n".join(
            f"Rating: {row['customer_rating']} | Review: {row['review_text']}"
            for _, row in df.iterrows()
        )
        summary = self.bedrock_client.summarize_reviews(reviews_text)
        return {"summary": summary}
