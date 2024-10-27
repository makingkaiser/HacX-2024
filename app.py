import streamlit as st
import os 
import requests
import asyncio
from htmlgeneratorfunc import generate_html_content
from main import flesh_out_html_images, flesh_out_html_text
from extractors import extract_text_descriptions
from regenpipeline import regenerate_image, regenerate_text, replace_image_descriptions, replace_text_descriptions, extract_image_links
from azure.storage.blob import BlobServiceClient
import base64  # Add this at the top with your other imports

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def navbar():
    # Get the base64 encoded logo
    logo_base64 = get_base64_encoded_image("logo.png")

    navbar_html = f"""
        <div class="navbar">
            <div class="nav-content">
                <div class="nav-logo-container">
                    <img src="data:image/png;base64,{logo_base64}" class="nav-logo-img" alt="Logo">
                    <span class="nav-logo-text">Drug Education Generator</span>
                </div>
                <div class="nav-links">
                    <a href="/" class="nav-link">Home</a>
                    <a href="/about" class="nav-link">About</a>
                    <a href="/contact" class="nav-link">Contact</a>
                </div>
            </div>
        </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="Preventative Drug Education Generator", page_icon=":octopus:")

@st.fragment
def load_css():
    return """
    <style>
    /* Navigation Bar */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;  /* Increased height to accommodate logo */
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 1000;
            display: flex;
            align-items: center;
            padding: 0 2rem;
        }

        .nav-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
        }

        .nav-logo-container {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .nav-logo-img {
            height: 40px;  /* Adjust size as needed */
            width: auto;
        }

        .nav-logo-text {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1E3A8A;
        }

        /* Modern Layout and Spacing */
        .main {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Typography */
        h1, h2, h3, h4 {
            color: #1E3A8A;
            font-family: 'Inter', sans-serif;
            margin-bottom: 1.5rem;
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
            min-width: 200px;  /* Optional: sets minimum width */
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
        
        .content-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px -1px rgba(0,0,0,0.15);
        }
        
        /* Sidebar */
        .css-1d391kg {
            background: #F8FAFC;
            padding: 2rem 1rem;
        }
        
        /* Custom Classes */
        .text-gradient {
            background: linear-gradient(90deg, #FF8C00, #FF8CFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .container {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
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

    navbar()
    
    st.title("Preventive Drug Education Material Generator")
    st.markdown("Hello DrugFreeSG Champions! Welcome to Your Creative Hub for Preventive Drug Education creation!")
    st.image("logo.png")  # If the image is in the same directory as app.py



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
        target_audience = st.text_input("Tell me about your audience — Who are you creating this for?")
        stylistic_description = st.text_input("Pick your style — From comic-book fun to 90s cartoons, choose the look that fits best.")
        content_description = st.text_input("Describe your message — What's the focus? Awareness, safety, or myth-busting?")
        format = st.text_input("Format — How do you want to deliver this message? A pamphlet, a poster, or a newsletter?")

    with st.container():
        st.markdown("### Hi, I'm Inky!")
        st.write("""<div style="max-width: 850px; margin-left: 0 auto; margin-bottom: 100 auto;">
            I'm your friendly guide in creating impactful, educational content on drug prevention. Whether you're a teacher, community leader, or advocate, I'm here to help you craft meaningful materials that speak to your audience. Let's work together to make cool content! just use the form on the left to tell me your ideas. Once you're ready, click the button below.
            </div>""", unsafe_allow_html=True)
        st.write("")
        st.write("")
        st.write("")
        

        
        if st.button("Generate!✨"):
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

            st.download_button(
            label="Download HTML",
            data=st.session_state.fleshed_out_html_content,
            file_name="generated_content.html",
            mime="text/html"
            )

            # Regeneration section
            if st.button("Regenerate"):
                st.session_state.regenerate_clicked = True
                st.session_state.selected_component = None

        if st.session_state.regenerate_clicked and st.session_state.fleshed_out_html_content:
            st.subheader("Select a component to regenerate")
            
            image_elements = st.session_state.image_elements_before_regeneration
            text_elements = st.session_state.text_elements_before_regeneration
            updated_html = st.session_state.fleshed_out_html_content

            # Display image components with inline regeneration
            for i, image_element in enumerate(image_elements):
                st.image(image_element.content, caption=f"{image_element.description[:60]}...", width = 500)

                if st.button(f"Select Image {i+1}", key=f"select_img_{i}"):
                        st.session_state.selected_component = ('image', i)

                # Show regeneration input right below the selected component
                if st.session_state.selected_component and st.session_state.selected_component == ('image', i):
                    image_input = st.text_input(
                        "How would you like to refine this image?",
                        key=f"image_input_{i}"
                    )
                    if st.button("Submit", key=f"submit_img_{i}"):
                        with st.spinner("Regenerating image..."):
                            regenerated_image_element = await regenerate_image(
                                user_input=image_input,
                                target_audience=target_audience,
                                stylistic_description=stylistic_description,
                                content_description=content_description,
                                format=format,
                                element=image_elements[i]
                            )
                            st.subheader("Regenerated Image")
                            st.markdown("---")
                            st.image(regenerated_image_element.content, caption=f"{regenerated_image_element.refined[:60]}...", width=500)
                            st.markdown("---")
                            image_elements[i] = regenerated_image_element
                            updated_html = replace_image_descriptions(st.session_state.placeholder_html_content, image_elements)
                            updated_html = replace_text_descriptions(updated_html, text_elements)
                            st.session_state.fleshed_out_html_content = updated_html

            # Display text components with inline regeneration
            for i, text_element in enumerate(text_elements):
                st.html(text_element.refined)
                
                if st.button(f"Select Text {i+1}", key=f"select_text_{i}", use_container_width = True):
                    st.session_state.selected_component = ('text', i)

                # Show regeneration input right below the selected component
                if st.session_state.selected_component and st.session_state.selected_component == ('text', i):
                    text_input = st.text_input(
                        "How would you like to refine this text?",
                        key=f"text_input_{i}"
                    )
                    if st.button("Submit", key=f"submit_text_{i}"):
                        with st.spinner("Regenerating text..."):
                            regenerated_text_element = await regenerate_text(
                                text_input,
                                text_elements[i]
                            )
                            st.subheader("Regenerated text")
                            st.markdown("---")
                            st.html(regenerated_text_element.refined)
                            st.markdown("---")
                            text_elements[i] = regenerated_text_element
                            updated_html = replace_text_descriptions(st.session_state.placeholder_html_content, text_elements)
                            updated_html = replace_image_descriptions(updated_html, image_elements)
                            st.session_state.fleshed_out_html_content = updated_html

            # Display final updated HTML at the bottom
            st.markdown("---")
            st.subheader("Regenerated HTML")
            st.html(st.session_state.fleshed_out_html_content)

            st.download_button(
                label="Download Updated HTML",
                data=st.session_state.fleshed_out_html_content,
                file_name="updated_content.html",
                mime="text/html"
            )
                
if __name__ == "__main__":
    asyncio.run(main())
