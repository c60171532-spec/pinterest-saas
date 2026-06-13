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

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Pinterest SEO Strategy", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt=str(data))
    return pdf.output(dest='S').encode('latin-1')

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
                
                st.success("Campaign Generated Successfully!")
                
                # Display Results
                st.subheader("📊 Generated Data")
                st.write(data)
                
                # Zip File Logic (Fixed bytes issue)
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    zf.writestr("seo_package.pdf", create_pdf(data.get("seo_package", {})))
                    zf.writestr("calendar.txt", str(data.get("posting_calendar", "")))
                    zf.writestr("pins_data.json", json.dumps(data.get("pins", []), indent=4))
                
                # Download Button (Fixed with .getvalue())
                st.download_button(
                    label="📥 Download Campaign.zip",
                    data=zip_buffer.getvalue(),
                    file_name="Campaign.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"Something went wrong: {e}")
