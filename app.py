import streamlit as st
import openai
import requests
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image
import random
import string

# Streamlit UI Setup
st.set_page_config(page_title="DALL·E 3 Image Generator", layout="wide")

st.title("🖼️ DALL·E 3 Image Generator")

# Sidebar Settings
st.sidebar.header("⚙️ Settings")

# API Key Input
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
if not api_key:
    st.warning("Enter your OpenAI API key to continue.")
    st.stop()

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

# Image Settings
size_options = {
    "Square (1024x1024)": "1024x1024",
    "Wide (1792x1024)": "1792x1024",
    "Tall (1024x1792)": "1024x1792"
}
quality_options = ["Standard", "HD"]

size = st.sidebar.selectbox("Select Image Size", list(size_options.keys()))
quality = st.sidebar.radio("Select Quality", quality_options, horizontal=True)

# Function to generate a unique filename
def generate_filename():
    current_time = datetime.now().strftime('%Y%m%d-%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_letters, k=3))
    return f"{current_time}-{random_suffix}.jpg"

# Main Input
prompt = st.text_area("Enter a prompt for DALL·E 3:")

if st.button("🎨 Generate Image"):
    if prompt:
        try:
            # Call OpenAI API to generate image
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size=size_options[size],
                quality=quality.lower()  # "standard" or "hd"
            )
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt if hasattr(response.data[0], "revised_prompt") else prompt

            # Download and display the image
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))
            st.image(image, caption="🖼️ Generated Image", use_column_width=True)

            # Display revised prompt if it was modified
            if revised_prompt != prompt:
                st.info(f"**Revised Prompt:** {revised_prompt}")

            # Save the image as a downloadable file
            filename = generate_filename()
            img_path = Path(filename)
            image.save(img_path)

            with open(img_path, "rb") as file:
                st.download_button(
                    label="⬇️ Download Image",
                    data=file,
                    file_name=filename,
                    mime="image/jpeg"
                )
        except Exception as e:
            st.error(f"🚨 Error: {e}")
    else:
        st.warning("⚠️ Please enter a prompt.")

st.write("🔗 Powered by OpenAI DALL·E 3")
