import streamlit as st
from groq import Groq
import json
from json_repair import repair_json # Nayi library
import io
import zipfile
from fpdf import FPDF

# ... (API Setup wahi rahega)
# ... (PDF Function wahi rahega)

if st.button("Generate Campaign"):
    # ... (URL validation wahi rahega)
    try:
        with st.spinner('Generating...'):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a Pinterest SEO expert. Return ONLY valid JSON for keys 'pins', 'seo_package', and 'posting_calendar'. Do not include any intro or outro text."},
                    {"role": "user", "content": f"Analyze {url}. Return JSON only."}
                ]
            )
            
            raw_content = completion.choices[0].message.content
            # Yahan repair use kar rahe hain
            data = json.loads(repair_json(raw_content)) 
            
            st.success("Campaign Generated!")
            st.json(data)
            # ... (Download button logic)
    except Exception as e:
        st.error(f"Error: {e}. Raw Content was: {raw_content[:100]}...") # Error ko debug karne ke liye
