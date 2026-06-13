import streamlit as st
import openai
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Pinterest SaaS Generator")

st.title("🚀 Pinterest Sales Generator")
url = st.text_input("Enter Product URL:")

if st.button("Generate Campaign"):
    if url:
        with st.spinner('Generating your Pinterest Strategy...'):
            # Yahan OpenAI API call logic aayega
            st.success("Campaign Generated!")
            st.write("Displaying SEO Package and Pin Details...")
            # Download buttons logic
    else:
        st.warning("Please enter a URL first!")
