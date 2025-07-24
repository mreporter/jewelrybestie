import streamlit as st
import openai
import os
from PIL import Image
import io
import base64

st.set_page_config(page_title="Jewelry Bestie AI", page_icon="💎", layout="centered")

st.title("💎 Jewelry Bestie AI")
st.write("Upload a photo of your jewelry and get help identifying, describing, pricing, and organizing it — just like your AI best friend would help you do!")

uploaded_file = st.file_uploader("Upload a jewelry photo", type=["jpg", "jpeg", "png"])

condition = st.selectbox("What's the condition?", ["Excellent", "Good", "Fair", "Poor"])
include_price = st.checkbox("Include resale price suggestion", value=True)
include_description = st.checkbox("Include detailed product description", value=True)
include_keywords = st.checkbox("Include SEO keywords", value=True)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Jewelry Image", use_column_width=True)

    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    prompt = f"""
    You are a jewelry identification expert. A user has uploaded a photo of a jewelry piece in {condition} condition. 
    Please provide the following:
    {'- A resale price suggestion based on current market trends.' if include_price else ''}
    {'- A detailed product description including material, style, and likely era.' if include_description else ''}
    {'- A list of relevant SEO keywords someone might use to search for this item online.' if include_keywords else ''}

    Use markdown formatting. Be concise, helpful, and specific.
    """

    if st.button("Analyze Jewelry"):
        with st.spinner("Analyzing your jewelry..."):
            try:
                openai.api_key = st.secrets["OPENAI_API_KEY"]

                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert in jewelry appraisal and description."},
                        {"role": "user", "content": prompt}
                    ]
                )

                output = response.choices[0].message.content
                st.markdown(output)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
