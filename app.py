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
        <img src='https://raw.githubusercontent.com/mreporter/jewelrybestie/main/bestie1.png' width='80'>
        <h1 style='display: inline-block; vertical-align: middle; margin: 0 10px;'>Jewelry Bestie AI</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Your AI-powered best friend that instantly helps you identify, describe, and price your jewelry!")

uploaded_file = st.file_uploader("Upload a jewelry photo", type=["jpg", "jpeg", "png"])

condition = st.selectbox("What's the condition?", ["Excellent", "Good", "Fair", "Poor"])

if uploaded_file is not None:
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

    st.image(image, caption="Uploaded Jewelry Image", use_container_width=True)

    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    prompt = f"""
    You are a jewelry identification expert. A user has uploaded a photo of a jewelry piece in {condition} condition. 
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
    Based on similar items, resale prices typically range from **$30 to $150**, depending on the maker, condition, and rarity.

    For a formal appraisal, it is recommended to consult a jewelry expert.
    """

    with st.spinner("Analyzing your jewelry..."):
        try:
            openai.api_key = st.secrets["OPENAI_API_KEY"]

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in jewelry appraisal and description."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ]
            )

            output = response.choices[0].message.content
            st.markdown(output)

        except Exception as e:
            st.error(f"Something went wrong: {e}")
