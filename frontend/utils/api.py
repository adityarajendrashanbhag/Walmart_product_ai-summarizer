import os, requests
from dotenv import load_dotenv
load_dotenv()

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

def extract_id(url: str) -> dict:
    r = requests.post(f"{API_BASE}/extract_id", json={"url": url}, timeout=15)
    r.raise_for_status()
    return r.json()

def scrape(product_id: str) -> dict:
    r = requests.post(f"{API_BASE}/scrape", json={"product_id": product_id}, timeout=60)
    r.raise_for_status()
    return r.json()
