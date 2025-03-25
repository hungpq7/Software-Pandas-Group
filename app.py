import streamlit as st

page_prediction = st.Page('pages/prediction.py', title='Stock Return Prediction')
page_chatbot = st.Page('pages/chatbot.py', title='Investment Buddy')

pg = st.navigation([page_prediction, page_chatbot])
pg.run()