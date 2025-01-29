import streamlit as st
import requests
import openai

# ✅ Load API keys correctly
FMP_API_KEY = st.secrets["api_keys"]["FMP_API_KEY"]
OPENAI_API_KEY = st.secrets["api_keys"]["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# 🎨 UI Header
st.title("📊 AI-Powered Stock Analysis Dashboard")

# 🔍 User Input: Ticker Symbol
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")

if st.button("Analyze Stock"):
    # 🚀 Fetch Data from Financial Modeling Prep (FMP)
    try:
        # 📌 Fetch Company Profile (for sector and price)
        profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
        profile_data = requests.get(profile_url).json()

        if not profile_data or "symbol" not in profile_data[0]:
            st.error("No data found for this ticker. Please check the ticker symbol and try again.")
            st.stop()

        company = profile_data[0]
        company_name = company["companyName"]
        stock_price = float(company["price"])
        sector = company["sector"]

        # 📌 Fetch DCF Valuation
        dcf_url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{ticker}?apikey={FMP_API_KEY}"
        dcf_data = requests.get(dcf_url).json()
        intrinsic_value = float(dcf_data[0]["dcf"]) if dcf_data else None

        # 📌 Fetch Balance Sheet
        balance_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={FMP_API_KEY}&limit=1"
        balance_data = requests.get(balance_url).json()
        latest_balance = balance_data[0] if balance_data else {}

        # 📌 Fetch Cash Flow Statement
        cashflow_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={FMP_API_KEY}&limit=1"
        cashflow_data = requests.get(cashflow_url).json()
        latest_cashflow = cashflow_data[0] if cashflow_data else {}

        # 📌 Fetch Ratios
        ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={FMP_API_KEY}&limit=1"
        ratios_data = requests.get(ratios_url).json()
        latest_ratios = ratios_data[0] if ratios_data else {}

        # 📌 Fetch Financial Score (Altman Z & Piotroski)
        score_url = f"https://financialmodelingprep.com/api/v4/score?symbol={ticker}&apikey={FMP_API_KEY}"
        score_data = requests.get(score_url).json()
        latest_score = score_data[0] if score_data else {}

        # 📌 Fetch Sector P/E for Comparison
        sector_pe_url = f"https://financialmodelingprep.com/api/v4/sector_price_earning_ratio?date=latest&exchange=NYSE&apikey={FMP_API_KEY}"
        sector_pe_data = requests.get(sector_pe_url).json()

        sector_pe = None
        for sec in sector_pe_data:
            if sec["sector"] == sector:
                sector_pe = float(sec["pe"])
                break

        # 🎯 Display Stock Analysis Data
        st.write(f"## 🏢 {company_name} ({ticker})")

        # 📌 DCF Valuation vs Stock Price
        if intrinsic_value:
            st.markdown("### 🌟 DCF Valuation")
            st.write(f"📄 **Intrinsic Value (DCF):** ${intrinsic_value:.2f}")

            # 📈 Stock Price and % Difference
            st.write("### 💰 Stock Price")
            st.write(f"💵 **Current Price:** ${stock_price:.2f}")
            difference = ((stock_price - intrinsic_value) / intrinsic_value) * 100
            st.write(f"📊 **Difference:** {difference:.2f}%")

        # 📌 Balance Sheet
        st.markdown("### 🏦 Balance Sheet (Latest Year)")
        st.write(f"**Total Assets:** ${latest_balance.get('totalAssets', 'N/A'):,}")
        st.write(f"**Total Liabilities:** ${latest_balance.get('totalLiabilities', 'N/A'):,}")
        st.write(f"**Shareholder Equity:** ${latest_balance.get('totalStockholdersEquity', 'N/A'):,}")

        # 📌 Cash Flow Statement
        st.markdown("### 💵 Cash Flow Statement (Latest Year)")
        st.write(f"**Operating Cash Flow:** ${latest_cashflow.get('operatingCashFlow', 'N/A'):,}")
        st.write(f"**Capital Expenditures:** ${latest_cashflow.get('capitalExpenditure', 'N/A'):,}")
        st.write(f"**Free Cash Flow:** ${latest_cashflow.get('freeCashFlow', 'N/A'):,}")

        # 📌 Key Ratios
        st.markdown("### 📊 Key Financial Ratios")
        st.write(f"📌 **P/E Ratio:** {latest_ratios.get('priceEarningsRatio', 'N/A')}")
        st.write(f"📌 **ROE:** {latest_ratios.get('returnOnEquity', 'N/A')}")
        st.write(f"📌 **Debt/Equity Ratio:** {latest_ratios.get('debtEquityRatio', 'N/A')}")

        # 📌 Financial Health Scores
        st.markdown("### 🏆 Financial Health Scores")
        st.write(f"📊 **Altman Z-Score:** {latest_score.get('altmanZScore', 'N/A')}")
        st.write(f"📈 **Piotroski Score:** {latest_score.get('piotroskiScore', 'N/A')}")

        # 📌 Sector P/E Comparison
        if sector_pe:
            st.markdown("### 🔍 Sector P/E Comparison")
            st.write(f"🏢 **Sector:** {sector}")
            st.write(f"📌 **Sector P/E Ratio:** {sector_pe:.2f}")
            if latest_ratios.get("priceEarningsRatio"):
                pe_ratio = latest_ratios["priceEarningsRatio"]
                st.write(f"📈 **Stock P/E Ratio:** {pe_ratio}")
                difference_pe = ((pe_ratio - sector_pe) / sector_pe) * 100
                st.write(f"📊 **P/E Difference from Sector:** {difference_pe:.2f}%")

        # 🧠 AI Insights (GPT-4)
        st.markdown("### 🤖 AI Insights")
        try:
            prompt = f"""
            Analyze the financial health and valuation of {company_name} ({ticker}) based on:
            - DCF valuation (${intrinsic_value:.2f}) vs Current Price (${stock_price:.2f})
            - P/E Ratio ({latest_ratios.get('priceEarningsRatio', 'N/A')}) vs Sector P/E ({sector_pe})
            - Altman Z-Score: {latest_score.get('altmanZScore', 'N/A')}
            - Piotroski Score: {latest_score.get('piotroskiScore', 'N/A')}
            - Balance Sheet, Cash Flow, and Key Ratios.
            """
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "Provide a financial analysis."},
                          {"role": "user", "content": prompt}]
            )
            st.write(response["choices"][0]["message"]["content"])
        except Exception as e:
            st.warning("⚠ AI analysis failed. Try again later.")
            st.error(str(e))

    except Exception as e:
        st.error("An error occurred. Please try again later.")
        st.error(str(e))

