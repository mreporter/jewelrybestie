import streamlit as st
import openai
import base64
from PIL import Image
import io
import os

# Use the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Jewelry Bestie", page_icon="💎")
st.title("💎 Jewelry Bestie")
st.write("Your AI-powered best friend for identifying, pricing, and describing jewelry.")

# Allow multiple image uploads
uploaded_files = st.file_uploader("Upload one or more photos of your jewelry piece:", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    images_base64 = []

    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode()
        images_base64.append(img_b64)

    st.markdown("---")
    st.write("😨 Analyzing your jewelry pieces with AI magic...")

    # Build content block for each image
    image_inputs = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img}"}
        } for img in images_base64
    ]

    # Add prompt as the first input
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are a vintage jewelry identification expert. Based on these images, what type of jewelry is shown? "
                        "Choose from: earrings, ring, bracelet, brooch, pendant, necklace. "
                        "If any item has a pin or clasp on the back, it's likely a brooch. "
                        "If there are two identical items, it may be earrings. Use all the images to make one identification. "
                        "Also describe the style, era, and estimated resale price."
                    )
                },
                *image_inputs
            ]
        }
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=700
        )

        result = response.choices[0].message.content
        st.markdown("---")
        st.subheader("📋 Jewelry Bestie's Report")
        st.write(result)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

else:
    st.info("Upload one or more photos above to get started!")
