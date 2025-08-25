import streamlit as st
import pandas as pd
from utils.api import extract_id, scrape

st.set_page_config(page_title="Walmart Review Analyzer", page_icon="🛒", layout="centered")
st.title("Walmart Product Reviews AI Summarizer")

with st.form("summarize_form"):
    url = st.text_input("Enter Walmart product URL")
    submit = st.form_submit_button("Summarize")

if submit:
    if not url or not url.strip():
        st.info("Please enter a valid Walmart product URL and click 'Summarize'.")
    else:
        try:
            with st.spinner("Extracting product ID..."):
                pid = extract_id(url)["product_id"]
            st.success(f"Product ID: {pid}")

            with st.spinner("Scraping…"):
                data = scrape(pid)["rows"]
            st.dataframe(pd.DataFrame(data))
        except Exception as e:
            st.error(f"Error: {e}")

