import streamlit as st

from src.prediction.data import ingest_data

st.button('Ingest data', on_click=ingest_data)