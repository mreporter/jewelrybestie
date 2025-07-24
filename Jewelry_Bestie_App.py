import streamlit as st
from PIL import Image, ExifTags, UnidentifiedImageError
import io
import base64
import os

# Install missing dependency
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    st.error("The Google Generative AI module is not installed. Please add 'google-generativeai' to your requirements.txt file.")
    st.stop()

# Required packages for Streamlit deployment
# Add this to requirements.txt if not already present:
# streamlit
# Pillow
# google-generativeai

st.set_page_config(page_title="Jewelry Bestie - AI Jewelry Identifier", layout="centered")
st.title(":gem: Jewelry Bestie")
st.caption("Your AI powered best friend for identifying, pricing, and describing jewelry.")

if "report_history" not in st.session_state:
    st.session_state.report_history = []
if "current_images" not in st.session_state:
    st.session_state.current_images = []
if "generate_report" not in st.session_state:
    st.session_state.generate_report = False
if "reset" not in st.session_state:
    st.session_state.reset = False

# Set your Gemini API key
if "gemini_api_key" not in st.secrets or st.secrets["gemini_api_key"] == "your-gemini-api-key-here":
    st.error("Gemini API key is missing or invalid. Please set a valid key in your Streamlit app secrets.")
    st.stop()

# Use the updated Gemini model
genai.configure(api_key=st.secrets["gemini_api_key"])
model = genai.GenerativeModel('models/gemini-1.5-flash')

def correct_image_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())
        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    except Exception:
        pass
    return image

def analyze_jewelry_with_gemini(image_bytes):
    image_parts = [
        {
            "mime_type": "image/jpeg",
            "data": image_bytes
        }
    ]

    prompt = """
    You are an expert in vintage jewelry identification and pricing.
    Given the following image of a jewelry item, analyze and return:
    - Jewelry Type
    - Materials
    - Estimated Era or Style
    - Detailed Description
    - Estimated Resale Value Range in USD
    Format clearly with labels.
    """

    response = model.generate_content([prompt, image_parts[0]])
    return response.text

if not st.session_state.generate_report:
    st.markdown("Upload up to 20 photos of your jewelry for AI powered identification results.")
    uploaded_files = st.file_uploader("Upload photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        st.session_state.current_images = uploaded_files[:20]  # Limit to 20 files

    if st.button("Generate Jewelry Report"):
        st.session_state.generate_report = True
        st.session_state.reset = False
        with st.spinner(":mag: Analyzing your jewelry with AI-powered tools... Please wait."):
            st.rerun()

if st.session_state.generate_report:
    report_images = []
    thumbnail = None
    thumbnail_image = None
    try:
        uploaded_file = st.session_state.current_images[0]
        image = Image.open(uploaded_file)
        image = correct_image_orientation(image)
        st.image(image, caption="Uploaded Jewelry Image", use_container_width=True)
        image_bytes = uploaded_file.read()
        report_images.append(uploaded_file.name)

        # Create thumbnail
        thumbnail = uploaded_file.name
        thumbnail_io = io.BytesIO()
        image_copy = image.copy()
        image_copy.thumbnail((75, 75))
        image_copy.save(thumbnail_io, format='PNG')
        thumbnail_image = thumbnail_io.getvalue()

        # Call AI
        gemini_output = analyze_jewelry_with_gemini(image_bytes)

        # Attempt to parse fields
        price_range = ""
        jewelry_type = materials = era_style = description = ""

        for line in gemini_output.split("\n"):
            line = line.strip()
            if line.lower().startswith("jewelry type"):
                jewelry_type = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("materials"):
                materials = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("estimated era"):
                era_style = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("detailed description"):
                description = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("estimated resale"):
                price_range = line.split(":", 1)[-1].strip()

        price_range = price_range.replace("-", "–")

        report_data = {
            "thumbnail": thumbnail,
            "thumbnail_image": thumbnail_image,
            "images": report_images,
            "Jewelry Type": jewelry_type,
            "Materials": materials,
            "Estimated Era or Style": era_style,
            "Detailed Description": description,
            "Estimated Resale Value Range": price_range
        }

        st.session_state.report_history.insert(0, report_data)

        st.markdown("---")
        st.markdown(f"**Jewelry Type:** {jewelry_type}")
        st.markdown(f"**Materials:** {materials}")
        st.markdown(f"**Estimated Era or Style:** {era_style}")
        st.markdown(f"**Detailed Description:** {description}")
        st.markdown(f"**Estimated Resale Value Range:** {price_range}")

        if st.button("Start New Report"):
            st.session_state.generate_report = False
            st.session_state.current_images = []
            st.session_state.reset = True

    except UnidentifiedImageError:
        st.error("The uploaded file could not be identified as an image. Please upload a valid image file.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

if st.session_state.report_history:
    st.markdown("---")
    st.subheader("Previous Reports")
    for idx, report in enumerate(st.session_state.report_history):
        with st.expander(f"Report {idx + 1}"):
            if "thumbnail_image" in report:
                st.image(report["thumbnail_image"], caption="Thumbnail", width=75)
            for key, value in report.items():
                if key == "images":
                    for image_name in value:
                        st.text(f"Image: {image_name}")
                elif key not in ["thumbnail", "thumbnail_image"]:
                    st.markdown(f"**{key}:** {value}")
