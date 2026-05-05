"""Application settings loaded from environment variables."""

import os


class Settings:
    """Central configuration for cloud region, storage, and model settings."""

    aws_region: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    s3_bucket: str = os.getenv("S3_BUCKET", "walmart-scraped-data")
    bedrock_model_id: str = os.getenv("BEDROCK_MODEL_ID", "qwen.qwen3-32b-v1:0")


settings = Settings()
