import streamlit as st

st.set_page_config(
    page_title="Financy — Your Financial Companion",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open("styles/main.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



