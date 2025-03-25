import streamlit as st

page_predition = st.Page('prediction/streamlit.py', title='Stock Return Prediction')
page_chatbot = st.Page('chatbot/streamlit.py', title='Investment Buddy')

pg = st.navigation([page_predition, page_chatbot])
pg.run()