"""Executive view: one North Star, four supporting KPIs, exceptions only, one trend, one gap chart."""
from __future__ import annotations
import streamlit as st
from models.schemas import PipelineResult
from ui import theme as T
from ui.helpers import (THRESH, rates_for, complaints_by_bank, mortgage_by_bank, fed_rate,
                        savings_status, short)


def render(result: PipelineResult):
    banks = result.selected_banks
    r = rates_for(banks)
    cmp_ = complaints_by_bank(result, banks)
    mort = mortgage_by_bank(result, banks)
    fed = fed_rate(result)

    if not r["savings"]:
        st.info("Select at least one bank in the sidebar.")
        return

    best_bank = max(r["savings"], key=r["savings"].get)
    best = r["savings"][best_bank]
    avg_sv = sum(r["savings"].values()) / len(r["savings"])
    gap = fed - best

    T.page_title(
        "Overview",
        (f"{best_bank} pays the most of {len(r['savings'])} selected banks, "
         f"but still {gap:.2f} pts under the Fed funds rate.") if gap > 0 else
        f"{best_bank} leads {len(r['savings'])} selected banks and beats the Fed funds rate.",
    )

    # ── North Star (top-left, biggest) + four supporting KPIs ────────────
    left, right = st.columns([1.15, 2], gap="large")
    with left:
        T.north_star("Best savings APY", f"{best:.2f}", "%", f"{best_bank} · Fed funds {fed:.2f}%")
    with right:
        k1, k2, k3, k4 = st.columns(4, gap="medium")
        with k1:
            T.kpi("Avg savings APY", f"{avg_sv:.2f}%", f"{avg_sv - fed:+.2f} pts vs Fed",
                  savings_status(avg_sv - fed))
        with k2:
            if r["cc"]:
                lo = min(r["cc"], key=r["cc"].get)
                v = r["cc"][lo]
                T.kpi("Lowest card APR", f"{v:.1f}%", short(lo, 16),
                      "warn" if v > THRESH["cc_apr_warn"] else "good")
            else:
                T.kpi("Lowest card APR", "—", "no data")
        with k3:
            if cmp_:
                tot = sum(c["total"] for c in cmp_.values())
                tim = sum(c["timely"] * c["total"] for c in cmp_.values()) / tot
                T.kpi("Timely response", f"{tim:.1f}%", "complaints answered on time",
                      "alert" if tim < THRESH["timely_alert"] else "warn" if tim < THRESH["timely_warn"] else "good")
            else:
                T.kpi("Timely response", "—", "no data")
        with k4:
            if mort:
                ap = sum(m.approval_rate for m in mort.values()) / len(mort)
                T.kpi("Mortgage approval", f"{ap:.1f}%", "avg of selected",
                      "warn" if ap < THRESH["approval_warn"] else "good")
            else:
                T.kpi("Mortgage approval", "—", "no data")

    # ── Exceptions: same rules that colour the KPIs ──────────────────────
    T.section("Exceptions",
              f"Thresholds: savings {THRESH['savings_gap_warn']:.0f} pt (watch) / {THRESH['savings_gap_alert']:.0f} pts "
              f"(act) under Fed funds · timely response under {THRESH['timely_warn']:.0f}% / {THRESH['timely_alert']:.0f}% "
              f"· mortgage approval under {THRESH['approval_warn']:.0f}%.")
    shown = 0
    by_status = {"alert": [], "warn": []}
    for b, v in r["savings"].items():
        s = savings_status(v - fed)
        if s in by_status:
            by_status[s].append((b, fed - v))
    if by_status["alert"]:
        names = ", ".join(f"<b>{b}</b> ({g:.2f})" for b, g in sorted(by_status["alert"], key=lambda x: -x[1])[:4])
        T.exception("alert", f"Savings more than {THRESH['savings_gap_alert']:.0f} pts under Fed funds: {names}.",
                    f"Moving $10,000 to {best_bank} earns about ${(best - min(r['savings'].values())) * 100:,.0f} "
                    f"more per year than the lowest payer.")
        shown += 1
    if by_status["warn"]:
        names = ", ".join(f"<b>{b}</b> ({g:.2f})" for b, g in sorted(by_status["warn"], key=lambda x: -x[1])[:4])
        T.exception("warn", f"Savings {THRESH['savings_gap_warn']:.0f}–{THRESH['savings_gap_alert']:.0f} pts under "
                            f"Fed funds: {names}.", "Compare rates in the Compare tab.")
        shown += 1
    for b, c in cmp_.items():
        if c["timely"] < THRESH["timely_alert"]:
            T.exception("alert", f"<b>{b}</b> answers only {c['timely']:.1f}% of complaints on time.",
                        "Open Drill-down to see which products drive it.")
            shown += 1
        elif c["timely"] < THRESH["timely_warn"]:
            T.exception("warn", f"<b>{b}</b> answers {c['timely']:.1f}% of complaints on time "
                                f"(target {THRESH['timely_warn']:.0f}%).")
            shown += 1
    for b, m in mort.items():
        if m.approval_rate < THRESH["approval_warn"]:
            T.exception("warn", f"<b>{b}</b> approves {m.approval_rate:.1f}% of mortgage applications.")
            shown += 1
    if not shown:
        st.markdown('<p class="ok-line">● No exceptions. All selected banks are inside thresholds.</p>',
                    unsafe_allow_html=True)

    # ── Trend + gap ──────────────────────────────────────────────────────
    c1, c2 = st.columns(2, gap="large")
    with c1:
        hist = result.fed_history
        if hist:
            first, last = hist[0], hist[-1]
            delta = float(last["value"]) - float(first["value"])
            T.section("Fed funds rate over time",
                      f"{'Down' if delta < 0 else 'Up'} {abs(delta):.2f} pts since {first['date']}; "
                      f"the best savings account pays {best:.2f}%.")
            T.show(T.trend_line([h["date"] for h in hist], [float(h["value"]) for h in hist],
                                name="Fed funds", reference=best,
                                reference_label=f"{best_bank} {best:.2f}%"))
        else:
            T.section("Fed funds rate over time", "History needs a FRED API key; showing the latest value only.")
            st.caption(f"Latest benchmark: {fed:.2f}%")
    with c2:
        gaps = {short(b): v - fed for b, v in r["savings"].items()}
        T.section("Savings APY vs Fed funds",
                  f"{sum(1 for g in gaps.values() if g < 0)} of {len(gaps)} selected banks pay below the benchmark.")
        T.show(T.diverging_bar(list(gaps), list(gaps.values())))

    stale = [h.source.upper() for h in result.health if h.error and h.is_healthy]
    T.footnote(
        f"Data as of {result.as_of}. "
        + (f"Reference-year data (not live): {', '.join(stale)}. " if stale else "")
        + "Sources: FDIC, CFPB, Federal Reserve FRED, HMDA, NCUA. No affiliate links or sponsored results."
    )
