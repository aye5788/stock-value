import streamlit as st
import requests
import openai

# Load API Key from Streamlit Secrets
FMP_API_KEY = st.secrets["FMP_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

openai.api_key = OPENAI_API_KEY

# Function to fetch data from FMP
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to format large numbers
def format_large_number(number):
    return f"{number:,.0f}"

# Streamlit UI
st.title("📊 AI-Powered Stock Analysis Dashboard")

# Stock Ticker Input
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")

if st.button("Analyze Stock"):
    st.success("✅ API Keys loaded successfully! Fetching data...")

    # ---- Fetch Stock Profile (Market Cap & Current Price) ----
    profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    profile_data = fetch_data(profile_url)

    if profile_data:
        stock_price = profile_data[0]['price']
        market_cap = profile_data[0]['mktCap']
        sector = profile_data[0]['sector']

        st.markdown(f"### 💰 **Market Cap**")
        st.markdown(f"**${format_large_number(market_cap)}**")

    # ---- Fetch DCF Valuation ----
    dcf_url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{ticker}?apikey={FMP_API_KEY}"
    dcf_data = fetch_data(dcf_url)

    if dcf_data:
        dcf_value = dcf_data[0]['dcf']
        difference = ((stock_price - dcf_value) / dcf_value) * 100

        st.markdown("### 🌟 **DCF Valuation**")
        st.markdown(f"📉 **Intrinsic Value (DCF):** ${dcf_value:.2f}")
        st.markdown(f"💲 **Current Stock Price:** ${stock_price:.2f}")
        st.markdown(f"📊 **Difference:** {difference:.2f}%")

    # ---- Fetch Balance Sheet ----
    balance_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={FMP_API_KEY}&limit=1"
    balance_data = fetch_data(balance_url)

    if balance_data:
        latest_balance = balance_data[0]
        total_assets = latest_balance['totalAssets']
        total_liabilities = latest_balance['totalLiabilities']
        shareholder_equity = latest_balance['totalStockholdersEquity']

        st.markdown("### 🏦 **Balance Sheet (Latest Year)**")
        st.markdown(f"**Total Assets:** ${format_large_number(total_assets)}")
        st.markdown(f"**Total Liabilities:** ${format_large_number(total_liabilities)}")
        st.markdown(f"**Shareholder Equity:** ${format_large_number(shareholder_equity)}")

    # ---- Fetch Cash Flow Statement ----
    cashflow_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={FMP_API_KEY}&limit=1"
    cashflow_data = fetch_data(cashflow_url)

    if cashflow_data:
        latest_cf = cashflow_data[0]
        operating_cash_flow = latest_cf['operatingCashFlow']
        capex = latest_cf['capitalExpenditure']
        free_cash_flow = latest_cf['freeCashFlow']

        st.markdown("### 💵 **Cash Flow Statement (Latest Year)**")
        st.markdown(f"**Operating Cash Flow:** ${format_large_number(operating_cash_flow)}")
        st.markdown(f"**Capital Expenditures:** ${format_large_number(capex)}")
        st.markdown(f"**Free Cash Flow:** ${format_large_number(free_cash_flow)}")

    # ---- Fetch Financial Ratios ----
    ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={FMP_API_KEY}&limit=1"
    ratios_data = fetch_data(ratios_url)

    if ratios_data:
        latest_ratios = ratios_data[0]
        pe_ratio = latest_ratios['priceEarningsRatio']
        roe = latest_ratios['returnOnEquity']
        debt_to_equity = latest_ratios['debtEquityRatio']

        st.markdown("### 📊 **Key Financial Ratios**")
        st.markdown(f"📈 **P/E Ratio:** {pe_ratio:.2f}")
        st.markdown(f"🏦 **ROE:** {roe:.2f}")
        st.markdown(f"⚖️ **Debt/Equity Ratio:** {debt_to_equity:.2f}")

    # ---- Fetch Sector P/E Ratio ----
    sector_pe_url = f"https://financialmodelingprep.com/api/v4/sector_price_earning_ratio?date=2023-10-10&exchange=NYSE&apikey={FMP_API_KEY}"
    sector_pe_data = fetch_data(sector_pe_url)

    sector_pe = None
    if sector_pe_data:
        for entry in sector_pe_data:
            if entry['sector'] == sector:
                sector_pe = entry['pe']

    # ---- Fetch Altman Z-Score & Piotroski Score ----
    score_url = f"https://financialmodelingprep.com/api/v4/score?symbol={ticker}&apikey={FMP_API_KEY}"
    score_data = fetch_data(score_url)

    if score_data:
        latest_score = score_data[0]
        altman_z = latest_score["altmanZScore"]
        piotroski_score = latest_score["piotroskiScore"]

        st.markdown("### 🏆 **Financial Health Scores**")
        st.markdown(f"📉 **Altman Z-Score:** {altman_z:.2f}")
        st.markdown(f"📊 **Piotroski Score:** {piotroski_score:.2f}")

    # ---- AI Insights Section ----
    st.markdown("### 🤖 **AI Insights**")

    ai_prompt = f"""
    Analyze {ticker} based on the following:
    - Stock Price: ${stock_price}
    - DCF Intrinsic Value: ${dcf_value}
    - Price Difference to DCF: {difference:.2f}%
    - P/E Ratio: {pe_ratio:.2f}
    - Sector: {sector}
    - Sector P/E Ratio: {sector_pe}
    - ROE: {roe:.2f}
    - Debt/Equity Ratio: {debt_to_equity:.2f}
    - Altman Z-Score: {altman_z:.2f}
    - Piotroski Score: {piotroski_score:.2f}

    Provide a **concise investment analysis** based on these metrics.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an AI financial analyst."},
                      {"role": "user", "content": ai_prompt}]
        )
        ai_analysis = response['choices'][0]['message']['content']
        st.write(ai_analysis)

    except Exception as e:
        st.error("⚠️ AI analysis failed. Try again later.")
        st.error(str(e))


