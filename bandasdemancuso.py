import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Streamlit app configuration
st.title("Análisis de Bandas con yFinance")

# Ticker input
ticker_input = st.text_input("Ingrese el ticker o relación de tickers (ej. AAPL, MSFT/AAPL):", value="AAPL")

# Date range selection
start_date = st.date_input("Fecha de inicio", value=pd.to_datetime("2022-01-01"))
end_date = st.date_input("Fecha de fin", value=datetime.now().date())

# Fetch data from yFinance
def fetch_data(ticker, start, end):
    # Handle ratio of tickers
    if "/" in ticker:
        ticker1, ticker2 = ticker.split("/")
        data1 = yf.download(ticker1, start=start, end=end)
        data2 = yf.download(ticker2, start=start, end=end)
        return data1['Adj Close'] / data2['Adj Close']
    else:
        data = yf.download(ticker, start=start, end=end)
        return data['Adj Close']

# Fetch selected ticker data
prices = fetch_data(ticker_input, start_date, end_date)
df = pd.DataFrame(prices, columns=['Close'])

# Calculate the upper, lower, and middle bands
def calculate_bands(df):
    df['Min 10D'] = df['Close'].rolling(window=10).min()
    df['Max 10D'] = df['Close'].rolling(window=10).max()

    # Ranges over the last 3 days
    df['Range'] = df['Close'].rolling(window=1).max() - df['Close'].rolling(window=1).min()
    avg_range_last_3_days = df['Range'].rolling(window=3).mean()

    # Upper band: max of last 10 days + 2 * average range of last 3 days
    df['Upper Band'] = df['Max 10D'] + 2 * avg_range_last_3_days

    # Lower band: min of last 10 days - 2 * average range of last 3 days
    df['Lower Band'] = df['Min 10D'] - 2 * avg_range_last_3_days

    # Middle band: midpoint between the upper and lower band
    df['Middle Band'] = (df['Upper Band'] + df['Lower Band']) / 2

    return df

# Apply the band calculation
df = calculate_bands(df)

# Plotting the data
fig = go.Figure()

# Plot the actual price
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name=ticker_input))

# Plot the upper, middle, and lower bands
fig.add_trace(go.Scatter(x=df.index, y=df['Upper Band'], mode='lines', name='Banda Superior', line=dict(color='green')))
fig.add_trace(go.Scatter(x=df.index, y=df['Middle Band'], mode='lines', name='Banda Intermedia', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=df.index, y=df['Lower Band'], mode='lines', name='Banda Inferior', line=dict(color='red')))

# Update layout for better visualization
fig.update_layout(
    title=f"Precio de {ticker_input} con Bandas Superior, Inferior y Intermedia",
    xaxis_title="Fecha",
    yaxis_title="Precio",
    legend_title="Indicadores",
    hovermode="x unified"
)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

