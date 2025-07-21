import streamlit as st
from PIL import Image, ExifTags, UnidentifiedImageError
import io

st.set_page_config(page_title="Jewelry Bestie - AI Jewelry Identifier", layout="centered")
st.title("Jewelry Bestie")
st.caption("Your AI powered best friend for identifying, pricing, and describing jewelry.")

uploaded_file = st.file_uploader("Upload a photo of the jewelry", type=["jpg", "jpeg", "png"])

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

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        image = correct_image_orientation(image)
        st.image(image, caption="Uploaded Jewelry Image", use_container_width=True)

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

        st.markdown("---")
        st.markdown(f"**Jewelry Type:** {jewelry_type}")
        st.markdown(f"**Materials:** {materials}")
        st.markdown(f"**Estimated Era or Style:** {era_style}")
        st.markdown(f"**Detailed Description:** {description}")
        st.markdown(f"**Estimated Resale Value Range:** \${price_min}–\${price_max} USD")

    except UnidentifiedImageError:
        st.error("The uploaded file could not be identified as an image. Please upload a valid image file.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

st.markdown("---")
st.button("Start New Report")
