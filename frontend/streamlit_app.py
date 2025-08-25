import streamlit as st
import pandas as pd
from utils.api import extract_id, scrape

st.set_page_config(page_title="Walmart Review Analyzer", page_icon="🛒", layout="centered")
st.title("Walmart Review Analyzer (Streamlit + FastAPI)")

url = st.text_input("Paste Walmart product URL")

if st.button("Summarize") and url:
    try:
        with st.spinner("Extracting product ID..."):
            pid = extract_id(url)["product_id"]
        st.success(f"Product ID: {pid}")

        with st.spinner("Scraping (demo)…"):
            data = scrape(pid)["rows"]
        st.dataframe(pd.DataFrame(data))
    except Exception as e:
        st.error(f"Error: {e}")
