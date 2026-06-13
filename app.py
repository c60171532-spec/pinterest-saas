import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import json, io, zipfile, textwrap
from fpdf import FPDF
from json_repair import repair_json

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_unique_branded_pin(title, hook):
    img = Image.new('RGB', (1000, 1500), color=(12, 17, 40))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    # Title
    lines = textwrap.wrap(title.upper(), width=20)
    y = 400
    for line in lines:
        d.text((100, y), line, font=font, fill=(255, 255, 255))
        y += 60
        
    # Hook
    d.text((100, 800), hook.upper(), font=font, fill=(200, 200, 255))
    
    # Button
    d.rectangle([100, 1100, 900, 1250], fill=(79, 70, 229))
    d.text((350, 1160), "UNLOCK STRATEGY", font=font, fill=(255, 255, 255))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest Sales Machine")
url = st.text_input("Enter Product URL:")

if st.button("Generate Campaign"):
    if not url:
        st.error("URL enter karo!")
    else:
        try:
            with st.spinner('Generating...'):
                prompt = f"Analyze {url}. Return JSON: {{'pins': [{'title': 'Example Title', 'hook': 'Example Hook'}], 'seo': {'keywords': ['tag1'], 'description': 'desc'}}}"
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                raw_json = completion.choices[0].message.content
                data = json.loads(repair_json(raw_json))
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    # PDF Setup
                    seo_data = data.get("seo", {})
                    seo_str = f"Keywords: {', '.join(seo_data.get('keywords', []))}\nDescription: {seo_data.get('description', '')}"
                    
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt="SEO Strategy", ln=True)
                    pdf.multi_cell(0, 10, txt=seo_str)
                    zf.writestr("seo.pdf", pdf.output(dest='S').encode('latin-1'))
                    
                    # Pins
                    for i, pin in enumerate(data.get("pins", [])):
                        img_bytes = create_unique_branded_pin(pin.get("title", "Pin"), pin.get("hook", "Hook"))
                        zf.writestr(f"pin_{i}.png", img_bytes)
                
                st.success("Campaign Ready!")
                st.download_button("📥 Download Campaign", zip_buffer.getvalue(), "campaign.zip")
        except Exception as e:
            st.error(f"Error: {e}")
