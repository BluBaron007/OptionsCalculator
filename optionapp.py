import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import datetime

# ---- Custom CSS Styling ----
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #1c1c1e, #2c2c2e);
    color: #deb887 ;
    animation: fadeInBody 1s ease-in;
}

@keyframes fadeInBody {
    from {opacity: 0;}
    to {opacity: 1;}
}

html, body, [class*="css"] {
    font-family: 'Arial', sans-serif;
    color: #deb887 ;
}

.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stButton>button {
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.9);
    color: black;
    border: 1px solid #555555;
    padding: 8px;
    font-size: 14px;
    animation: fadeInBox 1s ease-in;
}

@keyframes fadeInBox {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}

h1, h3, p {
    animation: fadeInHeader 1s ease-in;
}

@keyframes fadeInHeader {
    from {opacity: 0; transform: translateY(-10px);}
    to {opacity: 1; transform: translateY(0);}
}

label {
    color: black !important;
    font-weight: bold;
}

.block-container {
    max-width: 100%;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
}

hr {
    border: 1px solid #444444;
    margin: 20px 0;
}

.css-1d391kg {
    background-color: #deb887;
    color: white;
}

@media screen and (max-width: 600px) {
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stButton>button {
        padding: 6px;
        font-size: 12px;
    }
}
</style>
""", unsafe_allow_html=True)

# ---- Title ----
st.markdown("<h1 style='text-align: center;'>Options Strategy Predictor</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Where Game Theory & Stock Options Combine</h3>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---- Input Form ----
with st.form("input_form"):
    st.markdown("<h3 style='text-align: center;'>Input Parameters</h3>", unsafe_allow_html=True)

    ticker = st.text_input("Stock Ticker", "AAPL").upper()
    num_contracts = st.number_input("Number of Contracts", min_value=1, value=1, step=1)
    percent_up = st.number_input("Stock Move Up (%)", min_value=1, max_value=500, value=10, step=1)
    percent_down = st.number_input("Stock Move Down (%)", min_value=1, max_value=500, value=10, step=1)

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

    submit_button = st.form_submit_button(label='Run Strategy Analysis')

# ---- After Submit ----
if submit_button and ticker and exp_date and chosen_strike:

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Market Data & Option Chain</h3>", unsafe_allow_html=True)

    history = stock.history(period="250d")  # 1 year of data
    current_price = history['Close'].iloc[-1]
    st.markdown(f"<p style='text-align: center;'>Current Stock Price: <strong>${current_price:.2f}</strong></p>", unsafe_allow_html=True)

    # ---- Moving Averages ----
    ma_5 = history['Close'].rolling(window=5).mean().iloc[-1]
    ma_10 = history['Close'].rolling(window=10).mean().iloc[-1]
    ma_50 = history['Close'].rolling(window=50).mean().iloc[-1]
    ma_200 = history['Close'].rolling(window=200).mean().iloc[-1]

    st.markdown("<h3 style='text-align: center;'>Trend Analysis (MA)</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>5D MA: <strong>${ma_5:.2f}</strong> | 10D MA: <strong>${ma_10:.2f}</strong><br>50D MA: <strong>${ma_50:.2f}</strong> | 200D MA: <strong>${ma_200:.2f}</strong></p>", unsafe_allow_html=True)

    # ---- Trend Classification ----
    if current_price > ma_5 and current_price > ma_10 and current_price > ma_50 and current_price > ma_200:
        trend = "Uptrend"
    elif current_price < ma_5 and current_price < ma_10 and current_price < ma_50 and current_price < ma_200:
        trend = "Downtrend"
    else:
        trend = "Sideways"

    st.markdown(f"<p style='text-align: center;'><strong>Detected Trend:</strong> {trend}</p>", unsafe_allow_html=True)

    # ---- Volatility Calculation ----
    history['Return'] = history['Close'].pct_change()
    volatility = history['Return'].std()

    expiry_date = datetime.datetime.strptime(exp_date, "%Y-%m-%d")
    today = datetime.datetime.today()
    days_to_expiry = (expiry_date - today).days

    if volatility == 0 or days_to_expiry <= 0:
        st.error("Volatility data unavailable or expiration date is invalid.")
    else:
        annual_vol = volatility * np.sqrt(252)
        daily_vol = annual_vol / np.sqrt(252)

        threshold_up = percent_up / 100
        threshold_down = -percent_down / 100

        z_up = (threshold_up) / (daily_vol * np.sqrt(days_to_expiry))
        z_down = (threshold_down) / (daily_vol * np.sqrt(days_to_expiry))

        prob_up = 1 - norm.cdf(z_up)
        prob_down = norm.cdf(z_down)
        prob_flat = 1 - (prob_up + prob_down)

        # ---- Adjust Probabilities Based on Trend ----
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

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Scenario Probabilities</h3>", unsafe_allow_html=True)

        up_color = "green" if prob_up > 0.5 else "red"
        down_color = "green" if prob_down > 0.5 else "red"
        flat_color = "green" if prob_flat > 0.5 else "red"

        st.markdown(f"<p style='text-align: center; color:{up_color};'>Probability Stock Up > +{percent_up}%: <strong>{prob_up:.2f}</strong></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color:{down_color};'>Probability Stock Down > -{percent_down}%: <strong>{prob_down:.2f}</strong></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color:{flat_color};'>Probability Flat (within ±{max(percent_up, percent_down)}%): <strong>{prob_flat:.2f}</strong></p>", unsafe_allow_html=True)

        # ---- Payoff Matrix Calculation ----
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Payoff Matrix</h3>", unsafe_allow_html=True)

        shares_per_contract = 100
        strategies = ['Buy Call', 'Buy Put', 'Write Call', 'Write Put']
        scenarios = [f'Stock Up {percent_up}%', f'Stock Down {percent_down}%', 'Stock Flat']
        payoff_matrix = []

        for strategy in strategies:
            row = []
            for scenario in scenarios:
                if scenario.startswith('Stock Up'):
                    new_price = chosen_strike * (1 + percent_up / 100)
                elif scenario.startswith('Stock Down'):
                    new_price = chosen_strike * (1 - percent_down / 100)
                else:
                    new_price = chosen_strike

                call_price_row = calls.loc[calls['strike'] == chosen_strike]
                put_price_row = puts.loc[puts['strike'] == chosen_strike]

                call_price = call_price_row['lastPrice'].values[0] if not call_price_row.empty else 0
                put_price = put_price_row['lastPrice'].values[0] if not put_price_row.empty else 0

                if strategy == 'Buy Call':
                    payoff = (max(0, new_price - chosen_strike) - call_price) * shares_per_contract * num_contracts
                elif strategy == 'Buy Put':
                    payoff = (max(0, chosen_strike - new_price) - put_price) * shares_per_contract * num_contracts
                elif strategy == 'Write Call':
                    payoff = (call_price - max(0, new_price - chosen_strike)) * shares_per_contract * num_contracts
                elif strategy == 'Write Put':
                    payoff = (put_price - max(0, chosen_strike - new_price)) * shares_per_contract * num_contracts

                row.append(round(payoff, 2))
            payoff_matrix.append(row)

        df = pd.DataFrame(payoff_matrix, index=strategies, columns=scenarios)
        st.dataframe(df.style.set_table_attributes("style='margin-left: auto; margin-right: auto;'"))

        # ---- Strategy Recommendations ----
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Strategy Recommendations</h3>", unsafe_allow_html=True)

        probabilities = [prob_up, prob_down, prob_flat]
        row_mins = np.min(payoff_matrix, axis=1)
        minimax_value = np.max(row_mins)
        optimal_minimax_index = np.argmax(row_mins)
        optimal_minimax_strategy = strategies[optimal_minimax_index]

        expected_values = np.dot(payoff_matrix, probabilities)
        optimal_expected_index = np.argmax(expected_values)
        optimal_expected_strategy = strategies[optimal_expected_index]

        st.markdown(f"<p style='text-align: center;'><strong>Minimax Strategy:</strong> {optimal_minimax_strategy} (Worst-case payoff = ${minimax_value:.2f})</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'><strong>Expected Value Strategy:</strong> {optimal_expected_strategy} (Expected payoff = ${expected_values[optimal_expected_index]:.2f})</p>", unsafe_allow_html=True)
