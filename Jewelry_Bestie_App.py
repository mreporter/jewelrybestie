import streamlit as st
import openai
import base64
from PIL import Image
import io
import os
import re
from datetime import datetime

# Use the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Jewelry Bestie", page_icon="💎")
st.title("💎 Jewelry Bestie")
st.write("Your AI-powered best friend for identifying, pricing, and describing jewelry.")

# Allow multiple image uploads
uploaded_files = st.file_uploader("Upload one or more photos of your jewelry piece:", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Optional user input for additional context
user_notes = st.text_area("Optional: Add any notes about the piece (e.g., markings, brand name, where it was purchased, etc.):")

if uploaded_files:
    images_base64 = []

    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode()
        images_base64.append(img_b64)

    st.markdown("---")
    st.write("Analyzing your jewelry pieces with AI magic...")

    image_inputs = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img}"}
        } for img in images_base64
    ]

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are a seasoned expert in vintage and antique jewelry appraisal. Carefully examine the uploaded images and provide a professional-level report using this structure:\n"
                        "Type: [Select from: earrings, ring, bracelet, brooch, pendant, necklace]\n"
                        "Style and Era: [e.g., Art Deco, Mid-century, Victorian, 1950s, etc.]\n"
                        "Materials: [e.g., silver-tone metal, rhinestones, lucite, bakelite, etc.]\n"
                        "Details: Describe in depth the design elements (e.g., filigree, repoussé, carved motifs), clasp types, settings (e.g., prong, bezel), backing (e.g., screw back, post), known or suspected brands or makers, markings, engraving, provenance, and the condition including wear, tarnish, or restoration signs. Use expert-level language and if possible, draw comparisons to similar iconic pieces, brands, or time periods.\n"
                        "Estimated Resale Price: [e.g., $25 to $40 USD — based on sales trends on eBay, Etsy, and Ruby Lane]\n\n"
                        f"Additional Notes from User: {user_notes}\n\n"
                        "Ensure your language is rich, confident, and filled with expertise. Include historical references when applicable. If unsure, explain what limits your confidence. Output in plain text only."
                    )
                },
                *image_inputs
            ]
        }
    ]

    def fix_price_formatting(text):
        match = re.search(r'Estimated Resale Price:\s*\$?(\d{1,5})\s*(?:to|-)?\s*\$?(\d{1,5})', text)
        if match:
            low, high = sorted([int(match.group(1)), int(match.group(2))])
            formatted_price = f"Estimated Resale Price: ${low} to ${high} USD"
            text = re.sub(r'Estimated Resale Price:.*', formatted_price, text)
        return text

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000
        )

        result = response.choices[0].message.content.strip()
        result = fix_price_formatting(result)

        st.markdown("---")
        st.text(result)

        st.download_button(
            label="📀 Download Report",
            data=result,
            file_name="jewelry_report.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

else:
    st.info("Upload one or more photos above to get started!")
