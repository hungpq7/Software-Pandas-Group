import streamlit as st

page_predition = st.Page('pages/prediction.py', title='Stock Return Prediction')
page_chatbot = st.Page('pages/chatbot.py', title='Investment Buddy')

pg = st.navigation([page_predition, page_chatbot])
pg.run()