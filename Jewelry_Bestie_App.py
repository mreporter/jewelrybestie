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
                        "You are a vintage jewelry identification expert. Based on these images, provide a detailed report using this structure:\n"
                        "Type: [one of: earrings, ring, bracelet, brooch, pendant, necklace]\n"
                        "Style and Era: [e.g., Art Deco, Mid-century, 1950s, etc.]\n"
                        "Materials: [list of metals, stones, finishes, etc.]\n"
                        "Details: [what makes this piece unique – motifs, settings, design traits, maker’s marks, hallmarks, etc.]\n"
                        "Estimated Resale Price: [formatted as: $XX to $XX USD]\n\n"
                        "Be thorough but concise. Base your estimates on typical resale platforms (eBay, Etsy, Ruby Lane). Output should be plain text, no markdown or emojis."
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
            max_tokens=700
        )

        result = response.choices[0].message.content.strip()
        result = fix_price_formatting(result)

        st.markdown("---")
        st.text(result)

        st.download_button(
            label="💾 Download Report",
            data=result,
            file_name="jewelry_report.txt",
            mime="text/plain"
        )

        if 'history' not in st.session_state:
            st.session_state['history'] = []

        st.session_state['history'].append(result)

        if st.session_state['history']:
            st.markdown("### 📜 Previous Reports")
            for i, r in enumerate(st.session_state['history'][::-1], 1):
                st.text(f"Report #{i}\n{r}\n")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

else:
    st.info("Upload one or more photos above to get started!")
