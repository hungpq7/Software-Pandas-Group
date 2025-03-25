import streamlit as st

page_prediction = st.Page('prediction/streamlit.py', title='Stock Return Prediction')
page_chatbot = st.Page('chatbot/streamlit.py', title='Investment Buddy')

pg = st.navigation([page_prediction, page_chatbot])
pg.run()