import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import json, io, zipfile, os
from fpdf import FPDF
from json_repair import repair_json

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_pin_image(title):
    # Ek basic template (1000x1500)
    img = Image.new('RGB', (1000, 1500), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((100, 700), title, fill=(255, 255, 255)) # Yahan tum font bhi load kar sakte ho
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Pinterest Sales Strategy", ln=True, align='C')
    pdf.multi_cell(0, 10, txt=str(data))
    return pdf.output(dest='S').encode('latin-1')

st.title("📌 Pinterest Sales Conversion Machine")
url = st.text_input("Product URL:")

if st.button("Generate Growth Campaign"):
    with st.spinner('Crafting high-converting strategy...'):
        prompt = f"""
        Analyze {url}. Create 5 high-converting Pinterest Pins.
        Return ONLY valid JSON with keys: 
        "pins": [{"title": "...", "hook": "...", "cta": "..."}, ...],
        "seo_package": {"keywords": [...], "board_names": [...]},
        "posting_calendar": "30-day growth plan"
        """
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(repair_json(completion.choices[0].message.content))
        
        # Zip Creation
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # Add SEO PDF
            zf.writestr("seo_strategy.pdf", create_pdf(data["seo_package"]))
            # Generate 5 Pin Images
            for i, pin in enumerate(data["pins"]):
                img_data = create_pin_image(pin["title"])
                zf.writestr(f"Pin_{i+1}.png", img_data)
        
        st.download_button("📥 Download Growth Campaign.zip", zip_buffer.getvalue(), "Growth_Campaign.zip", "application/zip")
