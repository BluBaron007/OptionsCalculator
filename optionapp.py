import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import datetime

# -----------------------------
# 🔧 CSS for Background
# -----------------------------
st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #F8F8FF !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State Initialization
# -----------------------------
if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = None
if 'exp_date' not in st.session_state:
    st.session_state.exp_date = None
if 'strike' not in st.session_state:
    st.session_state.strike = None

# -----------------------------
# 🔷 Logo-Only Header (Centered + Large)
# -----------------------------
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://raw.githubusercontent.com/BluBaron007/OptionsCalculator/main/strikely_logo.png' width='500' style='margin-bottom: 0px;'/>
        <h4 style='margin-top: 0px;'>Where Game Theory & Stock Options Collide</h4>
    </div>
    <hr>
""", unsafe_allow_html=True)

# -----------------------------
# 📦 Form Section
# -----------------------------
st.markdown("<div class='glass-form'>", unsafe_allow_html=True)

with st.form("input_form"):
    st.subheader("Input Parameters")
    ticker = st.text_input("Stock Ticker", "AAPL").upper()

    if ticker != st.session_state.last_ticker:
        st.session_state.last_ticker = ticker
        st.session_state.exp_date = None
        st.session_state.strike = None

    num_contracts = st.number_input("Number of Contracts", min_value=1, value=1)
    percent_up = st.number_input("Stock Move Up (%)", min_value=1, value=10)
    percent_down = st.number_input("Stock Move Down (%)", min_value=1, value=10)

    submit = False
    show_submit = True

    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options

        if len(expirations) == 0:
            st.warning("⚠️ No expiration dates found. Invalid or illiquid ticker.")
            show_submit = False
        else:
            st.session_state.exp_date = st.selectbox("Select Expiration Date", expirations, index=expirations.index(st.session_state.exp_date) if st.session_state.exp_date in expirations else 0)
            options_chain = stock.option_chain(st.session_state.exp_date)
            calls = options_chain.calls[['strike', 'lastPrice']]
            puts = options_chain.puts[['strike', 'lastPrice']]
            available_strikes = sorted(list(set(calls['strike']).intersection(set(puts['strike']))))

            st.session_state.strike = st.selectbox("Select Strike Price", available_strikes, index=available_strikes.index(st.session_state.strike) if st.session_state.strike in available_strikes else 0)
    except Exception:
        st.warning("⚠️ Waiting for a valid ticker...")

    if show_submit:
        submit = st.form_submit_button("Run Strategy Analysis")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 📈 Run the Strategy
# -----------------------------
if submit:
    st.markdown("---")
    st.subheader("Market Snapshot")
    history = stock.history(period="250d")
    current_price = history['Close'].iloc[-1]
    st.write(f"📌 Current Stock Price: **${current_price:.2f}**")

    # Moving Averages
    ma_5 = history['Close'].rolling(window=5).mean().iloc[-1]
    ma_10 = history['Close'].rolling(window=10).mean().iloc[-1]
    ma_75 = history['Close'].rolling(window=75).mean().iloc[-1]
    ma_200 = history['Close'].rolling(window=200).mean().iloc[-1]

    st.markdown(
        f"""
        <p style='text-align: center;'>
        📊 <strong>Moving Averages:</strong>
        <strong>5D</strong>: ${ma_5:.2f}, 
        <strong>10D</strong>: ${ma_10:.2f}, 
        <strong>75D</strong>: ${ma_75:.2f}, 
        <strong>200D</strong>: ${ma_200:.2f}
        </p>
        """,
        unsafe_allow_html=True
    )

    # --- Dynamic Weighted Trend Logic ---
    expiry_date = datetime.datetime.strptime(st.session_state.exp_date, "%Y-%m-%d")
    days_to_expiry = (expiry_date - datetime.datetime.today()).days

    if days_to_expiry <= 21:  # Short-term
        w5, w10, w75, w200 = 2, 2, 1, 0
    elif days_to_expiry <= 60:  # Medium-term
        w5, w10, w75, w200 = 2, 2, 2, 1
    else:  # Long-term
        w5, w10, w75, w200 = 2, 2, 3, 1

    trend_score = 0
    if current_price > ma_5: trend_score += w5
    if current_price > ma_10: trend_score += w10
    if current_price > ma_75: trend_score += w75
    if current_price > ma_200: trend_score += w200

    if trend_score >= 6:
        trend = "Uptrend"
    elif trend_score <= 2:
        trend = "Downtrend"
    else:
        trend = "Sideways"

    st.write(f"📊 Detected Trend: **{trend}**")

    # Volatility & Probabilities
    history['Return'] = history['Close'].pct_change()
    volatility = history['Return'].std()

    if volatility == 0 or days_to_expiry <= 0:
        st.error("⚠️ Not enough volatility data or invalid expiration.")
    else:
        daily_vol = (volatility * np.sqrt(252)) / np.sqrt(252)
        z_up = (percent_up / 100) / (daily_vol * np.sqrt(days_to_expiry))
        z_down = (-percent_down / 100) / (daily_vol * np.sqrt(days_to_expiry))

        prob_up = 1 - norm.cdf(z_up)
        prob_down = norm.cdf(z_down)
        prob_flat = 1 - (prob_up + prob_down)

        if trend == "Uptrend":
            prob_up *= 1.10
            prob_down *= 0.90
        elif trend == "Downtrend":
            prob_down *= 1.10
            prob_up *= 0.90
        else:
            prob_flat *= 1.10

        total = prob_up + prob_down + prob_flat
        prob_up /= total
        prob_down /= total
        prob_flat /= total

        st.subheader("Scenario Probabilities")
        st.write(f"• Stock Up > +{percent_up}%: **{prob_up:.2%}**")
        st.write(f"• Stock Down > -{percent_down}%: **{prob_down:.2%}**")
        st.write(f"• Flat (within range): **{prob_flat:.2%}**")

        # Payoff Matrix
        strategies = ['Buy Call', 'Buy Put', 'Write Call', 'Write Put']
        scenarios = [f'Up {percent_up}%', f'Down {percent_down}%', 'Flat']
        matrix = []

        for strat in strategies:
            row = []
            for s in scenarios:
                if 'Up' in s:
                    price = st.session_state.strike * (1 + percent_up / 100)
                elif 'Down' in s:
                    price = st.session_state.strike * (1 - percent_down / 100)
                else:
                    price = st.session_state.strike

                call_price = calls[calls['strike'] == st.session_state.strike]['lastPrice'].values[0]
                put_price = puts[puts['strike'] == st.session_state.strike]['lastPrice'].values[0]

                if strat == 'Buy Call':
                    payoff = (max(0, price - st.session_state.strike) - call_price) * 100 * num_contracts
                elif strat == 'Buy Put':
                    payoff = (max(0, st.session_state.strike - price) - put_price) * 100 * num_contracts
                elif strat == 'Write Call':
                    payoff = (call_price - max(0, price - st.session_state.strike)) * 100 * num_contracts
                elif strat == 'Write Put':
                    payoff = (put_price - max(0, st.session_state.strike - price)) * 100 * num_contracts

                row.append(round(payoff, 2))
            matrix.append(row)

        df = pd.DataFrame(matrix, index=strategies, columns=scenarios)
        st.subheader("Payoff Matrix")
        st.dataframe(df)

        st.subheader("📌 Strategy Recommendations")
        row_mins = np.min(matrix, axis=1)
        minimax = np.max(row_mins)
        minimax_strategy = strategies[np.argmax(row_mins)]

        ev = np.dot(matrix, [prob_up, prob_down, prob_flat])
        best_ev_strategy = strategies[np.argmax(ev)]

        st.write(f"🛡 Minimax: **{minimax_strategy}** (${minimax:.2f})")
        st.write(f"🎯 Expected Value: **{best_ev_strategy}** (${ev[np.argmax(ev)]:.2f})")

# -----------------------------
# ⚠️ Disclaimer (Soft Gray)
# -----------------------------
st.markdown("""
<hr>
<p style='font-size: 0.85em; color: #999999; text-align: center;'>
<b>Disclaimer:</b> This tool is for informational and educational purposes only. It does not constitute financial advice, investment recommendations, or a guarantee of future performance. Trading options involves risk, and users should consult a licensed financial advisor before making any trading decisions.
</p>
""", unsafe_allow_html=True)
