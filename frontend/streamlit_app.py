import streamlit as st
import pandas as pd
import base64
from utils.api import extract_id, scrape, data_clean

# Add background image using Base64 encoding
def add_bg_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set the background image
add_bg_image("frontend/walmart-background.jpg")

st.set_page_config(page_title="Walmart Review Analyzer", page_icon="🛒", layout="centered")
st.title("Walmart Product Reviews AI Summarizer")

with st.form("summarize_form"):
    url = st.text_input("Enter Walmart product URL")
    submit = st.form_submit_button("Summarize")

if submit:
    if not url or not url.strip():
        st.info("Please enter a valid Walmart product URL")
    else:
        try:
            # Extract product ID
            with st.spinner("Extracting product ID..."):
                pid = extract_id(url)["product_id"]

            # Scrape reviews using SerpAPI
            with st.spinner("Scraping…"):
                data = scrape(pid)["rows"]

            # Cleaning the data using tokenization
            with st.spinner("Cleaning data ...."):
                cleaned_data = data_clean(data, pid)

            # Summarize from S3
            with st.spinner("Summarizing with Bedrock..."):
                from utils.api import summarize  # import your summarize API wrapper
                summary = summarize(pid)["summary"]

            st.subheader("📊 AI-Generated Summary")
            st.markdown(summary)

        except Exception as e:
            st.error(f"Error: {e}")

