import streamlit as st
from groq import Groq
import json
import io
import zipfile
from fpdf import FPDF
from json_repair import repair_json

st.set_page_config(page_title="Pinterest SaaS", layout="centered")

# API Setup
api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# PDF Function
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Pinterest SEO Strategy", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt=json.dumps(data, indent=2))
    return pdf.output(dest='S').encode('latin-1')

# UI Elements (Order mein hain)
st.title("📌 Pinterest Sales Generator")
url = st.text_input("Enter Product URL:", placeholder="https://your-product-link.com")

if st.button("Generate Campaign"):
    if not url:
        st.warning("Please enter a URL first!")
    elif not api_key:
        st.error("GROQ_API_KEY is missing!")
    else:
        try:
            with st.spinner('Generating campaign...'):
                prompt = f"Analyze {url}. Return JSON only with keys: 'pins', 'seo_package', 'posting_calendar'."
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a Pinterest SEO expert. Return ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                raw_content = completion.choices[0].message.content
                data = json.loads(repair_json(raw_content))
                
                st.success("Campaign Generated!")
                st.json(data)
                
                # Download Logic
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    zf.writestr("seo_package.pdf", create_pdf(data["seo_package"]))
                    zf.writestr("calendar.txt", data["posting_calendar"])
                
                st.download_button("📥 Download Campaign.zip", zip_buffer.getvalue(), "Campaign.zip", "application/zip")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
