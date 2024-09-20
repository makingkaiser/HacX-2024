import streamlit as st
import os
import tempfile

def main():
    uploaded_file = st.file_uploader("Choose a file")
    # If user attempts to upload a file.
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        # Show the image filename and image.
        st.write(f'filename: {uploaded_file.name}')
        st.image(bytes_data)

if __name__ == "__main__":
    main()