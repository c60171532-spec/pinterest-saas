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
        
    # Hook & Button
    d.text((100, 800), hook.upper(), font=font, fill=(200, 200, 255))
    d.rectangle([100, 1100, 900, 1250], fill=(79, 70, 229))
    d.text((350, 1160), "UNLOCK STRATEGY", font=font, fill=(255, 255, 255))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest Sales Machine")
url = st.text_input("Enter Product URL:")

if st.button("Generate Campaign"):
    with st.spinner('Generating...'):
        # Prompt fix: Braces double kar diye hain taaki error na aaye
        prompt = f"""
        Analyze {url}. Return JSON: 
        {{
            "pins": [
                {{"title": "Title 1", "hook": "Hook 1"}},
                {{"title": "Title 2", "hook": "Hook 2"}}
            ],
            "seo": {{
                "keywords": ["tag1", "tag2"],
                "description": "Short desc"
            }}
        }}
        """
        
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
        
        st.success("Done!")
        st.download_button("📥 Download Campaign", zip_buffer.getvalue(), "campaign.zip")
