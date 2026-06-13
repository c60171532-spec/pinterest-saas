import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import json, io, zipfile, textwrap, os
from fpdf import FPDF
from json_repair import repair_json

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_unique_branded_pin(title, hook):
    img = Image.new('RGB', (1000, 1500), color=(12, 17, 40))
    d = ImageDraw.Draw(img)
    
    # 1. FIXED FONT LOGIC: 
    # Hum 'arial.ttf' ko system path se dhoondenge
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    
    try:
        font_large = ImageFont.truetype(font_path, 80)
        font_med = ImageFont.truetype(font_path, 50)
        font_btn = ImageFont.truetype(font_path, 50)
    except:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_btn = ImageFont.load_default()
    
    # 2. Text Placement (Adjusted Coordinates)
    lines = textwrap.wrap(title.upper(), width=15)
    y = 350
    for line in lines:
        d.text((100, y), line, font=font_large, fill=(255, 255, 255))
        y += 120 # Space between lines
        
    # Hook
    d.text((100, 850), hook.upper(), font=font_med, fill=(200, 200, 255))
    
    # 3. Button
    d.rectangle([100, 1150, 900, 1300], fill=(79, 70, 229))
    d.text((250, 1200), "UNLOCK STRATEGY →", font=font_btn, fill=(255, 255, 255))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
