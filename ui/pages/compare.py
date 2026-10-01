"""Operational view. Chart type follows data structure:
ranked bars for rankings, dot plots for tight ranges (with peers), scatters for relationships."""
from __future__ import annotations
import streamlit as st
from models.schemas import PipelineResult
from ui import theme as T
from ui.helpers import (THRESH, ALL_BANKS, rates_for, complaints_by_bank, mortgage_by_bank,
                        score_by_bank, fed_rate, short)


def render(result: PipelineResult):
    banks = result.selected_banks
    fed = fed_rate(result)
    r = rates_for(banks)
    allr = rates_for(ALL_BANKS)
    cmp_ = complaints_by_bank(result, banks)
    cmp_all = complaints_by_bank(result, ALL_BANKS)
    mort = mortgage_by_bank(result, banks)
    mort_all = mortgage_by_bank(result, ALL_BANKS)
    scores = score_by_bank(result, banks)

    T.page_title("Compare", "Blue marks your selected banks; gray shows every tracked bank for context.")

    # ── Rates ────────────────────────────────────────────────────────────
    T.section("Rates", "What you earn on deposits and what you pay on cards (ranked, best first).")
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        if r["savings"]:
            T.show(T.ranked_bar([short(b, 18) for b in r["savings"]], list(r["savings"].values()),
                                benchmark=fed, benchmark_label=f"Fed {fed:.2f}%",
                                title="Savings APY (higher is better)"))
    with c2:
        if r["cd"]:
            T.show(T.ranked_bar([short(b, 18) for b in r["cd"]], list(r["cd"].values()),
                                title="12-month CD APY (higher is better)"))
    with c3:
        if r["cc"]:
            T.show(T.ranked_bar([short(b, 18) for b in r["cc"]], list(r["cc"].values()),
                                fmt="{:.1f}%", higher_is_better=False,
                                title="Credit-card APR (lower is better)"))

    left, right = st.columns(2, gap="large")
    with left:
        pts = {b: (allr["savings"][b], allr["cc"][b]) for b in ALL_BANKS if b in allr["savings"] and b in allr["cc"]}
        if pts:
            top = max(pts, key=lambda b: pts[b][0] - pts[b][1] / 10)
            T.section("Savings vs card cost", "Banks that pay more on savings and charge less on cards sit top-right.")
            T.show(T.labelled_scatter(pts, banks, x_title="Savings APY (%)", y_title="Card APR (%)",
                                      x_higher_better=True, y_higher_better=False))
    with right:
        if scores:
            lead = max(scores.values(), key=lambda s: s.overall_score)
            T.section("Overall score",
                      f"{lead.institution_name} scores highest ({lead.overall_score:.0f}/100, grade {lead.grade}).")
            T.show(T.ranked_bar([short(b, 22) for b in scores], [s.overall_score for s in scores.values()],
                                fmt="{:.0f}", axis_max=115))

    # ── Complaints ───────────────────────────────────────────────────────
    T.section("Complaint handling", "Volume is a ranked bar; relief and timeliness differ by only a few points, "
                                    "so they are dot plots against all tracked banks.")
    if cmp_:
        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            T.show(T.ranked_bar([short(b, 18) for b in cmp_], [v["total"] for v in cmp_.values()],
                                fmt="{:,.0f}", higher_is_better=False,
                                title="Complaint volume (fewer is better)"))
        with c2:
            T.show(T.dot_plot({b: v["relief"] for b, v in cmp_all.items()}, list(cmp_),
                              title="Closed with relief, % (higher is better)",
                              benchmark=THRESH["relief_warn"], benchmark_label=f"{THRESH['relief_warn']:.0f}%"))
        with c3:
            T.show(T.dot_plot({b: v["timely"] for b, v in cmp_all.items()}, list(cmp_),
                              title="Timely response, % (higher is better)",
                              benchmark=THRESH["timely_warn"], benchmark_label=f"{THRESH['timely_warn']:.0f}%"))
    else:
        st.caption("No complaint data for the selected banks.")

    # ── Mortgages ────────────────────────────────────────────────────────
    T.section("Mortgage lending", "Higher approval and lower rate is the best zone.")
    if mort:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            pts = {b: (m.approval_rate, m.avg_interest_rate) for b, m in mort_all.items() if m.avg_interest_rate}
            T.show(T.labelled_scatter(pts, banks, x_title="Approval rate (%)", y_title="Average rate (%)",
                                      x_higher_better=True, y_higher_better=False))
        with c2:
            T.show(T.ranked_bar([short(b, 18) for b in mort], [m.approval_rate for m in mort.values()],
                                fmt="{:.1f}%", benchmark=THRESH["approval_warn"],
                                benchmark_label=f"{THRESH['approval_warn']:.0f}%",
                                title="Approval rate (higher is better)"))
    else:
        st.caption("No mortgage data for the selected banks.")

    cus = [cu for cu in result.credit_unions if cu.savings_rate]
    if cus:
        T.section("Credit unions", "Shown because the sidebar toggle is on.")
        cus = sorted(cus, key=lambda c: c.savings_rate, reverse=True)[:8]
        T.show(T.ranked_bar([short(c.name, 28) for c in cus], [c.savings_rate for c in cus],
                            benchmark=fed, benchmark_label=f"Fed {fed:.2f}%",
                            title="Credit-union savings APY (higher is better)"))
