import streamlit as st
from groq import Groq
import json
import io
import zipfile
from fpdf import FPDF

# Groq API Key (Secrets mein set karo)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_campaign(url):
    prompt = f"Analyze {url} and return JSON with pins, seo_package, calendar."
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192", # Groq ka model
        response_format={"type": "json_object"}
    )
    return json.loads(chat_completion.choices[0].message.content)

# Baaki UI aur Download logic wahi rahega jo pehle tha...
