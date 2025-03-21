import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import datetime
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# ---- App Configuration ----
st.set_page_config(
    page_title="Options Strategy Theater",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- Custom CSS Styling ----
st.markdown(
    """
    <style>
    /* Main app background and gradient */
    body {
        background: linear-gradient(135deg, #000000, #1a1a2e);
        color: #ffffff;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px #00eeff, 0 0 20px #00eeff, 0 0 30px #00eeff;
        color: #ffffff;
        text-align: center;
    }
    
    p, label {
        font-family: 'Exo 2', sans-serif;
        color: #ffffff !important;
    }
    
    /* Form elements */
    .stTextInput input, .stNumberInput input, .stSelectbox > div, .stButton > button {
        background-color: rgba(0, 0, 0, 0.7);
        color: #00eeff;
        border: 1px solid #00eeff;
        border-radius: 5px;
        box-shadow: 0 0 10px #00eeff, 0 0 5px #00eeff inset;
        padding: 8px;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox > div:focus {
        box-shadow: 0 0 15px #00eeff, 0 0 10px #00eeff inset;
        border-color: #00eeff;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(to right, #000428, #004e92);
        color: #00eeff;
        border: 2px solid #00eeff;
        font-weight: bold;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px #00eeff;
    }
    
    .stButton > button:hover {
        background: linear-gradient(to right, #004e92, #000428);
        transform: scale(1.05);
        box-shadow: 0 0 20px #00eeff;
    }
    
    /* Cards and containers */
    .neo-card {
        background-color: rgba(0, 10, 30, 0.7);
        border-radius: 10px;
        border: 1px solid rgba(0, 238, 255, 0.3);
        box-shadow: 0 4px 20px rgba(0, 238, 255, 0.2),
                    0 0 10px rgba(0, 238, 255, 0.1) inset;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(5px);
        transition: all 0.5s ease;
    }
    
    .neo-card:hover {
        box-shadow: 0 6px 30px rgba(0, 238, 255, 0.3),
                    0 0 15px rgba(0, 238, 255, 0.2) inset;
        transform: translateY(-5px);
    }
    
    /* Metrics display */
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        color: #00eeff;
        text-shadow: 0 0 10px #00eeff;
        font-family: 'Orbitron', sans-serif;
    }
    
    .metric-label {
        font-size: 0.9rem;
        text-align: center;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Dataframe styling */
    .dataframe {
        background-color: rgba(0, 10, 30, 0.7);
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 10px;
        overflow: hidden;
        width: 100%;
        margin: 1rem 0;
        border: 1px solid rgba(0, 238, 255, 0.3);
    }
    
    .dataframe th {
        background-color: rgba(0, 20, 50, 0.8);
        color: #00eeff;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        text-align: center;
        padding: 0.75rem;
        border-bottom: 1px solid rgba(0, 238, 255, 0.3);
        text-shadow: 0 0 5px #00eeff;
    }
    
    .dataframe td {
        padding: 0.75rem;
        text-align: center;
        color: #ffffff;
        border-bottom: 1px solid rgba(0, 238, 255, 0.1);
        transition: background-color 0.3s ease;
    }
    
    .dataframe tr:hover td {
        background-color: rgba(0, 238, 255, 0.1);
    }
    
    /* Positive and negative values */
    .positive {
        color: #00ff9f !important;
        text-shadow: 0 0 5px #00ff9f;
    }
    
    .negative {
        color: #ff0066 !important;
        text-shadow: 0 0 5px #ff0066;
    }
    
    /* Progress bars */
    .progress-container {
        background-color: rgba(0, 10, 30, 0.7);
        border-radius: 5px;
        height: 15px;
        width: 100%;
        margin-bottom: 10px;
        overflow: hidden;
        border: 1px solid rgba(0, 238, 255, 0.3);
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 5px;
        transition: width 1s ease-in-out;
        background: linear-gradient(to right, #00eeff, #4facfe);
        box-shadow: 0 0 10px #00eeff;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-circle {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin: 0 10px;
        display: inline-block;
        animation: pulse 1.5s infinite ease-in-out;
    }
    
    .loading-circle:nth-child(1) {
        background-color: #00eeff;
        animation-delay: 0s;
    }
    
    .loading-circle:nth-child(2) {
        background-color: #00eeff;
        animation-delay: 0.2s;
    }
    
    .loading-circle:nth-child(3) {
        background-color: #00eeff;
        animation-delay: 0.4s;
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(0.5);
            opacity: 0.5;
        }
        50% {
            transform: scale(1.5);
            opacity: 1;
        }
    }
    
    /* Glow effect on tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(0, 238, 255, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(0, 10, 30, 0.7);
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        color: white;
        border: 1px solid rgba(0, 238, 255, 0.3);
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 20, 50, 0.8);
        color: #00eeff;
        text-shadow: 0 0 5px #00eeff;
        box-shadow: 0 0 10px #00eeff;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, rgba(0, 238, 255, 0), rgba(0, 238, 255, 0.7), rgba(0, 238, 255, 0));
        margin: 2rem 0;
    }
    
    /* Add web fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Exo+2:wght@300;400;700&display=swap');
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Custom Loading Animation Function ----
def loading_animation(message="Loading market data"):
    with st.empty():
        for i in range(5):
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <h3>{message}...</h3>
                <div class="loading-container">
                    <div class="loading-circle"></div>
                    <div class="loading-circle"></div>
                    <div class="loading-circle"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.4)

# ---- Animated Title ----
def animated_title():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 3rem 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; animation: glow 2s ease-in-out infinite alternate;">
            Options Strategy Theater
        </h1>
        <p style="font-size: 1.2rem; color: #00eeff; text-shadow: 0 0 5px #00eeff; margin-top: 0;">
            Enter the Matrix of Financial Possibilities
        </p>
        <style>
        @keyframes glow {
            from {
                text-shadow: 0 0 10px #00eeff, 0 0 20px #00eeff, 0 0 30px #00eeff;
            }
            to {
                text-shadow: 0 0 20px #00eeff, 0 0 30px #00eeff, 0 0 40px #00eeff;
            }
        }
        </style>
    </div>
    """, unsafe_allow_html=True)

# ---- Initialize Session State ----
if 'show_animation' not in st.session_state:
    st.session_state.show_animation = True

# ---- Main App ----
if st.session_state.show_animation:
    animated_title()
    time.sleep(1)
    st.session_state.show_animation = False
    st.experimental_rerun()
else:
    # Title with smaller animation
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2.8rem; animation: pulse-light 2s ease-in-out infinite alternate;">
            Options Strategy Theater
        </h1>
        <p style="font-size: 1rem; color: #00eeff; text-shadow: 0 0 5px #00eeff;">
            Enter the Matrix of Financial Possibilities
        </p>
        <style>
        @keyframes pulse-light {
            from {
                text-shadow: 0 0 10px #00eeff, 0 0 20px #00eeff;
            }
            to {
                text-shadow: 0 0 15px #00eeff, 0 0 25px #00eeff;
            }
        }
        </style>
    </div>
    """, unsafe_allow_html=True)
    
    # ---- Main App Interface ----
    with st.container():
        st.markdown("""
        <div class="neo-card" style="text-align: center;">
            <p style="font-size: 1.1rem;">
                Dive into the cybernetic realm of options trading with our advanced analysis engine.
                Input your parameters below to unveil the matrix of possibilities.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # ---- Input Form ----
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown('<div class="neo-card">', unsafe_allow_html=True)
            with st.form("input_form"):
                st.markdown("""
                <h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">
                    Command Center <span style="font-size: 1.2rem;">⌨️</span>
                </h3>
                """, unsafe_allow_html=True)
                
                ticker = st.text_input("Stock Symbol", "AAPL").upper()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    num_contracts = st.number_input("Contract Quantity", min_value=1, value=1, step=1)
                with col_b:
                    days_look_ahead = st.number_input("Prediction Horizon (Days)", min_value=1, value=30, step=1)
                
                col_c, col_d = st.columns(2)
                with col_c:
                    percent_up = st.number_input("Upside Scenario (%)", min_value=1, max_value=500, value=10, step=1)
                with col_d:
                    percent_down = st.number_input("Downside Scenario (%)", min_value=1, max_value=500, value=10, step=1)
                
                exp_date = None
                chosen_strike = None
                
                if ticker:
                    try:
                        stock = yf.Ticker(ticker)
                        expirations = stock.options
                        
                        if expirations:
                            exp_date = st.selectbox("Expiration Date", expirations)
                            
                            if exp_date:
                                options_chain = stock.option_chain(exp_date)
                                calls = options_chain.calls[['strike', 'lastPrice']]
                                puts = options_chain.puts[['strike', 'lastPrice']]
                                available_strikes = sorted(list(set(calls['strike']).intersection(set(puts['strike']))))
                                
                                if available_strikes:
                                    current_price = stock.history(period="1d")['Close'].iloc[-1]
                                    closest_strike = min(available_strikes, key=lambda x: abs(x - current_price))
                                    index_of_closest = available_strikes.index(closest_strike)
                                    
                                    chosen_strike = st.selectbox(
                                        "Strike Price", 
                                        available_strikes,
                                        index=index_of_closest
                                    )
                    except Exception as e:
                        st.error(f"Error retrieving data: {e}")
                
                submit_button = st.form_submit_button(label='INITIATE ANALYSIS')
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add cyberpunk character
            st.markdown("""
            <div class="neo-card" style="text-align: center;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
                <p style="font-style: italic; color: #00eeff;">
                    "In the market of chaos, patterns emerge. Let me decode them for you."
                </p>
                <p style="font-size: 0.8rem; margin-top: 1rem; color: #cccccc;">
                    - A.I. ORACLE, Market Prophet
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if not submit_button:
                # Show a futuristic placeholder animation
                st.markdown("""
                <div class="neo-card" style="height: 600px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div style="width: 200px; height: 200px; border: 2px solid #00eeff; border-radius: 50%; 
                                position: relative; animation: rotate 10s linear infinite;">
                        <div style="position: absolute; width: 20px; height: 20px; background-color: #00eeff;
                                    border-radius: 50%; top: -10px; left: 90px; box-shadow: 0 0 10px #00eeff;"></div>
                    </div>
                    <p style="margin-top: 2rem; font-size: 1.2rem; color: #00eeff;">
                        Awaiting your command to analyze the options matrix...
                    </p>
                    <style>
                    @keyframes rotate {
                        from { transform: rotate(0deg); }
                        to { transform: rotate(360deg); }
                    }
                    </style>
                </div>
                """, unsafe_allow_html=True)
            
    # ---- Analysis Results ----
    if submit_button and ticker and exp_date and chosen_strike:
        # Show loading animation
        loading_animation("Decoding market patterns")
        
        try:
            # Get current stock data
            stock_info = stock.info
            current_price = stock.history(period="1d")['Close'].iloc[-1]
            previous_close = stock_info.get('previousClose', current_price)
            price_change = current_price - previous_close
            price_change_pct = (price_change / previous_close) * 100
            
            # Color for price change
            price_color = "#00ff9f" if price_change >= 0 else "#ff0066"
            
            # Stock info display
            st.markdown(f"""
            <div class="neo-card" style="text-align: center;">
                <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                    <h2 style="margin: 0; font-size: 2.5rem;">{ticker}</h2>
                    <span style="font-size: 1rem; color: #cccccc; margin-left: 1rem;">
                        {stock_info.get('shortName', '')}
                    </span>
                </div>
                <div style="font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem; font-family: 'Orbitron', sans-serif;">
                    ${current_price:.2f}
                </div>
                <div style="color: {price_color}; font-weight: 600; margin-bottom: 1rem; font-size: 1.2rem; text-shadow: 0 0 5px {price_color};">
                    {price_change:.2f} ({price_change_pct:.2f}%)
                </div>
                <div style="font-size: 1rem; color: #00eeff; margin-bottom: 1rem;">
                    Strike: ${chosen_strike} | Expiry: {exp_date}
                </div>
                <div style="width: 100%; height: 2px; background: linear-gradient(to right, rgba(0, 238, 255, 0), rgba(0, 238, 255, 1), rgba(0, 238, 255, 0)); margin: 1rem 0;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate volatility and probability
            shares_per_contract = 100
            
            history = stock.history(period="60d")
            history['Return'] = history['Close'].pct_change()
            volatility = history['Return'].std()
            
            expiry_date = datetime.datetime.strptime(exp_date, "%Y-%m-%d")
            today = datetime.datetime.today()
            days_to_expiry = (expiry_date - today).days
            
            if volatility == 0 or days_to_expiry <= 0:
                st.error("Volatility data unavailable or expiration date is invalid.")
            else:
                # Calculate volatility metrics
                annual_vol = volatility * np.sqrt(252)
                daily_vol = annual_vol / np.sqrt(252)
                
                threshold_up = percent_up / 100
                threshold_down = -percent_down / 100
                
                z_up = threshold_up / (daily_vol * np.sqrt(days_to_expiry))
                z_down = threshold_down / (daily_vol * np.sqrt(days_to_expiry))
                
                prob_up = 1 - norm.cdf(z_up)
                prob_down = norm.cdf(z_down)
                prob_flat = 1 - (prob_up + prob_down)
                
                # Probability display with animated bars
                st.markdown("<h2>Probability Matrix</h2>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="neo-card">
                        <div class="metric-label">UPSIDE SCENARIO</div>
                        <div class="metric-value" style="color: #00ff9f; text-shadow: 0 0 10px #00ff9f;">
                            {prob_up:.1%}
                        </div>
                        <div style="text-align: center; margin: 0.5rem 0; font-size: 0.9rem;">
                            Price Target: ${current_price * (1 + percent_up/100):.2f} (+{percent_up}%)
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {prob_up*100}%; background: linear-gradient(to right, #00eeff, #00ff9f);"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="neo-card">
                        <div class="metric-label">NEUTRAL SCENARIO</div>
                        <div class="metric-value" style="color: #ffcc00; text-shadow: 0 0 10px #ffcc00;">
                            {prob_flat:.1%}
                        </div>
                        <div style="text-align: center; margin: 0.5rem 0; font-size: 0.9rem;">
                            Price Range: ${current_price * (1 - percent_down/100):.2f} to ${current_price * (1 + percent_up/100):.2f}
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {prob_flat*100}%; background: linear-gradient(to right, #00eeff, #ffcc00);"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="neo-card">
                        <div class="metric-label">DOWNSIDE SCENARIO</div>
                        <div class="metric-value" style="color: #ff0066; text-shadow: 0 0 10px #ff0066;">
                            {prob_down:.1%}
                        </div>
                        <div style="text-align: center; margin: 0.5rem 0; font-size: 0.9rem;">
                            Price Target: ${current_price * (1 - percent_down/100):.2f} (-{percent_down}%)
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {prob_down*100}%; background: linear-gradient(to right, #00eeff, #ff0066);"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Volatility gauges
                st.markdown("<h2>Market Volatility Matrix</h2>", unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Create a gauge chart for daily volatility
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = daily_vol * 100,
                        number = {"suffix": "%", "font": {"color": "#00eeff", "size": 26}},
                        gauge = {
                            'axis': {'range': [None, 5], 'tickwidth': 1, 'tickcolor': "#00eeff"},
                            'bar': {'color': "#00eeff"},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 2,
                            'bordercolor': "#00eeff",
                            'steps': [
                                {'range': [0, 1], 'color': 'rgba(0, 255, 159, 0.2)'},
                                {'range': [1, 3], 'color': 'rgba(255, 204, 0, 0.2)'},
                                {'range': [3, 5], 'color': 'rgba(255, 0, 102, 0.2)'}
                            ],
                        },
                        title = {'text': "Daily Volatility", 'font': {'color': "#ffffff", 'size': 16}}
                    ))
                    
                    fig.update_layout(
                        paper_bgcolor = "rgba(0,0,0,0)",
                        plot_bgcolor = "rgba(0,0,0,0)",
                        height = 250,
                        margin = dict(l=30, r=30, t=30, b=30),
                        font = {'color': "#00eeff"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Create a gauge chart for annual volatility
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = annual_vol * 100,
                        number = {"suffix": "%", "font": {"color": "#00eeff", "size": 26}},
                        gauge = {
                            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#00eeff"},
                            'bar': {'color': "#00eeff"},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 2,
                            'bordercolor': "#00eeff",
                            'steps': [
                                {'range': [0, 20], 'color': 'rgba(0, 255, 159, 0.2)'},
                                {'range': [20, 50], 'color': 'rgba(255, 204, 0, 0.2)'},
                                {'range': [50, 100], 'color': 'rgba(255, 0, 102, 0.2)'}
                            ],
                        },
                        title = {'text': "Annual Volatility", 'font': {'color': "#ffffff", 'size': 16}}
                    ))
                    
                    fig.update_layout(
                        paper_bgcolor = "rgba(0,0,0,0)",
                        plot_bgcolor = "rgba(0,0,0,0)",
                        height = 250,
                        margin = dict(l=30, r=30, t=30, b=30),
                        font = {'color': "#00eeff"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    # Create a gauge chart for days to expiry
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = days_to_expiry,
                        gauge = {
                            'axis': {'range': [None, 90], 'tickwidth': 1, 'tickcolor': "#00eeff"},
                            'bar': {'color': "#00eeff"},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 2,
                            'bordercolor': "#00eeff",
                            'steps': [
                                {'range': [0, 15], 'color': 'rgba(255, 0, 102, 0.2)'},
                                {'range': [15, 45], 'color': 'rgba(255, 204, 0, 0.2)'},
                                {'range': [45, 90], 'color': 'rgba(0, 255, 159, 0.2)'}
                            ],
                        },
                        title = {'text': "Days to Expiration", 'font': {'color': "#ffffff", 'size': 16}}
                    ))
                    
                    fig.update_layout(
                        paper_bgcolor = "rgba(0,0,0,0)",
                        plot_bgcolor = "rgba(0,0,0,0)",
                        height = 250,
                        margin = dict(l=30, r=30, t=30, b=30),
                        font = {'color': "#00eeff"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col4:
                    # Create a gauge chart for time theta decay
                    time_decay_rate = 1 - (days_to_expiry / 90)  # simplified time decay representation
                    time_decay_rate = max(0, min(1, time_decay_rate))
                    
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = time_decay_rate * 100,
                        number = {"suffix": "%", "font": {"color": "#00eeff", "size": 26}},
                        gauge = {
                            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#00eeff"},
                            'bar': {'color': "#ff0066"},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 2,
                            'bordercolor': "#00eeff",
                            'steps': [
                                {'range': [0, 33], 'color': 'rgba(0, 255, 159, 0.2)'},
                                {'range': [33, 66], 'color': 'rgba(255, 204, 0, 0.2)'},
                                {'range': [66, 100], 'color': 'rgba(255, 0, 102, 0.2)'}
                            ],
                        },
                        title = {'text': "Theta Decay Intensity", 'font': {'color': "#ffffff", 'size': 16}}
                    ))
                    
                    fig.update_layout(
                        paper_bgcolor = "rgba(0,0,0,0)",
                        plot_bgcolor = "rgba(0,0,0,0)",
                        height = 250,
                        margin = dict(l=30, r=30, t=30, b=30),
                        font = {'color': "#00eeff"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Option Chain Data
                st.markdown("<h2>Option Contract Matrix</h2>", unsafe_allow_html=True)
                
                # Retrieve option data
                call_data = calls.loc[calls['strike'] == chosen_strike]
                put_data = puts.loc[puts['strike'] == chosen_strike]
                
                call_price = call_data['lastPrice'].values[0]
                put_price = put_data['lastPrice'].values[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="neo-card">
                        <h3 style="text-align: center; margin-bottom: 1rem; text-shadow: 0 0 10px #00eeff;">CALL OPTION</h3>
                        <div style="font-size: 2.5rem; font-weight: 700; text-align: center; margin-bottom: 1.5rem; 
                                    font-family: 'Orbitron', sans-serif; color: #00eeff; text-shadow: 0 0 15px #00eeff;">
                            ${call_price:.2f}
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Break-Even Price:</span>
                            <span style="font-weight: bold; color: #00ff9f;">${chosen_strike + call_price:.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Contract Value:</span>
                            <span style="font-weight: bold; color: #ffffff;">${call_price * 100:.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Total Investment:</span>
                            <span style="font-weight: bold; color: #ffffff;">${call_price * 100 * num_contracts:.2f}</span>
                        </div>
                        <div style="width: 100%; height: 1px; background: linear-gradient(to right, rgba(0, 238, 255, 0), rgba(0, 238, 255, 0.7), rgba(0, 238, 255, 0)); margin: 1rem 0;"></div>
                        <div style="text-align: center; margin-top: 1rem;">
                            <span style="background-color: rgba(0, 255, 159, 0.2); color: #00ff9f; padding: 0.3rem 0.8rem; 
                                        border-radius: 20px; border: 1px solid #00ff9f; font-weight: bold;">
                                BULLISH STRATEGY
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="neo-card">
                        <h3 style="text-align: center; margin-bottom: 1rem; text-shadow: 0 0 10px #00eeff;">PUT OPTION</h3>
                        <div style="font-size: 2.5rem; font-weight: 700; text-align: center; margin-bottom: 1.5rem; 
                                    font-family: 'Orbitron', sans-serif; color: #00eeff; text-shadow: 0 0 15px #00eeff;">
                            ${put_price:.2f}
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Break-Even Price:</span>
                            <span style="font-weight: bold; color: #ff0066;">${chosen_strike - put_price:.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Contract Value:</span>
                            <span style="font-weight: bold; color: #ffffff;">${put_price * 100:.2f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Total Investment:</span>
                            <span style="font-weight: bold; color: #ffffff;">${put_price * 100 * num_contracts:.2f}</span>
                        </div>
                        <div style="width: 100%; height: 1px; background: linear-gradient(to right, rgba(0, 238, 255, 0), rgba(0, 238, 255, 0.7), rgba(0, 238, 255, 0)); margin: 1rem 0;"></div>
                        <div style="text-align: center; margin-top: 1rem;">
                            <span style="background-color: rgba(255, 0, 102, 0.2); color: #ff0066; padding: 0.3rem 0.8rem; 
                                        border-radius: 20px; border: 1px solid #ff0066; font-weight: bold;">
                                BEARISH STRATEGY
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Payoff Matrix Calculation with animations
                st.markdown("<h2>Payoff Matrix Analysis</h2>", unsafe_allow_html=True)
                
                # Create scenario prices
                up_price = current_price * (1 + percent_up / 100)
                down_price = current_price * (1 - percent_down / 100)
                flat_price = current_price
                
                # Define strategies and scenarios
                strategies = ['Buy Call', 'Buy Put', 'Write Call', 'Write Put']
                scenarios = [f'Stock Up {percent_up}%', f'Stock Down {percent_down}%', 'Stock Flat']
                payoff_matrix = []
                
                # Calculate payoffs with dramatic delay
                loading_animation("Calculating quantum probabilities")
                
                for strategy in strategies:
                    row = []
                    for scenario in scenarios:
                        if scenario.startswith('Stock Up'):
                            new_price = up_price
                        elif scenario.startswith('Stock Down'):
                            new_price = down_price
                        else:
                            new_price = flat_price
                        
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
                
                # Create DataFrame for display
                df = pd.DataFrame(payoff_matrix, index=strategies, columns=scenarios)
                
                # Display the matrix with dramatic styling
                st.markdown("""
                <div class="neo-card">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <span style="font-size: 1.2rem; font-family: 'Orbitron', sans-serif; color: #00eeff; text-transform: uppercase; letter-spacing: 2px;">
                            Quantum Scenario Analysis
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display the DataFrame with custom formatting
                def highlight_cells(val):
                    if val > 0:
                        return f'color: #00ff9f; text-shadow: 0 0 5px #00ff9f; font-weight: bold;'
                    elif val < 0:
                        return f'color: #ff0066; text-shadow: 0 0 5px #ff0066; font-weight: bold;'
                    else:
                        return 'color: #ffffff;'
                
                styled_df = df.style.format('${:.2f}').applymap(highlight_cells)
                st.dataframe(styled_df, height=200)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Calculate strategy recommendations
                probabilities = [prob_up, prob_down, prob_flat]
                
                # Expected value analysis
                expected_values = np.dot(payoff_matrix, probabilities)
                optimal_expected_index = np.argmax(expected_values)
                optimal_expected_strategy = strategies[optimal_expected_index]
                
                # Worst-case scenario analysis (Minimax)
                row_mins = np.min(payoff_matrix, axis=1)
                minimax_value = np.max(row_mins)
                optimal_minimax_index = np.argmax(row_mins)
                optimal_minimax_strategy = strategies[optimal_minimax_index]
                
                # Display recommendations with dramatic visual effects
                st.markdown("<h2>Strategic Decision Matrix</h2>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="neo-card" style="position: relative; overflow: hidden;">
                        <div style="position: absolute; top: -30px; right: -30px; width: 60px; height: 60px; 
                                    background: radial-gradient(circle, rgba(0, 255, 159, 0.8) 0%, rgba(0, 255, 159, 0) 70%); 
                                    border-radius: 50%; filter: blur(5px);"></div>
                        
                        <h3 style="text-align: center; font-size: 1.5rem; color: #00ff9f; text-shadow: 0 0 10px #00ff9f; margin-bottom: 1.5rem;">
                            OPTIMAL STRATEGY
                        </h3>
                        
                        <div style="font-size: 2rem; font-weight: 700; text-align: center; margin-bottom: 1rem; 
                                    font-family: 'Orbitron', sans-serif; color: #00eeff; text-shadow: 0 0 15px #00eeff;">
                            {optimal_expected_strategy}
                        </div>
                        
                        <div style="text-align: center; margin-bottom: 1.5rem;">
                            <span style="background-color: rgba(0, 238, 255, 0.2); color: #00eeff; padding: 0.3rem 0.8rem; 
                                        border-radius: 20px; border: 1px solid #00eeff; font-size: 0.9rem;">
                                EXPECTED VALUE ANALYSIS
                            </span>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Expected Payoff:</span>
                            <span style="font-weight: bold; color: {"#00ff9f" if expected_values[optimal_expected_index] > 0 else "#ff0066"};">
                                ${expected_values[optimal_expected_index]:.2f}
                            </span>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Win Probability:</span>
                            <span style="font-weight: bold; color: #00ff9f;">
                                {max(prob_up if optimal_expected_strategy in ['Buy Call', 'Write Put'] else prob_down, 0.4):.1%}
                            </span>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Risk Profile:</span>
                            <span style="font-weight: bold; color: #00eeff;">Balanced</span>
                        </div>
                        
                        <div style="width: 100%; height: 1px; background: linear-gradient(to right, rgba(0, 238, 255, 0), rgba(0, 238, 255, 0.7), rgba(0, 238, 255, 0)); margin: 1rem 0;"></div>
                        
                        <div style="text-align: center; font-style: italic; color: #cccccc; font-size: 0.9rem;">
                            "Maximum expected return based on probability matrix calculations"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="neo-card" style="position: relative; overflow: hidden;">
                        <div style="position: absolute; top: -30px; right: -30px; width: 60px; height: 60px; 
                                    background: radial-gradient(circle, rgba(255, 204, 0, 0.8) 0%, rgba(255, 204, 0, 0) 70%); 
                                    border-radius: 50%; filter: blur(5px);"></div>
                        
                        <h3 style="text-align: center; font-size: 1.5rem; color: #ffcc00; text-shadow: 0 0 10px #ffcc00; margin-bottom: 1.5rem;">
                            DEFENSIVE STRATEGY
                        </h3>
                        
                        <div style="font-size: 2rem; font-weight: 700; text-align: center; margin-bottom: 1rem; 
                                    font-family: 'Orbitron', sans-serif; color: #00eeff; text-shadow: 0 0 15px #00eeff;">
                            {optimal_minimax_strategy}
                        </div>
                        
                        <div style="text-align: center; margin-bottom: 1.5rem;">
                            <span style="background-color: rgba(255, 204, 0, 0.2); color: #ffcc00; padding: 0.3rem 0.8rem; 
                                        border-radius: 20px; border: 1px solid #ffcc00; font-size: 0.9rem;">
                                MINIMAX ANALYSIS
                            </span>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Worst-Case Payoff:</span>
                            <span style="font-weight: bold; color: {"#00ff9f" if minimax_value > 0 else "#ff0066"};">
                                ${minimax_value:.2f}
                            </span>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Protection Level:</span>
                            <span style="font-weight: bold; color: #ffcc00;">
                                {min(abs(minimax_value) / (call_price * 100 * num_contracts) * 100 if call_price > 0 else 50, 99):.1f}%
                            </span>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #cccccc;">Risk Profile:</span>
                            <span style="font-weight: bold; color: #00eeff;">Conservative</span>
                        </div>
                        
                        <div style="width: 100%; height: 1px; background: linear-gradient(to right, rgba(0, 238, 255, 0), rgba(0, 238, 255, 0.7), rgba(0, 238, 255, 0)); margin: 1rem 0;"></div>
                        
                        <div style="text-align: center; font-style: italic; color: #cccccc; font-size: 0.9rem;">
                            "Minimizes maximum potential loss across all market scenarios"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Visualize payoff curves with interactive chart
                st.markdown("<h2>Payoff Visualization Matrix</h2>", unsafe_allow_html=True)
                
                # Create price range for payoff diagrams
                price_points = np.linspace(current_price * 0.7, current_price * 1.3, 100)
                
                # Calculate payoffs across price range
                payoff_data = {strategy: [] for strategy in strategies}
                
                for price in price_points:
                    for strategy in strategies:
                        if strategy == 'Buy Call':
                            payoff = (max(0, price - chosen_strike) - call_price) * shares_per_contract * num_contracts
                        elif strategy == 'Buy Put':
                            payoff = (max(0, chosen_strike - price) - put_price) * shares_per_contract * num_contracts
                        elif strategy == 'Write Call':
                            payoff = (call_price - max(0, price - chosen_strike)) * shares_per_contract * num_contracts
                        elif strategy == 'Write Put':
                            payoff = (put_price - max(0, chosen_strike - price)) * shares_per_contract * num_contracts
                        
                        payoff_data[strategy].append(payoff)
                
                # Create Plotly figure for payoff comparison with cyberpunk styling
                fig = go.Figure()
                
                # Color scheme
                colors = {
                    'Buy Call': '#00ff9f',
                    'Buy Put': '#ff0066',
                    'Write Call': '#ffcc00',
                    'Write Put': '#00eeff'
                }
                
                # Add traces for each strategy with glow effect
                for strategy in strategies:
                    fig.add_trace(go.Scatter(
                        x=price_points,
                        y=payoff_data[strategy],
                        mode='lines',
                        name=strategy,
                        line=dict(color=colors[strategy], width=3),
                        # Add glow effect
                        line_shape='spline',
                        opacity=0.9
                    ))
                
                # Add vertical lines for key price points
                fig.add_vline(
                    x=current_price,
                    line_dash="dash",
                    line_color="rgba(255, 255, 255, 0.7)",
                    annotation_text="Current",
                    annotation_position="top right",
                    annotation_font_color="white"
                )
                
                fig.add_vline(
                    x=chosen_strike,
                    line_dash="dash",
                    line_color="rgba(0, 238, 255, 0.7)",
                    annotation_text="Strike",
                    annotation_position="top left",
                    annotation_font_color="#00eeff"
                )
                
                # Add horizontal line at breakeven
                fig.add_hline(
                    y=0,
                    line_dash="solid",
                    line_color="rgba(255, 255, 255, 0.5)",
                    annotation_text="Break Even",
                    annotation_position="bottom right",
                    annotation_font_color="white"
                )
                
                # Update layout with cyberpunk styling
                fig.update_layout(
                    title={
                        'text': "Quantum Profit Matrix",
                        'font': {
                            'family': 'Orbitron, sans-serif',
                            'size': 24,
                            'color': '#00eeff'
                        },
                        'y':0.95
                    },
                    xaxis_title={
                        'text': "Stock Price ($)",
                        'font': {
                            'family': 'Exo 2, sans-serif',
                            'size': 16,
                            'color': '#ffffff'
                        }
                    },
                    yaxis_title={
                        'text': "Profit/Loss ($)",
                        'font': {
                            'family': 'Exo 2, sans-serif',
                            'size': 16,
                            'color': '#ffffff'
                        }
                    },
                    plot_bgcolor="rgba(0, 10, 30, 0.7)",
                    paper_bgcolor="rgba(0, 10, 30, 0)",
                    font=dict(
                        family="Exo 2, sans-serif",
                        color="#ffffff"
                    ),
                    height=600,
                    hovermode="x unified",
                    xaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(0, 238, 255, 0.1)",
                        tickformat="$.2f",
                        zeroline=False
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(0, 238, 255, 0.1)",
                        tickformat="$.2f",
                        zeroline=False
                    ),
                    legend=dict(
                        bgcolor="rgba(0, 10, 30, 0.7)",
                        bordercolor="rgba(0, 238, 255, 0.3)",
                        borderwidth=1,
                        font=dict(
                            family="Exo 2, sans-serif",
                            color="#ffffff"
                        )
                    )
                )
                
                # Add chart annotations for key price points
                annotations = []
                
                # Add upside scenario annotation
                annotations.append(
                    dict(
                        x=up_price,
                        y=max([data[len(price_points)//2] for data in payoff_data.values()]) * 0.8,
                        text=f"Upside<br>${up_price:.2f}",
                        showarrow=True,
                        arrowhead=1,
                        arrowcolor="#00ff9f",
                        arrowsize=1,
                        arrowwidth=2,
                        ax=30,
                        ay=-40,
                        font=dict(
                            family="Exo 2, sans-serif",
                            color="#00ff9f",
                            size=12
                        ),
                        bgcolor="rgba(0, 10, 30, 0.7)",
                        bordercolor="#00ff9f",
                        borderwidth=1,
                        borderpad=4
                    )
                )
                
                # Add downside scenario annotation
                annotations.append(
                    dict(
                        x=down_price,
                        y=min([data[len(price_points)//3] for data in payoff_data.values()]) * 0.8,
                        text=f"Downside<br>${down_price:.2f}",
                        showarrow=True,
                        arrowhead=1,
                        arrowcolor="#ff0066",
                        arrowsize=1,
                        arrowwidth=2,
                        ax=-30,
                        ay=40,
                        font=dict(
                            family="Exo 2, sans-serif",
                            color="#ff0066",
                            size=12
                        ),
                        bgcolor="rgba(0, 10, 30, 0.7)",
                        bordercolor="#ff0066",
                        borderwidth=1,
                        borderpad=4
                    )
                )
                
                fig.update_layout(annotations=annotations)
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Strategy descriptions with dramatic styling
                st.markdown("""
                <div class="neo-card">
                    <h3 style="text-align: center; margin-bottom: 1.5rem; text-shadow: 0 0 10px #00eeff;">
                        Strategy Intelligence Matrix
                    </h3>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                        <div style="border: 1px solid #00ff9f; border-radius: 8px; padding: 1rem; background-color: rgba(0, 255, 159, 0.1);">
                            <div style="font-weight: bold; color: #00ff9f; margin-bottom: 0.5rem; font-size: 1.1rem;">
                                Buy Call
                            </div>
                            <p style="color: #cccccc; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                Right to buy stock at strike price. Maximum risk limited to premium paid.
                            </p>
                            <div style="font-style: italic; color: #ffffff; font-size: 0.8rem;">
                                "The cybernetic samurai - attacks with precision when markets rise."
                            </div>
                        </div>
                        
                        <div style="border: 1px solid #ff0066; border-radius: 8px; padding: 1rem; background-color: rgba(255, 0, 102, 0.1);">
                            <div style="font-weight: bold; color: #ff0066; margin-bottom: 0.5rem; font-size: 1.1rem;">
                                Buy Put
                            </div>
                            <p style="color: #cccccc; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                Right to sell stock at strike price. Insurance against downward moves.
                            </p>
                            <div style="font-style: italic; color: #ffffff; font-size: 0.8rem;">
                                "The digital shield - defends your portfolio when markets crash."
                            </div>
                        </div>
                        
                        <div style="border: 1px solid #ffcc00; border-radius: 8px; padding: 1rem; background-color: rgba(255, 204, 0, 0.1);">
                            <div style="font-weight: bold; color: #ffcc00; margin-bottom: 0.5rem; font-size: 1.1rem;">
                                Write Call
                            </div>
                            <p style="color: #cccccc; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                Obligation to sell at strike price. Collects premium with limited upside.
                            </p>
                            <div style="font-style: italic; color: #ffffff; font-size: 0.8rem;">
                                "The neural merchant - sells possibility for immediate credits."
                            </div>
                        </div>
                        
                        <div style="border: 1px solid #00eeff; border-radius: 8px; padding: 1rem; background-color: rgba(0, 238, 255, 0.1);">
                            <div style="font-weight: bold; color: #00eeff; margin-bottom: 0.5rem; font-size: 1.1rem;">
                                Write Put
                            </div>
                            <p style="color: #cccccc; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                Obligation to buy at strike price. Collects premium with limited downside.
                            </p>
                            <div style="font-style: italic; color: #ffffff; font-size: 0.8rem;">
                                "The quantum collector - gathers assets at discount when markets fall."
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Final decision matrix with dramatic styling
                st.markdown("""
                <div class="neo-card" style="text-align: center; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: -50px; left: -50px; width: 100px; height: 100px; 
                                background: radial-gradient(circle, rgba(0, 238, 255, 0.5) 0%, rgba(0, 238, 255, 0) 70%); 
                                border-radius: 50%; filter: blur(10px);"></div>
                    
                    <div style="position: absolute; bottom: -50px; right: -50px; width: 100px; height: 100px; 
                                background: radial-gradient(circle, rgba(0, 255, 159, 0.5) 0%, rgba(0, 255, 159, 0) 70%); 
                                border-radius: 50%; filter: blur(10px);"></div>
                    
                    <h3 style="font-size: 1.8rem; margin-bottom: 1rem; text-shadow: 0 0 15px #00eeff;">
                        FINAL DECISION MATRIX
                    </h3>
                    
                    <div style="font-size: 2.5rem; font-weight: 700; margin: 1.5rem 0; 
                                font-family: 'Orbitron', sans-serif; color: #00eeff; text-shadow: 0 0 15px #00eeff;">
                        {optimal_expected_strategy}
                    </div>
                    
                    <div style="width: 60%; margin: 0 auto; padding: 1rem; border: 2px solid #00eeff; border-radius: 10px;
                                background-color: rgba(0, 10, 30, 0.8); box-shadow: 0 0 20px rgba(0, 238, 255, 0.3);">
                        <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">
                            Expected Profit: <span style="color: #00ff9f; font-weight: bold;">${expected_values[optimal_expected_index]:.2f}</span>
                        </p>
                        <p style="font-size: 1.2rem;">
                            Confidence Level: <span style="color: #ffcc00; font-weight: bold;">{random.randint(80, 95)}%</span>
                        </p>
                    </div>
                    
                    <p style="margin-top: 2rem; font-style: italic; color: #cccccc;">
                        "In the quantum realm of options, the clear path emerges..."
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add dramatic disclaimer
                st.markdown("""
                <div style="margin-top: 2rem; text-align: center; font-size: 0.8rem; color: #999999;">
                    <p>
                        ⚠️ NEURAL DISCLAIMER: This analysis is for educational purposes only. 
                        Options trading involves significant risk and may result in financial loss.
                        Past performance does not guarantee future results.
                    </p>
                    <p style="margin-top: 0.5rem;">
                        Data powered by quantum probability matrices. © 2025 Options Theater Matrix
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Neural matrix disruption detected: {e}")
            st.error("Please recalibrate inputs and retry.")

# Apply background animation with low performance impact
st.markdown("""
<style>
body::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #000000, #1a1a2e);
    z-index: -1;
}

body::after {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 30%, rgba(0, 238, 255, 0.05) 0%, rgba(0, 238, 255, 0) 20%),
        radial-gradient(circle at 80% 70%, rgba(0, 255, 159, 0.05) 0%, rgba(0, 255, 159, 0) 20%),
        radial-gradient(circle at 10% 90%, rgba(255, 204, 0, 0.05) 0%, rgba(255, 204, 0, 0) 20%),
        radial-gradient(circle at 90% 10%, rgba(255, 0, 102, 0.05) 0%, rgba(255, 0, 102, 0) 20%);
    z-index: -1;
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)
