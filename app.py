import streamlit as st
import requests
import openai
import os

# Load API Keys from Secrets
FMP_API_KEY = os.getenv("FMP_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Function to Fetch Data from FMP
def fetch_fmp_data(endpoint, symbol, params=""):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{symbol}?apikey={FMP_API_KEY}&{params}"
    response = requests.get(url)
    
    # Debugging output
    st.write(f"📡 API Request: {url}")
    st.write(f"📡 API Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        return response.json()
    return None

# Streamlit App UI
st.set_page_config(page_title="AI-Powered Stock Analysis", layout="wide")

st.markdown("## 📊 AI-Powered Stock Analysis Dashboard")
st.text_input("Enter Stock Ticker (e.g., AAPL)", key="ticker")

if st.button("Analyze Stock"):
    ticker = st.session_state.ticker.strip().upper()
    
    if not ticker:
        st.warning("⚠️ Please enter a stock ticker.")
    else:
        st.success("✅ API Keys loaded successfully! Fetching data...")

        # Fetch Data
        profile = fetch_fmp_data("profile", ticker)
        dcf_data = fetch_fmp_data("discounted-cash-flow", ticker)
        balance_sheet = fetch_fmp_data("balance-sheet-statement", ticker, "limit=1")
        cash_flow = fetch_fmp_data("cash-flow-statement", ticker, "limit=1")
        key_ratios = fetch_fmp_data("ratios", ticker, "period=annual&limit=1")
        financial_score = fetch_fmp_data("score", ticker)

        if not profile or "Error Message" in profile:
            st.error("⚠️ No data found for this ticker. Please check the ticker symbol and try again.")
        else:
            company = profile[0]
            stock_price = company.get("price", "N/A")
            market_cap = company.get("mktCap", "N/A")

            # Fetch DCF Valuation
            dcf_value = dcf_data[0].get("dcf", "N/A") if dcf_data else "N/A"
            dcf_diff = round(((stock_price - dcf_value) / stock_price) * 100, 2) if stock_price != "N/A" and dcf_value != "N/A" else "N/A"

            # Display Company Info
            st.markdown(f"### **{company['companyName']} ({ticker})**")

            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Stock Price", f"${stock_price}")
            col2.metric("🏢 Market Cap", f"${market_cap:,}")
            col3.metric("📉 DCF Valuation", f"${dcf_value} ({dcf_diff}% Difference)")

            # Display Balance Sheet
            if balance_sheet:
                latest_bs = balance_sheet[0]
                st.markdown("### 📜 **Balance Sheet (Latest Year)**")
                st.write(f"**Total Assets:** ${latest_bs['totalAssets']:,}")
                st.write(f"**Total Liabilities:** ${latest_bs['totalLiabilities']:,}")
                st.write(f"**Shareholder Equity:** ${latest_bs['totalStockholdersEquity']:,}")

            # Display Cash Flow
            if cash_flow:
                latest_cf = cash_flow[0]
                st.markdown("### 💸 **Cash Flow Statement (Latest Year)**")
                st.write(f"**Operating Cash Flow:** ${latest_cf['operatingCashFlow']:,}")
                st.write(f"**Capital Expenditures:** ${latest_cf['capitalExpenditure']:,}")
                st.write(f"**Free Cash Flow:** ${latest_cf['freeCashFlow']:,}")

            # Display Key Ratios
            if key_ratios:
                latest_ratios = key_ratios[0]
                st.markdown("### 📊 **Key Financial Ratios**")
                st.write(f"**P/E Ratio:** {latest_ratios['priceEarningsRatio']}")
                st.write(f"**Return on Equity (ROE):** {latest_ratios['returnOnEquity']}")
                st.write(f"**Debt-to-Equity Ratio:** {latest_ratios['debtEquityRatio']}")
                st.write(f"**Current Ratio:** {latest_ratios['currentRatio']}")

            # Display Financial Score (Piotroski Score Included)
            if financial_score:
                latest_score = financial_score[0]
                st.markdown("### 📈 **Financial Score & Health**")
                st.write(f"**Altman Z-Score:** {latest_score['altmanZScore']}")
                st.write(f"**Piotroski Score:** {latest_score['piotroskiScore']} (Higher is better)")
                st.write(f"**Working Capital:** ${latest_score['workingCapital']:,}")
                st.write(f"**EBIT:** ${latest_score['ebit']:,}")

            # AI Interpretation
            st.markdown("## 🤖 AI Insights")
            with st.spinner("Analyzing financial health..."):
                analysis_prompt = f"""
                Analyze the stock {company['companyName']} ({ticker}) using the provided data:
                - **DCF Valuation**: ${dcf_value} (Current Price: ${stock_price}, Difference: {dcf_diff}%)
                - **P/E Ratio**: {latest_ratios['priceEarningsRatio']}
                - **ROE**: {latest_ratios['returnOnEquity']}
                - **Debt-to-Equity Ratio**: {latest_ratios['debtEquityRatio']}
                - **Altman Z-Score**: {latest_score['altmanZScore']}
                - **Piotroski Score**: {latest_score['piotroskiScore']}
                - **Operating Cash Flow**: ${latest_cf['operatingCashFlow']:,}
                - **Free Cash Flow**: ${latest_cf['freeCashFlow']:,}

                Provide an investment analysis based on valuation, profitability, and financial health.
                """
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "system", "content": "You are a financial analyst."},
                                  {"role": "user", "content": analysis_prompt}],
                        max_tokens=300
                    )
                    ai_insight = response["choices"][0]["message"]["content"]
                    st.markdown(ai_insight)
                except openai.error.OpenAIError as e:
                    st.error(f"⚠️ AI analysis failed. Try again later. Error: {e}")
