import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw
import json, io, zipfile
from fpdf import FPDF
from json_repair import repair_json

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_pin_image(title):
    img = Image.new('RGB', (1000, 1500), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((100, 700), title[:40], fill=(255, 255, 255)) 
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest Sales Conversion Machine")
url = st.text_input("Product URL:")

if st.button("Generate Growth Campaign"):
    with st.spinner('Crafting strategy...'):
        # FIXED PROMPT: JSON brackets ko escape kiya hai
        prompt = f"""
        Analyze {url}. Create 5 high-converting Pinterest Pins.
        Return ONLY valid JSON with this structure: 
        {{"pins": [{{"title": "...", "hook": "...", "cta": "..."}}], "seo_package": {{"keywords": [], "board_names": []}}, "posting_calendar": "30-day plan"}}
        """
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw_content = completion.choices[0].message.content
        data = json.loads(repair_json(raw_content))
        
        # Zip Creation
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # SEO Strategy PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=str(data.get("seo_package", "No SEO Data")), ln=True)
            zf.writestr("seo_strategy.pdf", pdf.output(dest='S').encode('latin-1'))
            
            # Generate 5 Pin Images
            for i, pin in enumerate(data.get("pins", [])):
                img_data = create_pin_image(pin.get("title", "Check this out!"))
                zf.writestr(f"Pin_{i+1}.png", img_data)
        
        st.download_button("📥 Download Growth Campaign.zip", zip_buffer.getvalue(), "Growth_Campaign.zip", "application/zip")
