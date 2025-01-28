import streamlit as st
import requests
import openai

# API Keys
FMP_API_KEY = "your_fmp_api_key"
OPENAI_API_KEY = "your_openai_api_key"
openai.api_key = OPENAI_API_KEY

# Function to Fetch Data
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Function to Get Financial Data
def get_financial_data(symbol):
    base_url = "https://financialmodelingprep.com/api/v3"
    
    endpoints = {
        "profile": f"{base_url}/profile/{symbol}?apikey={FMP_API_KEY}",
        "dcf": f"{base_url}/discounted-cash-flow/{symbol}?apikey={FMP_API_KEY}",
        "balance_sheet": f"{base_url}/balance-sheet-statement/{symbol}?apikey={FMP_API_KEY}&limit=1",
        "cash_flow": f"{base_url}/cash-flow-statement/{symbol}?apikey={FMP_API_KEY}&limit=1",
        "ratios": f"{base_url}/ratios/{symbol}?apikey={FMP_API_KEY}&limit=1",
        "financial_score": f"{base_url}/score?symbol={symbol}&apikey={FMP_API_KEY}"
    }

    data = {key: fetch_data(url) for key, url in endpoints.items()}
    
    # Fetch Sector PE
    sector = data["profile"][0]["sector"] if data["profile"] else None
    sector_pe = None
    if sector:
        sector_pe_url = f"https://financialmodelingprep.com/api/v4/sector_price_earning_ratio?date=latest&exchange=NYSE&apikey={FMP_API_KEY}"
        sector_data = fetch_data(sector_pe_url)
        if sector_data:
            for entry in sector_data:
                if entry["sector"] == sector:
                    sector_pe = entry["pe"]
                    break

    return data, sector, sector_pe

# Streamlit UI
st.title("📊 AI-Powered Stock Analysis Dashboard")
symbol = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL")

if st.button("Analyze Stock"):
    st.success("✅ API Keys loaded successfully! Fetching data...")
    
    data, sector, sector_pe = get_financial_data(symbol)
    
    if not data["profile"]:
        st.error("⚠️ No data found for this ticker. Please check the symbol and try again.")
    else:
        profile = data["profile"][0]
        dcf = data["dcf"][0] if data["dcf"] else None
        balance = data["balance_sheet"][0] if data["balance_sheet"] else None
        cash_flow = data["cash_flow"][0] if data["cash_flow"] else None
        ratios = data["ratios"][0] if data["ratios"] else None
        financial_score = data["financial_score"][0] if data["financial_score"] else None

        # Stock Price and DCF Comparison
        current_price = profile["price"]
        intrinsic_value = dcf["dcf"] if dcf else None
        dcf_difference = None
        if intrinsic_value:
            dcf_difference = ((current_price - intrinsic_value) / intrinsic_value) * 100

        # Display DCF & Price
        st.markdown("### 🌟 DCF Valuation")
        st.markdown(f"📄 **Intrinsic Value (DCF):** ${intrinsic_value:.2f}" if intrinsic_value else "⚠️ DCF not available")
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between;">
            <div style="color: green; font-weight: bold;">💲 Current Stock Price: ${current_price:.2f}</div>
            <div style="color: blue; font-weight: bold;">📊 Difference: {dcf_difference:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

        # Balance Sheet
        if balance:
            st.markdown("### 📜 Balance Sheet (Latest Year)")
            st.markdown(f"**Total Assets:** ${balance['totalAssets']:,}")
            st.markdown(f"**Total Liabilities:** ${balance['totalLiabilities']:,}")
            st.markdown(f"**Shareholder Equity:** ${balance['totalStockholdersEquity']:,}")

        # Cash Flow
        if cash_flow:
            st.markdown("### 💰 Cash Flow Statement (Latest Year)")
            st.markdown(f"**Operating Cash Flow:** ${cash_flow['netCashProvidedByOperatingActivities']:,}")
            st.markdown(f"**Capital Expenditures:** ${cash_flow['capitalExpenditure']:,}")
            st.markdown(f"**Free Cash Flow:** ${cash_flow['freeCashFlow']:,}")

        # Key Ratios
        if ratios:
            st.markdown("### 📊 Key Financial Ratios")
            st.markdown(f"**P/E Ratio:** {ratios['priceEarningsRatio']:.2f}")
            st.markdown(f"**Sector P/E Ratio:** {sector_pe:.2f}" if sector_pe else "⚠️ Sector P/E not available")
            st.markdown(f"**P/B Ratio:** {ratios['priceBookValueRatio']:.2f}")
            st.markdown(f"**ROE:** {ratios['returnOnEquity']:.2%}")
            st.markdown(f"**ROA:** {ratios['returnOnAssets']:.2%}")
            st.markdown(f"**Debt-to-Equity:** {ratios['debtEquityRatio']:.2f}")
            st.markdown(f"**Profit Margin:** {ratios['netProfitMargin']:.2%}")

        # AI Analysis
        st.markdown("### 🤖 AI Insights")
        if financial_score:
            altman_z = financial_score["altmanZScore"]
            piotroski = financial_score["piotroskiScore"]
            pe_ratio = ratios["priceEarningsRatio"] if ratios else None

            ai_prompt = f"""
            Based on the given metrics, {profile['companyName']} ({symbol}) appears to be financially healthy. 
            - **Altman Z-Score**: {altman_z}, indicating a {("low" if altman_z < 3 else "strong")} probability of financial distress.
            - **Piotroski Score**: {piotroski}, a {("weak" if piotroski < 5 else "strong")} financial health rating.
            - **DCF vs. Price**: The DCF valuation is {dcf_difference:.2f}% lower than the current stock price, suggesting {("undervaluation" if dcf_difference < 0 else "overvaluation")}.
            - **P/E vs. Sector**: The company's P/E ratio is {pe_ratio:.2f}, while its sector average is {sector_pe:.2f}, implying {("undervaluation" if pe_ratio < sector_pe else "overvaluation")} compared to peers.
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "Analyze the financial health of the given company based on provided metrics."},
                          {"role": "user", "content": ai_prompt}]
            )
            st.write(response["choices"][0]["message"]["content"])
        else:
            st.error("⚠️ AI analysis failed. Try again later.")


