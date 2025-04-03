import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import datetime

# -----------------------------
# 🔧 CSS for Minimal Design
# -----------------------------
st.markdown("""
    <style>
    /* Clean, minimal background */
    html, body, .stApp {
        background-color: #f8f9fa !important;
    }
    
    /* Remove default streamlit bottom decoration and padding */
    .main .block-container {
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }
    
    footer {
        display: none !important;
    }
    
    /* Simple card effect */
    .card-container {
        background-color: white;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Clean form elements */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 4px;
        border: 1px solid #dee2e6;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4568dc;
        color: white;
        border: none;
        border-radius: 4px;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #3a56b4;
    }
    
    /* Subheader styling */
    h2, h3, .stSubheader {
        color: #343a40;
        font-weight: 500;
    }
    
    /* Table styling */
    .dataframe {
        border: none !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .dataframe th {
        background-color: #f1f3f5;
        color: #495057;
    }
    
    /* Responsive design adjustments */
    @media screen and (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }
        
        .stTextInput, .stNumberInput, .stSelectbox, .stButton {
            width: 100% !important;
        }
        
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        .dataframe {
            font-size: 0.8rem !important;
            overflow-x: auto !important;
        }
    }
    </style>
""", unsafe_allow_html=True)
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #4568dc, #3f5efb) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(63, 94, 251, 0.4) !important;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 6px !important;
        border: 1px solid rgba(173, 216, 230, 0.5) !important;
        padding: 10px 15px !important;
        background-color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Subheader styling */
    h2, h3, .stSubheader {
        color: #1e3a8a !important;
        font-weight: 600 !important;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: none !important;
        background-color: rgba(255, 255, 255, 0.7) !important;
    }
    
    .dataframe th {
        background-color: rgba(63, 94, 251, 0.1) !important;
        color: #1e3a8a !important;
    }
    
    /* Result sections */
    [data-testid="stVerticalBlock"] > div {
        background: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border-radius: 10px !important;
        padding: 10px 15px !important;
        margin-bottom: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.1) !important;
    }
    
    /* Responsive design adjustments */
    @media screen and (max-width: 768px) {
        /* Adjust content padding for mobile */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }
        
        /* Make form elements full width on mobile */
        .stTextInput, .stNumberInput, .stSelectbox, .stButton {
            width: 100% !important;
        }
        
        /* Reduce header sizes on mobile */
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
        
        /* Adjust table display for mobile */
        .dataframe {
            font-size: 0.8rem !important;
            overflow-x: auto !important;
        }
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
# 🧊 Logo - Minimal Style
# -----------------------------
st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='font-family: Arial, sans-serif; color: #343a40; font-weight: 500; margin-bottom: 0;'>
            <span style='color: #4568dc;'>Strikely</span>.ai
        </h1>
    </div>
""", unsafe_allow_html=True)

# -----------------------------
# 📦 Form Section
# -----------------------------
st.markdown("<div class='card-container'>", unsafe_allow_html=True)

with st.form("input_form"):
    st.subheader("INPUT PARAMETERS")
    
    # Use columns for better space utilization on both desktop and mobile
    col1, col2 = st.columns([1, 1])
    
    with col1:
        ticker = st.text_input("Stock Ticker", "AAPL").upper()

        if ticker != st.session_state.last_ticker:
            st.session_state.last_ticker = ticker
            st.session_state.exp_date = None
            st.session_state.strike = None
            
        num_contracts = st.number_input("Number of Contracts", min_value=1, value=1)
    
    with col2:
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
        submit = st.form_submit_button("RUN ANALYSIS")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 📈 Run the Strategy
# -----------------------------
if submit:
    st.markdown("---")
    
    # Create a terminal card container for results section
    st.markdown("""
        <div class="card-container">
    """, unsafe_allow_html=True)
    
    st.subheader("MARKET SNAPSHOT")
    history = stock.history(period="250d")
    current_price = history['Close'].iloc[-1]
    
    # Change to terminal style with colored values
    change_pct = ((current_price - history['Close'].iloc[-2]) / history['Close'].iloc[-2]) * 100
    if change_pct > 0:
        change_class = "positive"
        change_sign = "+"
    else:
        change_class = "negative"
        change_sign = ""
        
    st.markdown(f"""
        <div style='font-family: Consolas, monospace;'>
            <span style='color: #8fcaff;'>TICKER:</span> {ticker} | 
            <span style='color: #8fcaff;'>PRICE:</span> ${current_price:.2f} | 
            <span style='color: #8fcaff;'>CHANGE:</span> <span class='{change_class}'>{change_sign}{change_pct:.2f}%</span>
        </div>
    """, unsafe_allow_html=True)

    # Moving Averages
    ma_5 = history['Close'].rolling(window=5).mean().iloc[-1]
    ma_10 = history['Close'].rolling(window=10).mean().iloc[-1]
    ma_75 = history['Close'].rolling(window=75).mean().iloc[-1]
    ma_200 = history['Close'].rolling(window=200).mean().iloc[-1]

    st.markdown(
        f"""
        <div style='font-family: Consolas, monospace; margin: 10px 0;'>
        <span style='color: #8fcaff;'>MA:</span>
        <span style='color: #f0f0f0;'>5D=${ma_5:.2f}</span> | 
        <span style='color: #f0f0f0;'>10D=${ma_10:.2f}</span> | 
        <span style='color: #f0f0f0;'>75D=${ma_75:.2f}</span> | 
        <span style='color: #f0f0f0;'>200D=${ma_200:.2f}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Trend Logic ---
    expiry_date = datetime.datetime.strptime(st.session_state.exp_date, "%Y-%m-%d")
    days_to_expiry = (expiry_date - datetime.datetime.today()).days

    if days_to_expiry <= 21:
        w5, w10, w75, w200 = 2, 2, 1, 0
    elif days_to_expiry <= 60:
        w5, w10, w75, w200 = 2, 2, 2, 1
    else:
        w5, w10, w75, w200 = 2, 2, 3, 1

    trend_score = 0
    if current_price > ma_5: trend_score += w5
    if current_price > ma_10: trend_score += w10
    if current_price > ma_75: trend_score += w75
    if current_price > ma_200: trend_score += w200

    if trend_score >= 6:
        trend = "UPTREND"
        trend_class = "positive"
    elif trend_score <= 2:
        trend = "DOWNTREND"
        trend_class = "negative"
    else:
        trend = "SIDEWAYS"
        trend_class = ""

    st.markdown(f"""
        <div style='font-family: Consolas, monospace; margin: 10px 0;'>
            <span style='color: #8fcaff;'>TREND:</span> <span class='{trend_class}'>{trend}</span> [SCORE: {trend_score}/8]
        </div>
    """, unsafe_allow_html=True)

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

        st.subheader("SCENARIO PROBABILITIES")
        
        # Terminal-style table header
        st.markdown(f"""
            <div style='font-family: Consolas, monospace; margin: 10px 0;'>
                <span style='color: #8fcaff;'>SCENARIO</span> <span style='color: #f0f0f0;'>| PROBABILITY</span>
                <hr style='border-color: #333333; margin: 5px 0;'>
            </div>
        """, unsafe_allow_html=True)
        
        # Probability rows with color coding
        up_class = "positive" if prob_up > 0.25 else ""
        down_class = "negative" if prob_down > 0.25 else ""
        
        st.markdown(f"""
            <div style='font-family: Consolas, monospace;'>
                <div style='margin: 5px 0;'>
                    <span style='color: #f0f0f0;'>UP > +{percent_up}%</span> | <span class='{up_class}'>{prob_up:.2%}</span>
                </div>
                <div style='margin: 5px 0;'>
                    <span style='color: #f0f0f0;'>DOWN > -{percent_down}%</span> | <span class='{down_class}'>{prob_down:.2%}</span>
                </div>
                <div style='margin: 5px 0;'>
                    <span style='color: #f0f0f0;'>FLAT (within range)</span> | <span>{prob_flat:.2%}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

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

        # Payoff Matrix with Terminal styling
        st.subheader("PAYOFF MATRIX")
        
        # Convert matrix to DataFrame but customize display
        df = pd.DataFrame(matrix, index=strategies, columns=scenarios)
        
        # Create custom styled terminal table header
        st.markdown("""
            <style>
            /* Make table responsive on mobile */
            .stDataFrame div[data-testid="stHorizontalBlock"] {
                overflow-x: auto !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
        # Format DataFrame values with color coding
        def highlight_cells(val):
            color = '#00ff9d' if val > 0 else '#ff6b6b' if val < 0 else '#f0f0f0'
            return f'color: {color}'
            
        styled_df = df.style.map(highlight_cells)
        st.dataframe(styled_df, use_container_width=True)

        st.subheader("STRATEGY RECOMMENDATIONS")
        
        # Terminal-style recommendation output
        minimax_color = "positive" if minimax > 0 else "negative" if minimax < 0 else ""
        ev_color = "positive" if ev[np.argmax(ev)] > 0 else "negative" if ev[np.argmax(ev)] < 0 else ""
        
        st.markdown(f"""
            <div style='font-family: Consolas, monospace; margin: 10px 0;'>
                <div style='margin: 5px 0;'>
                    <span style='color: #8fcaff;'>MINIMAX:</span> {minimax_strategy} [<span class='{minimax_color}'>${minimax:.2f}</span>]
                </div>
                <div style='margin: 5px 0;'>
                    <span style='color: #8fcaff;'>EXPECTED VALUE:</span> {best_ev_strategy} [<span class='{ev_color}'>${ev[np.argmax(ev)]:.2f}</span>]
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # Close the terminal card for results section
    st.markdown("""
        </div>
    """, unsafe_allow_html=True)

# -----------------------------
# ⚠️ Disclaimer (Terminal Style)
# -----------------------------
st.markdown("""
<hr style="border-color: #333333; margin-top: 2rem;">
<p style='font-family: Consolas, "Courier New", monospace; font-size: 0.8em; color: #666666; text-align: center; padding: 0 10px;'>
/* DISCLAIMER: FOR INFORMATIONAL AND EDUCATIONAL PURPOSES ONLY. NOT FINANCIAL ADVICE. */
</p>
<div style="height: 20px;"></div>
""", unsafe_allow_html=True)
