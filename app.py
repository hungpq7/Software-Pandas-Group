import streamlit as st

page_prediction = st.Page('pages/prediction.py', title='STOCK PREDICTION')
page_chatbot = st.Page('pages/chatbot.py', title='INVESTMENT BUDDY')

pg = st.navigation([page_prediction, page_chatbot])
pg.run()