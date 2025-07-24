import streamlit as st
from PIL import Image
import openai
import os
import io

# Set Streamlit page config
st.set_page_config(page_title="Jewelry Bestie AI", layout="centered")

st.title("💎 Jewelry Bestie AI")
st.markdown("Upload a photo of your jewelry and get help identifying, describing, pricing, and organizing it — just like your AI best friend would help you do!")

# Upload image
uploaded_file = st.file_uploader("Upload a jewelry photo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Jewelry Image", use_column_width=True)

    # Get additional inputs from user
    condition = st.selectbox("What's the condition?", ["Excellent", "Good", "Fair", "Poor"])
    include_price = st.checkbox("Include resale price suggestion")
    include_description = st.checkbox("Include detailed product description")
    include_keywords = st.checkbox("Include SEO keywords")

    # Submit button
    if st.button("Analyze Jewelry"):
        with st.spinner("Analyzing your jewelry..."):
            # Convert image to base64 string for OpenAI
            img_bytes = uploaded_file.read()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

            openai.api_key = st.secrets["OPENAI_API_KEY"]

            # Build GPT-4o prompt with image
            messages = [
                {
                    "role": "system",
                    "content": "You are a jewelry appraiser and reseller's virtual assistant. Analyze the jewelry image, give a name/title, estimate the resale value range, and format the output clearly for resale listings."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Here is a piece of jewelry. It's in {condition} condition. Please help me identify it."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ]

            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000
            )

            result = response.choices[0].message.content

            st.markdown("---")
            st.subheader("📝 Jewelry Report")
            st.markdown(result)

            # Save output to downloadable .txt file
            output_name = uploaded_file.name.replace(".jpg", "").replace(".jpeg", "").replace(".png", "")
            output_filename = f"{output_name}_jewelry_report.txt"
            st.download_button("📄 Download Report", result, file_name=output_filename, mime="text/plain")
