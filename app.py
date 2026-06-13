import streamlit as st
import openai
import json
import zipfile
import io
from fpdf import FPDF

# Page Config
st.set_page_config(page_title="Pinterest SaaS Generator", layout="wide")

# API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Helper: PDF Generation
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Pinterest SEO Strategy Package", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=str(data["seo_package"]))
    return pdf.output(dest='S').encode('latin-1')

# Helper: ZIP Generation
def create_zip(data, pdf_bytes):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("seo_package.pdf", pdf_bytes)
        zf.writestr("posting_calendar.txt", data["posting_calendar"])
        # Add pins data as JSON
        zf.writestr("pins_data.json", json.dumps(data["pins"], indent=4))
    return zip_buffer.getvalue()

st.title("🚀 Pinterest Sales Generator")
url = st.text_input("Paste your Product URL here:")

if st.button("Generate Campaign"):
    if not url:
        st.warning("Please enter a URL first!")
    else:
        with st.spinner('AI is generating your Pinterest Strategy...'):
            prompt = f"""
            Analyze {url} and return JSON with keys:
            "pins": List of 5 objects (title, description, keywords, hashtags, hook, cta),
            "seo_package": {{"keyword_research": "...", "board_strategy": "..."}},
            "posting_calendar": "30-day plan"
            """
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            
            data = json.loads(response.choices[0].message.content)
            
            # Display UI
            st.success("Campaign Generated Successfully!")
            for i, pin in enumerate(data.get("pins", [])):
                with st.expander(f"Pin {i+1}: {pin['title']}"):
                    st.write(f"**Hook:** {pin['hook']}")
                    st.write(f"**CTA:** {pin['cta']}")
                    st.code(f"Keywords: {', '.join(pin['keywords'])}")
            
            # Prepare files
            pdf_bytes = create_pdf(data)
            zip_data = create_zip(data, pdf_bytes)
            
            # Download
            st.download_button(
                label="📥 Download Campaign.zip",
                data=zip_data,
                file_name="Campaign.zip",
                mime="application/zip"
            )
