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
                        "Also describe the style, era, and estimated resale price. "
                        "Provide the resale price in USD as a realistic range based on sold comps from eBay or Etsy within the last year. "
                        "Assume the item is in good, wearable condition. Factor in design, craftsmanship, and materials such as silver-tone vs sterling. "
                        "If the item looks designer-signed, branded, or handmade, price it on the higher end. If it looks like generic costume jewelry, price it on the lower end. "
                        "If it's a known collectible brand, mention that too. Format the price range using this exact format: \"$XX to $XX USD\" — always with a space before and after 'to', a dollar sign before both numbers, and 'USD' at the end. Do NOT merge the numbers (e.g., NEVER write '30to100' or '$30to$100'). Always include both dollar signs and always use numerals (e.g., '$25 to $75 USD', NOT 'twenty-five to seventy-five'). This format is REQUIRED."
                        "Always output the full report using this exact structure with headers: \n\n"
                        "**Style and Era**\n\n[Your output here]\n\n**Materials**\n\n[Your output here]\n\n**Estimated Resale Price**\n\n[Your output here including the price range like '$30 to $100 USD']"
                    )
                },
                *image_inputs
            ]
        }
    ]

    # Function to fix bad price formatting
    def fix_price_formatting(text):
        pattern1 = re.compile(r'\b(\d{1,3})\s*to\s*(\d{1,3})\b(?!\s*USD)', re.IGNORECASE)
        text = pattern1.sub(r'$\1 to $\2 USD', text)

        pattern2 = re.compile(r'\b(\d{1,3})to(\d{1,3})\s*(usd|USD)\b', re.IGNORECASE)
        text = pattern2.sub(r'$\1 to $\2 USD', text)

        pattern3 = re.compile(r'\$(\d{1,3})\s*to\s*\$?(\d{1,3})\b(?!\s*USD)', re.IGNORECASE)
        text = pattern3.sub(r'$\1 to $\2 USD', text)

        pattern4 = re.compile(r'(?<!\$)(\d{1,3})to(\d{1,3})(?!\s*USD)', re.IGNORECASE)
        text = pattern4.sub(r'$\1 to $\2 USD', text)

        return text

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=700
        )

        result = response.choices[0].message.content
        result = fix_price_formatting(result)  # Fix price formatting before display

        st.markdown("---")
        st.subheader("📋 Jewelry Bestie's Report")
        st.markdown(result)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

else:
    st.info("Upload one or more photos above to get started!")
