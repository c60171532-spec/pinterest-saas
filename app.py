import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import json, io, zipfile, textwrap
from fpdf import FPDF
from json_repair import repair_json

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_unique_branded_pin(title, hook):
    # Dark Navy Background
    img = Image.new('RGB', (1000, 1500), color=(12, 17, 40))
    d = ImageDraw.Draw(img)
    
    # Font Handling (fallback to default if arial not present)
    try:
        font_large = ImageFont.truetype("arial.ttf", 90)
        font_med = ImageFont.truetype("arial.ttf", 60)
        font_btn = ImageFont.truetype("arial.ttf", 55)
    except:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_btn = ImageFont.load_default()
    
    # Title Placement
    lines = textwrap.wrap(title.upper(), width=16)
    y = 300
    for line in lines:
        d.text((80, y), line, font=font_large, fill=(255, 255, 255))
        y += 110
        
    # Hook Placement
    wrapped_hook = textwrap.fill(hook.upper(), width=30)
    d.text((80, 800), wrapped_hook, font=font_med, fill=(200, 200, 255))
    
    # CTA Button
    d.rectangle([100, 1100, 900, 1250], fill=(79, 70, 229)) # Vibrant Purple
    d.text((250, 1140), "UNLOCK STRATEGY →", font=font_btn, fill=(255, 255, 255))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

st.title("📌 Pinterest Sales & SEO Machine")
url = st.text_input("Product URL:")

if st.button("Generate Growth Campaign"):
    if not url:
        st.error("Please enter a URL!")
    else:
        with st.spinner('Crafting SEO & Pin Strategy...'):
            prompt = f"""
            Analyze {url} and provide a complete growth strategy.
            Return ONLY JSON with these keys:
            {{
                "pins": [{{"title": "...", "hook": "..."}}],
                "seo_package": {{
                    "target_keywords": ["keyword1", "keyword2", "keyword3"],
                    "pinterest_board_names": ["Board1", "Board2"],
                    "optimized_description": "A 2-sentence description for Pinterest with keywords."
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
                # SEO Strategy PDF
                seo = data.get("seo_package", {})
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="Pinterest SEO Strategy Package", ln=True, align='C')
                pdf.ln(10)
                
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(200, 10, txt="Target Keywords:", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, txt=", ".join(seo.get("target_keywords", [])))
                
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(200, 10, txt="Recommended Boards:", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, txt=", ".join(seo.get("pinterest_board_names", [])))
                
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(200, 10, txt="Optimized Description:", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, txt=seo.get("optimized_description", ""))
                
                zf.writestr("seo_strategy.pdf", pdf.output(dest='S').encode('latin-1'))
                
                # Pins Generation
                for i, pin in enumerate(data.get("pins", [])):
                    img_data = create_unique_branded_pin(pin.get("title", "Growth"), pin.get("hook", "Learn More"))
                    zf.writestr(f"Unique_Pin_{i+1}.png", img_data)
            
            st.success("Campaign & SEO Strategy Ready!")
            st.download_button("📥 Download Growth Campaign.zip", zip_buffer.getvalue(), "Growth_Campaign.zip", "application/zip")
