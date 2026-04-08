# BankCheck — Unbiased Banking Intelligence

> Compare US banks and credit unions on rates, complaints, mortgage approvals, and financial safety — built entirely on free government data. No affiliate links. No sponsored rankings.

---

## Why This Exists

Every major bank comparison site (NerdWallet, Bankrate, The Points Guy) earns $200–$400 per card signup. Their "best" rankings are paid placements. BankCheck uses only official US government APIs — the same data Bloomberg terminals and bank analysts use — so every recommendation is traceable to a public source.

---

## What It Does

### Five Interactive Dashboard Pages

| Page | What You Learn | Interactive Features |
|------|---------------|---------------------|
| **Overview** | Hero section, quick picks, live rankings, bank matcher quiz | ✨ 30-sec bank finder, savings calculator, personalized quiz |
| **Rate Intelligence** | Savings APY vs Fed benchmark, CD rates, credit card APRs, rate pass-through | 📊 Animated charts, benchmark overlays, interactive filters |
| **Complaint Intelligence** | CFPB complaint heatmap, resolution rates, monthly trends | 🏆 Achievement badges for best performers, interactive heatmaps |
| **Mortgage & Lending** | Lender approval rates, interest rates offered, denial reasons (HMDA) | 📈 Interactive visualizations, filterable data |
| **Safety & Scores** | FDIC capital ratios, composite A–F grades, credit unions vs banks | ⭐ Animated score cards, gamified rankings |

### 🎯 New Engagement Features

- **🚀 Hero Section**: Find your perfect bank in 30 seconds with quick-pick buttons
- **💰 Savings Calculator**: Interactive tool showing how much more you could earn by switching banks
- **🎯 Bank Matcher Quiz**: 4-question quiz providing personalized bank recommendations
- **🏆 Live Rankings**: Real-time leaderboard of top-performing banks
- **✨ Animated Score Cards**: Beautiful glassmorphism design with achievement badges
- **📊 Enhanced Charts**: Interactive Plotly charts with animations and range selectors
- **📱 Mobile-Responsive**: Optimized for phones, tablets, and desktops
- **🎨 Modern UI**: Glassmorphism effects, gradient backgrounds, smooth animations

### Sidebar Controls

- **Multi-select banks** — compare any combination of 19 major institutions
- **Product category** — filter all views to Credit Cards, Mortgages, Auto Loans, etc.
- **Time range** — 3 months / 6 months / 12 months / 3 years of complaint data
- **Include credit unions** — toggle 10 major CUs into the comparison
- **Refresh** — clears cache and fetches fresh data from all sources

### Quick Actions (New!)

- **💰 Best Savings** — Instantly see top 3 banks by APY
- **🏠 Best Mortgage** — Top lenders by approval rate
- **💳 Best Credit Card** — Lowest APR options
- **🧮 Savings Calculator** — Calculate potential earnings difference
- **🎯 Bank Matcher** — Take 4-question quiz for personalized recommendations

### Composite Scoring (A–F)

Each institution is graded on four dimensions from government data:

```
Overall Score = Rate Score (35%) + Complaint Score (35%) + Safety Score (20%) + Fairness Score (10%)
```

| Dimension | Source | What It Measures |
|-----------|--------|-----------------|
| Rate Score | FDIC / FRED | Savings APY vs Fed funds benchmark |
| Complaint Score | CFPB | Complaint volume + % resolved with monetary relief |
| Safety Score | FDIC | Tier 1 capital ratio vs regulatory minimums |
| Fairness Score | HMDA | Mortgage approval rate |

---

## Data Sources

All sources are free US government APIs. No scraping. No third-party data vendors.

| Source | API | Key Required | What It Provides | Refresh |
|--------|-----|-------------|-----------------|---------|
| **FDIC BankFind** | `banks.data.fdic.gov/api` | None | Bank financials, capital ratios, branch count, NIM, ROA | Daily |
| **CFPB Complaints** | `api.consumerfinance.gov` | None | Complaint volume, product breakdown, resolution rates | Daily |
| **Federal Reserve FRED** | `api.stlouisfed.org/fred` | Free (optional) | G.19/H.15 benchmark rates — falls back to published national averages if no key | Daily |
| **HMDA** | `ffiec.cfpb.gov` | None | Mortgage approval rates, denial reasons, rates offered by lender | Annual |
| **NCUA** | Published data | None | Credit union savings/loan rates, membership info | Quarterly |

> **No API key needed to run the app.** FRED key is optional — without it, the app uses published national average rates from Q4 2024. All other four sources are fully keyless.

---

## Institutions Tracked

### Banks (19)

Ally Bank · American Express · Bank of America · Capital One · Citibank · Citizens Bank · Discover · Fifth Third Bank · Goldman Sachs (Marcus) · Huntington Bank · JPMorgan Chase · KeyBank · PNC Bank · Regions Bank · Synchrony Bank · TD Bank · Truist Bank · U.S. Bank · Wells Fargo

### Credit Unions (10)

Navy Federal Credit Union · State Employees' CU (SECU) · Pentagon Federal CU (PenFed) · Alliant Credit Union · Connexus Credit Union · Consumers Credit Union · DCU (Digital Federal CU) · First Tech Federal CU · Bethpage Federal CU · SchoolsFirst FCU

---

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/your-username/bankcheck.git
cd bankcheck
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

First install takes ~30 seconds. No ML models — total install is under 200MB.

### 3. (Optional) Add a FRED API key

```bash
cp .env.example .env
# Edit .env and paste your free FRED API key
# Get one at: https://fred.stlouisfed.org/docs/api/api_key.html
```

Without a key, the app works fully — FRED shows static national averages and the health panel marks it as degraded so you always know.

### 4. Run

```bash
streamlit run main.py
```

Opens at `http://localhost:8501`

- **First run:** ~5–15 seconds to fetch live data from FDIC, CFPB, HMDA
- **Subsequent runs:** <1 second from cache (1-hour TTL)
- Click **Refresh Live Data** in the sidebar to force fresh data

---

## Project Structure

```
bankcheck/
├── main.py                     # Streamlit entry point, sidebar, pipeline orchestration
├── config.py                   # Settings (Pydantic), FEDERAL_FUNDS_RATE constant
├── requirements.txt
├── .env.example
│
├── connectors/                 # One file per data source
│   ├── base.py                 # Abstract base with retry logic (tenacity)
│   ├── fdic.py                 # FDIC BankFind Suite
│   ├── cfpb.py                 # CFPB Consumer Complaint Database (2023 annual data)
│   ├── fred.py                 # Federal Reserve FRED (with keyless fallback)
│   ├── hmda.py                 # Home Mortgage Disclosure Act (2023 published data)
│   └── ncua.py                 # National Credit Union Administration
│
├── models/
│   └── schemas.py              # Pydantic v2 models for all data types
│
├── processing/
│   ├── normalizer.py           # Canonical bank name resolution across sources
│   ├── aggregator.py           # Per-bank rate data (savings, CD, credit card)
│   └── scorer.py               # Composite A–F scoring engine
│
├── analytics/                  # Plotly chart builders, one module per page
│   ├── rate_analysis.py
│   ├── complaint_analysis.py
│   ├── mortgage_analysis.py
│   └── safety_analysis.py
│
└── ui/
    ├── components.py           # Shared base components (metric cards, badges, dividers)
    ├── interactive.py          # Engagement components (hero, calculator, quiz, leaderboard)
    ├── charts.py               # Enhanced animated Plotly chart builders
    └── pages/
        ├── overview.py         # Overview tab — hero, rankings, calculator, quiz, scorecards
        ├── rates.py            # Rate Intelligence tab
        ├── complaints.py       # Complaint Intelligence tab
        ├── mortgage.py         # Mortgage & Lending tab
        └── safety.py           # Safety & Scores tab
```

---

## Updating Rates

Two values need manual updates each quarter:

| What | Where | Source |
|------|-------|--------|
| `FEDERAL_FUNDS_RATE` | `config.py` | [FRED FEDFUNDS](https://fred.stlouisfed.org/series/FEDFUNDS) |
| `BANK_SAVINGS_RATES`, `BANK_CD_12MO_RATES`, `BANK_CC_RATES` | `processing/aggregator.py` | Bank websites / FDIC published rates |

With a FRED API key, benchmark rates update automatically. Bank-specific rates (savings, CD, credit card APR) are from published disclosures and are updated in `aggregator.py`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Dashboard | Streamlit 1.56 |
| Data models | Pydantic v2 |
| Charts | Plotly |
| Data | Pandas, NumPy |
| HTTP | Requests + Tenacity (retry with exponential backoff) |
| Caching | `@st.cache_data` (1-hour TTL) |
| Logging | Loguru (rotating file + console) |
| Config | Pydantic Settings + python-dotenv |

---

## Consumer Questions This Answers

| Question | Where to Look |
|----------|--------------|
| Which savings account pays the most? | Rate Intelligence → Savings APY bar |
| Which bank passes Fed rate hikes to savers? | Rate Intelligence → Rate Pass-Through chart |
| Which bank resolves complaints fairly? | Complaint Intelligence → Resolution Rate |
| Which credit card issuer has fewest complaints? | Complaint Intelligence → Heatmap |
| Which mortgage lender approves the most applications? | Mortgage & Lending → Approval Rate scatter |
| Is my bank financially safe? | Safety & Scores → FDIC capital ratio table |
| Are credit unions better than my bank? | Safety & Scores → CU vs Bank comparison |
| Which banks should I avoid? | Overview → F-grade scorecards |

---

## Recent Enhancements ✨

- [x] **Interactive Hero Section** with quick bank finder
- [x] **Savings Calculator** showing real dollar impact
- [x] **Bank Matcher Quiz** with personalized recommendations
- [x] **Live Rankings Leaderboard** with medal system
- [x] **Animated Score Cards** with achievement badges
- [x] **Enhanced Plotly Charts** with animations and interactivity
- [x] **Glassmorphism UI** with modern styling
- [x] **Mobile-Responsive Design** optimized for all devices
- [x] **Gamification Elements** (badges, rankings, progress indicators)
- [x] **Micro-Interactions** (hover effects, transitions, animations)

## Future Roadmap

- [ ] Historical rate tracking (SQLite) — see how bank rates changed over time
- [ ] Email/Slack alerts when a bank's complaint rate spikes
- [ ] Zip code level mortgage lender comparison (HMDA)
- [ ] Auto-update bank rates via web scraping (Playwright)
- [ ] User accounts with saved comparisons
- [ ] PDF export for bank comparison reports
- [ ] Docker deployment
- [ ] Additional credit unions (expand to 50+)

---

## License

MIT
