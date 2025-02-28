import streamlit as st
import openai
import requests
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image
import random
import string
import time

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
num_images = st.sidebar.slider("Number of Images", 1, 4, 1)  # Generate 1 to 4 images

# Image Inspiration Upload
st.sidebar.subheader("🖼️ Optional: Upload an Inspiration Image")
uploaded_image = st.sidebar.file_uploader("Upload an image (JPG, PNG)", type=["jpg", "jpeg", "png"])

# Function to generate a unique filename
def generate_filename(index):
    current_time = datetime.now().strftime('%Y%m%d-%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_letters, k=3))
    return f"{current_time}-{index}-{random_suffix}.jpg"

# Main Input
prompt = st.text_area("Enter a prompt for DALL·E 3:")

# State variables to store images and filenames
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
    st.session_state.image_filenames = []
    st.session_state.revised_prompt = None

if st.button("🎨 Generate Image(s)"):
    if prompt:
        try:
            # Clear previous images
            st.session_state.generated_images = []
            st.session_state.image_filenames = []

            # Convert uploaded image to bytes if provided
            image_bytes = None
            if uploaded_image:
                image = Image.open(uploaded_image)
                img_buffer = BytesIO()
                image.save(img_buffer, format="PNG")  # Convert to PNG format
                image_bytes = img_buffer.getvalue()

            # Generate images separately (DALL·E 3 requires n=1 per request)
            for i in range(num_images):
                with st.spinner(f"Generating Image {i+1}/{num_images}..."):
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        n=1,  # DALL·E 3 only allows n=1 per request
                        size=size_options[size],
                        quality=quality.lower(),  # "standard" or "hd"
                        image=image_bytes  # Include uploaded image if available
                    )
                    image_url = response.data[0].url
                    revised_prompt = response.data[0].revised_prompt if hasattr(response.data[0], "revised_prompt") else prompt

                    # Download the image
                    image_response = requests.get(image_url)
                    generated_image = Image.open(BytesIO(image_response.content))

                    # Store in session state
                    st.session_state.generated_images.append(generated_image)
                    st.session_state.image_filenames.append(generate_filename(i))

                    # Avoid hitting rate limits
                    time.sleep(1)

            # Store revised prompt
            st.session_state.revised_prompt = revised_prompt

        except Exception as e:
            st.error(f"🚨 Error: {e}")

# Display generated images (if available)
if st.session_state.generated_images:
    # Display revised prompt if modified
    if st.session_state.revised_prompt and st.session_state.revised_prompt != prompt:
        st.info(f"**Revised Prompt:** {st.session_state.revised_prompt}")

    # Layout for multiple images
    cols = st.columns(len(st.session_state.generated_images))  # Create dynamic columns

    for i, (generated_image, filename) in enumerate(zip(st.session_state.generated_images, st.session_state.image_filenames)):
        with cols[i]:  # Place each image in its respective column
            st.image(generated_image, caption=f"🖼️ Image {i+1}", use_container_width=True)

            # Save image for download
            with open(filename, "wb") as img_file:
                generated_image.save(img_file)

            # Download button for each image
            with open(filename, "rb") as file:
                st.download_button(
                    label=f"⬇️ Download Image {i+1}",
                    data=file,
                    file_name=filename,
                    mime="image/jpeg"
                )

st.write("🔗 Powered by OpenAI DALL·E 3")
