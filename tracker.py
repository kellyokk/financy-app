import streamlit as st
import json
import time

# ── helpers ──────────────────────────────────────────────────────────────────

def _back():
    st.session_state.page = "home"
    st.session_state.pop("analysis", None)
    st.rerun()


def _color_bar(pct: float, color: str) -> str:
    return f"""
    <div class="spend-bar-track">
      <div class="spend-bar-fill" style="width:{min(pct,100):.1f}%;background:{color};"></div>
    </div>"""


def _health_color(score: int) -> str:
    if score >= 80: return "#2ecc8f"
    if score >= 60: return "#c9a84c"
    if score >= 40: return "#e09a2c"
    return "#e05c7a"


# ── main render ───────────────────────────────────────────────────────────────

def render():
    # Back button
    if st.button("← Back to Home", key="back_tracker"):
        _back()

    # Page header
    st.markdown("""
    <div class="page-header">
        <div class="page-eyebrow">✦ AI-Powered Analysis</div>
        <h1 class="page-title">Your Personalized Financial Tracker</h1>
        <p class="page-subtitle">Upload 1–3 months of bank statements and let our model do the heavy lifting.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload section ────────────────────────────────────────────────────────
    if "analysis" not in st.session_state:
        st.markdown("### 📁 Upload Your Statements")
        st.markdown(
            "<p style='color:var(--text-secondary);font-size:0.875rem;'>"
            "Accepted formats: <strong>PDF</strong>, <strong>CSV</strong>, or plain <strong>TXT</strong>. "
            "Your data is processed securely and never stored.</p>",
            unsafe_allow_html=True
        )

        uploaded_files = st.file_uploader(
            "Drop your bank statements here",
            type=["pdf", "csv", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

        if uploaded_files:
            if len(uploaded_files) > 3:
                st.warning("Please upload a maximum of 3 statements.")
                return

            st.markdown(f"<p style='color:var(--emerald);font-size:0.85rem;'>✓ {len(uploaded_files)} file(s) ready</p>",
                        unsafe_allow_html=True)

            col_a, col_b, _ = st.columns([2, 2, 4])
            with col_a:
                go = st.button("🔍 Analyse My Statements", use_container_width=True)

            if go:
                with st.spinner(""):
                    progress = st.progress(0, text="Reading your statements…")
                    combined_text = ""

                    for i, f in enumerate(uploaded_files):
                        progress.progress((i + 1) / (len(uploaded_files) + 2),
                                          text=f"Parsing {f.name}…")
                        raw = f.read()

                        if f.name.lower().endswith(".pdf"):
                            from utils.analyser import extract_text_from_pdf
                            combined_text += f"\n\n== FILE: {f.name} ==\n" + extract_text_from_pdf(raw)
                        else:
                            combined_text += f"\n\n== FILE: {f.name} ==\n" + raw.decode("utf-8", errors="replace")

                    progress.progress(0.7, text="Running financial model…")

                    try:
                        from utils.analyser import analyse_statements_with_claude
                        result = analyse_statements_with_claude(combined_text)
                        st.session_state.analysis = result
                        progress.progress(1.0, text="Analysis complete!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

        else:
            # Tips
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class="analysis-section">
                <div class="analysis-section-title">💡 Tips for best results</div>
                <div class="rec-item">
                    <div class="rec-dot" style="background:#c9a84c;"></div>
                    <div class="rec-text">Export statements as <strong>CSV</strong> from your bank's online portal for the most accurate data.</div>
                </div>
                <div class="rec-item">
                    <div class="rec-dot" style="background:#c9a84c;"></div>
                    <div class="rec-text">Include at least <strong>2 months</strong> of data for a reliable spending pattern.</div>
                </div>
                <div class="rec-item">
                    <div class="rec-dot" style="background:#c9a84c;"></div>
                    <div class="rec-text">PDF statements from most Canadian banks (TD, RBC, BMO, Scotiabank, CIBC) are supported.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        return

    # ── Results section ───────────────────────────────────────────────────────
    data = st.session_state.analysis
    summary = data.get("summary", {})
    score = data.get("financial_health_score", 50)
    score_label = data.get("health_score_label", "Fair")
    score_color = _health_color(score)

    col_reset, _ = st.columns([2, 8])
    with col_reset:
        if st.button("↩ Upload New Statements", use_container_width=True):
            st.session_state.pop("analysis")
            st.rerun()

    # ── Diagnosis box ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="diagnosis-box">
        <div class="diagnosis-label">🔬 Model Diagnosis</div>
        <div class="diagnosis-text">{data.get('diagnosis', '')}</div>
        <div style="margin-top:1rem;display:flex;align-items:center;gap:1rem;">
            <div style="font-family:'Playfair Display',serif;font-size:2.5rem;font-weight:700;color:{score_color};">{score}</div>
            <div>
                <div style="font-size:0.7rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-muted);">Financial Health Score</div>
                <div style="font-size:1rem;font-weight:600;color:{score_color};">{score_label}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary metrics ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="analysis-section">
        <div class="analysis-section-title">📈 Financial Summary</div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    metrics = [
        (m1, f"${summary.get('total_income',0):,.0f}", "Total Income"),
        (m2, f"${summary.get('total_spending',0):,.0f}", "Total Spent"),
        (m3, f"${summary.get('net_savings',0):,.0f}", "Net Savings"),
        (m4, f"{summary.get('savings_rate_pct',0):.1f}%", "Savings Rate"),
        (m5, f"${summary.get('avg_monthly_spending',0):,.0f}", "Avg/Month"),
    ]
    for col, val, label in metrics:
        with col:
            color = "#2ecc8f" if label == "Net Savings" and summary.get("net_savings", 0) > 0 else "var(--gold-light)"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color};">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Tabs for the deeper analysis ──────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["💳 Spending Breakdown", "🔍 Patterns & Insights", "🎯 Recommendations", "📅 Your Tracker"])

    # ---- TAB 1: Spending Breakdown ----
    with tab1:
        categories = data.get("spending_categories", [])
        if categories:
            st.markdown("<br>", unsafe_allow_html=True)
            col_chart, col_bars = st.columns([1, 2])

            with col_chart:
                # Simple donut via plotly
                try:
                    import plotly.graph_objects as go
                    fig = go.Figure(go.Pie(
                        labels=[c["category"] for c in categories],
                        values=[c["amount"] for c in categories],
                        hole=0.6,
                        marker=dict(colors=[c.get("color", "#c9a84c") for c in categories]),
                        textinfo="none",
                    ))
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        showlegend=False,
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=260,
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                except ImportError:
                    st.info("Install plotly for chart: pip install plotly")

            with col_bars:
                st.markdown("<br>", unsafe_allow_html=True)
                for cat in categories:
                    pct = cat.get("pct_of_spending", 0)
                    color = cat.get("color", "#c9a84c")
                    st.markdown(f"""
                    <div class="spend-bar-wrap">
                        <div class="spend-bar-header">
                            <span>{cat['category']}</span>
                            <span>${cat['amount']:,.0f} &nbsp;·&nbsp; {pct:.1f}%</span>
                        </div>
                        {_color_bar(pct, color)}
                    </div>
                    """, unsafe_allow_html=True)

        merchants = data.get("top_merchants", [])
        if merchants:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""<div class="analysis-section-title">🏪 Top Merchants</div>""", unsafe_allow_html=True)
            cols = st.columns(min(len(merchants), 4))
            for i, m in enumerate(merchants[:4]):
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="font-size:1.1rem;">${m['amount']:,.0f}</div>
                        <div class="metric-label">{m['merchant']}</div>
                        <div style="font-size:0.7rem;color:var(--text-muted);margin-top:0.2rem;">{m.get('frequency','-')}x visits</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ---- TAB 2: Patterns ----
    with tab2:
        patterns = data.get("patterns", [])
        improvements = data.get("improvement_points", [])

        if patterns:
            st.markdown("<br><div class='analysis-section'>", unsafe_allow_html=True)
            st.markdown("<div class='analysis-section-title'>🧠 Spending Patterns Detected</div>", unsafe_allow_html=True)
            for p in patterns:
                st.markdown(f"""
                <div class="rec-item">
                    <div class="rec-dot" style="background:#a8c8e8;"></div>
                    <div class="rec-text">{p}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if improvements:
            st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
            st.markdown("<div class='analysis-section-title'>⚠️ Areas for Improvement</div>", unsafe_allow_html=True)
            for item in improvements:
                saving = item.get("potential_monthly_saving", 0)
                st.markdown(f"""
                <div class="rec-item">
                    <div class="rec-dot" style="background:#e05c7a;"></div>
                    <div class="rec-text">
                        <strong>{item['title']}</strong> — {item['detail']}
                        {"<br><span style='color:#2ecc8f;font-size:0.8rem;'>💰 Potential saving: $" + f"{saving:,.0f}/mo" + "</span>" if saving else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ---- TAB 3: Recommendations ----
    with tab3:
        recs = data.get("recommendations", [])
        if recs:
            st.markdown("<br>", unsafe_allow_html=True)
            for rec in recs:
                current = rec.get("current_spend", 0)
                recommended = rec.get("recommended_spend", 0)
                diff = current - recommended
                diff_color = "#2ecc8f" if diff > 0 else "#e05c7a"
                diff_label = f"Save ${diff:,.0f}/mo" if diff > 0 else f"Increase ${abs(diff):,.0f}/mo"

                st.markdown(f"""
                <div class="analysis-section" style="margin-bottom:0.85rem;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div style="font-weight:600;color:var(--text-primary);margin-bottom:0.25rem;">{rec['category']}</div>
                            <div style="font-size:0.8rem;color:var(--text-secondary);">{rec.get('tip','')}</div>
                        </div>
                        <div style="text-align:right;flex-shrink:0;margin-left:1rem;">
                            <div style="font-size:0.75rem;color:var(--text-muted);">Current → Recommended</div>
                            <div style="font-size:0.95rem;font-weight:600;color:var(--text-primary);">${current:,.0f} → ${recommended:,.0f}</div>
                            <div style="font-size:0.75rem;color:{diff_color};">{diff_label}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ---- TAB 4: Personalized Tracker ----
    with tab4:
        tracker = data.get("personalized_tracker", {})
        if tracker:
            st.markdown("<br>", unsafe_allow_html=True)

            t1, t2, t3 = st.columns(3)
            with t1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color:#2ecc8f;">${tracker.get('savings_goal_monthly',0):,.0f}</div>
                    <div class="metric-label">Monthly Savings Goal</div>
                </div>""", unsafe_allow_html=True)
            with t2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">${tracker.get('weekly_budget',0):,.0f}</div>
                    <div class="metric-label">Weekly Spending Budget</div>
                </div>""", unsafe_allow_html=True)
            with t3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color:#a8c8e8;">${tracker.get('emergency_fund_target',0):,.0f}</div>
                    <div class="metric-label">Emergency Fund Target</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
            st.markdown("<div class='analysis-section-title'>📋 Monthly Budget Breakdown</div>", unsafe_allow_html=True)

            breakdown = tracker.get("monthly_budget_breakdown", [])
            total_budget = sum(b["budget"] for b in breakdown) or 1
            for b in breakdown:
                pct = (b["budget"] / total_budget) * 100
                st.markdown(f"""
                <div class="spend-bar-wrap">
                    <div class="spend-bar-header">
                        <span style="color:var(--text-primary);font-weight:500;">{b['category']}</span>
                        <span>${b['budget']:,.0f}/mo &nbsp;·&nbsp; {pct:.0f}%</span>
                    </div>
                    {_color_bar(pct, '#c9a84c')}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # CTA to chat
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="analysis-section" style="text-align:center;background:linear-gradient(135deg,rgba(46,204,143,0.05),rgba(201,168,76,0.05));">
        <div style="font-family:'Playfair Display',serif;font-size:1.2rem;color:var(--text-primary);margin-bottom:0.5rem;">
            Have questions about your results?
        </div>
        <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:1rem;">
            Talk to Financy for personalised advice on any of these findings.
        </div>
    </div>
    """, unsafe_allow_html=True)
    col_x, col_cta, col_y = st.columns([3, 2, 3])
    with col_cta:
        if st.button("💬 Talk to Financy", use_container_width=True):
            st.session_state.page = "financy_chat"
            st.rerun()
