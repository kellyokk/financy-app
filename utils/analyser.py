"""
utils/analyser.py
Handles PDF text extraction and Claude-powered bank statement analysis.
"""

import json
import re
import streamlit as st
import anthropic


# ── API key ───────────────────────────────────────────────────────────────────

def _get_api_key() -> str:
    """Retrieve the Anthropic API key from Streamlit secrets."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except KeyError:
        st.error("⚠️ Anthropic API key not found. Add `ANTHROPIC_API_KEY` to your `.streamlit/secrets.toml` file.")
        st.stop()


# ── PDF extraction ────────────────────────────────────────────────────────────

def extract_text_from_pdf(raw_bytes: bytes) -> str:
    """Extract plain text from a PDF's raw bytes using pypdf."""
    try:
        import pypdf
        import io
        reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages) if pages else "[Could not extract text from PDF]"
    except ImportError:
        return "[pypdf not installed — run: pip install pypdf]"
    except Exception as e:
        return f"[PDF extraction error: {e}]"


# ── Prompt ────────────────────────────────────────────────────────────────────

ANALYSIS_PROMPT = """You are an expert personal finance analyst. You will be given raw text from 1–3 months of bank statements.

Analyse the transactions carefully and return a single JSON object — no markdown, no preamble, just raw JSON.

The JSON must match this exact schema:

{
  "diagnosis": "A 2–3 sentence plain-English diagnosis of the person's financial health.",
  "financial_health_score": <integer 0–100>,
  "health_score_label": "<Excellent|Good|Fair|Needs Work|Critical>",
  "summary": {
    "total_income": <number>,
    "total_spending": <number>,
    "net_savings": <number>,
    "savings_rate_pct": <number>,
    "avg_monthly_spending": <number>
  },
  "spending_categories": [
    {
      "category": "<name>",
      "amount": <number>,
      "pct_of_spending": <number>,
      "color": "<hex color string>"
    }
  ],
  "top_merchants": [
    { "merchant": "<name>", "amount": <number>, "frequency": <integer> }
  ],
  "patterns": [
    "<string describing a pattern>"
  ],
  "improvement_points": [
    {
      "title": "<short title>",
      "detail": "<one sentence>",
      "potential_monthly_saving": <number or 0>
    }
  ],
  "recommendations": [
    {
      "category": "<category name>",
      "current_spend": <number>,
      "recommended_spend": <number>,
      "tip": "<one actionable sentence>"
    }
  ],
  "personalized_tracker": {
    "savings_goal_monthly": <number>,
    "weekly_budget": <number>,
    "emergency_fund_target": <number>,
    "monthly_budget_breakdown": [
      { "category": "<name>", "budget": <number> }
    ]
  }
}

Rules:
- Use realistic numbers derived from the actual statement data.
- If income cannot be determined, estimate from deposits.
- spending_categories should have 5–8 categories with distinct hex colors (use a warm palette: golds, greens, blues, corals).
- top_merchants: list the top 4 by total amount.
- patterns: 3–5 behavioural observations.
- improvement_points: 2–4 items.
- recommendations: 3–5 items.
- monthly_budget_breakdown should mirror spending_categories but with recommended (not actual) budgets.
- Return ONLY the JSON object. No explanation, no markdown fences.
"""


# ── Main analysis function ────────────────────────────────────────────────────

def analyse_statements_with_claude(combined_text: str) -> dict:
    """
    Send extracted statement text to Claude and return the parsed analysis dict.
    Raises ValueError if the response cannot be parsed as JSON.
    """
    client = anthropic.Anthropic(api_key=_get_api_key())

    user_message = f"Here are the bank statement(s) to analyse:\n\n{combined_text[:12000]}"  # cap to avoid token overflow

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=ANALYSIS_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()

    # Strip accidental markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned invalid JSON: {e}\n\nRaw response:\n{raw[:500]}")
