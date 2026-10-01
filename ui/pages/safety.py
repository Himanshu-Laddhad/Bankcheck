import streamlit as st
from models.schemas import PipelineResult
from ui.components import page_header, section_divider, alert_card, metric_card
from ui.interactive import animated_score_card, achievement_badge
from analytics.safety_analysis import (
    build_score_gauge_row, build_score_breakdown_bar,
    build_cu_vs_bank_comparison, build_safety_table, build_score_table,
)


def render(result: PipelineResult):
    page_header(
        "Safety & Scores",
        "FDIC capital ratios, composite A–F grades, and credit union comparison"
    )

    banks = result.selected_banks
    institutions = result.institutions
    scores = result.scores
    credit_unions = result.credit_unions

    # ── Top Performers with Badges ───────────────────────────────────────────
    if scores:
        section_divider("Top Performers")
        top_3 = sorted(scores, key=lambda x: x.overall_score, reverse=True)[:3]
        cols = st.columns(3)
        for i, score in enumerate(top_3):
            with cols[i]:
                animated_score_card(score, rank=i+1)
    
    # ── Score Gauges ──────────────────────────────────────────────────────────
    if scores:
        section_divider("Institution Grades")
        st.plotly_chart(build_score_gauge_row(scores[:6]), width="stretch")

    # ── Score KPIs ────────────────────────────────────────────────────────────
    if scores:
        col1, col2, col3, col4 = st.columns(4)
        top = max(scores, key=lambda x: x.overall_score)
        bottom = min(scores, key=lambda x: x.overall_score)
        a_grades = sum(1 for s in scores if s.grade in ("A+", "A"))
        f_grades = sum(1 for s in scores if s.grade == "F")
        with col1:
            metric_card("Top Performer", top.institution_name[:20], delta=f"Grade {top.grade}", delta_good=True)
        with col2:
            metric_card("Lowest Scorer", bottom.institution_name[:20], delta=f"Grade {bottom.grade}", delta_good=False)
        with col3:
            metric_card("A-Grade Banks", str(a_grades), delta="Recommended")
        with col4:
            metric_card("F-Grade Banks", str(f_grades), delta="Avoid", delta_good=False)

    # ── Breakdown Bar ─────────────────────────────────────────────────────────
    if scores:
        section_divider("Score Breakdown by Category")
        alert_card(
            "Scoring: Rate (35%) + Complaints (35%) + Safety (20%) + Fairness (10%). "
            "All inputs from US government data sources.",
            "info"
        )
        st.plotly_chart(build_score_breakdown_bar(scores), width="stretch")

    # ── FDIC Safety Table ─────────────────────────────────────────────────────
    if institutions:
        section_divider("FDIC Financial Safety Data")
        df = build_safety_table(institutions, banks)
        if not df.empty:
            st.dataframe(df, width="stretch", hide_index=True)

    # ── Credit Union Comparison ───────────────────────────────────────────────
    section_divider("Credit Unions vs Banks — Savings APY")
    alert_card(
        "Credit unions are non-profit and typically offer higher savings rates and lower loan rates than banks. "
        "Membership is required — many are open to anyone in a state or profession.",
        "info"
    )
    if credit_unions or banks:
        st.plotly_chart(build_cu_vs_bank_comparison(credit_unions, banks), width="stretch")

    if credit_unions:
        import pandas as pd
        cu_rows = []
        for cu in credit_unions:
            cu_rows.append({
                "Credit Union": cu.name,
                "State": cu.state or "N/A",
                "Membership": cu.membership_type or "N/A",
                "Savings APY": f"{cu.savings_rate:.2f}%" if cu.savings_rate else "N/A",
                "Loan Rate": f"{cu.loan_rate:.2f}%" if cu.loan_rate else "N/A",
                "NCUA Insured": "Yes",
            })
        st.dataframe(pd.DataFrame(cu_rows), width="stretch", hide_index=True)

    # ── Full Score Table ──────────────────────────────────────────────────────
    if scores:
        section_divider("Full Scorecard Table")
        df = build_score_table(scores)
        if not df.empty:
            st.dataframe(df, width="stretch", hide_index=True)

    st.markdown(
        '<p style="color:#6B7280;font-size:0.75rem;margin-top:0.5rem;">'
        'Sources: FDIC BankFind Suite · NCUA Call Report Data · CFPB · HMDA</p>',
        unsafe_allow_html=True
    )
