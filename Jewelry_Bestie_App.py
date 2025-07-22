import streamlit as st
from PIL import Image, ExifTags, UnidentifiedImageError
import io

st.set_page_config(page_title="Jewelry Bestie - AI Jewelry Identifier", layout="centered")
st.title("Jewelry Bestie")
st.caption("Your AI powered best friend for identifying, pricing, and describing jewelry.")

if "report_history" not in st.session_state:
    st.session_state.report_history = []
if "current_images" not in st.session_state:
    st.session_state.current_images = []
if "generate_report" not in st.session_state:
    st.session_state.generate_report = False
if "reset" not in st.session_state:
    st.session_state.reset = False

def correct_image_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())
        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    except Exception:
        pass
    return image

if not st.session_state.generate_report:
    st.markdown("Upload up to 20 photos of your jewelry for AI powered identification results.")
    uploaded_files = st.file_uploader("Upload photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        st.session_state.current_images = uploaded_files

    st.button("Generate Jewelry Report", key="generate_button")

    if st.session_state.current_images and st.session_state.generate_report == False:
        if st.button("Click to Generate Report"):
            st.session_state.generate_report = True
            st.session_state.reset = False

if st.session_state.generate_report:
    report_images = []
    for uploaded_file in st.session_state.current_images:
        image = Image.open(uploaded_file)
        image = correct_image_orientation(image)
        st.image(image, caption="Uploaded Jewelry Image", use_container_width=True)
        report_images.append(uploaded_file.name)

    try:
        # Simulated AI response (to be replaced with actual model/API call)
        jewelry_type = "Brooch and Earrings Set"
        materials = "Enamel, metal"
        era_style = "1960s, Mod"
        description = (
            "This set features a bold floral design with red, white, and blue enamel petals, "
            "reminiscent of the 1960s mod style. The brooch and matching earrings both have a vibrant, symmetrical "
            "pattern with a glossy finish. The items appear to be in good vintage condition with no visible signs of significant wear."
        )
        price_min, price_max = 50, 80

        report_data = {
            "images": report_images,
            "Jewelry Type": jewelry_type,
            "Materials": materials,
            "Estimated Era or Style": era_style,
            "Detailed Description": description,
            "Estimated Resale Value Range": f"\${price_min}–\${price_max} USD"
        }

        st.session_state.report_history.insert(0, report_data)

        st.markdown("---")
        st.markdown(f"**Jewelry Type:** {jewelry_type}")
        st.markdown(f"**Materials:** {materials}")
        st.markdown(f"**Estimated Era or Style:** {era_style}")
        st.markdown(f"**Detailed Description:** {description}")
        st.markdown(f"**Estimated Resale Value Range:** \${price_min}–\${price_max} USD")

        if st.button("Start New Report"):
            st.session_state.generate_report = False
            st.session_state.current_images = []
            st.session_state.reset = True

    except UnidentifiedImageError:
        st.error("The uploaded file could not be identified as an image. Please upload a valid image file.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

if st.session_state.report_history:
    st.markdown("---")
    st.subheader("Previous Reports")
    for idx, report in enumerate(st.session_state.report_history):
        with st.expander(f"Report {idx + 1}"):
            for key, value in report.items():
                if key == "images":
                    for image_name in value:
                        st.text(f"Image: {image_name}")
                else:
                    if key == "Estimated Resale Value Range":
                        st.markdown(f"**{key}:** {value}")
                    else:
                        st.markdown(f"**{key}:** {value}")
