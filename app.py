import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import json, io, zipfile, textwrap
from fpdf import FPDF
from json_repair import repair_json

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_unique_branded_pin(title, hook):
    img = Image.new('RGB', (1000, 1500), color=(12, 17, 40))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    # Title - Wrapping text to fit nicely
    lines = textwrap.wrap(title.upper(), width=20)
    y = 300
    for line in lines:
        d.text((100, y), line, font=font, fill=(255, 255, 255))
        y += 80
        
    # Hook
    d.text((100, 700), hook.upper(), font=font, fill=(200, 200, 255))
    
    # Button
    d.rectangle([100, 1100, 900, 1250], fill=(79, 70, 229))
    d.text((350, 1160), "CLICK HERE", font=font, fill=(255, 255, 255))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest 5-Pin Growth Machine")
url = st.text_input("Product URL:")

if st.button("Generate 5 Pins + SEO"):
    with st.spinner('Generating 5 high-quality pins...'):
        # Prompt explicitly asking for 5 pins
        json_format = '{"pins": [{"title": "T1", "hook": "H1"}, {"title": "T2", "hook": "H2"}, {"title": "T3", "hook": "H3"}, {"title": "T4", "hook": "H4"}, {"title": "T5", "hook": "H5"}], "seo": {"keywords": ["k1"], "description": "d1"}}'
        prompt = "Analyze " + url + ". Create exactly 5 unique, high-converting Pinterest pins. Return ONLY valid JSON in this format: " + json_format
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        
        data = json.loads(repair_json(completion.choices[0].message.content))
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # SEO PDF
            seo_data = data.get("seo", {})
            seo_str = "SEO PACKAGE:\nKeywords: " + ", ".join(seo_data.get("keywords", [])) + "\nDescription: " + seo_data.get("description", "")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt=seo_str)
            zf.writestr("seo_package.pdf", pdf.output(dest='S').encode('latin-1'))
            
            # Loop through all 5 pins
            for i, pin in enumerate(data.get("pins", [])):
                img_bytes = create_unique_branded_pin(pin.get("title", "Growth"), pin.get("hook", "Learn More"))
                zf.writestr(f"Pin_{i+1}.png", img_bytes)
        
        st.success("5 Pins & SEO Package Created!")
        st.download_button("📥 Download All Files", zip_buffer.getvalue(), "pinterest_campaign.zip")
