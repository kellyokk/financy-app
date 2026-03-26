import re
import io
from typing import Optional
import anthropic


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def extract_text_from_csv(file_bytes: bytes) -> str:
    """Extract text from a CSV file."""
    try:
        return file_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[CSV extraction error: {e}]"


def analyse_statements_with_claude(statements_text: str) -> dict:
    """
    Send statement text to Claude for deep financial analysis.
    Returns structured dict with categories, insights, recommendations, diagnosis.
    """
    client = anthropic.Anthropic()

    system_prompt = """You are a world-class personal finance analyst AI. 
You receive raw bank statement text (possibly from 1-3 months) and produce a thorough, 
empathetic financial analysis. You MUST respond ONLY in valid JSON — no markdown, no preamble.

Your JSON must have this exact structure:
{
  "summary": {
    "total_income": <number>,
    "total_spending": <number>,
    "net_savings": <number>,
    "savings_rate_pct": <number>,
    "avg_monthly_spending": <number>,
    "months_analysed": <number>
  },
  "spending_categories": [
    {"category": "<name>", "amount": <number>, "pct_of_spending": <number>, "color": "<hex>"}
  ],
  "top_merchants": [
    {"merchant": "<name>", "amount": <number>, "frequency": <number>}
  ],
  "patterns": [
    "<insight string>", ...
  ],
  "improvement_points": [
    {"title": "<short title>", "detail": "<detail>", "potential_monthly_saving": <number>}
  ],
  "recommendations": [
    {"category": "<budget category>", "current_spend": <number>, "recommended_spend": <number>, "tip": "<tip>"}
  ],
  "personalized_tracker": {
    "weekly_budget": <number>,
    "monthly_budget_breakdown": [
      {"category": "<name>", "budget": <number>}
    ],
    "emergency_fund_target": <number>,
    "savings_goal_monthly": <number>
  },
  "diagnosis": "<2-4 sentence empathetic financial health diagnosis — highlight strengths and areas to work on>",
  "financial_health_score": <integer 1-100>,
  "health_score_label": "<Poor | Fair | Good | Excellent>"
}

If numbers cannot be determined from the statement, use reasonable estimates and note "estimated" in the diagnosis.
Make spending_categories have 5-8 categories. Use vivid hex colors for each category.
All currency values are in the user's inferred currency (default CAD if unclear).
"""

    user_message = f"""Please analyse the following bank statement(s) and return your structured JSON analysis:

---STATEMENT DATA---
{statements_text[:12000]}
---END STATEMENT DATA---
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()
    # Strip possible markdown fences
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"```\s*$", "", raw)

    import json
    return json.loads(raw)
