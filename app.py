import streamlit as st
import requests
import openai

# ✅ Load API keys correctly from secrets
FMP_API_KEY = st.secrets["api_keys"]["FMP_API_KEY"]
OPENAI_API_KEY = st.secrets["api_keys"]["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY  # Set OpenAI API key

# 🎨 Streamlit App Title
st.title("📊 AI-Powered Stock Analysis Dashboard")

# 🔍 User Input for Stock Ticker
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")

if st.button("Analyze Stock"):
    try:
        # ✅ Fetch Company Profile (includes sector)
        profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
        profile_data = requests.get(profile_url).json()
        
        if not profile_data or "error" in profile_data:
            st.error("No data found for this ticker. Please check the symbol and try again.")
            st.stop()

        company_name = profile_data[0]["companyName"]
        sector = profile_data[0]["sector"]
        stock_price = profile_data[0]["price"]

        # ✅ Fetch Financial Ratios
        ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={FMP_API_KEY}"
        ratios_data = requests.get(ratios_url).json()

        if not ratios_data or isinstance(ratios_data, dict):
            st.error("Failed to retrieve financial ratios.")
            st.stop()

        latest_ratios = ratios_data[0]
        pe_ratio = latest_ratios.get("priceEarningsRatio", "N/A")
        roe = latest_ratios.get("returnOnEquity", "N/A")
        debt_to_equity = latest_ratios.get("debtEquityRatio", "N/A")

        # ✅ Fetch Sector P/E Ratio for comparison
        sector_pe_url = f"https://financialmodelingprep.com/api/v4/sector_price_earning_ratio?date=2023-10-10&exchange=NYSE&apikey={FMP_API_KEY}"
        sector_pe_data = requests.get(sector_pe_url).json()
        sector_pe_ratio = next((item["pe"] for item in sector_pe_data if item["sector"] == sector), "N/A")

        # ✅ Fetch Financial Health Scores
        health_url = f"https://financialmodelingprep.com/api/v3/financial-growth/{ticker}?apikey={FMP_API_KEY}"
        health_data = requests.get(health_url).json()

        if not health_data or isinstance(health_data, dict):
            st.error("Failed to retrieve financial health scores.")
            st.stop()

        latest_health = health_data[0]
        altman_z_score = latest_health.get("altmanZScore", "N/A")
        piotroski_score = latest_health.get("piotroskiScore", "N/A")

        # 🎯 Display Results
        st.markdown(f"## {company_name} ({ticker})")
        st.markdown(f"**Sector:** {sector}")
        st.markdown(f"**Current Stock Price:** ${stock_price}")

        # 📊 Key Financial Ratios
        st.subheader("📊 Key Financial Ratios")
        st.write(f"🔹 **P/E Ratio:** {pe_ratio}")
        st.write(f"🔹 **Sector P/E Ratio:** {sector_pe_ratio}")
        st.write(f"🔹 **ROE:** {roe}")
        st.write(f"🔹 **Debt/Equity Ratio:** {debt_to_equity}")

        # 🏆 Financial Health Scores
        st.subheader("🏆 Financial Health Scores")
        st.write(f"🎖 **Altman Z-Score:** {altman_z_score}")
        st.write(f"📊 **Piotroski Score:** {piotroski_score}")

        # 🧠 AI Insights
        st.subheader("🤖 AI Insights")
        ai_prompt = f"""
        Analyze the financial health of {company_name} ({ticker}) based on the following:
        - Sector: {sector}
        - Current Price: ${stock_price}
        - P/E Ratio: {pe_ratio} vs. Sector P/E: {sector_pe_ratio}
        - ROE: {roe}
        - Debt/Equity Ratio: {debt_to_equity}
        - Altman Z-Score: {altman_z_score}
        - Piotroski Score: {piotroski_score}

        Provide insights on whether this stock is overvalued or undervalued, and whether it is financially healthy.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a financial analyst."},
                          {"role": "user", "content": ai_prompt}],
            )
            ai_analysis = response["choices"][0]["message"]["content"]
        except Exception as e:
            ai_analysis = f"⚠️ AI analysis failed. Error: {e}"

        st.markdown(ai_analysis)

    except Exception as e:
        st.error(f"An error occurred. Please try again later.\n\nError: {e}")

