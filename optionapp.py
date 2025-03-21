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
    /* Softer Gradient */
    body {
        background: linear-gradient(135deg, #1c1c1e, #2c2c2e);
        color: #e0e0e0;
    }

    html, body, [class*="css"]  {
        font-family: 'Arial', sans-serif;
        color: #e0e0e0;
    }

    /* Input fields styling */
    .stTextInput input, .stNumberInput input, .stSelectbox div, .stButton button {
        border-radius: 8px;
        background-color: #333333;
        color: white;
        border: 1px solid #444444;
        padding: 10px;
    }

    /* Button Hover Effect */
    .stButton>button:hover {
        background-color: #444444;
        color: white;
    }

    /* Section Headers */
    .block-container {
        padding-top: 2rem;
    }

    hr {
        border: 1px solid #444444;
        margin: 20px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---- Title ----
st.title("Options Strategy Predictor")
st.markdown("<hr>", unsafe_allow_html=True)

# ---- Input Form ----
with st.form("input_form"):
    st.subheader("Input Parameters")

    ticker = st.text_input("Stock Ticker", "AAPL").upper()
    num_contracts = st.number_input("Number of Contracts", min_value=1, value=1, step=1)
    percent_up = st.number_input("Stock Move Up (%)", min_value=1, max_value=500, value=10, step=1)
    percent_down = st.number_input("Stock Move Down (%)", min_value=1, max_value=500, value=10, step=1)

    # --- Fetch expiration & strike dynamically ---
    if ticker:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        exp_date = st.selectbox("Select Expiration Date", expirations)

        # Strike prices
        options_chain = stock.option_chain(exp_date)
        calls = options_chain.calls[['strike', 'lastPrice']]
        puts = options_chain.puts[['strike', 'lastPrice']]
        available_strikes = sorted(list(set(calls['strike']).intersection(set(puts['strike']))))
        chosen_strike = st.selectbox("Select Strike Price", available_strikes)

    submit_button = st.form_submit_button(label='Run Strategy Analysis')


# ---- Processing After Submission ----
if submit_button:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Market Data & Option Chain")

    stock = yf.Ticker(ticker)
    current_price = stock.history(period="1d")['Close'].iloc[-1]
    st.write(f"Current Stock Price: **${current_price:.2f}**")

    # Expiration Dates
    expirations = stock.options
    exp_date = st.selectbox("Select Expiration Date", expirations)
    options_chain = stock.option_chain(exp_date)

    # Strike Price Options
    calls = options_chain.calls[['strike', 'lastPrice']]
    puts = options_chain.puts[['strike', 'lastPrice']]
    available_strikes = sorted(list(set(calls['strike']).intersection(set(puts['strike']))))
    chosen_strike = st.selectbox("Select Strike Price", available_strikes)

    shares_per_contract = 100

    # Historical Volatility Calculation
    history = stock.history(period="60d")
    history['Return'] = history['Close'].pct_change()
    volatility = history['Return'].std()

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

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Scenario Probabilities")
    st.write(f"Probability Stock Up > +{percent_up}%: **{prob_up:.2f}**")
    st.write(f"Probability Stock Down > -{percent_down}%: **{prob_down:.2f}**")
    st.write(f"Probability Flat (within ±{max(percent_up, percent_down)}%): **{prob_flat:.2f}**")

    # ---- Payoff Matrix Calculation ----
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Payoff Matrix Calculation")

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
    st.dataframe(df)

    # ---- Strategy Suggestions ----
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Strategy Recommendations")

    probabilities = [prob_up, prob_down, prob_flat]
    row_mins = np.min(payoff_matrix, axis=1)
    minimax_value = np.max(row_mins)
    optimal_minimax_index = np.argmax(row_mins)
    optimal_minimax_strategy = strategies[optimal_minimax_index]

    expected_values = np.dot(payoff_matrix, probabilities)
    optimal_expected_index = np.argmax(expected_values)
    optimal_expected_strategy = strategies[optimal_expected_index]

    st.write(f"**Minimax Strategy:** {optimal_minimax_strategy} (worst-case payoff = ${minimax_value:.2f})")
    st.write(f"**Expected Value Strategy:** {optimal_expected_strategy} (expected payoff = ${expected_values[optimal_expected_index]:.2f})")

    # ---- Visualization ----
    st.markdown("<hr>", unsafe_allow_html=True)
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
