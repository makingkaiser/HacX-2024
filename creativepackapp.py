# import streamlit as st
# import os
# from PIL import Image
# from dotenv import load_dotenv
# from detectandboundingbox import initialize_model, process_images_background, process_images_vector_collection
# from graphicpipelinegeneration import expand_flux_prompts, multiple_image_prediction
# from assemble import load_metadata, list_vector_images, get_placement_decision, overlay_images

# # Load environment variables
# load_dotenv()

# # Initialize model and device once to avoid overhead
# model, device = initialize_model()

# # Function to generate images
# def generate_images(target_audience, stylistic_description, content_description):
#     st.write("Generating images, please wait...")
#     prompts = expand_flux_prompts(target_audience, stylistic_description, content_description)
#     multiple_image_prediction(prompts)
#     st.success("Images have been generated. Ready to segment.")
#     st.session_state['rerun_needed'] = True

# # Function to process segmentation
# def segment_images():
#     image_dir = './generated_images'
#     if not os.path.exists(image_dir):
#         st.error("Image directory not found.")
#         return

#     for file_name in os.listdir(image_dir):
#         file_path = os.path.join(image_dir, file_name)
#         if 'background' in file_name:
#             process_images_background(model, file_path, device)
#             st.write(f"Processed background image: {file_name}")
#         elif 'vector' in file_name:
#             process_images_vector_collection(model, file_path, device)
#             st.write(f"Processed vector image: {file_name}")

#     st.session_state['segmentation_done'] = True
#     if st.session_state.get('rerun_needed'):
#         st.experimental_rerun()

# # Streamlit interface setup
# st.title('Image Generation and Segmentation for Drug Prevention Campaigns')

# with st.form("my_form"):
#     target_audience = st.text_input("Target Audience", "Youth")
#     stylistic_description = st.text_input("Stylistic Description", "Colorful and Dynamic")
#     content_description = st.text_input("Content Description", "Promote Positive Lifestyle Choices")
#     submit_gen = st.form_submit_button("Generate Images")

# if submit_gen:
#     generate_images(target_audience, stylistic_description, content_description)

# # Button to start segmentation
# if st.button('Start Image Processing'):
#     segment_images()

# # Display generated and segmented images if available and segmentation is done
# if 'segmentation_done' in st.session_state and st.session_state['segmentation_done']:
#     st.header("Generated Images")
#     generated_images_dir = './generated_images'
#     if os.path.exists(generated_images_dir):
#         files = os.listdir(generated_images_dir)
#         for file in files:
#             file_path = os.path.join(generated_images_dir, file)
#             if file.lower().endswith(('.png', '.jpg', '.jpeg')):
#                 st.image(file_path, caption=file, use_column_width=True)
#                 with open(file_path, "rb") as image_file:
#                     st.download_button(
#                         label="Download Image",
#                         data=image_file,
#                         file_name=file,
#                         mime="image/png"
#                     )

# # Async function to overlay images using metadata
# async def compose_and_display_images():
#     metadata_path = './generated_images/metadata.json'
#     vector_images_path = './generated_images/segmented_vector_images'
#     background_image_path = './generated_images/background.png'

#     metadata = load_metadata(metadata_path)
#     vector_images = list_vector_images(vector_images_path)
#     placement_decision = await get_placement_decision(metadata, vector_images)
#     result_image_path = overlay_images(background_image_path, placement_decision, vector_images_path)
#     st.image(result_image_path, caption="Composed Image", use_column_width=True)

# if st.button('Compose and Display Images'):
#     st.write("Composing images, please wait...")
#     st.session_state['compose_task'] = st.asyncio_loop.run_until_complete(compose_and_display_images())

import os
import asyncio
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from creativepackuserinputparse import refine_and_generate_main, refine_and_generate_points
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ensures absolute path resolution
GENERATED_IMAGES_DIR = os.path.join(BASE_DIR, 'generated_images')  # Path to the generated images directory

def ensure_directories_exist():
    """Ensure that all necessary directories exist."""
    os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)
    os.makedirs(os.path.join(GENERATED_IMAGES_DIR, 'bgs'), exist_ok=True)
    os.makedirs(os.path.join(GENERATED_IMAGES_DIR, 'slogans'), exist_ok=True)
    os.makedirs(os.path.join(GENERATED_IMAGES_DIR, 'cards'), exist_ok=True)
    os.makedirs(os.path.join(GENERATED_IMAGES_DIR, 'vectors'), exist_ok=True)
    os.makedirs(os.path.join(GENERATED_IMAGES_DIR, 'visualaids'), exist_ok=True)
    os.makedirs(os.path.join(GENERATED_IMAGES_DIR, 'graphs'), exist_ok=True)

def download_image(url):
    """Helper function to download and display an image from a URL."""
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image

def list_sorted_images(directory):
    """List and sort image files in a directory based on the modification time."""
    if os.path.exists(directory):
        files = sorted(
            [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(('.png', '.jpg', '.jpeg'))],
            key=lambda x: os.path.getmtime(x)
        )
        return files
    return []

def display_images_from_directory(directory_name, caption, num_columns=3):
    """Display images from a specified directory."""
    directory = os.path.join(GENERATED_IMAGES_DIR, directory_name)
    files = list_sorted_images(directory)
    if files:
        st.write(caption)
        cols = st.columns(num_columns)
        for col, file in zip(cols, files):
            col.image(file, use_column_width=True, caption=os.path.basename(file))

async def generate_and_display_images(target_audience, stylistic_description, content_description):
    """Generate and display images asynchronously."""
    await refine_and_generate_main(target_audience, stylistic_description, content_description)
    return True

def load_css():
    return """
    <style>
    /* Navigation Bar */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 1000;
            display: flex;
            align-items: center;
            padding: 0 2rem;
        }

        /* Button Styles */
        .stButton > button, .generate-button {
            background: linear-gradient(90deg, #FF8C00, #FF8CFF);
            color: #121212;
            font-weight: 600;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 18px;
            transition: background 0.3s ease, color 0.3s ease;
            border: none;
            width: auto;
            min-width: 200px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover, .generate-button:hover {
            background: linear-gradient(90deg, #FF6C00, #FF6CFF);
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            cursor: pointer;
        }

        /* Input Fields */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea {
            border-radius: 10px;
            border: 2px solid #E5E7EB;
            padding: 12px 16px;
            font-size: 16px;
            transition: border-color 0.3s ease;
            background: #F9FAFB;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #FF8C00;
            box-shadow: 0 0 0 2px rgba(255,140,0,0.1);
        }

        /* Cards and Containers */
        .content-box {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
    </style>
    """

def main():
    st.set_page_config(layout="wide", page_title="Drug Prevention Educational Material Generator", page_icon=":octopus:")
    st.markdown(load_css(), unsafe_allow_html=True)



    # Sidebar for input parameters
    with st.sidebar:
        st.write("## Generator Settings")
        st.markdown("### Fill out the details below:")
        target_audience = st.text_input("Who is your target audience?", "early teens still in school")
        stylistic_description = st.text_input("What artistic style would you like?", "cartoonish, colorful and engaging")
        content_description = st.text_area("What's your content about?", "Understanding the effects of cannabis on growing up")

    # Main content area
    st.title("Drug Prevention Educational Material Generator")
    # octopus_image = download_image("https://img.freepik.com/premium-vector/illustration-cute-cartoon-octopus-character-with-paint-bucket-brush_1151-69783.jpg")
    octopus_image = Image.open("sticky.png")  # Load local image instead of downloading
    st.image(octopus_image, caption="Meet our helper, the creative octopus!", width=300)
    
    # Welcome message in a container
    with st.container():
        st.markdown("### Welcome to the Creative Hub!")
        st.write("""<div style="max-width: 850px; margin-left: 0 auto; margin-bottom: 100 auto;">
            Create impactful educational materials for drug prevention campaigns. Use the sidebar to customize your content, 
            and let's work together to make engaging and effective materials!
            </div>""", unsafe_allow_html=True)
        st.write("")
        st.write("")


    # Generation button with new styling
    if st.button("Generate Background, Slogans, and Cards ✨", key="generate_main"):
        with st.spinner('Generating materials...'):
            for i in range(3):
                result = asyncio.run(generate_and_display_images(target_audience, stylistic_description, content_description))
            if result:
                st.success("Materials have been generated successfully!")
                st.session_state['images_generated'] = True

    # Rest of your display logic with enhanced styling
    if 'images_generated' in st.session_state and st.session_state['images_generated']:
        st.markdown("### Generated Materials")
        
        # Display images in styled containers
        with st.container():
            display_images_from_directory("bgs", "Background Images")
            display_images_from_directory("slogans", "Campaign Slogans")
            display_images_from_directory("cards", "Information Cards")

        # Statistics input section
        st.markdown("### Add Supporting Statistics")
        further_input = st.text_input(
            "What statistics would you like to include?", 
            placeholder="Enter statistics separated by commas"
        )

        # Continue with your existing statistics processing logic...

if __name__ == "__main__":
    main()