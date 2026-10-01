import streamlit as st
from models.schemas import PipelineResult
from ui.components import page_header, section_divider, alert_card, metric_card
from analytics.mortgage_analysis import (
    build_approval_rate_scatter, build_denial_reasons_bar,
    build_approval_rate_bar, build_mortgage_table,
)


def render(result: PipelineResult):
    page_header(
        "Mortgage & Lending",
        "HMDA data — approval rates, denial reasons, and interest rates by lender"
    )

    banks = result.selected_banks
    summaries = result.mortgage_summaries

    if not summaries:
        alert_card(
            "No mortgage data loaded. This uses HMDA (Home Mortgage Disclosure Act) data from the CFPB. "
            "Click Refresh in the sidebar to fetch.",
            "info"
        )
        return

    # ── KPIs ──────────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    total_apps = sum(s.total_applications for s in summaries)
    avg_approval = sum(s.approval_rate for s in summaries) / len(summaries) if summaries else 0
    best_lender = max(summaries, key=lambda x: x.approval_rate) if summaries else None
    rates = [s.avg_interest_rate for s in summaries if s.avg_interest_rate]
    avg_rate = sum(rates) / len(rates) if rates else 0

    with col1:
        metric_card("Total Applications", f"{total_apps:,}")
    with col2:
        metric_card("Avg Approval Rate", f"{avg_approval:.1f}%", delta_good=(avg_approval >= 65))
    with col3:
        metric_card("Best Lender", best_lender.institution_name[:20] if best_lender else "N/A",
                    delta=f"{best_lender.approval_rate:.1f}% approval" if best_lender else "")
    with col4:
        metric_card("Avg Rate Offered", f"{avg_rate:.2f}%" if avg_rate else "N/A")

    # ── Scatter ───────────────────────────────────────────────────────────────
    section_divider("Lender Comparison — Approval Rate vs Rate Offered")
    alert_card(
        "Best lenders are top-right: high approval rate AND low interest rate. "
        "Bubble size = number of applications. Green = approval rate ≥70%.",
        "info"
    )
    st.plotly_chart(build_approval_rate_scatter(summaries), width="stretch")

    # ── Approval Rate Bar + Denial Reasons ───────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        section_divider("Approval Rates by Lender")
        st.plotly_chart(build_approval_rate_bar(summaries, banks), width="stretch")
    with col2:
        section_divider("Why Applications Are Denied")
        st.plotly_chart(build_denial_reasons_bar(summaries, banks), width="stretch")

    # ── Table ─────────────────────────────────────────────────────────────────
    section_divider("Lender Detail Table")
    df = build_mortgage_table(summaries)
    if not df.empty:
        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            column_config={
                "Institution": st.column_config.TextColumn("Institution", width="medium"),
                "Approval Rate": st.column_config.TextColumn("Approval Rate"),
                "Avg Rate Offered": st.column_config.TextColumn("Avg Rate Offered"),
                "Total Applications": st.column_config.TextColumn("Total Applications"),
                "Top Denial Reason": st.column_config.TextColumn("Top Denial Reason", width="large"),
            }
        )

    st.markdown(
        '<p style="color:#6B7280;font-size:0.75rem;margin-top:0.5rem;">'
        'Source: HMDA (Home Mortgage Disclosure Act) · ffiec.cfpb.gov · 2023 data</p>',
        unsafe_allow_html=True
    )
