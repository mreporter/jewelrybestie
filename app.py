import streamlit as st
import openai
import os
from PIL import Image, ExifTags
import io
import base64
from datetime import datetime

st.set_page_config(page_title="Jewelry Bestie AI", page_icon="💎", layout="centered")

st.markdown(
    """
    <div style='text-align: center;'>
        <img src='https://raw.githubusercontent.com/mreporter/jewelrybestie/main/bestie1.png' width='300' style='vertical-align: middle;'>
        <h1 style='display: inline-block; vertical-align: middle; margin: 0 10px;'>Jewelry Bestie AI</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Your AI-powered best friend that instantly helps you identify, describe, and price your jewelry!")

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'jewelry_type' not in st.session_state:
    st.session_state.jewelry_type = "Ring"
if 'set_details' not in st.session_state:
    st.session_state.set_details = ""
if 'condition' not in st.session_state:
    st.session_state.condition = "Excellent"
if 'history' not in st.session_state:
    st.session_state.history = []
if 'thumbnails' not in st.session_state:
    st.session_state.thumbnails = []
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = []
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False

if st.session_state.report_generated:
    if st.button("Start New Report"):
        st.session_state.uploaded_files = []
        st.session_state.jewelry_type = "Ring"
        st.session_state.set_details = ""
        st.session_state.condition = "Excellent"
        st.session_state.report_generated = False
        st.experimental_rerun()

uploaded_files = st.file_uploader("Upload up to 20 jewelry photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files

if st.session_state.uploaded_files:
    st.markdown("### Uploaded Photos (up to 6 shown)")
    cols = st.columns(3)
    for i, uploaded_file in enumerate(st.session_state.uploaded_files[:6]):
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
        cols[i % 3].image(image.resize((512, 512)), use_container_width=True)

jewelry_type = st.selectbox("What type of jewelry is this?", ["Ring", "Brooch", "Bracelet", "Necklace", "Earrings", "Set"], index=["Ring", "Brooch", "Bracelet", "Necklace", "Earrings", "Set"].index(st.session_state.jewelry_type))
st.session_state.jewelry_type = jewelry_type

if jewelry_type == "Set":
    set_details = st.text_input("What items are included in the set? (e.g., brooch and earrings, necklace and bracelet, etc.)", value=st.session_state.set_details)
    st.session_state.set_details = set_details
    if set_details:
        st.success("Saved ✅")

condition = st.selectbox("What's the condition?", ["Excellent", "Good", "Fair", "Poor"], index=["Excellent", "Good", "Fair", "Poor"].index(st.session_state.condition))
st.session_state.condition = condition

if st.button("Generate Report"):
    if not st.session_state.uploaded_files:
        st.error("Please upload at least one photo.")
    elif jewelry_type == "Set" and not st.session_state.set_details.strip():
        st.error("Please describe the items included in the set.")
    else:
        images_base64 = []
        thumbnail = None
        for i, uploaded_file in enumerate(st.session_state.uploaded_files):
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

            image = image.resize((512, 512))
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            images_base64.append(img_base64)

            if i == 0:
                thumbnail = img_base64

        jewelry_type_full = jewelry_type
        if jewelry_type == "Set" and st.session_state.set_details:
            jewelry_type_full = f"Set including {st.session_state.set_details.strip()}"

        prompt = f"""
        You are a jewelry identification expert. A user has uploaded multiple photos of a jewelry piece in {st.session_state.condition} condition. 
        The type of jewelry is a **{jewelry_type_full}**. Please interpret the description and structure below precisely.

        ### Product Description

        **Title:** [Generate a compelling title that accurately matches the piece type and style.]

        **Description:** [Write a detailed paragraph explaining what the item is, what pieces are included, its style, likely era, and visible condition. Mention any typical use cases or styling ideas.]

        **Materials:**
        - [Material 1]
        - [Material 2]

        **Style/Era:**
        - [Style 1]
        - [Style 2]
        - [Era, if apparent]

        ### SEO Keywords
        - keyword 1
        - keyword 2
        - keyword 3
        - keyword 4
        - keyword 5

        ### Resale Price Suggestion
        Please include a resale price range in bold (e.g., **$30–$150**) followed by this sentence: "This estimate is based on current market trends and may vary. For a formal appraisal, consult a certified expert."
        """

        with st.spinner("Analyzing your jewelry with AI magic..."):
            try:
                openai.api_key = st.secrets["OPENAI_API_KEY"]

                content = [
                    {"type": "text", "text": prompt}
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
                        {"role": "system", "content": "You are an expert in jewelry appraisal and description."},
                        {"role": "user", "content": content}
                    ]
                )

                output = response.choices[0].message.content
                for i, img_base64 in enumerate(images_base64[:6]):
                    img_data = base64.b64decode(img_base64)
                    st.image(Image.open(io.BytesIO(img_data)), caption=f"Uploaded Jewelry Image {i+1}", use_container_width=True)
                st.markdown(output)

                st.session_state.history.insert(0, output)
                st.session_state.thumbnails.insert(0, thumbnail)
                st.session_state.timestamps.insert(0, datetime.now().strftime("%b %d, %I:%M%p"))
                st.session_state.report_generated = True

            except Exception as e:
                st.error(f"Something went wrong: {e}")

if st.session_state.history:
    st.markdown("---")
    st.subheader("Previous Reports")
    for i, report in enumerate(st.session_state.history):
        timestamp = st.session_state.timestamps[i] if i < len(st.session_state.timestamps) else f"Report {len(st.session_state.history) - i}"
        with st.expander(f"Report {len(st.session_state.history) - i} ({timestamp})"):
            if i < len(st.session_state.thumbnails):
                thumb_data = base64.b64decode(st.session_state.thumbnails[i])
                st.image(Image.open(io.BytesIO(thumb_data)), caption="Thumbnail", width=100)
            st.markdown(report)
