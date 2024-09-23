import streamlit as st
import os 
import requests
import asyncio
from htmlgeneratorfunc import generate_html_content
from main import flesh_out_html_images, flesh_out_html_text
from azure.storage.blob import BlobServiceClient

st.set_page_config(layout="wide", page_title="Preventive Drug Education Generator", page_icon=":octopus:")

@st.cache_data
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
        .stTextInput>div>div>input {
            border-radius: 10px;
            padding: 10px;
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
    with st.container():
        if not image_urls:
            st.write("No images to display.")
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

async def main():
    st.markdown(load_css(), unsafe_allow_html=True)
    
    st.title("Preventive Drug Education Material Generator")
    st.image("https://img.freepik.com/premium-vector/cute-octopus-artist-painting-cartoon-vector-icon-illustration-animal-education-icon-isolated-flat_138676-6683.jpg?w=360")

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
        
        if st.button("Write Content!"):
            if not target_audience or not stylistic_description or not content_description or not format:
                st.error("All fields must be filled out before submitting.")
            else:
                with st.spinner("Inky is thinking..."):
                    html_content = await generate_html_content(
                        target_audience=target_audience,
                        stylistic_description=stylistic_description,
                        content_description=content_description,
                        format=format
                    )
                    st.success("Inky has thought of an idea!")

                with st.spinner("Inky is finding images.. please wait"):
                    fleshed_out_html, image_titles = await flesh_out_html_images(
                        html_content,
                        target_audience=target_audience,
                        stylistic_description=stylistic_description,
                        content_description=content_description,
                        format=format
                    )
                    image_titles = [title.replace('_caption', '') for title in image_titles]

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

                st.success("Inky is done generating images!")

                with st.spinner("Inky is writing text... just a little more..."):
                    fleshed_out_html = await flesh_out_html_text(
                        fleshed_out_html,
                        target_audience=target_audience,
                        content_description=content_description,
                        format=format
                    )
                    st.success("Inky is done! Here is what Inky made:")
                    st.html(fleshed_out_html)

if __name__ == "__main__":
    asyncio.run(main())
