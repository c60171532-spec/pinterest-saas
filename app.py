import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import json, io, zipfile, textwrap
from fpdf import FPDF
from json_repair import repair_json

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_unique_branded_pin(title, hook):
    # Base Image (Dark Navy)
    img = Image.new('RGB', (1000, 1500), color=(12, 17, 40))
    d = ImageDraw.Draw(img)
    
    # Simple default font to avoid any path errors
    font = ImageFont.load_default()
    
    # 1. Title (Wrapped)
    # PIL default font chota hota hai, hum text ko center alignment ke liye logic likh rahe hain
    lines = textwrap.wrap(title.upper(), width=20)
    y = 400
    for line in lines:
        d.text((100, y), line, fill=(255, 255, 255))
        y += 60
        
    # 2. Hook
    d.text((100, 800), hook.upper(), fill=(200, 200, 255))
    
    # 3. CTA Button
    d.rectangle([100, 1100, 900, 1250], fill=(79, 70, 229))
    d.text((350, 1160), "UNLOCK STRATEGY", fill=(255, 255, 255))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest Sales Machine")
url = st.text_input("Enter Product URL:")

if st.button("Generate Campaign"):
    if not url:
        st.error("URL daalo bhai!")
    else:
        with st.spinner('Generating...'):
            prompt = f"Analyze {url}. Return JSON: {{'pins': [{'title': '...', 'hook': '...'}], 'seo': {'keywords': ['...'], 'description': '...'}}}"
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            data = json.loads(repair_json(completion.choices[0].message.content))
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                # SEO PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="SEO Strategy", ln=True)
                pdf.multi_cell(0, 10, txt=str(data.get("seo", "")))
                zf.writestr("seo.pdf", pdf.output(dest='S').encode('latin-1'))
                
                # Pins
                for i, pin in enumerate(data.get("pins", [])):
                    img = create_unique_branded_pin(pin["title"], pin["hook"])
                    zf.writestr(f"pin_{i}.png", img)
            
            st.download_button("📥 Download ZIP", zip_buffer.getvalue(), "campaign.zip")
