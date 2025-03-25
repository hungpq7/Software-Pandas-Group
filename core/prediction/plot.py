import plotly.graph_objects as go
import pandas as pd

def plot_candlestick(ticker, df):
    fig = go.Figure(
        data=[go.Candlestick(x=df['Date'],
        open=df['AAPL.Open'],
        high=df['AAPL.High'],
        low=df['AAPL.Low'],
        close=df['AAPL.Close'])]
    )
    return fig