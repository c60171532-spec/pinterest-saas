import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import json, io, zipfile, textwrap, os
from fpdf import FPDF
from json_repair import repair_json

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_unique_branded_pin(title, hook):
    img = Image.new('RGB', (1000, 1500), color=(12, 17, 40))
    d = ImageDraw.Draw(img)
    
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font_large = ImageFont.truetype(font_path, 80)
        font_med = ImageFont.truetype(font_path, 50)
        font_btn = ImageFont.truetype(font_path, 50)
    except:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_btn = ImageFont.load_default()
    
    lines = textwrap.wrap(title.upper(), width=15)
    y = 350
    for line in lines:
        d.text((100, y), line, font=font_large, fill=(255, 255, 255))
        y += 120
        
    d.text((100, 850), hook.upper(), font=font_med, fill=(200, 200, 255))
    d.rectangle([100, 1150, 900, 1300], fill=(79, 70, 229))
    d.text((250, 1200), "UNLOCK STRATEGY →", font=font_btn, fill=(255, 255, 255))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest Sales & SEO Machine")
url = st.text_input("Product URL:")

if st.button("Generate Growth Campaign"):
    with st.spinner('Crafting SEO & Pin Strategy...'):
        prompt = f"Analyze {url} and provide 3 Pinterest pin titles, hooks, and SEO strategy in JSON format."
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(repair_json(completion.choices[0].message.content))
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # Generate Pins
            for i, pin in enumerate(data.get("pins", [])):
                img_data = create_unique_branded_pin(pin.get("title", "Pin"), pin.get("hook", "Learn More"))
                zf.writestr(f"Pin_{i+1}.png", img_data)
        
        st.success("Campaign Ready!")
        st.download_button("📥 Download Campaign", zip_buffer.getvalue(), "Campaign.zip")
