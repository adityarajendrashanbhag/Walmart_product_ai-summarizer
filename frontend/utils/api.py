import os, requests
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

def extract_id(url: str) -> dict:
    """
    Extracting the product ID from a given Walmart product URL.
    1. Call the /extract_id endpoint with the given URL.
    2. If successful, return the JSON response containing the product ID.
    :param url: https://www.walmart.com/ip/Apple-AirPods-Pro-2-Wireless-Earbuds-Active-Noise-Cancellation-Hearing-Aid-Feature/5689919121?classType=VARIANT&athbdg=L1102&from=/search
    :return: 5689919121
    """
    r = requests.post(f"{API_BASE}/extract_id", json={"url": url}, timeout=60)
    r.raise_for_status()
    return r.json()

def scrape(product_id: str) -> dict:
    """
    Scrape Walmart reviews using the provided product ID.
    :param product_id: 5689919121
    :return: reviews data in JSON format

    """
    r = requests.post(f"{API_BASE}/scrape", json={"product_id": product_id}, timeout=60)
    r.raise_for_status()
    return r.json()

def data_clean(data: list[dict], pid: str) -> dict:
    """
    Perform data cleaning on the provided reviews data.
    :param data: reviews data in JSON format
    :return: cleaned data in JSON format

    """
    r = requests.post(f"{API_BASE}/data_clean", json={"json_result": data, "product_id": pid}, timeout=60)
    r.raise_for_status()
    return r.json()

def summarize(product_id: str):
    payload = {
        "bucket": "walmart-scraped-data",
        "key": f"{product_id}.csv"
    }
    res = requests.post(f"{API_BASE}/summarize", json=payload)
    res.raise_for_status()
    return res.json()