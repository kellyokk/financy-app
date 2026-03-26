import streamlit as st

st.set_page_config(
    page_title="Financy — Your Financial Companion",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
with open("styles/main.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Navigation state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Route pages
if st.session_state.page == "home":
    from home import render
    render()
elif st.session_state.page == "tracker":
    from tracker import render
    render()
elif st.session_state.page == "financy_chat":
    from chat import render
    render()
