import streamlit as st
import openai
import base64
from PIL import Image, ExifTags
import io
import os
import re
from datetime import datetime

# Use the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Jewelry Bestie", page_icon="💎")
st.markdown("""
    <style>
    .reportview-container .markdown-text-container {
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        color: #444;
    }
    .jb-section {
        font-family: 'Georgia', serif;
        font-size: 18px;
        font-weight: bold;
        color: #3c3c3c;
        margin-top: 1.5em;
    }
    .copy-box {
        background-color: #f4f4f4;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
    }
    </style>
    <script>
        window.onload = function() {
            if (window.location.hash === "#scroll-to-top") {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }
    </script>
    """, unsafe_allow_html=True)

st.title("💎 Jewelry Bestie")
st.write("Your AI-powered best friend for identifying, pricing, and describing jewelry.")

# Session state to store history
if 'report_history' not in st.session_state:
    st.session_state.report_history = []
if 'image_thumbnails' not in st.session_state:
    st.session_state.image_thumbnails = []
if 'clear_fields' not in st.session_state:
    st.session_state.clear_fields = False
if 'new_report' not in st.session_state:
    st.session_state.new_report = False
if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")

# Initialize input field values in session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None
if 'jewelry_type' not in st.session_state:
    st.session_state.jewelry_type = ""
if 'user_notes' not in st.session_state:
    st.session_state.user_notes = ""

# Display Upload and Input Fields
if not st.session_state.clear_fields:
    st.session_state.uploaded_files = st.file_uploader("Upload one or more photos of your jewelry piece:", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f'file_uploader_{st.session_state.session_id}')
    st.session_state.jewelry_type = st.selectbox("Optional: Select the type of jewelry (if known):", ["", "Earrings", "Ring", "Bracelet", "Brooch", "Pendant", "Necklace", "Set (e.g., Brooch and Earrings)"], key=f'type_selector_{st.session_state.session_id}')
    st.session_state.user_notes = st.text_area("Optional: Add any notes about the piece (e.g., markings, brand name, where it was purchased, etc.):", key=f'notes_area_{st.session_state.session_id}')

# Add button to trigger analysis
generate_report = st.button("✨ Generate Jewelry Report")

uploaded_files = st.session_state.uploaded_files
jewelry_type = st.session_state.jewelry_type
user_notes = st.session_state.user_notes

# Show success when a new report is ready
if generate_report and uploaded_files:
    st.success("🎉 Your jewelry report is ready! Scroll down to view your results.")
    st.markdown("<a name='scroll-to-top'></a>", unsafe_allow_html=True)
    st.session_state.report_history.append({
        "images": uploaded_files,
        "type": jewelry_type,
        "notes": user_notes
    })
    st.session_state.clear_fields = False

# Start New Report Button (only after a report has been generated)
if st.session_state.report_history:
    if st.button("Start New Report"):
        st.session_state.clear_fields = True
        st.session_state.new_report = True
        st.session_state.uploaded_files = None
        st.session_state.jewelry_type = ""
        st.session_state.user_notes = ""
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.experimental_rerun()
