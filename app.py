import streamlit as st
import openai
import os
from PIL import Image, ExifTags
import io
import base64

st.set_page_config(page_title="Jewelry Bestie AI", page_icon="💎", layout="centered")

st.markdown(
    """
    <div style='text-align: center;'>
        <img src='https://raw.githubusercontent.com/mreporter/jewelrybestie/main/bestie1.png' width='80' style='vertical-align: middle;'>
        <h1 style='display: inline-block; vertical-align: middle; margin: 0 10px;'>Jewelry Bestie AI</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Your AI-powered best friend that instantly helps you identify, describe, and price your jewelry!")

uploaded_files = st.file_uploader("Upload up to 20 jewelry photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Show first 6 uploaded images
if uploaded_files:
    st.markdown("### Uploaded Photos (up to 6 shown)")
    cols = st.columns(3)
    for i, uploaded_file in enumerate(uploaded_files[:6]):
        image = Image.open(uploaded_file)
        cols[i % 3].image(image, use_column_width=True)

jewelry_type = st.selectbox("What type of jewelry is this?", ["Ring", "Brooch", "Bracelet", "Necklace", "Earrings", "Set (Necklace & Earrings)"])

condition = st.selectbox("What's the condition?", ["Excellent", "Good", "Fair", "Poor"])

if 'history' not in st.session_state:
    st.session_state.history = []

if 'thumbnails' not in st.session_state:
    st.session_state.thumbnails = []

if st.button("Generate Report") and uploaded_files:
    images_base64 = []
    thumbnail = None
    for i, uploaded_file in enumerate(uploaded_files):
        image = Image.open(uploaded_file)

        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = image._getexif()
            if exif is not None:
                orientation = exif.get(orientation, None)
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except:
            pass

        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        images_base64.append(img_base64)

        if i == 0:
            thumbnail = img_base64

    prompt = f"""
    You are a jewelry identification expert. A user has uploaded multiple photos of a jewelry piece in {condition} condition. The type of jewelry is a {jewelry_type}.
    Please provide the following information in clearly formatted markdown:

    ### Product Description

    **Title:** [Generate a compelling title that describes the piece]

    **Description:** [Detailed paragraph about the item, including what it is, its use, its style, likely era, and visible condition. Mention typical use cases or occasions.]

    **Materials:**
    - [Material 1]
    - [Material 2]

    **Style/Era:**
    - [Style 1]
    - [Style 2]
    - [Era if known]

    ### SEO Keywords
    - keyword 1
    - keyword 2
    - keyword 3
    - keyword 4
    - keyword 5

    ### Resale Price Suggestion
    Based on similar items, resale prices typically range from $30 to $150, depending on the maker, condition, and rarity.

    Price suggestions are based on current market estimates. For a formal appraisal, please consult with a certified jewelry expert.
    """

    with st.spinner("Analyzing your jewelry with AI magic..."):
        try:
            openai.api_key = st.secrets["OPENAI_API_KEY"]

            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            for img_base64 in images_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_base64}"
                    }
                })

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in jewelry appraisal and description."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

            output = response.choices[0].message.content
            for i, img_base64 in enumerate(images_base64[:6]):
                img_data = base64.b64decode(img_base64)
                st.image(Image.open(io.BytesIO(img_data)), caption=f"Uploaded Jewelry Image {i+1}", use_container_width=True)
            st.markdown(output)

            # Save report and thumbnail to session history
            st.session_state.history.insert(0, output)
            st.session_state.thumbnails.insert(0, thumbnail)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

# Display report history
if st.session_state.history:
    st.markdown("---")
    st.subheader("Previous Reports")
    for i, report in enumerate(st.session_state.history):
        with st.expander(f"Report {len(st.session_state.history) - i}"):
            if i < len(st.session_state.thumbnails):
                thumb_data = base64.b64decode(st.session_state.thumbnails[i])
                st.image(Image.open(io.BytesIO(thumb_data)), caption="Thumbnail", width=100)
            st.markdown(report)
