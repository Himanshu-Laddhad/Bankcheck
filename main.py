import streamlit as st
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="BankCheck — Unbiased Banking Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Dark theme with subtle gradient */
.stApp { 
    background: linear-gradient(180deg, #0A0F1E 0%, #111827 100%);
}

/* Glassmorphism sidebar */
.stSidebar { 
    background: rgba(13, 17, 23, 0.95) !important;
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(99, 102, 241, 0.2);
}
.stSidebar .stMarkdown p { color: #9CA3AF; font-size: 0.82rem; }
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

/* Enhanced metric cards with glassmorphism */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
    border-color: rgba(99, 102, 241, 0.4);
}
[data-testid="stMetricLabel"] { color: #9CA3AF !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: #E5E7EB !important; font-size: 1.5rem !important; font-weight: 700 !important; }

/* Animated buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.5);
    background: linear-gradient(135deg, #7C3AED, #A78BFA) !important;
}
.stButton > button:active {
    transform: translateY(0px);
}

/* Primary button variant */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #10B981, #059669) !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #059669, #047857) !important;
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.5);
}

/* Enhanced tabs */
.stTabs [data-baseweb="tab-list"] { 
    background: rgba(17, 24, 39, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 6px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.stTabs [data-baseweb="tab"] { 
    color: #9CA3AF;
    border-radius: 8px;
    font-weight: 500;
    padding: 0.75rem 1.25rem;
    transition: all 0.3s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #E5E7EB;
    background: rgba(255, 255, 255, 0.05);
}
.stTabs [aria-selected="true"] { 
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

/* DataFrames with glassmorphism */
[data-testid="stDataFrame"] { 
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    overflow: hidden;
    backdrop-filter: blur(10px);
}
.dvn-scroller { 
    background: rgba(17, 24, 39, 0.8);
}

/* Enhanced multiselect and selectbox */
.stMultiSelect [data-baseweb="select"] { 
    background: rgba(31, 41, 55, 0.8);
    backdrop-filter: blur(10px);
    border-color: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    transition: all 0.3s ease;
}
.stMultiSelect [data-baseweb="select"]:hover {
    border-color: rgba(99, 102, 241, 0.5);
}
.stRadio > label { color: #9CA3AF; font-size: 0.85rem; }
.stSelectbox [data-baseweb="select"] { 
    background: rgba(31, 41, 55, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 10px;
}

/* Custom scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { 
    background: rgba(17, 24, 39, 0.5);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb { 
    background: linear-gradient(180deg, #6366F1, #8B5CF6);
    border-radius: 4px;
    transition: all 0.3s ease;
}
::-webkit-scrollbar-thumb:hover { 
    background: linear-gradient(180deg, #8B5CF6, #A78BFA);
}

/* Expander with animation */
.streamlit-expanderHeader { 
    background: rgba(31, 41, 55, 0.8) !important;
    backdrop-filter: blur(10px);
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    transition: all 0.3s ease;
}
.streamlit-expanderHeader:hover {
    border-color: rgba(99, 102, 241, 0.4) !important;
}

/* Divider */
hr { 
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.5), transparent);
    margin: 2rem 0;
}

/* Input fields */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(31, 41, 55, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    color: #E5E7EB;
    transition: all 0.3s ease;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: rgba(99, 102, 241, 0.6);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Slider */
.stSlider > div > div > div {
    background: rgba(99, 102, 241, 0.2);
}
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #6366F1, #8B5CF6);
}

/* Animation keyframes */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Apply animations */
[data-testid="stMetric"],
[data-testid="stButton"] {
    animation: fadeIn 0.5s ease-out;
}

/* Card hover effects */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.3);
    border-color: rgba(99, 102, 241, 0.4);
}

/* Pulse animation for live indicators */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Mobile Responsive Design */
@media (max-width: 768px) {
    /* Stack columns on mobile */
    [data-testid="column"] {
        min-width: 100% !important;
        margin-bottom: 1rem;
    }
    
    /* Adjust tab padding for mobile */
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 0.75rem;
        font-size: 0.85rem;
    }
    
    /* Reduce hero text size on mobile */
    h1 {
        font-size: 1.5rem !important;
    }
    
    /* Make buttons more touch-friendly */
    .stButton > button {
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
    }
    
    /* Adjust metric cards for mobile */
    [data-testid="stMetric"] {
        padding: 0.75rem !important;
    }
    
    /* Hide some decorative elements on mobile */
    .glass-card {
        backdrop-filter: blur(5px);
    }
}

/* Tablet adjustments */
@media (min-width: 769px) and (max-width: 1024px) {
    [data-testid="column"] {
        min-width: calc(50% - 0.5rem) !important;
    }
}

/* Touch-friendly interactions */
@media (hover: none) and (pointer: coarse) {
    /* Increase touch targets */
    .stButton > button {
        min-height: 48px;
    }
    
    /* Disable hover effects on touch devices */
    [data-testid="stMetric"]:hover {
        transform: none;
        box-shadow: none;
    }
    
    .stButton > button:hover {
        transform: none;
    }
}

/* Loading skeleton animation */
@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.skeleton {
    animation: shimmer 2s infinite linear;
    background: linear-gradient(
        to right,
        rgba(255, 255, 255, 0.05) 0%,
        rgba(255, 255, 255, 0.1) 50%,
        rgba(255, 255, 255, 0.05) 100%
    );
    background-size: 1000px 100%;
}
</style>
""", unsafe_allow_html=True)

# ── Imports ────────────────────────────────────────────────────────────────
from connectors.fdic import FDICConnector
from connectors.cfpb import CFPBConnector
from connectors.fred import FREDConnector
from connectors.hmda import HMDAConnector
from connectors.ncua import NCUAConnector
from processing.normalizer import normalise_institutions, normalise_complaints, normalise_mortgage_summaries
from processing.aggregator import build_rate_records, BANK_SAVINGS_RATES
from processing.scorer import score_all
from models.schemas import PipelineResult, SourceHealth

import ui.pages.top_lists   as pg_top_lists
import ui.pages.find_bank   as pg_find_bank
import ui.pages.intelligence as pg_intelligence

# ── All available banks ────────────────────────────────────────────────────
ALL_BANKS = sorted(BANK_SAVINGS_RATES.keys())


TIME_OPTIONS = {
    "Last 3 months":  90,
    "Last 6 months":  180,
    "Last 12 months": 365,
    "Last 3 years":   1095,
}


# ── Pipeline ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def run_pipeline(
    selected_banks: tuple,
    product_filter: str,
    days_back: int,
    include_credit_unions: bool,
) -> PipelineResult:
    result = PipelineResult(
        selected_banks=list(selected_banks),
        as_of=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )
    health = []
    banks_list = list(selected_banks) if selected_banks else ALL_BANKS[:10]

    # FDIC
    try:
        fdic = FDICConnector()
        institutions = fdic.fetch(bank_names=banks_list)
        result.institutions = normalise_institutions(institutions)
        health.append(fdic.health_check())
    except Exception as e:
        health.append(SourceHealth(source="fdic", is_healthy=False, error=str(e),
                                   last_checked=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))

    # CFPB — fetch filtered complaint records; summarise builds from full 2023 dataset
    try:
        cfpb = CFPBConnector()
        complaints = cfpb.fetch(bank_names=banks_list, product=product_filter)
        result.raw_complaints = normalise_complaints(complaints)
        result.complaint_summaries = cfpb.summarise(result.raw_complaints)
        health.append(cfpb.health_check())
    except Exception as e:
        health.append(SourceHealth(source="cfpb", is_healthy=False, error=str(e),
                                   last_checked=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))

    # FRED
    try:
        fred = FREDConnector()
        result.fed_rates = fred.fetch()
        result.rates = build_rate_records(banks_list)
        health.append(fred.health_check())
    except Exception as e:
        result.rates = build_rate_records(banks_list)
        health.append(SourceHealth(source="fred", is_healthy=False, error=str(e),
                                   last_checked=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))

    # HMDA — pass selected banks; None means return all lenders in dataset
    try:
        hmda = HMDAConnector()
        summaries = hmda.fetch(bank_names=None)  # always all banks so Top Lists is unaffected by filter
        result.mortgage_summaries = normalise_mortgage_summaries(summaries)
        health.append(hmda.health_check())
    except Exception as e:
        health.append(SourceHealth(source="hmda", is_healthy=False, error=str(e),
                                   last_checked=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))

    # NCUA
    if include_credit_unions:
        try:
            ncua = NCUAConnector()
            result.credit_unions = ncua.fetch()
            health.append(ncua.health_check())
        except Exception as e:
            health.append(SourceHealth(source="ncua", is_healthy=False, error=str(e),
                                       last_checked=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))

    # Scoring
    try:
        result.scores = score_all(
            bank_names=banks_list,
            institutions=result.institutions,
            complaint_summaries=result.complaint_summaries,
            mortgage_summaries=result.mortgage_summaries,
        )
    except Exception as e:
        from loguru import logger as _log
        _log.error(f"Scoring failed: {e}")
        health.append(SourceHealth(source="scorer", is_healthy=False, error=str(e),
                                   last_checked=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))

    result.health = health
    return result


# ── Session state defaults (must be before sidebar renders) ────────────────
if "sel_banks" not in st.session_state:
    st.session_state["sel_banks"] = ["Capital One", "Goldman Sachs (Marcus)", "American Express", "Discover"]

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo card
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1E1B4B,#312E81);
                border-radius:14px;padding:1rem;text-align:center;
                margin-bottom:1.25rem;border:1px solid rgba(99,102,241,0.3);">
        <div style="font-size:2rem;line-height:1;">💳 🏦 💰</div>
        <div style="font-size:1.15rem;font-weight:800;color:#E5E7EB;margin-top:0.3rem;">BankCheck</div>
        <div style="font-size:0.68rem;color:#A5B4FC;margin-top:0.15rem;letter-spacing:0.04em;">
            UNBIASED · GOVERNMENT DATA · LIVE DATA
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bank slicer ──────────────────────────────────────────────────────
    st.markdown(
        '<p style="color:#9CA3AF;font-size:0.72rem;font-weight:600;letter-spacing:0.07em;'
        'text-transform:uppercase;margin:0 0 0.4rem;">Banks</p>',
        unsafe_allow_html=True,
    )
    _ca, _cb = st.columns(2)
    with _ca:
        if st.button("Select All", key="btn_all_banks", use_container_width=True):
            st.session_state["sel_banks"] = list(ALL_BANKS)
            st.rerun()
    with _cb:
        if st.button("Clear All", key="btn_clear_banks", use_container_width=True):
            st.session_state["sel_banks"] = []
            st.rerun()
    selected_banks = st.pills(
        label="Banks",
        options=ALL_BANKS,
        selection_mode="multi",
        key="sel_banks",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Filters (proper dropdowns, no radio buttons) ─────────────────────
    st.markdown(
        '<p style="color:#9CA3AF;font-size:0.72rem;font-weight:600;letter-spacing:0.07em;'
        'text-transform:uppercase;margin:0 0 0.4rem;">Filters</p>',
        unsafe_allow_html=True,
    )
    time_label = st.selectbox(
        "Time Range",
        options=list(TIME_OPTIONS.keys()),
        index=2,
    )
    days_back = TIME_OPTIONS[time_label]

    include_cu = st.checkbox("Include Credit Unions", value=False)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    if st.button("↻  Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Data sources card
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
                border-radius:10px;padding:0.75rem;margin-top:1rem;">
        <div style="font-size:0.68rem;color:#4B5563;line-height:1.8;">
            <span style="color:#6B7280;font-weight:600;font-size:0.7rem;">DATA SOURCES</span><br>
            FDIC BankFind Suite (live)<br>
            CFPB 2023 Annual Report<br>
            Federal Reserve FRED<br>
            HMDA 2023 Published Data<br>
            NCUA Published Rates
        </div>
        <div style="margin-top:0.5rem;font-size:0.65rem;color:#374151;">
            No affiliate links · No sponsored results
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Run Pipeline ───────────────────────────────────────────────────────────
banks_tuple = tuple(selected_banks) if selected_banks else tuple(ALL_BANKS)

with st.spinner("Fetching live government data..."):
    result = run_pipeline(
        selected_banks=banks_tuple,
        product_filter=None,
        days_back=days_back,
        include_credit_unions=include_cu,
    )

result.selected_banks = list(banks_tuple)


# ── Navigation Tabs ────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "Intelligence",
    "Top Lists",
    "Find Your Bank",
])

with tab2:
    pg_top_lists.render(result)

with tab3:
    pg_find_bank.render(result)

with tab1:
    pg_intelligence.render(result)
