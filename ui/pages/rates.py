import streamlit as st
from models.schemas import PipelineResult
from ui.components import page_header, section_divider, alert_card, metric_card
from analytics.rate_analysis import (
    build_savings_rate_bar, build_cd_rate_bar,
    build_credit_card_apr_bar, build_rate_pass_through_chart,
    build_rate_comparison_table,
)
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CD_12MO_RATES, BANK_CC_RATES
from config import FEDERAL_FUNDS_RATE

FED_RATE = FEDERAL_FUNDS_RATE


def render(result: PipelineResult):
    page_header(
        "Rate Intelligence",
        "Compare savings, CD, and loan rates — ranked against the Federal Reserve benchmark"
    )

    banks = result.selected_banks or list(BANK_SAVINGS_RATES.keys())

    # ── KPI Row ───────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    savings_rates = [BANK_SAVINGS_RATES[b] for b in banks if b in BANK_SAVINGS_RATES]
    cc_rates = [BANK_CC_RATES[b] for b in banks if b in BANK_CC_RATES and BANK_CC_RATES[b]]

    with col1:
        metric_card("Fed Funds Rate", f"{FED_RATE:.2f}%", delta="Current benchmark")
    with col2:
        best = max(savings_rates) if savings_rates else 0
        metric_card("Best Savings APY", f"{best:.2f}%", delta=f"vs Fed {FED_RATE:.2f}%", delta_good=(best >= 4.0))
    with col3:
        worst = min(savings_rates) if savings_rates else None
        if worst is not None:
            loss = (FED_RATE - worst) * 10000 / 100
            metric_card("Worst Savings APY", f"{worst:.2f}%", delta=f"-${loss:,.0f}/yr on $10K", delta_good=False)
        else:
            metric_card("Worst Savings APY", "N/A")
    with col4:
        avg_cc = sum(cc_rates) / len(cc_rates) if cc_rates else 0
        metric_card("Avg Credit Card APR", f"{avg_cc:.1f}%" if avg_cc else "N/A")

    # ── Savings Rate ──────────────────────────────────────────────────────────
    section_divider("Savings Account APY")
    alert_card(
        f"The Fed funds rate is <b>{FED_RATE:.2f}%</b>. Banks with savings rates below 1% are keeping "
        f"the majority of interest income instead of passing it to customers.",
        "info"
    )
    st.plotly_chart(build_savings_rate_bar(banks, FED_RATE), use_container_width=True)

    # ── CD Rates ──────────────────────────────────────────────────────────────
    section_divider("12-Month CD Rates")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(build_cd_rate_bar(banks), use_container_width=True)
    with col2:
        st.plotly_chart(build_credit_card_apr_bar(banks, FED_RATE), use_container_width=True)

    # ── Rate Pass-Through ─────────────────────────────────────────────────────
    section_divider("Rate Pass-Through Analysis")
    alert_card(
        "When the Fed raises rates, banks quickly raise loan rates but are slow to raise savings rates. "
        "This chart shows what % of the Fed rate each bank actually passes to depositors.",
        "warning"
    )
    st.plotly_chart(build_rate_pass_through_chart(FED_RATE), use_container_width=True)

    # ── Comparison Table ──────────────────────────────────────────────────────
    section_divider("Full Rate Comparison Table")
    df = build_rate_comparison_table(banks)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Institution": st.column_config.TextColumn("Institution", width="medium"),
            "Savings APY": st.column_config.TextColumn("Savings APY"),
            "12-Mo CD APY": st.column_config.TextColumn("12-Mo CD APY"),
            "Credit Card APR": st.column_config.TextColumn("Credit Card APR"),
            "Savings vs Fed Gap": st.column_config.TextColumn("Gap to Fed Rate"),
        }
    )

    st.markdown(
        '<p style="color:#6B7280;font-size:0.75rem;margin-top:0.5rem;">'
        'Sources: Federal Reserve G.19 · FRED H.15 · FDIC Published Rates · NCUA</p>',
        unsafe_allow_html=True
    )
