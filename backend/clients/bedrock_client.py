"""Bedrock client wrapper for review summarization requests."""

import json

import boto3

from backend.config.settings import settings


class BedrockClient:
    """Encapsulates calls to an AWS Bedrock chat model."""

    def __init__(self, model_id: str | None = None, region_name: str | None = None):
        """Create a Bedrock runtime client using configured model and region."""

        self.model_id = model_id or settings.bedrock_model_id
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region_name or settings.aws_region,
        )

    def summarize_reviews(self, reviews_text: str):
        """Generate a structured product-review summary from cleaned review text."""

        prompt = f"""
        Summarize these Walmart product reviews into:
        - Pros (Top 4 bullet points)
        - Cons (Top 4 bullet points)
        - Recommendation (1-2 sentences) unbiased

        Reviews:
        {reviews_text}
        """

        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
            "max_tokens": 10000,
            "temperature": 0.3,
            "top_p": 0.9,
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        result = json.loads(response["body"].read())
        return result["choices"][0]["message"]["content"]
