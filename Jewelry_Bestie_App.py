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

# Initialize input field values in session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None
if 'jewelry_type' not in st.session_state:
    st.session_state.jewelry_type = ""
if 'user_notes' not in st.session_state:
    st.session_state.user_notes = ""

# Display Upload and Input Fields
if not st.session_state.clear_fields:
    st.session_state.uploaded_files = st.file_uploader("Upload one or more photos of your jewelry piece:", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key='file_uploader')
    st.session_state.jewelry_type = st.selectbox("Optional: Select the type of jewelry (if known):", ["", "Earrings", "Ring", "Bracelet", "Brooch", "Pendant", "Necklace", "Set (e.g., Brooch and Earrings)"], key='type_selector')
    st.session_state.user_notes = st.text_area("Optional: Add any notes about the piece (e.g., markings, brand name, where it was purchased, etc.):", key='notes_area')

# Add button to trigger analysis
generate_report = st.button("✨ Generate Jewelry Report")

uploaded_files = st.session_state.uploaded_files
jewelry_type = st.session_state.jewelry_type
user_notes = st.session_state.user_notes

if uploaded_files and generate_report:
    images_base64 = []
    primary_thumbnail = None

    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)

        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = image._getexif()
            if exif is not None:
                orientation_value = exif.get(orientation)
                if orientation_value == 3:
                    image = image.rotate(180, expand=True)
                elif orientation_value == 6:
                    image = image.rotate(270, expand=True)
                elif orientation_value == 8:
                    image = image.rotate(90, expand=True)
        except Exception:
            pass

        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode()
        images_base64.append(img_b64)

        if not primary_thumbnail:
            primary_thumbnail = img_b64

    st.markdown("---")
    st.write("Analyzing your jewelry pieces with AI magic...")

    image_inputs = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img}"}
        } for img in images_base64
    ]

    type_note = f"Jewelry Type (user selected): {jewelry_type}" if jewelry_type else ""

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are a seasoned expert in vintage and antique jewelry appraisal. Carefully examine the uploaded images and provide a professional-level report using this structure:\n"
                        "Type: [Select from: earrings, ring, bracelet, brooch, pendant, necklace, set] (If it's a set, describe all pieces included)\n"
                        "Style and Era: [e.g., Art Deco, Mid-century, Victorian, 1950s, etc.]\n"
                        "Materials: [e.g., silver-tone metal, rhinestones, lucite, bakelite, etc.]\n"
                        "Details: Describe in depth the design elements (e.g., filigree, repoussé, carved motifs), clasp types, settings (e.g., prong, bezel), backing (e.g., screw back, post), known or suspected brands or makers, markings, engraving, provenance, and the condition including wear, tarnish, or restoration signs. Use expert-level language and if possible, draw comparisons to similar iconic pieces, brands, or time periods.\n"
                        "Estimated Resale Price: [e.g., $25 to $40 USD — based on sales trends on eBay, Etsy, and Ruby Lane]\n\n"
                        f"{type_note}\n"
                        f"Additional Notes from User: {user_notes}\n\n"
                        "Ensure your language is rich, confident, and filled with expertise. Include historical references when applicable. If unsure, explain what limits your confidence. Output in plain text only without markdown, formatting symbols, or asterisks."
                    )
                },
                *image_inputs
            ]
        }
    ]

    def fix_price_formatting(text):
        match = re.search(r'Estimated Resale Price:\s*\\?\$?(\d{1,5})\s*(?:to|-)?\s*\\?\$?(\d{1,5})', text)
        if match:
            low, high = sorted([int(match.group(1)), int(match.group(2))])
            formatted_price = f"Estimated Resale Price: ${low} to ${high} USD"
            text = re.sub(r'Estimated Resale Price:.*', formatted_price, text)
        return text

    def format_output_for_display(text):
        lines = text.strip().split('\n')
        output = []
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.lower().startswith("type:"):
                output.append(f"<p class='jb-section'>Type:</p><p>{line_stripped[len('Type:'):].strip()}</p>")
            elif line_stripped.lower().startswith("style and era:"):
                output.append(f"<p class='jb-section'>Style and Era:</p><p>{line_stripped[len('Style and Era:'):].strip()}</p>")
            elif line_stripped.lower().startswith("materials:"):
                output.append(f"<p class='jb-section'>Materials:</p><p>{line_stripped[len('Materials:'):].strip()}</p>")
            elif line_stripped.lower().startswith("details:"):
                output.append(f"<p class='jb-section'>Details:</p><p>{line_stripped[len('Details:'):].strip()}</p>")
            elif line_stripped.lower().startswith("condition:"):
                output.append(f"<p class='jb-section'>Condition:</p><p>{line_stripped[len('Condition:'):].strip()}</p>")
            elif line_stripped.lower().startswith("estimated resale price:"):
                output.append(f"<p class='jb-section'>Estimated Resale Price:</p><p>{line_stripped[len('Estimated Resale Price:'):].strip()}</p>")
            elif line_stripped.lower().startswith("additional notes:"):
                output.append(f"<p class='jb-section'>Additional Notes:</p><p>{line_stripped[len('Additional Notes:'):].strip()}</p>")
            else:
                output.append(f"<p>{line_stripped}</p>")
        return "\n".join(output), text.strip()

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000
        )

        result = response.choices[0].message.content.strip()
        result = fix_price_formatting(result)
        formatted_html, raw_text = format_output_for_display(result)

        st.markdown("---")
        st.markdown(formatted_html, unsafe_allow_html=True)

        st.download_button(
            label="💼 Download Report",
            data=raw_text,
            file_name="jewelry_report.txt",
            mime="text/plain"
        )

        with st.expander("📋 Copy Full Listing Info for eBay or Etsy"):
            st.code(raw_text, language='text')

        st.session_state.report_history.insert(0, raw_text)
        st.session_state.image_thumbnails.insert(0, primary_thumbnail)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif uploaded_files and not generate_report:
    st.info("Click '✨ Generate Jewelry Report' after entering your details to proceed!")
else:
    st.info("Upload one or more photos above to get started!")

# Display session history
if st.session_state.report_history:
    st.markdown("---")
    st.markdown("### 📄 Previous Reports This Session")
    total_reports = len(st.session_state.report_history)
    for i, (report, thumb_b64) in enumerate(zip(st.session_state.report_history, st.session_state.image_thumbnails)):
        display_num = total_reports - i
        with st.expander(f"Report {display_num}"):
            st.image(f"data:image/png;base64,{thumb_b64}", width=100)
            st.code(report, language='text')

    if st.button("Start New Report"):
        st.session_state.clear_fields = True
        st.session_state.new_report = True
        st.session_state.uploaded_files = None
        st.session_state.jewelry_type = ""
        st.session_state.user_notes = ""
        st.success("Ready for a new report! ✨")
        st.experimental_rerun()
