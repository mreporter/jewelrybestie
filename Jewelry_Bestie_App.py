import streamlit as st
import openai
import base64
from PIL import Image
import io
import os
import re

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
    st.write("Analyzing your jewelry pieces with AI magic...")

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
                        "You are a vintage jewelry identification expert. Based on these images, provide a report using the structure below. "
                        "Choose one for type: earrings, ring, bracelet, brooch, pendant, necklace. "
                        "If there are two identical items, it's likely earrings. A pin/clasp usually indicates a brooch. "
                        "Use all images and your expertise to identify the piece and format your output as plain text, no markdown or emojis."
                        "\n\nFormat exactly like this:\n"
                        "Type: [type]\n"
                        "Style and Era: [style and estimated era]\n"
                        "Materials: [materials used]\n"
                        "Details: [any additional notes or identifiers]\n"
                        "Estimated Resale Price: $XX to $XX USD\n"
                        "\nEnsure price formatting matches this exactly: dollar signs before both numbers, the word 'to' spaced properly, and ending with 'USD'."
                    )
                },
                *image_inputs
            ]
        }
    ]

    def fix_price_formatting(text):
        text = re.sub(r'(Estimated Resale Price:\s*)(?!\$)(\d+\s*to\s*\d+)', r'\1$\2 USD', text)
        text = re.sub(r'(Estimated Resale Price:\s*)\$(\d+)\s*to\s*\$?(\d+)(?!\s*USD)', r'\1$\2 to $\3 USD', text)
        text = re.sub(r'(?<!\$)(\d{1,4})to(\d{1,4})(?!\s*USD)', r'$\1 to $\2 USD', text)
        text = re.sub(r'(?<!\$)(\d{1,4})\s*to\s*(\d{1,4})(?!\s*USD)', r'$\1 to $\2 USD', text)
        text = re.sub(r'(USD\s*)USD', r'USD', text)  # Fix double USD
        return text

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=700
        )

        result = response.choices[0].message.content.strip()
        result = fix_price_formatting(result)

        st.markdown("---")
        st.text(result)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

else:
    st.info("Upload one or more photos above to get started!")
