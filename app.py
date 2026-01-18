import streamlit as st
import yfinance as yf
import pandas as pd
import time

# -------------------------
# Hardcoded list of tickers
# -------------------------
tickers = [
"AAPL","MSFT","NVDA","AMZN","GOOGL","GOOG","META","BRK.B","TSLA","AVGO","LLY","WMT","JPM","V","MA","XOM","UNH","COST","HD","ABBV","PG","ORCL","MRK","KO","CVX","PEP","BAC","TMO","ADBE","CRM","NFLX","AMD","LIN","ACN","CSCO","MCD","WFC","INTU","ABT","DHR","TXN","VZ","QCOM","CMCSA","AMGN","DIS","UPS","PM","NEE","LOW","HON","RTX","COP","IBM","INTC","SPGI","CAT","GE","GS","AXP","BLK","PFE","ISRG","NOW","AMAT","ELV","BKNG","MDT","DE","SYK","ADI","TJX","LMT","MO","CB","MMC","VRTX","ZTS","GILD","C","SCHW","TMUS","ADP","PLD","PNC","SO","DUK","REGN","TGT","USB","BSX","CME","AON","ICE","CI","ITW","MU","NKE","SHW","BDX","FIS","CL","EQIX","ETN","WM","APD","HCA","MCK","NSC","EMR","FDX","CSX","ECL","HUM","ORLY","SLB","ROP","MAR","PSA","DG","ADSK","COF","KMB","AEP","KMI","PGR","AFL","EXC","SRE","MSI","NXPI","ROST","PCAR","AIG","MPC","VLO","AZO","DLR","SPG","MSCI","ALL","JCI","PAYX","TRV","CTVA","FANG","HLT","MTB","WMB","WELL","TEL","OTIS","AMP","RCL","LEN","IDXX","KHC","OKE","GPN","CPRT","IQV","AME","ANET","FAST","CMI","ED","CTAS","EA","PRU","RSG","KEYS","ODFL","URI","PEG","ES","PCG","DOV","VRSK","IR","YUM","EXPD","LUV","EBAY","HIG","WEC","STT","GWW","NDAQ","TT","EFX","FICO","KMX","MLM","SW","NVR","BRO","ETR","GRMN","PPG","CINF","WAT","ZBRA","LNT","XYL","ROK","FITB","HUBB","PPL","EQR","AVB","HBAN","AEE","WRB","RF","DGX","CHD","SJM","CMS","NI","IP","NTRS","TSCO","L","DRI","HOLX","LDOS","SBAC","STE","EXR","STLD","FOXA","FOX","CFG","BXP","DTE","UAL","HST","NRG","PHM","FSLR","LULU","ALB","POOL","ENPH","COIN","SNOW","DDOG","NET","MDB","CRWD","ZS","OKTA","PANW","FTNT","TEAM","DOCU","HUBS","TWLO","SHOP","SQ","PYPL","ROKU","ABNB","UBER","LYFT","HOOD","RIVN","LCID","PLTR","AFRM","SOFI","DKNG","RBLX","CVNA","WBD","PARA","CHWY","BILL","ETSY","PINS","ZI","F","GM","STLA","RACE","NIO","INTU","CDNS","SNPS","KLAC","LRCX","TER","MPWR","MCHP","ON","SWKS","QRVO","COHR","ALGN","BIIB","ILMN","INCY","MRNA","BMRN","EXEL","ICLR","TECH","CRL","WST","A","BR","IEX","ERIE","MKTX","MAS","AVY","BLL","HAS","HRL","DPZ","CLX","SWK","IVZ","BEN","CF","MOS","APA","DVN","EOG","HAL","BKR","OXY","PSX","CTRA","SMCI","PFG","JBHT","GPC","TYL","AMCR","SNA","HPQ","LII","IFF","MKC","DD","EVRG","TRMB","PNR","FTV","ZBH","ESS","TTD","CDW","INVH","HII","TXT","J","MAA","LYB","COO","GEN","FFIV","NDSN","BALL","VTRS","DECK","NWSA","KIM","BBY","ALLE","GDDY","BLDR","JKHY","UDR","AKAM","EG","REG","RVTY","DOC","UHS","BF.B","CPT","WYNN","EPAM","AIZ","PNW","DAY","GL","FDS","AES","AOS","NCLH","ARE","MOH","TAP","MGM","GNRC","HSIC","FRT","PAYC","CAG","CPB","MTCH","DVA","LW",

"PENN","MARA","RIOT","CLSK","HUT","BITF","SDIG","WKHS","NKLA","MULN","PLUG","FCEL","BLNK","QS","OPEN","WISH","SNDL","TLRY","CGC","ACB","HEXO","BB","NOK","RIG","GME","AMC","KOSS","EXPR","BBBYQ","CVNA","FUBO","ROOT","UPST","CLOV","WOOF","SPCE","ASTS","RKLB","IONQ","QBTS","SOUN","BBAI","AI","PATH","APLD","CORZ","HIMS","LMND","OPFI","SOLO","TUP","BIG","DDS","SKLZ","BLUE","CRSP","EDIT","BEAM","PACB","RXRX","VERV","DNA","FATE","NTLA","SGMO","ACHR","JOBY","LILM","EVGO","CHPT","MVIS","LAZR","VLDR","INVZ","AEVA","OUST"

]
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

