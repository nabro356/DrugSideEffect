import streamlit as st
import streamlit.components.v1 as components

u = "https://i.ibb.co/vm0FhBN/depositphotos-11673257-stock-photo-caduceus-medical-symbol.webp"
page_title = "Dhanvantari"

# Set page title and favicon.
st.set_page_config(page_title=page_title, page_icon=u)


def add_bg_from_url():
    st.markdown(
        f"""
         <style>
         .stApp {{
             background-image: url("https://i.ibb.co/HXcJq7g/pngtree-line-light-effect-yellow-and-blue-background-image-771374.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
        unsafe_allow_html=True,
    )


add_bg_from_url()

# Read file and keep in variable
with open("pages/dtech_main.html", "r") as f:
    html_data = f.read()

# Show in webpage
components.html(html_data, width=800, height=500)
