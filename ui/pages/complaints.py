import streamlit as st
from models.schemas import PipelineResult
from ui.components import page_header, section_divider, alert_card, metric_card
from ui.interactive import achievement_badge
from analytics.complaint_analysis import (
    build_complaint_heatmap, build_resolution_rate_bar,
    build_complaint_trend, build_complaint_summary_table,
)


def render(result: PipelineResult):
    page_header(
        "Complaint Intelligence",
        "Real consumer complaint data from the CFPB — no filters, no spin"
    )

    banks = result.selected_banks
    summaries = result.complaint_summaries
    complaints = result.raw_complaints

    # ── KPI Row ───────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    total = sum(s.total_complaints for s in summaries)
    avg_relief = (sum(s.relief_rate for s in summaries) / len(summaries)) if summaries else 0
    avg_timely = (sum(s.timely_response_rate for s in summaries) / len(summaries)) if summaries else 0
    unresolved = sum(s.total_complaints for s in summaries if s.relief_rate < 5)

    with col1:
        metric_card("Total Complaints", f"{total:,}", delta="Selected period")
    with col2:
        metric_card("Avg Relief Rate", f"{avg_relief:.1f}%",
                    delta="% resolved with money back", delta_good=(avg_relief >= 20))
    with col3:
        metric_card("Timely Response", f"{avg_timely:.1f}%",
                    delta="% responded on time", delta_good=(avg_timely >= 80))
    with col4:
        metric_card("Poor Resolvers", str(unresolved),
                    delta="complaints barely resolved", delta_good=False)
    
    # Show achievement badges for best performers
    if summaries:
        best_relief = max(summaries, key=lambda x: x.relief_rate)
        best_timely = max(summaries, key=lambda x: x.timely_response_rate)
        if best_relief.relief_rate >= 30:
            achievement_badge(f"{best_relief.institution_name} — Customer Champion", "💎", "#10B981")
        if best_timely.timely_response_rate >= 95:
            achievement_badge(f"{best_timely.institution_name} — Quick Responder", "⚡", "#6366F1")

    if not complaints and not summaries:
        alert_card(
            "No complaint data loaded yet. Select banks in the sidebar and click Refresh to fetch live CFPB data.",
            "info"
        )
        return

    # ── Heatmap ───────────────────────────────────────────────────────────────
    section_divider("Complaint Volume — Bank × Product")
    alert_card(
        "Darker red cells = higher complaint concentration. "
        "This shows which banks have the most problems with which products.",
        "info"
    )
    st.plotly_chart(build_complaint_heatmap(complaints, banks), width="stretch")

    # ── Resolution ────────────────────────────────────────────────────────────
    section_divider("Resolution Rate — Who Actually Helps Customers")
    alert_card(
        "Relief Rate = % of complaints resolved with actual monetary compensation. "
        "A low relief rate means the bank closes complaints without fixing the problem.",
        "warning"
    )
    st.plotly_chart(build_resolution_rate_bar(summaries, banks), width="stretch")

    # ── Trend ─────────────────────────────────────────────────────────────────
    section_divider("Monthly Complaint Trend")
    st.plotly_chart(build_complaint_trend(complaints, banks), width="stretch")

    # ── Table ─────────────────────────────────────────────────────────────────
    section_divider("Complaint Detail Table")
    df = build_complaint_summary_table(summaries, banks)
    if not df.empty:
        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            column_config={
                "Institution": st.column_config.TextColumn("Institution", width="medium"),
                "Product": st.column_config.TextColumn("Product"),
                "Total Complaints": st.column_config.NumberColumn("Total Complaints", format="%d"),
                "Relief Rate": st.column_config.TextColumn("Relief Rate"),
                "Timely Response": st.column_config.TextColumn("Timely Response"),
                "Top Issue": st.column_config.TextColumn("Top Issue", width="large"),
            }
        )
    else:
        st.info("No summary data available for selected filters.")

    st.markdown(
        '<p style="color:#6B7280;font-size:0.75rem;margin-top:0.5rem;">'
        'Source: CFPB Consumer Complaint Database — api.consumerfinance.gov</p>',
        unsafe_allow_html=True
    )
