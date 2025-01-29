import streamlit as st
import requests
import openai

# ✅ Load API keys correctly
FMP_API_KEY = st.secrets["FMP_API_KEY"]  # 🔥 FIXED: Now correctly accessing the key
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # 🔥 FIXED: Now correctly accessing the key

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# 🎨 Streamlit UI Setup
st.title("📊 AI-Powered Stock Analysis Dashboard")
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")

if st.button("Analyze Stock"):
    try:
        # ✅ Fetch DCF Valuation
        dcf_url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{ticker}?apikey={FMP_API_KEY}"
        dcf_data = requests.get(dcf_url).json()[0]
        dcf_value = float(dcf_data["dcf"])
        stock_price = float(dcf_data["Stock Price"])
        dcf_difference = ((stock_price - dcf_value) / dcf_value) * 100

        # ✅ Fetch Balance Sheet
        balance_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={FMP_API_KEY}&limit=1"
        balance_data = requests.get(balance_url).json()[0]
        total_assets = balance_data["totalAssets"]
        total_liabilities = balance_data["totalLiabilities"]
        shareholder_equity = balance_data["totalStockholdersEquity"]

        # ✅ Fetch Cash Flow Statement
        cashflow_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={FMP_API_KEY}&limit=1"
        cashflow_data = requests.get(cashflow_url).json()[0]
        operating_cash_flow = cashflow_data["operatingCashFlow"]
        capital_expenditures = cashflow_data["capitalExpenditure"]
        free_cash_flow = cashflow_data["freeCashFlow"]

        # ✅ Fetch Key Financial Ratios
        ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={FMP_API_KEY}&limit=1"
        ratios_data = requests.get(ratios_url).json()[0]
        pe_ratio = ratios_data["priceEarningsRatio"]
        roe = ratios_data["returnOnEquity"]
        debt_to_equity = ratios_data["debtEquityRatio"]

        # ✅ Fetch Financial Health Scores
        health_url = f"https://financialmodelingprep.com/api/v4/score?symbol={ticker}&apikey={FMP_API_KEY}"
        health_data = requests.get(health_url).json()[0]
        altman_z_score = health_data["altmanZScore"]
        piotroski_score = health_data["piotroskiScore"]

        # ✅ Fetch Sector and Compare P/E with Sector P/E
        profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
        profile_data = requests.get(profile_url).json()[0]
        stock_sector = profile_data["sector"]

        sector_pe_url = f"https://financialmodelingprep.com/api/v4/sector_price_earning_ratio?exchange=NYSE&apikey={FMP_API_KEY}"
        sector_pe_data = requests.get(sector_pe_url).json()
        sector_pe = next((s["pe"] for s in sector_pe_data if s["sector"] == stock_sector), None)

        # 🎯 **Display Data**
        st.markdown("## 🌟 DCF Valuation")
        st.markdown(f"📄 **Intrinsic Value (DCF)**: **${dcf_value:.2f}**")
        st.markdown(f"💰 **Current Stock Price**: **${stock_price:.2f}**")
        st.markdown(f"📊 **Difference**: {dcf_difference:.2f}%")

        st.markdown("## 📋 Balance Sheet (Latest Year)")
        st.write(f"**Total Assets**: ${total_assets:,.0f}")
        st.write(f"**Total Liabilities**: ${total_liabilities:,.0f}")
        st.write(f"**Shareholder Equity**: ${shareholder_equity:,.0f}")

        st.markdown("## 💵 Cash Flow Statement (Latest Year)")
        st.write(f"**Operating Cash Flow**: ${operating_cash_flow:,.0f}")
        st.write(f"**Capital Expenditures**: ${capital_expenditures:,.0f}")
        st.write(f"**Free Cash Flow**: ${free_cash_flow:,.0f}")

        st.markdown("## 📈 Key Financial Ratios")
        st.write(f"📊 **P/E Ratio**: {pe_ratio:.2f}")
        st.write(f"📈 **ROE**: {roe:.2f}")
        st.write(f"💳 **Debt/Equity Ratio**: {debt_to_equity:.2f}")

        if sector_pe:
            st.write(f"🏢 **Sector Average P/E (for {stock_sector})**: {sector_pe:.2f}")
            st.write(f"📉 **P/E Compared to Sector**: {'Overvalued' if pe_ratio > sector_pe else 'Undervalued'}")

        st.markdown("## 🏆 Financial Health Scores")
        st.write(f"🟢 **Altman Z-Score**: {altman_z_score:.2f}")
        st.write(f"🔵 **Piotroski Score**: {piotroski_score:.2f}")

        # ✅ **AI-Powered Insights**
        st.markdown("## 🤖 AI Insights")
        ai_prompt = f"""
        Based on the following financial metrics:
        - **DCF Valuation**: ${dcf_value:.2f} (Stock Price: ${stock_price:.2f}, Difference: {dcf_difference:.2f}%)
        - **Balance Sheet**: Total Assets: ${total_assets:,.0f}, Liabilities: ${total_liabilities:,.0f}, Equity: ${shareholder_equity:,.0f}
        - **Cash Flow**: Operating CF: ${operating_cash_flow:,.0f}, Free CF: ${free_cash_flow:,.0f}
        - **Key Ratios**: P/E Ratio: {pe_ratio:.2f}, ROE: {roe:.2f}, Debt/Equity: {debt_to_equity:.2f}
        - **Sector P/E**: {sector_pe:.2f} (Sector: {stock_sector})
        - **Financial Health**: Altman Z-Score: {altman_z_score:.2f}, Piotroski Score: {piotroski_score:.2f}

        Provide an analysis of the financial health and valuation of the stock.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a financial analyst."},
                          {"role": "user", "content": ai_prompt}]
            )
            ai_analysis = response["choices"][0]["message"]["content"]
            st.success("AI Analysis Generated Successfully!")
            st.write(ai_analysis)

        except Exception as e:
            st.error(f"AI analysis failed. Try again later. \n\nError: {str(e)}")

    except Exception as e:
        st.error(f"An error occurred. Please try again later.\n\nError: {str(e)}")
