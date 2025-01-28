import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI  # Ensure langchain_community import
from langchain.schema import HumanMessage

# ✅ FIXED: Set page config as the very first Streamlit command
st.set_page_config(page_title="📈 AI Stock Analyzer", layout="wide")

# Load environment variables
load_dotenv()

# Get API keys
FMP_API_KEY = os.getenv("FMP_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debugging: Check if API keys are loaded
st.write(f"🔍 DEBUG: FMP_API_KEY Loaded: {'Yes' if FMP_API_KEY else 'No'}")
st.write(f"🔍 DEBUG: OPENAI_API_KEY Loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

if not FMP_API_KEY or not OPENAI_API_KEY:
    st.error("❌ API keys are missing. Ensure they are set as GitHub Secrets and passed correctly.")

# Streamlit App Title
st.title("📊 AI-Powered Stock Analysis Dashboard")

# User Input
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL").upper()

# Function to fetch stock profile data from FMP API
def fetch_stock_profile(ticker):
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    return response.json()

# Function to generate AI analysis using LangChain (GPT-4)
def analyze_stock_with_ai(company):
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.2, openai_api_key=OPENAI_API_KEY)
    
    prompt = f"""
    Analyze the stock {company['companyName']} ({ticker}) based on:
    - Stock Price: ${company['price']}
    - Market Cap: ${company['mktCap']}
    - Industry: {company['industry']}
    - Sector: {company['sector']}
    - 52-Week High: ${company['range'].split('-')[1]}
    - 52-Week Low: ${company['range'].split('-')[0]}

    Provide insights on:
    - Growth potential
    - Risk factors
    - Investment outlook
    """

    response = llm([HumanMessage(content=prompt)]).content
    return response

# Run Stock Analysis on button click
if st.button("Analyze Stock"):
    if not FMP_API_KEY or not OPENAI_API_KEY:
        st.error("❌ API keys are missing. Ensure they are set as GitHub Secrets or in a .env file.")
    else:
        with st.spinner("Fetching stock data..."):
            data = fetch_stock_profile(ticker)

        if not data or "Error Message" in data:
            st.error("⚠️ No data found for this ticker.")
        else:
            company = data[0]
            st.subheader(f"📊 {company['companyName']} ({company['symbol']})")
            st.image(company["image"], width=100)

            # Display Key Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Stock Price", f"${company['price']}")
                st.metric("Market Cap", f"${company['mktCap']:,}")
                st.metric("52-Week High", f"${company['range'].split('-')[1]}")
            with col2:
                st.metric("52-Week Low", f"${company['range'].split('-')[0]}")
                st.metric("Industry", company["industry"])
                st.metric("Sector", company["sector"])

            # AI-Powered Stock Analysis
            with st.spinner("🤖 Analyzing with GPT-4..."):
                ai_analysis = analyze_stock_with_ai(company)

            st.subheader("🤖 AI Stock Assessment")
            st.write(ai_analysis)
