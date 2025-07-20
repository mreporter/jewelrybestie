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
if 'trigger_report_generation' not in st.session_state:
    st.session_state.trigger_report_generation = False

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

    if st.button("✨ Generate Jewelry Report"):
        if st.session_state.uploaded_files:
            images_base64 = []
            for uploaded_file in st.session_state.uploaded_files:
                bytes_data = uploaded_file.read()
                encoded = base64.b64encode(bytes_data).decode('utf-8')
                images_base64.append(encoded)

            prompt = f"Describe this piece of jewelry. Jewelry type: {st.session_state.jewelry_type}. Notes: {st.session_state.user_notes}."

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            *[
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}
                                for img in images_base64
                            ]
                        ]}
                    ],
                    max_tokens=800
                )

                report_text = response['choices'][0]['message']['content']
            except Exception as e:
                report_text = f"Error generating report: {e}"

            st.session_state.report_history.append({
                "images": st.session_state.uploaded_files,
                "type": st.session_state.jewelry_type,
                "notes": st.session_state.user_notes,
                "report": report_text
            })
            st.session_state.clear_fields = False
            st.session_state.new_report = True
            st.rerun()

# Display last report if available
if st.session_state.report_history:
    st.markdown("## 📄 Jewelry Report")
    last_report = st.session_state.report_history[-1]
    for image in last_report["images"]:
        st.image(image, caption="Uploaded Jewelry Image", use_container_width=True)
    st.markdown(f"**Jewelry Type:** {last_report['type']}")
    st.markdown(f"**Notes:** {last_report['notes']}")
    st.markdown("---")
    st.markdown(last_report.get("report", "No report available."))

    if st.button("Start New Report"):
        st.session_state.clear_fields = True
        st.session_state.new_report = True
        st.session_state.uploaded_files = None
        st.session_state.jewelry_type = ""
        st.session_state.user_notes = ""
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.rerun()

# Scroll to top if new session
if st.session_state.new_report:
    st.markdown("""
        <script>
        window.scrollTo({top: 0, behavior: 'smooth'});
        </script>
    """, unsafe_allow_html=True)
    st.session_state.new_report = False
