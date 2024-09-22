import streamlit as st
import os 
st.set_page_config(layout="wide")

import asyncio
from htmlgeneratorfunc import generate_html_content
from main import flesh_out_html_images, flesh_out_html_text
from azure.storage.blob import BlobServiceClient

blob_conn_str = os.getenv("CONNECTION_STRING")

    
async def main():
    
    st.title("Preventive Drug Education Material Generator")
    st.image("https://img.freepik.com/premium-vector/cute-octopus-artist-painting-cartoon-vector-icon-illustration-animal-education-icon-isolated-flat_138676-6683.jpg?w=360")
    st.write("Hello! I'm Inky, your friendly preventive drug education material generator. I can help you make content for your educational materials, based on the materials you uploaded. Just fill out the form below and I'll do the rest!")    

    target_audience = st.text_input("Target Audience", "type your desired audience here! e.g: general audience")
    stylistic_description = st.text_input("Stylistic Description", "type your desired style here! e.g: 90's cartoon style")
    content_description = st.text_input("Content Description", "type your desired content here! e.g: various scenes and landscapes")
    format = st.text_input("Format", "type your desired format here! e.g: pamphlet")

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
            
            blob_service_client = BlobServiceClient.from_connection_string(blob_conn_str)
            container_name = 'source-images'

            with st.spinner("Inky is finding images.. please wait"):
                fleshed_out_html, image_titles = await flesh_out_html_images(
                    html_content,
                    target_audience=target_audience,
                    stylistic_description=stylistic_description,
                    content_description=content_description,
                    format=format
                )
                
                container_client = blob_service_client.get_container_client(container_name)
                
                image_titles = [title.replace('_caption', '') for title in image_titles]
                st.success("Here are some images referenced!")

                for title in image_titles:
                    possible_extensions = ['.png', '.jpg', '.jpeg', '.gif']
                    found = False
                    for blob in container_client.list_blobs():
                        print(f"Checking blob: {blob.name}")  # Debug statement
                        name, ext = os.path.splitext(blob.name)
                        if name == title and ext in possible_extensions:
                            image_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob.name}"
                            st.image(image_url, caption=title)
                            found = True
                            break

                    if not found:
                        st.error(f"Image file for '{title}' not found.")

                st.success("Inky is done generating images!")

            # Then, process and update the HTML with the refined text
            with st.spinner("Inky is writing text... just a little more..."):
                fleshed_out_html = await flesh_out_html_text(
                    fleshed_out_html,  # Make sure to pass the HTML updated with images
                    target_audience=target_audience,
                    content_description=content_description,
                    format=format
                )
                st.success("Inky is done! Here is what Inky made:")
                st.html(fleshed_out_html)  # Update the displayed HTML with refined text

if __name__ == "__main__":
    asyncio.run(main())