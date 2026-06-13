import streamlit as st
from groq import Groq
import json, io, zipfile, random
from PIL import Image, ImageDraw
from fpdf import FPDF
from json_repair import repair_json

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_random_color():
    return (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))

def create_dynamic_pin(title):
    # Dynamic Background
    img = Image.new('RGB', (1000, 1500), color=get_random_color())
    d = ImageDraw.Draw(img)
    
    # Random Geometric Shapes for uniqueness
    for _ in range(3):
        x, y = random.randint(0, 800), random.randint(0, 1200)
        d.rectangle([x, y, x+250, y+250], fill=get_random_color())
    
    # Text overlay
    d.text((100, 750), title[:40], fill=(255, 255, 255))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest Sales Conversion Machine")
url = st.text_input("Product URL:")

if st.button("Generate Growth Campaign"):
    with st.spinner('Crafting unique high-converting strategy...'):
        prompt = f"""
        Analyze {url}. Create 5 unique, high-converting Pinterest Pins.
        Return ONLY valid JSON with keys: 
        {{"pins": [{{"title": "...", "hook": "...", "cta": "..."}}], "seo_package": {{"keywords": [], "board_names": []}}, "posting_calendar": "30-day growth plan"}}
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
            pdf.cell(200, 10, txt="SEO Strategy", ln=True)
            pdf.multi_cell(0, 10, txt=str(data.get("seo_package", "N/A")))
            zf.writestr("seo_strategy.pdf", pdf.output(dest='S').encode('latin-1'))
            
            # Generate Unique Pin Images
            for i, pin in enumerate(data.get("pins", [])):
                img_data = create_dynamic_pin(pin.get("title", "Growth Pin"))
                zf.writestr(f"Unique_Pin_{i+1}.png", img_data)
        
        st.success("Campaign Ready!")
        st.download_button("📥 Download Growth Campaign.zip", zip_buffer.getvalue(), "Growth_Campaign.zip", "application/zip")
