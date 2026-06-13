import streamlit as st
from groq import Groq
import json
import io
import zipfile
from fpdf import FPDF

# Groq Client Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Pinterest SEO Strategy", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=str(data))
    return pdf.output(dest='S').encode('latin-1')

st.title("📌 Pinterest Sales Generator")
url = st.text_input("Enter Product URL:")

if st.button("Generate Campaign"):
    if url:
        with st.spinner('Generating Campaign...'):
            # Groq API Call
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": f"Analyze {url} and provide a JSON response with 'pins', 'seo_package', and 'posting_calendar'."}],
                response_format={"type": "json_object"}
            )
            data = json.loads(completion.choices[0].message.content)
            
            # Show Results
            st.json(data)
            
            # Zip File Generation
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                zf.writestr("seo_package.pdf", create_pdf(data["seo_package"]))
                zf.writestr("calendar.txt", data["posting_calendar"])
            
            st.download_button("📥 Download Campaign.zip", zip_buffer.getvalue(), "Campaign.zip", "application/zip")
