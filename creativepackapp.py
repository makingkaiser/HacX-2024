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

def display_images_from_directory(directory, caption, num_columns=3):
    """Display images from a specified directory."""
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

def main():
    st.title("Drug Prevention Educational Material Generator")

    # Display the cute octopus image
    octopus_image = download_image("https://img.freepik.com/premium-vector/illustration-cute-cartoon-octopus-character-with-paint-bucket-brush_1151-69783.jpg")
    st.image(octopus_image, caption="Meet our helper, the creative octopus!")

    # Inputs for the generation process
    target_audience = st.text_input("Target Audience", "early teens still in school")
    stylistic_description = st.text_input("Artistic Style", "cartoonish, colorful and engaging")
    content_description = st.text_area("Content Description", "Understanding the effects of cannabis on growing up")

    if st.button("Generate Background, Slogans, and Cards"):
        with st.spinner('Generating Background, Slogans, and Cards...'):
            for i in range(3):
                result = asyncio.run(generate_and_display_images(target_audience, stylistic_description, content_description))
            if result:
                st.success("Images have been generated and are being displayed below.")
                st.session_state['images_generated'] = True

    if 'images_generated' in st.session_state and st.session_state['images_generated']:
        # Displaying generated images in a structured format
        display_images_from_directory("C:\\Users\\nicho\\OneDrive\\Desktop\\HacX-2024\\generated_images\\bgs", "Generated Background Images")
        display_images_from_directory("C:\\Users\\nicho\\OneDrive\\Desktop\\HacX-2024\\generated_images\\slogans", "Generated Slogan Images")
        display_images_from_directory("C:\\Users\\nicho\\OneDrive\\Desktop\\HacX-2024\\generated_images\\cards", "Generated Card Images")

        # User input for statistics
        further_input = st.text_input("Support your creation with statistics! What kind of statistics should we find?", placeholder="Enter statistics separated by commas")
        if further_input:
            further_input = "17% increase in cannabis users arrested, Cannabis makes up 19% of new drug abusers arrested in 2023, 64% of cannabis users below the age of 30"
            statistics = [stat.strip() for stat in further_input.split(',')]

            generate_stats = st.button("Generate Visual Aids and Graphs for Statistics")
            if generate_stats:
                with st.spinner('Generating visual aids and graphs...'):
                    asyncio.run(refine_and_generate_points(target_audience, stylistic_description, content_description, statistics))
                st.success("Visual aids and graphs have been generated for the provided statistics.")

                # Display corresponding visuals for each statistic
                for stat in statistics:
                    with st.container():
                        st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:10px;'>\
                            <h4 style='color:#333;'>{stat}</h4></div>", unsafe_allow_html=True)
                        vector_images = list_sorted_images("C:\\Users\\nicho\\OneDrive\\Desktop\\HacX-2024\\generated_images\\vectors")
                        visualaid_images = list_sorted_images("C:\\Users\\nicho\\OneDrive\\Desktop\\HacX-2024\\generated_images\\visualaids")
                        if vector_images and visualaid_images:
                            cols = st.columns(3)
                            index = statistics.index(stat)
                            cols[0].image(vector_images[index % len(vector_images)], caption="Vector Image", use_column_width=True)
                            cols[1].image(visualaid_images[index % len(visualaid_images)], caption="Visual Aid", use_column_width=True)
                            graph_images = list_sorted_images("C:\\Users\\nicho\\OneDrive\\Desktop\\HacX-2024\\generated_images\\graphs")
                            if index < len(graph_images):  # Check to avoid index out of range error
                                cols[2].image(graph_images[index], caption="Retrieved Graph", use_column_width=True)
                            else:
                                cols[2].write("")  # Placeholder text when no graph image is available

if __name__ == "__main__":
    main()


