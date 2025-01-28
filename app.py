import os
import requests
import streamlit as st
from dotenv import load_dotenv
import openai  # ✅ Updated Import

# ✅ Ensure environment variables are loaded
load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Set Streamlit Page Config
st.set_page_config(page_title="📈 AI Stock Analyzer", layout="wide")

st.title("📊 AI-Powered Stock Analysis Dashboard")

# Debug API Keys
st.sidebar.header("Debug Info")
st.sidebar.write(f"🔍 FMP_API_KEY Loaded: {'Yes' if FMP_API_KEY else 'No'}")
st.sidebar.write(f"🔍 OPENAI_API_KEY Loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL", max_chars=10)

# ✅ OpenAI ChatGPT Function (Updated)
def analyze_stock_with_ai(prompt):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # ✅ Updated Client
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"❌ OpenAI Error: {e}")
        return None

if st.button("Analyze Stock"):
    if not FMP_API_KEY or not OPENAI_API_KEY:
        st.error("❌ API keys are missing. Ensure they are set correctly.")
    else:
        st.success("✅ API Keys loaded successfully! Fetching data...")

        # ✅ Fetch stock data
        stock_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
        stock_response = requests.get(stock_url)

        if stock_response.status_code == 200 and stock_response.json():
            company = stock_response.json()[0]

            # ✅ Display Stock Info
            st.subheader(f"📌 {company['companyName']} ({company['symbol']})")
            st.image(company["image"], width=120)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Stock Price", f"${company['price']}")
                st.metric("🏢 Market Cap", f"${company['mktCap']:,}")
            with col2:
                st.metric("📉 52-Week Low", f"${company['range'].split('-')[0]}")
                st.metric("📈 52-Week High", f"${company['range'].split('-')[1]}")

            # ✅ AI Stock Analysis
            with st.spinner("🤖 Analyzing with GPT-4..."):
                prompt = f"Analyze {company['companyName']} stock based on its financials."
                ai_analysis = analyze_stock_with_ai(prompt)

            if ai_analysis:
                st.subheader("🤖 AI Stock Insights")
                st.markdown(f"**GPT-4 Analysis:**\n\n{ai_analysis}")
            else:
                st.error("⚠️ AI analysis failed. Try again later.")

        else:
            st.error("⚠️ No data found for this ticker.")

