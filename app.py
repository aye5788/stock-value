import streamlit as st
import requests
from openai import OpenAI

# ✅ Load API keys correctly
FMP_API_KEY = st.secrets["FMP_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to fetch company profile data
def get_company_profile(ticker):
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    return response.json()[0] if response.status_code == 200 else None

# Function to fetch sector P/E ratio
def get_sector_pe_ratio(sector):
    url = f"https://financialmodelingprep.com/api/v4/sector_price_earning_ratio?exchange=NYSE&apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        sector_data = response.json()
        for item in sector_data:
            if item["sector"] == sector:
                return item["pe"]
    return None

# Function to fetch key financial ratios
def get_financial_ratios(ticker):
    url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    return response.json()[0] if response.status_code == 200 else None

# Streamlit UI
st.title("📊 AI-Powered Stock Analysis Dashboard")

# User input for stock ticker
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")

if st.button("Analyze Stock"):
    st.write("🔄 Fetching data...")

    # ✅ Fetch company profile
    company_profile = get_company_profile(ticker)
    if not company_profile:
        st.error("❌ No data found for this ticker. Please check the symbol and try again.")
    else:
        st.header(f"{company_profile['companyName']} ({ticker})")
        st.write(f"**Sector:** {company_profile['sector']}")
        st.write(f"**Current Stock Price:** ${company_profile['price']}")

        # ✅ Fetch financial ratios
        ratios = get_financial_ratios(ticker)
        sector_pe = get_sector_pe_ratio(company_profile['sector'])

        if ratios:
            st.subheader("📌 Key Financial Ratios")
            st.write(f"🔹 **P/E Ratio:** {ratios['peRatio']}")
            if sector_pe:
                st.write(f"🔹 **Sector P/E Ratio:** {sector_pe}")
            st.write(f"🔹 **ROE:** {ratios['returnOnEquity']}")
            st.write(f"🔹 **Debt/Equity Ratio:** {ratios['debtEquityRatio']}")

        # AI Insights using OpenAI
        st.subheader("🤖 AI Insights")

        ai_prompt = f"""
        Analyze the financial health of {company_profile['companyName']} ({ticker}).
        The P/E ratio is {ratios['peRatio']} and the sector P/E ratio is {sector_pe}.
        ROE is {ratios['returnOnEquity']}, and the Debt/Equity ratio is {ratios['debtEquityRatio']}.
        Provide insights on whether this stock is undervalued or overvalued.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": ai_prompt},
                ],
            )
            ai_analysis = response.choices[0].message.content
        except Exception as e:
            ai_analysis = f"⚠️ AI analysis failed. Error: {e}"

        st.write(ai_analysis)

