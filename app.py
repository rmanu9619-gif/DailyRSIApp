import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import talib

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="Trading Dashboard", layout="wide")

tab1, tab2 = st.tabs(["📊 RSI App", "🎲 Monte Carlo Simulator"])

# =========================
# RSI APP
# =========================
with tab1:
    st.title("RSI App 📊")

    # Load tickers
    tickers = pd.read_csv("tickers.csv")["Ticker"].tolist()

    # --- Inputs ---
    search = st.text_input("Search ticker")
    color_filter = st.selectbox(
        "Filter by RSI Color",
        ["All", "Light Green (RSI ≤ 30)", "Dark Green (30 < RSI < 40)", "Bright Red (RSI ≥ 70)"]
    )

    if st.button("🔄 Recalculate RSI"):
        recalc = True
    else:
        recalc = False

    @st.cache_data
    def fetch_rsi(tickers):
        results = []
        for t in tickers:
            try:
                data = yf.download(t, period="6mo", progress=False)
                if data.empty:
                    continue
                close = data["Close"]
                rsi = talib.RSI(close, timeperiod=14)
                latest_rsi = rsi.iloc[-1]
                results.append((t, latest_rsi))
            except Exception:
                continue
        return pd.DataFrame(results, columns=["Ticker", "RSI"])

    if recalc:
        rsi_table = fetch_rsi(tickers)

        # Formatting RSI to 2 decimals without trailing zeros
        rsi_table["RSI"] = rsi_table["RSI"].apply(lambda x: f"{x:.2f}".rstrip("0").rstrip("."))

        # Color function
        def highlight_rsi(val):
            try:
                v = float(val)
                if v <= 30:
                    return "background-color: lightgreen"
                elif v < 40:
                    return "background-color: green; color: white"
                elif v >= 70:
                    return "background-color: red; color: white"
            except:
                return ""
            return ""

        styled = rsi_table.style.applymap(highlight_rsi, subset=["RSI"])

        # Search filter
        if search:
            styled = styled.loc[rsi_table["Ticker"].str.contains(search.upper(), na=False)]

        # Color filter
        if color_filter != "All":
            if "Light Green" in color_filter:
                styled = styled.loc[rsi_table["RSI"].astype(float) <= 30]
            elif "Dark Green" in color_filter:
                styled = styled.loc[(rsi_table["RSI"].astype(float) > 30) & (rsi_table["RSI"].astype(float) < 40)]
            elif "Bright Red" in color_filter:
                styled = styled.loc[rsi_table["RSI"].astype(float) >= 70]

        st.dataframe(styled)

# =========================
# MONTE CARLO SIMULATOR
# =========================
with tab2:
    st.title("Monte Carlo Stock Simulator 🎲")

    class MonteCarloSimulator:
        def __init__(self, experiment_fn, n_simulations=10000, random_seed=None):
            self.experiment_fn = experiment_fn
            self.n_simulations = n_simulations
            if random_seed is not None:
                np.random.seed(random_seed)

        def run(self):
            results = [self.experiment_fn() for _ in range(self.n_simulations)]
            return np.array(results)

        def summary(self, S0):
            results = self.run()
            prob_up = np.mean(results > S0) * 100
            avg_return = np.mean(results / S0 - 1) * 100
            return {
                "percent_chance_up": prob_up,
                "average_return_percent": avg_return
            }

    # User inputs
    ticker = st.text_input("Enter ticker for simulation:", "AAPL")
    n_simulations = st.slider("Number of simulations:", min_value=1000, max_value=50000, value=10000, step=1000)

    horizon_option = st.selectbox(
        "Time period:",
        ["1 week", "1 month", "3 months", "6 months", "1 year"]
    )

    horizons = {
        "1 week": 1/52,
        "1 month": 1/12,
        "3 months": 0.25,
        "6 months": 0.5,
        "1 year": 1.0
    }
    T = horizons[horizon_option]

    if st.button("Run Simulation"):
        with st.spinner("Fetching data and running simulations..."):
            data = yf.download(ticker, period="1y", progress=False)
            if data.empty:
                st.error("Ticker not found or no data available!")
            else:
                S0 = float(data["Close"].iloc[-1])
                returns = data["Close"].pct_change().dropna()
                mu = float(returns.mean() * 252)
                sigma = float(returns.std() * np.sqrt(252))

                def stock_sim(T):
                    Z = np.random.normal()
                    return S0 * np.exp((mu - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)

                sim = MonteCarloSimulator(lambda: stock_sim(T), n_simulations)
                result = sim.summary(S0)

                st.success(f"Simulation complete for {ticker} over {horizon_option}!")
                st.metric("Percent chance it goes up", f"{result['percent_chance_up']:.2f}%")
                st.metric("Average return", f"{result['average_return_percent']:.2f}%")
