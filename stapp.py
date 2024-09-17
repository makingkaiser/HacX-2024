import streamlit as st
with open("workinghtmltemplateforbrowser.html", "r") as file:
    html_content = file.read()

st.html(html_content)
