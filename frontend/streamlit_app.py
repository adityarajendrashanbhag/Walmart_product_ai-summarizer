import streamlit as st
import base64
from utils.api import extract_id, scrape, data_clean, summarize
import time
import boto3
import os

BACKEND_URL = os.getenv("API_BASE", "http://localhost:8000")  # fallback for local dev

def add_bg_image_from_s3(bucket_name, key):
    """
    Fetches an image from S3 and sets it as the background in Streamlit.
    :param bucket_name: Name of the S3 bucket.
    :param key: Key of the image file in the S3 bucket.
    """
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=key)
    image_data = response["Body"].read()
    encoded_string = base64.b64encode(image_data).decode()
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

# Example usage
add_bg_image_from_s3("walmart-scraped-data", "walmart-background/walmart-background.jpg")

# Mobile-friendly CSS tweaks
st.markdown("""
<style>
/* General mobile tweaks */
@media (max-width: 768px) {
    .stApp {
        font-size: 14px;
        padding: 8px;
    }
    h1, h2, h3 {
        font-size: 1.2em !important;
    }
    /* Make text input & button full width */
    .stTextInput, .stButton button {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)


def typing_effect(text, placeholder):
    """
    Simulates a typing effect by updating the placeholder with one character at a time.
    :param text: The full text to display.
    :param placeholder: The Streamlit placeholder to update.
    """
    for i in range(1, len(text) + 1):
        placeholder.markdown(text[:i])  # Update the placeholder with the current substring
        time.sleep(0.01)  # Adjust the delay for typing speed


st.set_page_config(
    page_title="Walmart Review Analyzer",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("Walmart Product Reviews AI Summarizer")

with st.form("summarize_form"):
    url = st.text_input("Enter Walmart product URL")
    submit = st.form_submit_button("Summarize")

if submit:
    if not url or not url.strip():
        st.info("Please enter a valid Walmart product URL")
    else:
        try:
            placeholder = st.empty()
            placeholder.markdown("")  # Reset the placeholder content

            # Extract product ID
            with st.spinner("Extracting product ID..."):
                pid = extract_id(url)["product_id"]

            # Scrape reviews using SerpAPI
            with st.spinner("Scraping…"):
                result = scrape(pid)

            if result.get("status") == "cached":
                with st.spinner("Summarizing with Bedrock..."):
                    summary = summarize(pid)["summary"]
            else:
                data = result["rows"]

                # Cleaning the data using tokenization
                with st.spinner("Cleaning data ...."):
                    cleaned_data = data_clean(data, pid)

                # Summarize from S3
                with st.spinner("Summarizing with Bedrock..."):
                    summary = summarize(pid)["summary"]
            if summary:
                placeholder.markdown("")  # Reset the placeholder content
                st.subheader("📊 AI Generated Summary")
                placeholder = st.empty()  # Create a placeholder for the summary
                typing_effect(summary, placeholder)

        except Exception as e:
            st.error(f"Error: {e}")