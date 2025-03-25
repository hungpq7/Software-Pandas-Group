import streamlit as st

from ..prediction.data import ingest_data, init_data
from ..prediction.plot import plot_candlestick
from ..prediction.ticker import TICKERS

df = init_data()

if st.button('Ingest data'):
    df = ingest_data()

ticker = st.radio('Ticker', options=TICKERS)

if st.button('Plot candlestick'):
    fig = plot_candlestick()
    st.plotly_chart(fig)