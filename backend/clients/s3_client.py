"""S3 repository wrapper for review-data storage and retrieval."""

from io import StringIO

import boto3
import pandas as pd

from backend.config.settings import settings


class S3Repository:
    """Handles review CSV persistence in Amazon S3."""

    def __init__(self, bucket: str | None = None, region_name: str | None = None):
        """Create an S3 client bound to the configured bucket and region."""

        self.bucket = bucket or settings.s3_bucket
        self.client = boto3.client("s3", region_name=region_name or settings.aws_region)

    def build_product_key(self, product_id: str) -> str:
        """Return the S3 object key used for a product's cleaned review file."""

        return f"{product_id}.csv"

    def uri_for_key(self, key: str) -> str:
        """Return an S3 URI for a bucket key."""

        return f"s3://{self.bucket}/{key}"

    def file_exists(self, key: str) -> bool:
        """Check whether a given S3 object already exists."""

        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except self.client.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "404":
                return False
            raise

    def load_reviews_df(self, key: str) -> pd.DataFrame:
        """Load a CSV object from S3 into a pandas DataFrame."""

        response = self.client.get_object(Bucket=self.bucket, Key=key)
        content = response["Body"].read().decode("utf-8")
        return pd.read_csv(StringIO(content))

    def upload_df(self, df: pd.DataFrame, key: str) -> str:
        """Upload a DataFrame to S3 as CSV and return its S3 URI."""

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        self.client.put_object(Bucket=self.bucket, Key=key, Body=csv_buffer.getvalue())
        return self.uri_for_key(key)
