import streamlit as st
import requests
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
FMP_API_KEY = os.getenv("FMP_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API Key
openai.api_key = OPENAI_API_KEY

# Function to fetch data from FMP API
def fetch_fmp_data(endpoint, symbol):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{symbol}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Streamlit App Layout
st.set_page_config(page_title="AI-Powered Stock Analysis", layout="wide")

st.title("📊 AI-Powered Stock Analysis Dashboard")

# Stock Input
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")
if st.button("Analyze Stock"):
    
    st.success("✅ API Keys loaded successfully! Fetching data...")

    # Fetch Data
    profile = fetch_fmp_data("profile", ticker)
    balance_sheet = fetch_fmp_data("balance-sheet-statement", ticker)
    cash_flow = fetch_fmp_data("cash-flow-statement", ticker)
    dcf = fetch_fmp_data("discounted-cash-flow", ticker)

    # Validate data
    if not profile or not balance_sheet or not cash_flow or not dcf:
        st.error("⚠️ No data found for this ticker. Please check the symbol and try again.")
    else:
        # Extract Key Metrics
        company = profile[0]
        dcf_value = dcf[0]["dcf"] if dcf and "dcf" in dcf[0] else "N/A"

        # Display Company Info
        st.markdown(f"### 🏛️ {company['companyName']} ({company['symbol']})")
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Stock Price", f"${company['price']}")
        col2.metric("📉 52-Week Low", f"${company['range'].split('-')[0].strip()}")
        col3.metric("📈 52-Week High", f"${company['range'].split('-')[1].strip()}")
        st.metric("🏦 Market Cap", f"${company['mktCap']:,.0f}")

        # **Discounted Cash Flow (DCF) Valuation**
        st.subheader("💡 DCF Valuation")
        st.metric("📊 Intrinsic Value (DCF)", f"${dcf_value}")

        # **Balance Sheet**
        st.subheader("📜 Balance Sheet (Latest Year)")
        latest_balance = balance_sheet[0]
        st.write(f"**Total Assets:** ${latest_balance['totalAssets']:,.0f}")
        st.write(f"**Total Liabilities:** ${latest_balance['totalLiabilities']:,.0f}")
        st.write(f"**Shareholder Equity:** ${latest_balance['totalStockholdersEquity']:,.0f}")

        # **Cash Flow Statement**
        st.subheader("💵 Cash Flow Statement (Latest Year)")
        latest_cashflow = cash_flow[0]
        st.write(f"**Operating Cash Flow:** ${latest_cashflow['operatingCashFlow']:,.0f}")
        st.write(f"**Capital Expenditures:** ${latest_cashflow['capitalExpenditure']:,.0f}")
        st.write(f"**Free Cash Flow:** ${latest_cashflow['freeCashFlow']:,.0f}")

        # **AI Interpretation of DCF & Ratios**
        st.subheader("🤖 AI Insights")
        ai_prompt = f"""
        The company {company['companyName']} ({ticker}) has a stock price of ${company['price']} and a discounted cash flow (DCF) valuation of ${dcf_value}.
        - Market Cap: ${company['mktCap']:,.0f}
        - Total Assets: ${latest_balance['totalAssets']:,.0f}
        - Total Liabilities: ${latest_balance['totalLiabilities']:,.0f}
        - Shareholder Equity: ${latest_balance['totalStockholdersEquity']:,.0f}
        - Free Cash Flow: ${latest_cashflow['freeCashFlow']:,.0f}

        Based on this data, summarize the **DCF valuation's significance** and what it means for investors. Also, provide insight into the company's **financial health and investment potential**.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": ai_prompt}
                ]
            )
            ai_output = response["choices"][0]["message"]["content"]
            st.write(ai_output)

        except openai.error.OpenAIError as e:
            st.error(f"⚠️ AI analysis failed. Error: {str(e)}")


