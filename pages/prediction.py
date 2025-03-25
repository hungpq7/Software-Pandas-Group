import streamlit as st

from core.prediction.data import ingest_data, init_data
from core.prediction.plot import plot_candlestick
from core.prediction.ticker import TICKERS

st.title('Stock Return Prediction')

df = init_data()
if st.button('Ingest data'):
    df = ingest_data()

ticker = st.selectbox('Ticker', options=TICKERS)

if st.button('Plot candlestick'):
    fig = plot_candlestick(df, ticker)
    st.plotly_chart(fig)