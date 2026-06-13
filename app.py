import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw
import json, io, zipfile, textwrap
from fpdf import FPDF
from json_repair import repair_json

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_unique_branded_pin(title, hook):
    # Dark Navy Background (Brand color)
    img = Image.new('RGB', (1000, 1500), color=(15, 20, 45))
    d = ImageDraw.Draw(img)
    
    # 1. Title Area
    lines = textwrap.wrap(title.upper(), width=18)
    y_text = 400
    for line in lines:
        d.text((100, y_text), line, fill=(255, 255, 255))
        y_text += 100 # Line spacing
        
    # 2. Hook/CTA Area
    d.text((100, 900), hook.upper(), fill=(200, 200, 255))
    
    # 3. Button Simulation (Bottom CTA)
    d.rectangle([200, 1100, 800, 1250], fill=(99, 102, 241)) # Purple Button
    d.text((320, 1150), "UNLOCK STRATEGY →", fill=(255, 255, 255))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest Sales Conversion Machine")
url = st.text_input("Product URL:")

if st.button("Generate Growth Campaign"):
    with st.spinner('Generating professional pins...'):
        prompt = f"""
        Analyze {url}. Create 5 unique, high-converting Pinterest Pin Titles and Hooks.
        Return ONLY valid JSON with keys: 
        {{"pins": [{{"title": "...", "hook": "..."}}], "seo_package": {{"keywords": [], "board_names": []}}}}
        """
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        
        data = json.loads(repair_json(completion.choices[0].message.content))
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # SEO Strategy PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="SEO Strategy", ln=True)
            pdf.multi_cell(0, 10, txt=str(data.get("seo_package", "N/A")))
            zf.writestr("seo_strategy.pdf", pdf.output(dest='S').encode('latin-1'))
            
            # Generate Pins
            for i, pin in enumerate(data.get("pins", [])):
                img_data = create_unique_branded_pin(pin.get("title", "Growth"), pin.get("hook", "Learn More"))
                zf.writestr(f"Pin_{i+1}.png", img_data)
        
        st.success("Campaign Ready!")
        st.download_button("📥 Download Growth Campaign.zip", zip_buffer.getvalue(), "Growth_Campaign.zip", "application/zip")
