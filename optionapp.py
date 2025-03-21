import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
import datetime

# ---- Custom CSS Styling ----
st.markdown(
    """
    <style>
    /* Background Gradient */
    body {
        background: linear-gradient(135deg, #1f1f1f, #2e2e2e);
        color: #ffffff;
    }

    html, body, [class*="css"]  {
        font-family: 'Arial', sans-serif;
        color: #ffffff;
    }

    /* Streamlit widgets background */
    .stTextInput, .stNumberInput, .stSelectbox, .stButton {
        background-color: #333333;
        color: #ffffff;
    }

    /* DataFrame styling */
    .css-1d391kg { 
        background-color: #333333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- App Title ----
st.title("Options Strategy Predictor")

# ---- Input Section ----
st.header("Input Parameters")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA)", "AAPL").upper()
num_contracts = st.number_input("Number of Contracts", min_value=1, max_value=100, value=1)
percent_up = st.number_input("Stock Move Up (%)", min_value=0, max_value=500, value=10)
percent_down = st.number_input("Stock Move Down (%)", min_value=0, max_value=500, value=10)

# ---- Fetch Stock Data ----
stock = yf.Ticker(ticker)
current_price = stock.history(period="1d")['Close'].iloc[-1]
st.write(f"Current Stock Price: ${current_price:.2f}")

# ---- Expiration Dates ----
expirations = stock.options
exp_date = st.selectbox("Select Expiration Date", expirations)
options_chain = stock.option_chain(exp_date)

# ---- Strike Price ----
calls = options_chain.calls[['strike', 'lastPrice']]
puts = options_chain.puts[['strike', 'lastPrice']]

available_strikes = sorted(list(set(calls['strike']).intersection(set(puts['strike']))))
chosen_strike = st.selectbox("Select Strike Price", available_strikes)

shares_per_contract = 100

# ---- Historical Volatility ----
history = stock.history(period="60d")
history['Return'] = history['Close'].pct_change()
volatility = history['Return'].std()

# ---- Probability Calculation ----
expiry_date = datetime.datetime.strptime(exp_date, "%Y-%m-%d")
today = datetime.datetime.today()
days_to_expiry = (expiry_date - today).days

annual_vol = volatility * np.sqrt(252)
daily_vol = annual_vol / np.sqrt(252)

threshold_up = percent_up / 100
threshold_down = -percent_down / 100

z_up = (threshold_up) / (daily_vol * np.sqrt(days_to_expiry))
z_down = (threshold_down) / (daily_vol * np.sqrt(days_to_expiry))

prob_up = 1 - norm.cdf(z_up)
prob_down = norm.cdf(z_down)
prob_flat = 1 - (prob_up + prob_down)

st.subheader("Scenario Probabilities")
st.write(f"Probability Stock Up > +{percent_up}%: {prob_up:.2f}")
st.write(f"Probability Stock Down > -{percent_down}%: {prob_down:.2f}")
st.write(f"Probability Flat (within ±{max(percent_up, percent_down)}%): {prob_flat:.2f}")

# ---- Payoff Matrix Calculation ----
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

        if not call_price_row.empty and not put_price_row.empty:
            call_price = call_price_row['lastPrice'].values[0]
            put_price = put_price_row['lastPrice'].values[0]
        else:
            call_price = 0
            put_price = 0

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

# ---- Display Payoff Matrix ----
st.subheader("Payoff Matrix")
st.dataframe(df)

# ---- Minimax + Expected Value Analysis ----
probabilities = [prob_up, prob_down, prob_flat]
row_mins = np.min(payoff_matrix, axis=1)
minimax_value = np.max(row_mins)
optimal_minimax_index = np.argmax(row_mins)
optimal_minimax_strategy = strategies[optimal_minimax_index]

expected_values = np.dot(payoff_matrix, probabilities)
optimal_expected_index = np.argmax(expected_values)
optimal_expected_strategy = strategies[optimal_expected_index]

st.subheader("Strategy Suggestions")
st.write(f"Minimax Strategy: {optimal_minimax_strategy} (worst-case payoff = ${minimax_value:.2f})")
st.write(f"Expected Value Strategy: {optimal_expected_strategy} (expected payoff = ${expected_values[optimal_expected_index]:.2f})")

# ---- Visualization ----
st.subheader("Payoff Matrix Heatmap")
fig, ax = plt.subplots(figsize=(8, 6))
cax = ax.imshow(payoff_matrix, cmap='coolwarm', interpolation='nearest')
ax.set_xticks(np.arange(len(scenarios)))
ax.set_yticks(np.arange(len(strategies)))
ax.set_xticklabels(scenarios)
ax.set_yticklabels(strategies)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
fig.colorbar(cax, label='Payoff ($)')
st.pyplot(fig)
