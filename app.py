import streamlit as st
import requests
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Streamlit Config (MUST BE FIRST)
st.set_page_config(page_title="📈 AI Stock Analyzer", layout="wide")

st.title("📊 AI-Powered Stock Analysis Dashboard")

# API Keys
FMP_API_KEY = os.getenv("FMP_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not FMP_API_KEY or not OPENAI_API_KEY:
    st.error("❌ API keys are missing. Ensure they are set in your environment variables.")
    st.stop()

# User Input
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL")


# Function to fetch stock profile (includes current price)
def fetch_stock_profile(ticker):
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch discounted cash flow (DCF) valuation
def fetch_dcf_valuation(ticker):
    url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch balance sheet
def fetch_balance_sheet(ticker):
    url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={FMP_API_KEY}&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch cash flow statement
def fetch_cash_flow(ticker):
    url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={FMP_API_KEY}&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch financial ratios
def fetch_financial_ratios(ticker):
    url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={FMP_API_KEY}&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch financial score
def fetch_financial_score(ticker):
    url = f"https://financialmodelingprep.com/api/v4/score?symbol={ticker}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Fetch data
profile = fetch_stock_profile(ticker)
dcf_data = fetch_dcf_valuation(ticker)
balance_sheet = fetch_balance_sheet(ticker)
cash_flow = fetch_cash_flow(ticker)
financial_ratios = fetch_financial_ratios(ticker)
financial_score = fetch_financial_score(ticker)

if profile and dcf_data and balance_sheet and cash_flow and financial_ratios and financial_score:
    
    # Extract relevant values
    current_price = float(profile[0]["price"])
    dcf_value = float(dcf_data[0]["dcf"])
    dcf_difference = ((current_price - dcf_value) / dcf_value) * 100  # Percentage difference

    latest_balance = balance_sheet[0]
    latest_cash_flow = cash_flow[0]
    latest_ratios = financial_ratios[0]
    latest_score = financial_score[0]  # FIXED: Defining `latest_score`

    # Display Market Cap
    st.markdown(f"### 💰 Market Cap\n**${profile[0]['mktCap']:,}**")

    # Display DCF Valuation
    st.markdown("### 🔆 DCF Valuation")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📉 Intrinsic Value (DCF)**\n${dcf_value:,.2f}")
    with col2:
        st.markdown(f"**💲 Current Stock Price**\n${current_price:,.2f}")
        st.markdown(f"**📊 Difference**: {dcf_difference:.2f}%")

    # Display Balance Sheet
    st.markdown("### 🏦 Balance Sheet (Latest Year)")
    st.markdown(f"**Total Assets**: ${latest_balance['totalAssets']:,}")
    st.markdown(f"**Total Liabilities**: ${latest_balance['totalLiabilities']:,}")
    st.markdown(f"**Shareholder Equity**: ${latest_balance['totalStockholdersEquity']:,}")

    # Display Cash Flow Statement
    st.markdown("### 💵 Cash Flow Statement (Latest Year)")
    st.markdown(f"**Operating Cash Flow**: ${latest_cash_flow['operatingCashFlow']:,}")
    st.markdown(f"**Capital Expenditures**: ${latest_cash_flow['capitalExpenditure']:,}")
    st.markdown(f"**Free Cash Flow**: ${latest_cash_flow['freeCashFlow']:,}")

    # AI Insights Section
    st.markdown("### 🤖 AI Insights")
    ai_prompt = f"""
    The discounted cash flow (DCF) valuation for {ticker} is ${dcf_value:,.2f}, while the current stock price is ${current_price:,.2f}.
    The balance sheet shows total assets of ${latest_balance['totalAssets']:,} and total liabilities of ${latest_balance['totalLiabilities']:,}.
    The company has a free cash flow of ${latest_cash_flow['freeCashFlow']:,}.

    The company's financial score includes:
    - **Altman Z-Score**: {latest_score['altmanZScore']}
    - **Piotroski Score**: {latest_score['piotroskiScore']}

    Provide a brief fundamental analysis of {ticker} based on these metrics.
    """

    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a financial analyst."},
                      {"role": "user", "content": ai_prompt}],
        )
        st.write(response["choices"][0]["message"]["content"])
    except Exception as e:
        st.error(f"⚠️ AI analysis failed. Try again later. Error: {e}")

else:
    st.warning("⚠️ No data found for this ticker. Please check the ticker symbol and try again.")
