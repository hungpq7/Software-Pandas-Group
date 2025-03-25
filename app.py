import streamlit as st

st.title('Stock')


pg = st.navigation([
    st.Page("pages/prediction.py"),
    st.Page("pages/chatbot.py")
])
pg.run()

