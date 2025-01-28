import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# ✅ Ensure Streamlit Page Config is Set First
st.set_page_config(page_title="📈 AI Stock Analyzer", layout="wide")

# Load environment variables (for local development)
load_dotenv()

# ✅ Use Streamlit Secrets for Cloud Deployment
FMP_API_KEY = st.secrets.get("FMP_API_KEY", os.getenv("FMP_API_KEY"))
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# ✅ Debugging API Keys
st.write(f"🔍 DEBUG: FMP_API_KEY Loaded: {'Yes' if FMP_API_KEY else 'No'}")
st.write(f"🔍 DEBUG: OPENAI_API_KEY Loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

if not FMP_API_KEY or not OPENAI_API_KEY:
    st.error("❌ API keys are missing. Ensure they are set as GitHub Secrets or in Streamlit Secrets.")

# Streamlit App Title
st.title("📊 AI-Powered Stock Analysis Dashboard")

# User Input
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL").upper()

# ✅ Function to Fetch Stock Profile
def fetch_stock_profile(ticker):
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    return response.json()

# ✅ Function to Fetch Income Statement
def fetch_income_statement(ticker):
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    return response.json()

# ✅ Function to Fetch Balance Sheet
def fetch_balance_sheet(ticker):
    url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    return response.json()

# ✅ Function to Fetch Cash Flow Statement
def fetch_cash_flow(ticker):
    url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    return response.json()

# ✅ Function to Analyze Stock with AI (Using GPT-4)
def analyze_stock_with_ai(company, income_statement, balance_sheet, cash_flow):
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.2, openai_api_key=OPENAI_API_KEY)
    
    prompt = f"""
    Analyze the stock {company['companyName']} ({ticker}) based on the following data:

    **Stock Profile:**
    - Stock Price: ${company['price']}
    - Market Cap: ${company['mktCap']}
    - Industry: {company['industry']}
    - Sector: {company['sector']}
    - 52-Week High: ${company['range'].split('-')[1]}
    - 52-Week Low: ${company['range'].split('-')[0]}

    **Latest Income Statement (Yearly):**
    - Revenue: ${income_statement[0]['revenue']:,}
    - Net Income: ${income_statement[0]['netIncome']:,}
    - EPS: ${income_statement[0]['eps']}

    **Latest Balance Sheet:**
    - Total Assets: ${balance_sheet[0]['totalAssets']:,}
    - Total Liabilities: ${balance_sheet[0]['totalLiabilities']:,}
    - Shareholder Equity: ${balance_sheet[0]['totalStockholdersEquity']:,}

    **Latest Cash Flow Statement:**
    - Operating Cash Flow: ${cash_flow[0]['operatingCashFlow']:,}
    - Free Cash Flow: ${cash_flow[0]['freeCashFlow']:,}

    Provide insights on:
    - Financial health
    - Growth potential
    - Risk factors
    - Investment outlook
    """

    response = llm([HumanMessage(content=prompt)]).content
    return response

# ✅ Run Stock Analysis on Button Click
if st.button("Analyze Stock"):
    if not FMP_API_KEY or not OPENAI_API_KEY:
        st.error("❌ API keys are missing. Ensure they are set as GitHub Secrets or in Streamlit Secrets.")
    else:
        with st.spinner("Fetching stock data..."):
            profile_data = fetch_stock_profile(ticker)
            income_data = fetch_income_statement(ticker)
            balance_data = fetch_balance_sheet(ticker)
            cash_flow_data = fetch_cash_flow(ticker)

        # ✅ Handle Missing Data
        if not profile_data or "Error Message" in profile_data:
            st.error("⚠️ No data found for this ticker. Please check the ticker symbol and try again.")
        else:
            company = profile_data[0]
            st.subheader(f"📊 {company['companyName']} ({company['symbol']})")
            st.image(company["image"], width=100)

            # ✅ Display Stock Profile
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Stock Price", f"${company['price']}")
                st.metric("Market Cap", f"${company['mktCap']:,}")
                st.metric("52-Week High", f"${company['range'].split('-')[1]}")
            with col2:
                st.metric("52-Week Low", f"${company['range'].split('-')[0]}")
                st.metric("Industry", company["industry"])
                st.metric("Sector", company["sector"])

            # ✅ Display Financial Statements
            st.subheader("📜 Income Statement (Latest Year)")
            st.write(income_data[0])

            st.subheader("📊 Balance Sheet (Latest Year)")
            st.write(balance_data[0])

            st.subheader("💰 Cash Flow Statement (Latest Year)")
            st.write(cash_flow_data[0])

            # ✅ AI-Powered Stock Analysis
            with st.spinner("🤖 Analyzing with GPT-4..."):
                ai_analysis = analyze_stock_with_ai(company, income_data, balance_data, cash_flow_data)

            st.subheader("🤖 AI Stock Assessment")
            st.write(ai_analysis)
