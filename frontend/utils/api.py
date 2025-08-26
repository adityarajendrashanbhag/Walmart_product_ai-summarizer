import os, requests
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

def extract_id(url: str) -> dict:
    r = requests.post(f"{API_BASE}/extract_id", json={"url": url}, timeout=60)
    r.raise_for_status()
    return r.json()

def scrape(product_id: str) -> dict:
    r = requests.post(f"{API_BASE}/scrape", json={"product_id": product_id}, timeout=60)
    r.raise_for_status()
    return r.json()

def data_clean(data: list[dict]) -> dict:
    r = requests.post(f"{API_BASE}/data_clean", json={"json_result": data}, timeout=60)
    r.raise_for_status()
    return r.json()
