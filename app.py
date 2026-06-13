import streamlit as st
from groq import Groq
import json
import io
import zipfile
from fpdf import FPDF

# App Config
st.set_page_config(page_title="Pinterest SaaS", layout="wide")

# API Setup
api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Pinterest SEO Strategy", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    # Convert dict to string for PDF
    pdf.multi_cell(0, 10, txt=json.dumps(data, indent=2))
    return pdf.output(dest='S').encode('latin-1')

st.title("📌 Pinterest Sales Generator")
url = st.text_input("Enter Product URL:")

if st.button("Generate Campaign"):
    if not api_key:
        st.error("GROQ_API_KEY is not set in secrets!")
    elif not url:
        st.warning("Please enter a URL.")
    else:
        try:
            with st.spinner('Generating content...'):
                prompt = f"""
                Analyze the product URL: {url}.
                Provide a JSON response with these exact keys:
                "pins": list of 5 objects (title, description, keywords, hashtags, hook, cta),
                "seo_package": object (keyword_research, board_strategy),
                "posting_calendar": string
                """
                
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Output only raw JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # JSON load
                content = completion.choices[0].message.content
                data = json.loads(content)
                
                st.success("Campaign Generated!")
                st.json(data)
                
                # Zip File Logic
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    zf.writestr("seo_package.pdf", create_pdf(data["seo_package"]))
                    zf.writestr("calendar.txt", data["posting_calendar"])
                
                st.download_button(
                    label="📥 Download Campaign.zip",
                    data=zip_buffer.getvalue(),
                    file_name="Campaign.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"Error: {e}")
