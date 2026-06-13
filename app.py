import streamlit as st
import openai
import json

# API Key setup (Streamlit secrets mein rakhna best hai)
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Pinterest Sales Generator", layout="wide")

st.title("📌 Pinterest Sales Conversion SaaS")
st.subheader("Generate 5 High-Converting Pins in 60 Seconds")

product_url = st.text_input("Paste your Product URL here:")

if st.button("Generate Campaign"):
    if not product_url:
        st.error("Please enter a URL!")
    else:
        with st.spinner('Analyzing your product and creating SEO strategy...'):
            # Prompt for AI
            prompt = f"""
            Analyze the product URL: {product_url}. 
            Provide a response in strict JSON format with these keys:
            "pins": List of 5 objects (title, description, keywords, hashtags, hook, cta),
            "seo_package": {{"keyword_research": "...", "board_strategy": "..."}},
            "posting_calendar": "30-day plan"
            """
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" }
                )
                
                data = json.loads(response.choices[0].message.content)
                
                # Show results
                st.success("Campaign Ready!")
                st.json(data) # Yahan tum UI ko behtar bana sakte ho
                
                # Download button logic (future step)
            except Exception as e:
                st.error(f"Error: {e}")
