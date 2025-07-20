import streamlit as st
import openai
import base64
from PIL import Image
from datetime import datetime

# Set OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit page config
st.set_page_config(page_title="Jewelry Bestie", page_icon="💎")
st.title("💎 Jewelry Bestie")
st.write("Your AI-powered best friend for identifying, pricing, and describing jewelry.")

# Initialize session state
if 'report_history' not in st.session_state:
    st.session_state.report_history = []
if 'clear_fields' not in st.session_state:
    st.session_state.clear_fields = False
if 'new_report' not in st.session_state:
    st.session_state.new_report = False
if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")

# Upload UI
if not st.session_state.clear_fields:
    uploaded_files = st.file_uploader("Upload one or more photos of your jewelry piece:", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f'file_uploader_{st.session_state.session_id}')
    jewelry_type = st.selectbox("Optional: Select the type of jewelry (if known):", ["", "Earrings", "Ring", "Bracelet", "Brooch", "Pendant", "Necklace", "Set (e.g., Brooch and Earrings)"], key=f'type_selector_{st.session_state.session_id}')
    user_notes = st.text_area("Optional: Add any notes about the piece (e.g., markings, brand name, where it was purchased, etc.):", key=f'notes_area_{st.session_state.session_id}')

    if st.button("✨ Generate Jewelry Report"):
        if uploaded_files:
            images_base64 = []
            for uploaded_file in uploaded_files:
                bytes_data = uploaded_file.read()
                encoded = base64.b64encode(bytes_data).decode('utf-8')
                images_base64.append(encoded)

            prompt = f"""You are a jewelry expert helping a reseller identify and describe pieces. Analyze the image and return a detailed report using this format:

**Jewelry Type:** (e.g., Brooch, Ring, Necklace, etc.)  
**Materials:** (e.g., enamel, rhinestones, silver tone, plastic, etc.)  
**Estimated Era or Style:** (e.g., Mid-century, Art Deco, 1980s, etc.)  
**Detailed Description:** (2-3 sentences describing the design, color, shape, and condition)  
**Estimated Resale Value Range:** (format like **\$30–\$60 USD** with correct bold styling and currency symbols)

Use this input for context if helpful:
Jewelry Type: {jewelry_type}  
Notes: {user_notes}"""

            try:
                with st.spinner("Analyzing your jewelry with AI magic..."):
                    response = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                *[
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}
                                    for img in images_base64
                                ]
                            ]}
                        ],
                        max_tokens=1500
                    )
                    report_text = response.choices[0].message.content
            except Exception as e:
                report_text = f"Error generating report: {e}"

            st.session_state.report_history.append({
                "images": uploaded_files,
                "type": jewelry_type,
                "notes": user_notes,
                "report": report_text
            })
            st.session_state.clear_fields = False
            st.session_state.new_report = True
            st.rerun()

# Display last report
if st.session_state.report_history:
    st.markdown("## 📄 Jewelry Report")
    last_report = st.session_state.report_history[-1]
    for image in last_report["images"]:
        st.image(image, caption="Uploaded Jewelry Image", use_container_width=True)
    st.markdown("---")
    st.markdown(last_report.get("report", "No report available.").replace("$", "\$"))

    with st.expander("📋 Copy report for eBay or Etsy"):
        st.code(last_report.get("report", "").replace("$", "\$"), language='markdown')

    if st.button("Start New Report"):
        st.session_state.clear_fields = True
        st.session_state.new_report = True
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.rerun()

    if len(st.session_state.report_history) > 1:
        st.markdown("## 🔍 Past Reports")
        for i, report in enumerate(reversed(st.session_state.report_history[:-1])):
            st.markdown(f"### Report #{len(st.session_state.report_history) - i - 1}")
            for image in report["images"]:
                st.image(image, caption="Uploaded Jewelry Image", use_container_width=True)
            st.markdown(report.get("report", "No report available.").replace("$", "\$"))
            st.markdown("---")

# Scroll to top
if st.session_state.new_report:
    st.markdown("""
        <script>
        window.scrollTo({top: 0, behavior: 'smooth'});
        </script>
    """, unsafe_allow_html=True)
    st.session_state.new_report = False
