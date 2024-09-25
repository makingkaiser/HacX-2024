import streamlit as st
import os 
import requests
import asyncio
from htmlgeneratorfunc import generate_html_content
from main import flesh_out_html_images, flesh_out_html_text
from extractors import extract_text_descriptions
from regenpipeline import regenerate_image, regenerate_text, replace_image_descriptions, replace_text_descriptions, extract_image_links
from azure.storage.blob import BlobServiceClient

st.set_page_config(layout="wide", page_title="Preventative Drug Education Generator", page_icon=":octopus:")

@st.fragment
def load_css():
    return """
    <style>
        .big-font {
            font-size:18px !important;
        }
        .stButton>button {
            width: 100%;
            border-radius: 20px;
            background-color: #0C9;
            color: white;
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border-radius: 15px;
            padding: 15px;
            width: calc(100% + 30px);  // Making input area wider
        }
        .stMarkdown {
            margin-top: -20px;
        }
        .container {
            padding: 5px;
        }
    </style>
    """

@st.fragment
def image_carousel(image_urls):
    if not image_urls:
        return

    current_image_index = st.session_state.get('img_index', 0)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous"):
            if current_image_index > 0:
                current_image_index -= 1
                st.session_state.img_index = current_image_index
    with col2:
        st.image(image_urls[current_image_index], caption=f"Image {current_image_index + 1} of {len(image_urls)}", use_column_width=True)
    with col3:
        if st.button("Next"):
            if current_image_index < len(image_urls) - 1:
                current_image_index += 1
                st.session_state.img_index = current_image_index

async def generate_content(target_audience, stylistic_description, content_description, format):
    html_content = await generate_html_content(
        target_audience=target_audience,
        stylistic_description=stylistic_description,
        content_description=content_description,
        format=format
    )
    
    fleshed_out_html, image_titles = await flesh_out_html_images(
        html_content,
        target_audience=target_audience,
        stylistic_description=stylistic_description,
        content_description=content_description,
        format=format
    )
    
    fleshed_out_html = await flesh_out_html_text(
        fleshed_out_html,
        target_audience=target_audience,
        content_description=content_description,
        format=format
    )
    
    return fleshed_out_html, image_titles

def get_image_urls(image_titles):
    github_img_base = "https://raw.githubusercontent.com/makingkaiser/HacX-2024/merge-nic-changes/data-ingress/images/source_images/"
    possible_extensions = ['.PNG', '.jpg', '.jpeg']
    image_urls = []

    for title in image_titles:
        title = title.replace('_caption', '')
        for ext in possible_extensions:
            image_url = f"{github_img_base}{title}{ext}"
            response = requests.head(image_url)
            if response.status_code == 200:
                image_urls.append(image_url)
                break
    
    return image_urls

async def main():
    st.markdown(load_css(), unsafe_allow_html=True)
    
    st.title("Preventive Drug Education Material Generator")
    st.image("https://img.freepik.com/premium-vector/cute-octopus-artist-painting-cartoon-vector-icon-illustration-animal-education-icon-isolated-flat_138676-6683.jpg?w=360")



    # Initialize session state
    if 'image_urls' not in st.session_state:
        st.session_state.image_urls = []
    if "placeholder_html_content" not in st.session_state:
        st.session_state.placeholder_html_content = None
    if "fleshed_out_html_content" not in st.session_state:
        st.session_state.fleshed_out_html_content = None
    if "text_elements_before_regeneration" not in st.session_state:
        st.session_state.text_elements_before_regeneration = None
    if "image_elements_before_regeneration" not in st.session_state:
        st.session_state.image_elements_before_regeneration = None
    if "selected_component" not in st.session_state:
        st.session_state.selected_component = None
    if "image_input" not in st.session_state:
        st.session_state.image_input = ""
    if "text_input" not in st.session_state:
        st.session_state.text_input = ""
    if "regenerate_clicked" not in st.session_state:
        st.session_state.regenerate_clicked = False
    if "component_ready_to_submit" not in st.session_state:
        st.session_state.component_ready_to_submit = False

    # Sidebar for input
    with st.sidebar:
        st.write("## Generator Settings")
        st.markdown("### Fill out the details below:")
        target_audience = st.text_input("Target Audience", "Type here, e.g.: general audience")
        stylistic_description = st.text_input("Stylistic Description", "Type here, e.g.: 90's cartoon style")
        content_description = st.text_input("Content Description", "Type here, e.g.: various scenes")
        format = st.text_input("Format", "Type here, e.g.: pamphlet")

    with st.container():
        st.markdown("### Your Generated Content")
        st.write("Use the form on the left to generate content. Once you're ready, click the button below.")
        
        if st.button("Generate!"):
            if not target_audience or not stylistic_description or not content_description or not format:
                st.error("All fields must be filled out before submitting.")
            else:
                with st.spinner("Alright! Let Inky give this a shot!"):
                    html_content = await generate_html_content(
                        target_audience=target_audience,
                        stylistic_description=stylistic_description,
                        content_description=content_description,
                        format=format
                    )
                    st.success("Inky came up with an idea!")
                    st.session_state.placeholder_html_content = html_content

                
                with st.spinner("Inky is finding images.. please wait"):
                    fleshed_out_html, image_titles, refined_image_elements = await flesh_out_html_images(
                        html_content,
                        target_audience=target_audience,
                        stylistic_description=stylistic_description,
                        content_description=content_description,
                        format=format
                    )
                    image_titles = [title.replace('_caption', '') for title in image_titles]
                    st.session_state.image_elements_before_regeneration = refined_image_elements
                    
                st.success("Inky found some inspiration from these images! Let's use these to guide our generation!")

                github_img_base = "https://raw.githubusercontent.com/makingkaiser/HacX-2024/merge-nic-changes/data-ingress/images/source_images/"
                possible_extensions = ['.PNG', '.jpg', '.jpeg']
                image_urls = []

                for title in image_titles:
                    for ext in possible_extensions:
                        image_url = f"{github_img_base}{title}{ext}"
                        response = requests.head(image_url)
                        if response.status_code == 200:
                            image_urls.append(image_url)
                            break

                image_carousel(image_urls)

                st.success("Okay! Inky is done generating images!")

                with st.spinner("Inky is writing text... just a little more..."):
                    fleshed_out_html, refined_text_elements = await flesh_out_html_text(
                        fleshed_out_html,
                        target_audience=target_audience,
                        content_description=content_description,
                        format=format
                    )
                    st.success("Inky is done! Have a look at what Inky made and let Inky know if any parts need to be regenerated!")
                    st.session_state.fleshed_out_html_content = fleshed_out_html
                    st.session_state.text_elements_before_regeneration = refined_text_elements

        # Main content area
        if st.session_state.fleshed_out_html_content:
            st.markdown("---")
            st.fragment("Generated content")
            image_carousel(st.session_state.image_urls)
            st.html(st.session_state.fleshed_out_html_content)

            # Regeneration section
            if st.button("Regenerate"):
                st.session_state.regenerate_clicked = True
                st.session_state.selected_component = None

        if st.session_state.regenerate_clicked and st.session_state.fleshed_out_html_content:
            st.subheader("Select a component to regenerate")
            
            image_elements = st.session_state.image_elements_before_regeneration
            text_elements = st.session_state.text_elements_before_regeneration

            # Display image components
            for i, image_element in enumerate(image_elements):
                st.image(image_element.content, caption=f"{image_element.description[:60]}...", use_column_width=True)
                if st.button(f"Select Image {i+1} for regeneration", key=f"select_img_{i}"):
                    st.session_state.selected_component = ('image', i)

            # Display text components
            for i, text_element in enumerate(text_elements):
                st.html(text_element.refined)
                if st.button(f"Select Text {i+1} for regeneration", key=f"select_text_{i}"):
                    st.session_state.selected_component = ('text', i)

            # Refinement input logic once a component is selected
            if st.session_state.selected_component:
                component_type, index = st.session_state.selected_component

                # Handle image refinement
                if component_type == "image" and index < len(image_elements):
                    image_element = image_elements[index]
                    st.session_state.image_input = st.text_input(
                        "How would you like to refine the image?", 
                        value=st.session_state.image_input
                    )
                    if st.button("Submit"):
                        st.session_state.component_ready_to_submit = True

                    
                # Handle text refinement
                elif component_type == "text" and index < len(text_elements):
                    text_element = text_elements[index]
                    st.session_state.text_input = st.text_input(
                        "How would you like to refine the text?", 
                        value=st.session_state.text_input
                    )
                    if st.button("Submit"):
                        st.session_state.component_ready_to_submit = True
                    
            # After submission, regenerate the selected component
            if st.session_state.component_ready_to_submit:
                st.subheader("Regenerating component...")
                with st.spinner("Inky is regenerating..."):
                    component_type, index = st.session_state.selected_component

                    # Regenerate the image
                    if component_type == "image":
                        regenerated_image_element = await regenerate_image(
                            st.session_state.image_input, 
                            image_elements[index]
                        )
                        st.image(regenerated_image_element.content, caption=regenerated_image_element.refined, use_column_width=True)
                        image_elements[index] = regenerated_image_element
                        updated_html = replace_image_descriptions(st.session_state.placeholder_html_content, image_elements)
                        updated_html = replace_text_descriptions(updated_html, text_elements)

                    
                    # Regenerate the text
                    elif component_type == "text":
                        regenerated_text_element = await regenerate_text(
                            st.session_state.text_input, 
                            text_elements[index]
                        )
                        st.html(regenerated_text_element.refined)
                        # text_elements is the list of text elements that is shown to user during first iteration
                        # replace (in the list) the element that user wants to refine with the regenerated text element
                        # replace the final list of elements back to the placeholder html
                        text_elements[index] = regenerated_text_element
                        updated_html = replace_text_descriptions(st.session_state.placeholder_html_content, text_elements)
                        updated_html = replace_image_descriptions(updated_html, image_elements)

                    # Update the session state with regenerated content
                    st.success("Components regenerated!")
                    st.session_state.fleshed_out_html_content = updated_html
                    st.markdown("---")
                    st.html(st.session_state.fleshed_out_html_content)
                    st.session_state.component_ready_to_submit = False  # Reset after regeneration
                    
                
if __name__ == "__main__":
    asyncio.run(main())
