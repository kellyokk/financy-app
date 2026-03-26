import streamlit as st
from datetime import datetime
import anthropic

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Financy, a warm, knowledgeable, and encouraging personal finance educator AI assistant.

Your personality:
- Friendly, approachable, and judgment-free — never shame users about past decisions
- Clear and jargon-light — explain complex concepts simply but accurately
- Empowering — your goal is to build the user's financial confidence
- Practical — always give actionable, concrete steps

Your expertise covers:
- Budgeting strategies (50/30/20, zero-based, envelope, etc.)
- Saving for specific goals: vacations, home down payments, emergencies, education
- Investing basics: index funds, ETFs, RRSPs, TFSAs (Canadian context), 401k/Roth IRA (US context)
- Debt management: credit cards, student loans, mortgages, snowball vs avalanche methods
- Credit building: credit scores, secured cards, utilization, payment history
- Side income and wealth-building mindset
- Insurance basics and financial protection

Important guidelines:
- Always clarify you're an educator, not a licensed financial advisor, for specific investment decisions
- Ask clarifying questions when needed to give personalized advice
- Use friendly formatting: short paragraphs, occasional bullet points, emojis sparingly
- Keep responses concise but complete — aim for clarity over length
- Reference specific numbers and percentages when helpful
- Celebrate wins and milestones — positive reinforcement matters

Format your responses in plain conversational text. No excessive markdown headers.
"""

# ── Suggested questions ───────────────────────────────────────────────────────

SUGGESTIONS = [
    "How do I build credit from scratch?",
    "Best way to save for a home down payment?",
    "Explain index funds simply",
    "How much should I have in emergency savings?",
    "How do I stop overspending on food?",
    "What's a TFSA and should I use one?",
    "Help me save $5,000 for a trip",
    "Snowball vs avalanche debt method?",
]

# ── helpers ───────────────────────────────────────────────────────────────────

def _timestamp():
    return datetime.now().strftime("%I:%M %p")


def _get_ai_response(messages: list) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return response.content[0].text


def _render_message(role: str, content: str, time_str: str):
    if role == "assistant":
        st.markdown(f"""
        <div class="msg-row">
            <div class="msg-avatar-sm">💎</div>
            <div>
                <div class="msg-bubble ai-bubble">{content}</div>
                <div class="msg-time">{time_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row user-row">
            <div class="msg-avatar-sm user-avatar-sm">👤</div>
            <div>
                <div class="msg-bubble user-bubble">{content}</div>
                <div class="msg-time" style="text-align:right;">{time_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── main render ───────────────────────────────────────────────────────────────

def render():
    # Init chat state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        st.session_state.chat_display = []  # includes timestamps

    # Back button
    if st.button("← Back to Home", key="back_chat"):
        st.session_state.page = "home"
        st.rerun()

    # Header
    st.markdown("""
    <div class="chat-header">
        <div class="chat-avatar">💎</div>
        <div>
            <div class="chat-info-name">Financy</div>
            <div class="chat-info-status">
                <span class="status-dot"></span> Online · Your Personal Finance Educator
            </div>
        </div>
    </div>
    <br>
    """, unsafe_allow_html=True)

    # Welcome message (static, shown before first message)
    if not st.session_state.chat_display:
        st.markdown("""
        <div class="msg-row">
            <div class="msg-avatar-sm">💎</div>
            <div>
                <div class="msg-bubble ai-bubble">
                    Hey! I'm <strong>Financy</strong> — your personal finance educator. 💎<br><br>
                    I'm here to help you with anything money-related: building credit, saving for big goals, understanding investing, budgeting strategies, and more.<br><br>
                    What's on your mind today? Feel free to ask anything — no judgment here.
                </div>
                <div class="msg-time">Just now</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Suggested chips
        st.markdown("<div class='chip-row'>", unsafe_allow_html=True)
        cols = st.columns(4)
        for i, suggestion in enumerate(SUGGESTIONS[:4]):
            with cols[i % 4]:
                if st.button(suggestion, key=f"chip_{i}", use_container_width=True):
                    st.session_state._pending_message = suggestion
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        cols2 = st.columns(4)
        for i, suggestion in enumerate(SUGGESTIONS[4:]):
            with cols2[i % 4]:
                if st.button(suggestion, key=f"chip2_{i}", use_container_width=True):
                    st.session_state._pending_message = suggestion
                    st.rerun()

    else:
        # Render message history
        for msg in st.session_state.chat_display:
            _render_message(msg["role"], msg["content"], msg["time"])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Input (wrapped in a form so Enter submits and input clears) ───────────
    with st.form(key="chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([8, 1])
        with col_input:
            user_input = st.text_input(
                "Ask Financy anything…",
                value=st.session_state.pop("_pending_message", ""),
                placeholder="e.g. How do I start investing with $500?",
                label_visibility="collapsed",
            )
        with col_send:
            send = st.form_submit_button("Send ➤", use_container_width=True)

    if send and user_input.strip():
        msg_text = user_input.strip()
        ts = _timestamp()

        # Add to display list
        st.session_state.chat_display.append({"role": "user", "content": msg_text, "time": ts})
        # Add to API messages
        st.session_state.chat_messages.append({"role": "user", "content": msg_text})

        # Get response
        with st.spinner("Financy is thinking…"):
            try:
                reply = _get_ai_response(st.session_state.chat_messages)
            except Exception as e:
                reply = f"Oops, I hit a snag — {e}. Please try again."

        reply_ts = _timestamp()
        st.session_state.chat_display.append({"role": "assistant", "content": reply, "time": reply_ts})
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})

        st.rerun()

    # Clear chat
    if st.session_state.chat_display:
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b, _ = st.columns([2, 2, 6])
        with col_a:
            if st.button("🗑 Clear Chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.session_state.chat_display = []
                st.rerun()
        with col_b:
            if st.button("📊 Get My Tracker", use_container_width=True):
                st.session_state.page = "tracker"
                st.rerun()

    # Footer
    st.markdown("""
    <div style="margin-top:2rem;text-align:center;">
        <p style="font-size:0.68rem;color:var(--text-muted);">
            Financy is an AI educator, not a licensed financial advisor. For major financial decisions, consult a certified professional.
        </p>
    </div>
    """, unsafe_allow_html=True)
