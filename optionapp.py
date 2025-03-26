import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import datetime

# --------------------------------------------
# 🔒 Force Background Color Before Anything Renders
# --------------------------------------------
st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #F0FFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------
# 📊 Title and Description
# --------------------------------------------
st.markdown("<h1 style='text-align: center;'>Options Strategy Predictor</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Where Game Theory & Stock Options Collide</h4>", unsafe_allow_html=True)
st.markdown("---")

# --------------------------------------------
# 🧾 Input Form
# --------------------------------------------
with st.form("input_form"):
    st.subheader("Input Parameters")
    ticker = st.text_input("Stock Ticker", "AAPL").upper()
    num_contracts = st.number_input("Number of Contracts", min_value=1, value=1)
    percent_up = st.number_input("Stock Move Up (%)", min_value=1, value=10)
    percent_down = st.number_input("Stock Move Down (%)", min_value=1, value=10)

    exp_date = None
    chosen_strike = None

    if ticker:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        exp_date = st.selectbox("Select Expiration Date", expirations)

        options_chain = stock.option_chain(exp_date)
        calls = options_chain.calls[['strike', 'lastPrice']]
        puts = options_chain.puts[['strike', 'lastPrice']]
        available_strikes = sorted(list(set(calls['strike']).intersection(set(puts['strike']))))
        chosen_strike = st.selectbox("Select Strike Price", available_strikes)

    submitted = st.form_submit_button("Run Strategy Analysis")

# --------------------------------------------
# 📈 Strategy Logic & Output
# --------------------------------------------
if submitted and ticker and exp_date and chosen_strike:
    st.markdown("---")
    st.subheader("Market Snapshot")
    history = stock.history(period="250d")
    current_price = history['Close'].iloc[-1]
    st.write(f"📌 Current Stock Price: **${current_price:.2f}**")

    ma_5 = history['Close'].rolling(window=5).mean().iloc[-1]
    ma_10 = history['Close'].rolling(window=10).mean().iloc[-1]
    ma_50 = history['Close'].rolling(window=50).mean().iloc[-1]
    ma_200 = history['Close'].rolling(window=200).mean().iloc[-1]
    st.write(f"📈 Moving Averages: 5D: ${ma_5:.2f}, 10D: ${ma_10:.2f}, 50D: ${ma_50:.2f}, 200D: ${ma_200:.2f}")

    if current_price > max(ma_5, ma_10, ma_50, ma_200):
        trend = "Uptrend"
    elif current_price < min(ma_5, ma_10, ma_50, ma_200):
        trend = "Downtrend"
    else:
        trend = "Sideways"

    st.write(f"📊 Detected Trend: **{trend}**")

    history['Return'] = history['Close'].pct_change()
    volatility = history['Return'].std()
    days_to_expiry = (datetime.datetime.strptime(exp_date, "%Y-%m-%d") - datetime.datetime.today()).days

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

        strategies = ['Buy Call', 'Buy Put', 'Write Call', 'Write Put']
        scenarios = [f'Up {percent_up}%', f'Down {percent_down}%', 'Flat']
        matrix = []

        for strat in strategies:
            row = []
            for s in scenarios:
                if 'Up' in s:
                    price = chosen_strike * (1 + percent_up / 100)
                elif 'Down' in s:
                    price = chosen_strike * (1 - percent_down / 100)
                else:
                    price = chosen_strike

                call_price = calls[calls['strike'] == chosen_strike]['lastPrice'].values[0]
                put_price = puts[puts['strike'] == chosen_strike]['lastPrice'].values[0]

                if strat == 'Buy Call':
                    payoff = (max(0, price - chosen_strike) - call_price) * 100 * num_contracts
                elif strat == 'Buy Put':
                    payoff = (max(0, chosen_strike - price) - put_price) * 100 * num_contracts
                elif strat == 'Write Call':
                    payoff = (call_price - max(0, price - chosen_strike)) * 100 * num_contracts
                elif strat == 'Write Put':
                    payoff = (put_price - max(0, chosen_strike - price)) * 100 * num_contracts

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
