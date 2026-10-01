import streamlit as st
from models.schemas import PipelineResult
from ui.components import metric_card, alert_card, source_health_row, section_divider
from ui.interactive import (
    hero_section, show_quick_picks, savings_calculator, 
    bank_matcher_quiz, animated_score_card, live_rankings_leaderboard
)
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CC_RATES
from config import FEDERAL_FUNDS_RATE


def render(result: PipelineResult):
    # Hero section with quick bank picker
    hero_section()
    
    # Show quick picks if user clicked one
    show_quick_picks(result)

    # ── Source Health ─────────────────────────────────────────────────────────
    if result.health:
        source_health_row(result.health)
        st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

    # ── Alerts ────────────────────────────────────────────────────────────────
    section_divider("Today's Alerts")
    fed_rate = FEDERAL_FUNDS_RATE
    alerts_shown = 0

    # Best savings rate alert — scoped to selected banks only
    selected_rates = {
        b: BANK_SAVINGS_RATES[b]
        for b in (result.selected_banks or list(BANK_SAVINGS_RATES.keys()))
        if b in BANK_SAVINGS_RATES
    }
    if selected_rates:
        best_bank  = max(selected_rates, key=selected_rates.get)
        best_rate  = selected_rates[best_bank]
        worst_bank = min(selected_rates, key=selected_rates.get)
        worst_rate = selected_rates[worst_bank]
        alert_card(f"Best savings rate today: <b>{best_bank}</b> at <b>{best_rate:.2f}% APY</b>", "success")
        alert_card(
            f"<b>{worst_bank}</b> savings rate is only {worst_rate:.2f}% — "
            f"that's {fed_rate - worst_rate:.2f}% below the Fed benchmark. "
            f"You're losing ~${(fed_rate - worst_rate) * 10000 / 100:.0f}/year on a $10,000 deposit.",
            "error"
        )
        alerts_shown += 2

    # High complaint bank alert
    if result.complaint_summaries:
        from collections import defaultdict
        bank_totals: dict = defaultdict(int)
        for s in result.complaint_summaries:
            bank_totals[s.institution_name] += s.total_complaints
        if bank_totals:
            worst_complaint = max(bank_totals, key=bank_totals.get)
            alert_card(
                f"<b>{worst_complaint}</b> has the highest complaint volume "
                f"({bank_totals[worst_complaint]:,} complaints) among selected banks.",
                "warning"
            )

    if not alerts_shown and not result.complaint_summaries:
        alert_card("Select banks in the sidebar to see personalised alerts.", "info")

    # ── KPI Row ───────────────────────────────────────────────────────────────
    section_divider("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        banks_count = len(result.selected_banks) or len(BANK_SAVINGS_RATES)
        metric_card("Banks Tracked", str(banks_count))
    with col2:
        best_rate_val = max(BANK_SAVINGS_RATES.values()) if BANK_SAVINGS_RATES else 0
        metric_card("Best Savings APY", f"{best_rate_val:.2f}%", delta="vs 0.64% national avg", delta_good=True)
    with col3:
        total_complaints = sum(s.total_complaints for s in result.complaint_summaries)
        metric_card("Complaints Tracked", f"{total_complaints:,}")
    with col4:
        metric_card("Fed Funds Rate", f"{fed_rate:.2f}%", delta="Current benchmark")

    # ── Live Rankings ─────────────────────────────────────────────────────────
    live_rankings_leaderboard()
    
    # ── Interactive Calculator ────────────────────────────────────────────────
    section_divider()
    savings_calculator(result)
    
    # ── Bank Matcher Quiz ─────────────────────────────────────────────────────
    section_divider()
    bank_matcher_quiz()
    
    # ── Score Cards ───────────────────────────────────────────────────────────
    if result.scores:
        section_divider("Institution Scorecards")
        # Sort scores by overall score
        sorted_scores = sorted(result.scores, key=lambda x: x.overall_score, reverse=True)
        cols = st.columns(min(len(sorted_scores), 3))
        for i, score in enumerate(sorted_scores[:6]):
            with cols[i % 3]:
                animated_score_card(score, rank=i+1)

    # ── Rate Snapshot ─────────────────────────────────────────────────────────
    section_divider("Quick Rate Snapshot")
    selected = result.selected_banks or list(BANK_SAVINGS_RATES.keys())[:8]
    rows = []
    for bank in selected:
        savings = BANK_SAVINGS_RATES.get(bank)
        cc = BANK_CC_RATES.get(bank)
        rows.append({
            "Institution": bank,
            "Savings APY": f"{savings:.2f}%" if savings is not None else "N/A",
            "Gap to Fed": f"-{fed_rate - savings:.2f}%" if savings is not None else "N/A",
            "Credit Card APR": f"{cc:.2f}%" if cc is not None else "N/A",
        })

    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            column_config={
                "Institution": st.column_config.TextColumn("Institution", width="medium"),
                "Savings APY": st.column_config.TextColumn("Savings APY"),
                "Gap to Fed": st.column_config.TextColumn("Gap to Fed Rate"),
                "Credit Card APR": st.column_config.TextColumn("Credit Card APR"),
            }
        )

    st.markdown(
        '<p style="color:#6B7280;font-size:0.75rem;text-align:center;margin-top:1rem;">'
        'Data sources: FDIC BankFind · CFPB Complaints · Federal Reserve FRED · HMDA · NCUA · '
        'All government data. No affiliate links. No sponsored results.</p>',
        unsafe_allow_html=True
    )
