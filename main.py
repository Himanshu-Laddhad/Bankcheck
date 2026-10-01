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

from ui.theme import inject_css
inject_css()

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

import ui.pages.executive as pg_executive
import ui.pages.compare   as pg_compare
import ui.pages.drilldown as pg_drilldown
import ui.pages.find_bank as pg_find_bank

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
        # Always load every bank so peer-context charts (dot plots, scatters) have a full field
        complaints = cfpb.fetch(bank_names=None, product=product_filter)
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
        result.fed_history = fred.history("DFF", days=days_back)
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
    st.markdown("### BankCheck")
    st.caption("Independent banking intelligence from public data.")

    st.markdown('<p class="sb-label">Banks</p>', unsafe_allow_html=True)
    _ca, _cb = st.columns(2)
    with _ca:
        if st.button("All", key="btn_all_banks", width="stretch"):
            st.session_state["sel_banks"] = list(ALL_BANKS)
            st.rerun()
    with _cb:
        if st.button("None", key="btn_clear_banks", width="stretch"):
            st.session_state["sel_banks"] = []
            st.rerun()
    selected_banks = st.pills(
        label="Banks", options=ALL_BANKS, selection_mode="multi",
        key="sel_banks", label_visibility="collapsed",
    )

    st.markdown('<p class="sb-label">Filters</p>', unsafe_allow_html=True)
    time_label = st.selectbox("Rate trend window", options=list(TIME_OPTIONS.keys()), index=2,
                              help="Sets how much Fed funds history the Overview trend chart shows.")
    days_back = TIME_OPTIONS[time_label]
    include_cu = st.checkbox("Include credit unions", value=False)

    if st.button("Refresh data", width="stretch"):
        st.cache_data.clear()
        st.rerun()

    st.toggle("Dark mode", key="dark_mode")

    st.markdown('<p class="sb-label">Sources</p>', unsafe_allow_html=True)
    st.caption("FDIC (live) · FRED (live) · CFPB 2023 · HMDA 2023 · NCUA")


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


# ── Navigation: executive -> operational -> analyst -> consumer ───────────
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Compare", "Drill-down", "Find your bank"])

with tab1:
    pg_executive.render(result)
with tab2:
    pg_compare.render(result)
with tab3:
    pg_drilldown.render(result)
with tab4:
    pg_find_bank.render(result)
