import streamlit as st
import openai
import requests

# Load API Keys
FMP_API_KEY = "your_fmp_api_key"
OPENAI_API_KEY = "your_openai_api_key"

openai.api_key = OPENAI_API_KEY  # Set OpenAI API key

# Function to fetch data from FMP API
def fetch_fmp_data(endpoint, params={}):
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}?apikey={FMP_API_KEY}"
    response = requests.get(url, params=params)
    return response.json()

# Function to analyze stock
def analyze_stock(ticker):
    st.title("📊 AI-Powered Stock Analysis Dashboard")

    # Fetch Company Profile
    company_profile = fetch_fmp_data(f"profile/{ticker}")
    if not company_profile or "Error Message" in company_profile:
        st.error("No data found for this ticker. Please check the ticker symbol and try again.")
        return

    stock_price = company_profile[0]["price"]
    company_name = company_profile[0]["companyName"]
    sector = company_profile[0]["sector"]

    st.header(f"📌 {company_name} ({ticker})")

    # Fetch DCF Valuation
    dcf_data = fetch_fmp_data(f"discounted-cash-flow/{ticker}")
    dcf_value = dcf_data[0]["dcf"] if dcf_data else None

    # Fetch Balance Sheet
    balance_sheet = fetch_fmp_data(f"balance-sheet-statement/{ticker}&limit=1")[0]
    total_assets = balance_sheet["totalAssets"]
    total_liabilities = balance_sheet["totalLiabilities"]
    shareholder_equity = balance_sheet["totalStockholdersEquity"]

    # Fetch Cash Flow Statement
    cash_flow = fetch_fmp_data(f"cash-flow-statement/{ticker}&limit=1")[0]
    operating_cash_flow = cash_flow["operatingCashFlow"]
    capital_expenditures = cash_flow["capitalExpenditure"]
    free_cash_flow = cash_flow["freeCashFlow"]

    # Fetch Key Financial Ratios
    ratios = fetch_fmp_data(f"ratios/{ticker}&limit=1")[0]
    pe_ratio = ratios["priceEarningsRatio"]
    roe = ratios["returnOnEquity"]
    debt_equity_ratio = ratios["debtEquityRatio"]

    # Fetch Financial Health Scores
    financial_health = fetch_fmp_data(f"score?symbol={ticker}")[0]
    altman_z_score = financial_health["altmanZScore"]
    piotroski_score = financial_health["piotroskiScore"]

    # Fetch Sector PE Ratio
    sector_pe_data = fetch_fmp_data(f"sector_price_earning_ratio?date=latest")
    sector_pe = None
    for s in sector_pe_data:
        if s["sector"] == sector:
            sector_pe = s["pe"]
            break

    # Display DCF Valuation and Stock Price Comparison
    st.subheader("🌟 DCF Valuation")
    st.write(f"📉 **Intrinsic Value (DCF):** ${dcf_value:.2f}" if dcf_value else "DCF data not available.")
    st.write(f"💲 **Current Stock Price:** ${stock_price:.2f}")
    if dcf_value:
        difference = ((stock_price - dcf_value) / dcf_value) * 100
        st.write(f"📊 **Difference:** {difference:.2f}%")

    # Display Balance Sheet
    st.subheader("🏛️ Balance Sheet (Latest Year)")
    st.write(f"**Total Assets:** ${total_assets:,}")
    st.write(f"**Total Liabilities:** ${total_liabilities:,}")
    st.write(f"**Shareholder Equity:** ${shareholder_equity:,}")

    # Display Cash Flow Statement
    st.subheader("💰 Cash Flow Statement (Latest Year)")
    st.write(f"**Operating Cash Flow:** ${operating_cash_flow:,}")
    st.write(f"**Capital Expenditures:** ${capital_expenditures:,}")
    st.write(f"**Free Cash Flow:** ${free_cash_flow:,}")

    # Display Key Financial Ratios
    st.subheader("📊 Key Financial Ratios")
    st.write(f"📈 **P/E Ratio:** {pe_ratio:.2f}")
    st.write(f"🔄 **ROE:** {roe:.2f}")
    st.write(f"⚖️ **Debt/Equity Ratio:** {debt_equity_ratio:.2f}")

    # Display Financial Health Scores
    st.subheader("🏆 Financial Health Scores")
    st.write(f"🟢 **Altman Z-Score:** {altman_z_score:.2f}")
    st.write(f"🔵 **Piotroski Score:** {piotroski_score:.2f}")

    # AI-Powered Insights
    st.subheader("🤖 AI Insights")
    ai_prompt = (
        f"Analyze the financial health of {company_name} ({ticker}) based on the following metrics:\n\n"
        f"Stock Price: ${stock_price:.2f}\n"
        f"DCF Valuation: ${dcf_value:.2f}\n"
        f"Difference between Price & DCF: {difference:.2f}%\n"
        f"P/E Ratio: {pe_ratio:.2f}\n"
        f"Sector P/E Ratio: {sector_pe if sector_pe else 'N/A'}\n"
        f"ROE: {roe:.2f}\n"
        f"Debt/Equity Ratio: {debt_equity_ratio:.2f}\n"
        f"Altman Z-Score: {altman_z_score:.2f}\n"
        f"Piotroski Score: {piotroski_score:.2f}\n"
        f"Based on these metrics, assess whether {company_name} is financially healthy, undervalued, or overvalued."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an AI financial analyst."},
                      {"role": "user", "content": ai_prompt}]
        )
        ai_analysis = response.choices[0].message.content  # ✅ NEW API FORMAT
        st.write(ai_analysis)
    except Exception as e:
        st.warning("⚠️ AI analysis failed. Try again later.")
        st.error(str(e))

# Streamlit App UI
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")
if st.button("Analyze Stock"):
    analyze_stock(ticker)

