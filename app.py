import streamlit as st
import yfinance as yf
import pandas as pd
import time

# -------------------------
# Hardcoded list of tickers
# -------------------------
tickers = [

    "AAL","AAPL","ACHC","ADBE","AEHR","AEP","AMD","AMGN","AMTX","AMZN","ARCB","AVGO",
    "BECN","BIDU","CAAS","CAKE","CASY","CHNR","CHPT","CMCSA","COST","CPRX","CSCO","CTSH",
    "CZR","DBX","DJCO","DLTR","ETSY","FIZZ","FTNT","GBCI","GEG","GILD","GMAB","GOGO",
    "GOOGL","GRPN","HAS","HBIO","HTLD","ILMN","INTC","IOSP","JBLU","KALU","KDP","LE","LQDA",
    "LULU","LYFT","MANH","MAR","MAT","META","MIDD","MNST","MSEX","MSFT","MTCH","MYGN","NCTY",
    "NTES","NTIC","NVDA","NXPI","ONB","ORLY","OZK","PCAR","PEP","PTON","PYPL","PZZA","QCOM",
    "REGN","RGLD","ROCK","RTC","SBUX","SEDG","SEIC","SFIX","SFM","SIRI","SKYW","SOHU","SWBI",
    "TROW","TSLA","TXN","TXRH","ULTA","URBN","USLM","UTSI","VEON","VRA","VRSK","WBA","WDFC",
    "WEN","YORW","ABBV","ABT","AEO","AFL","ALL","AMC","AMN","ANET","ANF","APAM","APD","APTV",
    "ASGN","ASH","AWK","AXP","AZO","BA","BABA","BAC","BAM","BAX","BBW","BBY","BCS","BEN","BILL",
    "BLK","BMY","BNED","BP","BUD","BURL","BWA","BX","C","CAT","CCJ","CL","CLW","CMG","CNC",
    "CNI","CP","CPB","CRH","CRM","CTVA","CVS","CVX","CYD","D","DAL","DB","DE","DEO","DFS","DG",
    "DIS","DLR","DOC","DOW","DXC","EDR","EDU","EL","EMN","ENB","ET","EXR","F","FCN","FCX","FE",
    "FICO","FL","FMC","FTS","GD","GE","GEO","GIS","GM","GMED","GRMN","GS","GSK","H","HD","HES",
    "HMC","HOG","HRB","HSY","ICE","IMAX","IQV","IRM","JNJ","JPM","K","KEY","KKR","KMI","KMX",
    "KO","KWR","L","LAC","LAZ","LCII","LMT","LOW","LUV","LVS","M","MA","MCD","MCK","MCO","MET",
    "MKC","MOV","MRK","MS","MTB","NCLH","NFG","NGS","NKE","NOC","NOV","NTR","NVO","NVS","OKE",
    "OPY","ORCL","PBH","PCG","PFE","PG","PKX","PLNT","PLOW","PNC","PRU","PSA","PSX","RBA",
    "RCI","RF","RTX","SAP","SAVE","SCHW","SJW","SNA","SNOW","SO","SONY","SPOT","SRE","SUN",
    "SYY","T","TAL","TAP","TCS","TEVA","TGT","THS","TJX","TM","TR","TREX","TRP","TSM","TSN",
    "TU","TWI","TXT","UA","UBER","UBS","UGI","UL","UNFI","UNH","UPS","V","VEEV","VFC","VZ",
    "WFC","WH","WHD","WMT","WNC","WSM","X","XOM","XRX","YUM","ZTO"
]

# -------------------------
# Wilder RSI function
# -------------------------

def wilder_rsi(prices, period=14):
    prices = prices.reset_index(drop=True)  # integer index
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Initialize full-length Series
    avg_gain = pd.Series(index=range(len(prices)), dtype=float)
    avg_loss = pd.Series(index=range(len(prices)), dtype=float)
    
    # First average is simple rolling mean
    avg_gain[period] = gain[:period+1].mean()
    avg_loss[period] = loss[:period+1].mean()
    
    # Wilder smoothing
    for i in range(period + 1, len(prices)):
        avg_gain[i] = (avg_gain[i-1] * (period - 1) + gain[i]) / period
        avg_loss[i] = (avg_loss[i-1] * (period - 1) + loss[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.round(2)
    return rsi

# -------------------------
# Batch download function
# -------------------------
@st.cache_data(ttl=86400)
def download_data_in_batches(tickers, batch_size=50):
    all_data = pd.DataFrame()
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        try:
            data = yf.download(batch, period="1y")["Close"]
            all_data = pd.concat([all_data, data], axis=1)
        except:
            pass
        time.sleep(1)
    return all_data

# -------------------------
# RSI calculation function
# -------------------------
def calculate_rsi(data):
    rsi_dict = {}
    for ticker in data.columns:
        prices = data[ticker].dropna()
        if len(prices) >= 14:
            rsi_series = wilder_rsi(prices)
            rsi_dict[ticker] = round(rsi_series.iloc[-1], 2)
        else:
            rsi_dict[ticker] = None
    rsi_table = pd.DataFrame(list(rsi_dict.items()), columns=["Ticker", "RSI"])
    rsi_table["RSI"] = rsi_table["RSI"].round(2)
        
    def rsi_to_color(val):
        if val is None:
            return 'white'
        elif val <= 30:
            return "lightgreen"
        elif val <= 40:
            return "green"
        elif val >= 70:
            return "red"
        else:
            return "white"
        

    rsi_table['Color'] = rsi_table['RSI'].apply(rsi_to_color)
    return rsi_table

# -------------------------
# Streamlit UI
# -------------------------
st.title("Stock RSI Dashboard")

st.text("Key: lightgreen(<30), green(<40), red(>70)")

    
# Download data (cached)
data = download_data_in_batches(tickers)

# Refresh button
if st.button("Refresh RSI"):
    st.cache_data.clear()  # clear cache to get fresh data
    data = download_data_in_batches(tickers)

# Calculate RSI
rsi_table = calculate_rsi(data)

# Search box
search = st.text_input("Search ticker:")
if search:
    filtered_table = rsi_table[rsi_table['Ticker'].str.contains(search.upper())]
else:
    filtered_table = rsi_table.copy()

# Color filter dropdown
color_options = ["All", "lightgreen", "green", "red"]
selected_color = st.selectbox("Filter by RSI color:", color_options)
if selected_color != "All":
    filtered_table = filtered_table[filtered_table['Color'] == selected_color]

# Display styled table
def color_rsi(val):
    return f'background-color: {val}'


rsi_table["RSI"] = rsi_table["RSI"].round(2)
styled_table = filtered_table.style.applymap(color_rsi, subset=['Color'])
st.dataframe(styled_table, height=600)

