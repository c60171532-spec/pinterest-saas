import streamlit as st
from groq import Groq
import json, io, zipfile, random, textwrap
from PIL import Image, ImageDraw
from fpdf import FPDF
from json_repair import repair_json

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_unique_branded_pin(title, hook):
    # 1. Random Background Color
    base_color = (random.randint(10, 40), random.randint(10, 40), random.randint(50, 100))
    img = Image.new('RGB', (1000, 1500), color=base_color)
    d = ImageDraw.Draw(img)
    
    # 2. Abstract Geometric Art
    for _ in range(5):
        x, y = random.randint(-200, 800), random.randint(-200, 1200)
        d.ellipse([x, y, x+600, y+600], fill=(base_color[0]+30, base_color[1]+30, base_color[2]+30))
    
    # 3. Text Area Overlay
    d.rectangle([50, 400, 950, 1100], fill=(50, 50, 50)) # Opaque box for text readability
    
    # 4. Text Overlay
    wrapped_title = textwrap.fill(title.upper(), width=15)
    d.text((100, 450), wrapped_title, fill=(255, 255, 255))
    d.text((100, 950), hook.upper(), fill=(255, 215, 0))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest Sales Conversion Machine")
url = st.text_input("Product URL:")

if st.button("Generate Growth Campaign"):
    with st.spinner('Generating...'):
        prompt = f"""
        Analyze {url}. Create 5 unique, high-converting Pinterest Pins.
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
            for i, pin in enumerate(data.get("pins", [])):
                img_data = create_unique_branded_pin(pin["title"], pin["hook"])
                zf.writestr(f"Unique_Pin_{i+1}.png", img_data)
        
        st.success("Campaign Ready!")
        st.download_button("📥 Download Growth Campaign.zip", zip_buffer.getvalue(), "Growth_Campaign.zip", "application/zip")
