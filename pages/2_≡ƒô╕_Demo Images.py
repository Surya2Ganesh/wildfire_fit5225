"""Streamlit page that displays the bundled wildfire demo images."""

import streamlit as st
from glob import glob

# Reuse the simple title styling from the main page so the demo pages match.
st.markdown(
        """
        <style>
        .container {
            max-width: 800px;
        }
        .title {
            text-align: center;
            font-size: 35px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .description {
            margin-bottom: 30px;
        }
        .instructions {
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div class='title'>Demo Images</div>", unsafe_allow_html=True)

# Load all JPEG images from the demo folder and render them one by one.
images = glob('demo-images/*.jpeg')

for image in images:
    st.image(image, use_column_width=True)
