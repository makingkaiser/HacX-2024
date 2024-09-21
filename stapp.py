import streamlit as st
st.set_page_config(layout="wide")

import asyncio
from htmlgeneratorfunc import generate_html_content
from main import flesh_out_html
async def main():
    
    st.title("Preventive Drug Education Material Generator")
    st.image("https://img.freepik.com/premium-vector/cute-octopus-artist-painting-cartoon-vector-icon-illustration-animal-education-icon-isolated-flat_138676-6683.jpg?w=360")
    st.write("Hello! I'm Inky, your friendly preventive drug education material generator. I can help you generate content for your educational materials, based on the materials you uploaded. Just fill out the form below and I'll do the rest!")    

    target_audience = st.text_input("Target Audience", "type your desired audience here! e.g: general audience")
    stylistic_description = st.text_input("Stylistic Description", "type your desired style here! e.g: 90's cartoon style")
    content_description = st.text_input("Content Description", "type your desired content here! e.g: various scenes and landscapes")
    format = st.text_input("Format", "type your desired format here! e.g: pamphlet")

    if st.button("Generate HTML"):
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

            with st.spinner("Inky is starting.. please wait"):
                fleshed_out_html = await flesh_out_html(
                    html_content,
                    target_audience=target_audience,
                    stylistic_description=stylistic_description,
                    content_description=content_description,
                    format=format
                )
                st.success("Inky is done!")
                st.html(fleshed_out_html)

if __name__ == "__main__":
    asyncio.run(main())