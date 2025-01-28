import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# ✅ Set Streamlit Page Config First
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

# ✅ Function to Fetch Stock Profile (Fixed)
def fetch_stock_profile(ticker):
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    data = response.json()  # Get JSON data

    # ✅ Debugging: Show API response
    st.write(f"🔍 DEBUG: API Response for {ticker}: {data}")

    # ✅ Ensure it's a valid list with data
    if isinstance(data, list) and len(data) > 0:
        return data[0]  # Return the first object
    else:
        return None  # Return None if no data is found

# ✅ Function to Fetch Financial Statements (Income, Balance, Cash Flow)
def fetch_financials(endpoint, ticker):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if isinstance(data, list) and len(data) > 0:
        return data[0]  # Return the latest available financial data
    else:
        return None

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

    **Latest Income Statement:**
    - Revenue: ${income_statement['revenue']:,}
    - Net Income: ${income_statement['netIncome']:,}
    - EPS: ${income_statement['eps']}

    **Latest Balance Sheet:**
    - Total Assets: ${balance_sheet['totalAssets']:,}
    - Total Liabilities: ${balance_sheet['totalLiabilities']:,}
    - Shareholder Equity: ${balance_sheet['totalStockholdersEquity']:,}

    **Latest Cash Flow Statement:**
    - Operating Cash Flow: ${cash_flow['operatingCashFlow']:,}
    - Free Cash Flow: ${cash_flow['freeCashFlow']:,}

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
        st.error("❌ API keys are missing. Ensure they are set in Streamlit Secrets or GitHub Actions.")
    else:
        with st.spinner("Fetching stock data..."):
            company = fetch_stock_profile(ticker)
            income_data = fetch_financials("income-statement", ticker)
            balance_data = fetch_financials("balance-sheet-statement", ticker)
            cash_flow_data = fetch_financials("cash-flow-statement", ticker)

        # ✅ If company data exists, display it
        if company:
            st.subheader(f"📊 {company['companyName']} ({company['symbol']})")
            st.image(company["image"], width=100)

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
            if income_data:
                st.subheader("📜 Income Statement (Latest Year)")
                st.write(income_data)
            else:
                st.warning("⚠️ No Income Statement data available.")

            if balance_data:
                st.subheader("📊 Balance Sheet (Latest Year)")
                st.write(balance_data)
            else:
                st.warning("⚠️ No Balance Sheet data available.")

            if cash_flow_data:
                st.subheader("💰 Cash Flow Statement (Latest Year)")
                st.write(cash_flow_data)
            else:
                st.warning("⚠️ No Cash Flow Statement data available.")

            # ✅ AI-Powered Stock Analysis
            if income_data and balance_data and cash_flow_data:
                with st.spinner("🤖 Analyzing with GPT-4..."):
                    ai_analysis = analyze_stock_with_ai(company, income_data, balance_data, cash_flow_data)

                st.subheader("🤖 AI Stock Assessment")
                st.write(ai_analysis)
            else:
                st.warning("⚠️ Not enough financial data for AI analysis.")
        else:
            st.error("⚠️ No data found for this ticker. Please check the ticker symbol and try again.")
