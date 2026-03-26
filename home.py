import streamlit as st

def render():
    st.markdown("""
    <div class="home-hero">
        <p class="hero-eyebrow">✦ Your Intelligent Financial Companion</p>
        <h1 class="hero-title">
            Fin<span class="hero-title-accent">ancy</span>
        </h1>
        <div class="hero-divider"></div>
        <p class="hero-subtitle">
            Decode your spending, build better habits, and get answers to every money question — powered by AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Center the cards
    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m:
        c1, c2 = st.columns(2, gap="large")

        with c1:
            st.markdown("""
            <div class="choice-card gold-card" id="tracker-card">
                <span class="card-icon">📊</span>
                <div class="card-title">Personalized Financial Tracker</div>
                <div class="card-desc">
                    Upload 1–3 months of bank statements. Our model analyses your spending patterns, identifies opportunities, and builds a custom tracker just for you.
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Get My Tracker", key="go_tracker", use_container_width=True):
                st.session_state.page = "tracker"
                st.rerun()

        with c2:
            st.markdown("""
            <div class="choice-card emerald-card" id="chat-card">
                <span class="card-icon">💬</span>
                <div class="card-title">Talk to Financy</div>
                <div class="card-desc">
                    Ask anything — investing, saving for a trip or home, credit building, budgeting strategies. Financy is your always-on personal finance educator.
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Chatting", key="go_chat", use_container_width=True):
                st.session_state.page = "financy_chat"
                st.rerun()

    # Bottom decorative footer text
    st.markdown("""
    <div style="text-align:center; margin-top:3rem; padding-bottom:2rem;">
        <p style="font-size:0.72rem; color:#3a3a52; letter-spacing:0.15em; text-transform:uppercase;">
            Your data stays private &nbsp;·&nbsp; No financial advice is stored
        </p>
    </div>
    """, unsafe_allow_html=True)
