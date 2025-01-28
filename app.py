import streamlit as st
import requests
import openai
import os

# Load API Keys from Streamlit Secrets
FMP_API_KEY = os.getenv("FMP_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Set OpenAI API Key
openai.api_key = OPENAI_API_KEY

# Function to fetch data from Financial Modeling Prep API
def fetch_fmp_data(endpoint, symbol):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{symbol}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Function to format large numbers
def format_large_number(value):
    return f"${value:,.0f}"

# Function to calculate percentage difference
def calculate_percentage_difference(current_price, dcf_value):
    return ((current_price - dcf_value) / dcf_value) * 100 if dcf_value else None

# Streamlit UI
st.title("📊 AI-Powered Stock Analysis Dashboard")

# Input field for stock symbol
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")

if st.button("Analyze Stock"):
    st.success("✅ API Keys loaded successfully! Fetching data...")

    # Fetch Financial Data
    stock_profile = fetch_fmp_data("profile", ticker)
    dcf_data = fetch_fmp_data("discounted-cash-flow", ticker)
    balance_sheet = fetch_fmp_data("balance-sheet-statement", ticker)
    cash_flow = fetch_fmp_data("cash-flow-statement", ticker)
    key_ratios = fetch_fmp_data("ratios", ticker)
    financial_score = fetch_fmp_data("score", ticker)

    if stock_profile and dcf_data and balance_sheet and cash_flow and key_ratios and financial_score:
        stock_profile = stock_profile[0]
        dcf_value = dcf_data[0].get("dcf", 0)
        current_price = stock_profile.get("price", 0)
        percentage_diff = calculate_percentage_difference(current_price, dcf_value)

        # Display Stock Price & DCF Comparison
        st.markdown("### 💡 DCF Valuation vs. Market Price")
        col1, col2, col3 = st.columns(3)
        col1.metric("Intrinsic Value (DCF)", format_large_number(dcf_value))
        col2.metric("Current Price", format_large_number(current_price))
        col3.metric("% Difference", f"{percentage_diff:.2f}%", delta=percentage_diff, delta_color="inverse")

        # Balance Sheet Section
        latest_balance_sheet = balance_sheet[0]
        st.markdown("### 📜 **Balance Sheet (Latest Year)**")
        st.write(f"**Total Assets:** {format_large_number(latest_balance_sheet.get('totalAssets', 0))}")
        st.write(f"**Total Liabilities:** {format_large_number(latest_balance_sheet.get('totalLiabilities', 0))}")
        st.write(f"**Shareholder Equity:** {format_large_number(latest_balance_sheet.get('totalStockholdersEquity', 0))}")

        # Cash Flow Section
        latest_cash_flow = cash_flow[0]
        st.markdown("### 💵 **Cash Flow Statement (Latest Year)**")
        st.write(f"**Operating Cash Flow:** {format_large_number(latest_cash_flow.get('operatingCashFlow', 0))}")
        st.write(f"**Capital Expenditures:** {format_large_number(latest_cash_flow.get('capitalExpenditure', 0))}")
        st.write(f"**Free Cash Flow:** {format_large_number(latest_cash_flow.get('freeCashFlow', 0))}")

        # Key Ratios Section
        latest_ratios = key_ratios[0]
        st.markdown("### 📊 **Key Financial Ratios**")
        st.write(f"**Current Ratio:** {latest_ratios.get('currentRatio', 'N/A')}")
        st.write(f"**Quick Ratio:** {latest_ratios.get('quickRatio', 'N/A')}")
        st.write(f"**Debt-to-Equity Ratio:** {latest_ratios.get('debtEquityRatio', 'N/A')}")
        st.write(f"**Return on Equity (ROE):** {latest_ratios.get('returnOnEquity', 'N/A')}%")
        st.write(f"**Return on Assets (ROA):** {latest_ratios.get('returnOnAssets', 'N/A')}%")
        st.write(f"**Price-to-Earnings (P/E) Ratio:** {latest_ratios.get('priceEarningsRatio', 'N/A')}")
        st.write(f"**Enterprise Value/EBITDA:** {latest_ratios.get('enterpriseValueOverEBITDA', 'N/A')}")

        # AI Insights Section
        latest_financial_score = financial_score[0]
        piotroski_score = latest_financial_score.get("piotroskiScore", "N/A")

        st.markdown("### 🤖 **AI Insights**")

        # AI-Powered Analysis
        ai_prompt = f"""
        The discounted cash flow (DCF) valuation for {ticker} is {dcf_value:.2f}, while its current market price is {current_price:.2f}, 
        representing a {percentage_diff:.2f}% difference. Analyze whether the stock is overvalued or undervalued based on this data.

        Additionally, analyze the financial health using the following ratios:
        - **Current Ratio**: {latest_ratios.get('currentRatio', 'N/A')}
        - **Quick Ratio**: {latest_ratios.get('quickRatio', 'N/A')}
        - **Debt-to-Equity Ratio**: {latest_ratios.get('debtEquityRatio', 'N/A')}
        - **Return on Equity (ROE)**: {latest_ratios.get('returnOnEquity', 'N/A')}
        - **Return on Assets (ROA)**: {latest_ratios.get('returnOnAssets', 'N/A')}
        - **Price-to-Earnings (P/E) Ratio**: {latest_ratios.get('priceEarningsRatio', 'N/A')}
        - **Enterprise Value/EBITDA**: {latest_ratios.get('enterpriseValueOverEBITDA', 'N/A')}
        - **Piotroski Score**: {piotroski_score}

        Provide a detailed analysis considering these factors.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": ai_prompt}]
            )
            ai_analysis = response["choices"][0]["message"]["content"]
            st.write(ai_analysis)
        except Exception as e:
            st.error(f"⚠️ AI analysis failed. Error: {str(e)}")

    else:
        st.error("⚠️ No data found for this ticker. Please check the ticker symbol and try again.")
