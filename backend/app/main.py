# backend/app/main.py  (run this with uvicorn)
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shared.walmart.scraper import fetch_walmart_reviews
import pandas as pd
import unicodedata
import boto3, json
from io import StringIO

app = FastAPI(title="Walmart API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten for prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# S3 client
s3 = boto3.client("s3", region_name="us-east-1")  # change region if needed
S3_BUCKET = "walmart-scraped-data"

WALMART_ID = re.compile(r"/ip/[^/]+/(\d+)")

class URLIn(BaseModel):
    url: str

class ScrapeIn(BaseModel):
    product_id: str
    pages: int = 5
    sort: str = "helpful"

def load_reviews_from_s3(bucket: str, key: str) -> pd.DataFrame:
    """
    Reads a CSV file from S3 and returns a pandas DataFrame.
    """
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    df = pd.read_csv(StringIO(content))
    return df

def s3_file_exists(bucket: str, key: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        raise

def upload_df_to_s3(df: pd.DataFrame, bucket: str, key: str):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())
    return f"s3://{bucket}/{key}"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/extract_id")
def extract_id(payload: URLIn):
    m = WALMART_ID.search(payload.url or "")
    if not m:
        raise HTTPException(400, "Could not extract product ID")
    return {"product_id": m.group(1)}

@app.post("/scrape")
def scrape(payload: ScrapeIn):
    try:
        reviews = fetch_walmart_reviews(
            product_id=payload.product_id,
            pages=payload.pages,
            sort=payload.sort,
        )
        return {"rows": reviews, "count": len(reviews)}
    except Exception as e:
        # Surface a friendly error to the UI
        raise HTTPException(500, f"Scrape failed: {e}")

@app.post("/data_clean")
def data_clean(payload: dict):  # payload already contains `json_result` and 'product_id'
    try:
        product_id = payload.get("product_id")
        if not product_id:
            raise HTTPException(400, "product_id is required in payload")

        s3_key = f"{product_id}.csv"

        # ✅ Step 1: Check if file exists in S3 (cache)
        if s3_file_exists(S3_BUCKET, s3_key):
            return {
                "status": "cached",
                "message": f"File already exists in S3: {s3_key}",
                "s3_uri": f"s3://{S3_BUCKET}/{s3_key}"
            }

        def clean_text(text: str) -> str:
            if not isinstance(text, str):
                return ""

            # Normalize unicode characters (é → e, curly quotes → ')
            text = unicodedata.normalize("NFKD", text)

            # Remove emojis and non-ASCII symbols
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)

            # Keep words, numbers, apostrophes
            text = re.sub(r"[^A-Za-z0-9' ]+", " ", text)

            # Remove stray apostrophes (not inside words)
            text = re.sub(r"\B'|'(?!\w)", "", text)

            # Collapse multiple spaces
            text = re.sub(r"\s+", " ", text).strip()
            return text

        # Step 1: Load reviews into DataFrame
        reviews_df = pd.DataFrame(payload["json_result"])

        # Step 2: Transform into clean format
        reviews_df = (
            reviews_df.drop(columns=["negative_feedback", "positive_feedback", "title"])
            .rename(
                columns={
                    "position": "customer_id",
                    "rating": "customer_rating",
                    "review_submission_time": "review_date",
                    "text": "review_text",
                }
            )
        )
        reviews_df["customer_id"] = "C" + reviews_df["customer_id"].astype(str)
        reviews_df["review_date"] = pd.to_datetime(reviews_df["review_date"])
        reviews_df["review_text"] = reviews_df["review_text"].astype(str).str.lower()
        reviews_df["review_text"] = reviews_df["review_text"].apply(clean_text)

        # ✅ Prevent NaN -> JSON error
        reviews_df = reviews_df.where(pd.notnull(reviews_df), None)

        # ✅ Step 3: Upload to S3
        upload_df_to_s3(reviews_df, S3_BUCKET, s3_key)

        return {
            "status": "uploaded",
            "s3_uri": f"s3://{S3_BUCKET}/{s3_key}",
            "count": len(reviews_df)
        }
        # return reviews_df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(500, f"Data cleaning failed: {e}")

@app.post("/summarize")
def summarize_from_s3(payload: dict):
    """
    Expects: {"bucket": "my-walmart-data", "key": "walmart_reviews.csv"}
    """
    try:
        bucket = payload.get("bucket")
        key = payload.get("key")

        if not bucket or not key:
            raise HTTPException(400, "Bucket and key required")

        # Load reviews from S3
        df = load_reviews_from_s3(bucket, key)

        # Convert reviews into one big text block
        reviews_text = "\n".join(
            [f"Rating: {row['customer_rating']} | Review: {row['review_text']}"
             for _, row in df.iterrows()]
        )

        # Prompt for Qwen
        prompt = f"""
        Summarize these Walmart product reviews into:
        - Pros (Top 4 bullet points)
        - Cons (Top 4 bullet points)
        - Recommendation (1–2 sentences) unbiased 

        Reviews:
        {reviews_text}
        """

        # Build Bedrock body (Chat format)
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            "max_tokens": 10000,
            "temperature": 0.3,
            "top_p": 0.9
        }

        response = bedrock.invoke_model(
            modelId="qwen.qwen3-32b-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )

        result = json.loads(response["body"].read())
        summary_text = result["choices"][0]["message"]["content"]

        return {"summary": summary_text}

    except Exception as e:
        raise HTTPException(500, f"Summarization failed: {e}")
