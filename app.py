import streamlit as st
import openai
import json
import zipfile
import io

# ... (Previous imports and setup)

# Function to create zip in memory
def create_zip(data):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # Save SEO package as text file
        seo_content = json.dumps(data["seo_package"], indent=4)
        zf.writestr("seo_package.txt", seo_content)
        
        # Save Calendar as text file
        zf.writestr("posting_calendar.txt", data["posting_calendar"])
        
    return zip_buffer.getvalue()

# Inside "Generate Campaign" block:
# ... (After getting the data)
st.json(data)

# Download Button
zip_data = create_zip(data)
st.download_button(
    label="📥 Download Campaign.zip",
    data=zip_data,
    file_name="Campaign.zip",
    mime="application/zip"
)
