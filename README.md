# 💎 Financy — Your Intelligent Financial Companion

A beautiful, AI-powered Streamlit app with two core features:
1. **Personalized Financial Tracker** — upload bank statements → ML analysis → custom tracker
2. **Talk to Financy** — conversational AI finance educator powered by Claude

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Run the app
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 📁 Project Structure

```
financy_app/
├── app.py                  # Entry point + page router
├── requirements.txt
├── styles/
│   └── main.css            # Luxury dark theme
├── pages/
│   ├── home.py             # Hero homepage
│   ├── tracker.py          # Financial tracker (upload + results)
│   └── chat.py             # Financy AI chat
└── utils/
    └── analyser.py         # PDF/CSV parser + Claude analysis
```

---

## 🗂 Supported Statement Formats

| Format | Notes |
|--------|-------|
| **CSV** | Best accuracy. Export from your bank's online portal. |
| **PDF** | Supported for most major banks (TD, RBC, BMO, Scotiabank, CIBC, Chase, BoA). |
| **TXT** | Plain text transaction exports. |

Upload 1–3 months for best pattern detection.

---

## 🔒 Privacy

- Files are processed in-memory only — nothing is stored on disk
- Statement text is sent to the Anthropic API for analysis and not retained
- No database or logging of financial data

---

## ✨ Features

### Homepage
- Luxury dark gold aesthetic with animated card hover effects
- Two clear pathways: Tracker or Chat

### Financial Tracker
- Multi-file upload (PDF, CSV, TXT)
- Claude-powered spending categorisation and pattern detection
- Financial health score with personalised diagnosis
- Interactive spending breakdown with donut chart
- Improvement points with estimated monthly savings
- Personalized monthly budget breakdown + weekly/emergency fund targets

### Financy Chat
- Full conversational memory within session
- Suggested topic chips to get started quickly
- Topics: investing, saving goals, credit building, debt payoff, budgeting, insurance
- Warm, judgment-free tone — the anti-boring finance tutor
