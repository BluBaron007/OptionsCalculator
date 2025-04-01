Introducing Strikely

The professional-grade web application for modeling and evaluating options strategies using live market data. This tool is designed for traders, analysts, and portfolio managers seeking robust decision-support for options trades.

---

## ✦ Key Features

- **Real-Time Market Data**  
  Live stock price and options chain data via Yahoo Finance API.
  
- **Customizable Inputs**  
  Define:
  - Stock ticker symbol
  - Expiration date
  - Strike price
  - Number of contracts
  - Custom up/down stock movement percentages

- **Advanced Scenario Analysis**  
  - Calculates scenario probabilities based on historical volatility.
  - Provides **Minimax Strategy** (worst-case payoff) and **Expected Value Strategy** recommendations based on John Von Neumanns' theory.

- **Payoff Matrix Visualization**  
  Interactive matrix and heatmap visuals displaying payoffs under user-defined scenarios.

---

## ✦ Technology Stack

- Python 3
- Streamlit
- yFinance API
- NumPy & Pandas
- Matplotlib
- SciPy (Probability Modeling)

---

## ✦ Deployment & Usage

**Run Locally:**

1. Clone repository:

```bash
git clone https://https://github.com/BluBaron007/optionsassistant
cd options-strategy-predictor
