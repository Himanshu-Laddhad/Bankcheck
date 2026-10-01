"""Analyst view: summary -> breakdown -> rows, plus a full exportable table."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from models.schemas import PipelineResult
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CD_12MO_RATES, BANK_CC_RATES
from ui import theme as T
from ui.helpers import (THRESH, match, complaints_by_bank, mortgage_by_bank, score_by_bank, short)

_CFG = {"displayModeBar": False}

_HIGHER = ["Score", "Savings APY %", "12-mo CD %", "Relief %", "Timely %", "Mortgage approval %", "Tier 1 capital %"]
_LOWER = ["Card APR %", "Complaints", "Avg mortgage rate %"]


def _styled(df: pd.DataFrame):
    """Conditional-format scorecard: blue intensity = better within each column (direction-aware)."""
    def shade(col: pd.Series):
        if col.name not in _HIGHER + _LOWER or col.dropna().nunique() < 2:
            return [""] * len(col)
        lo, hi = col.min(), col.max()
        out = []
        for v in col:
            if pd.isna(v):
                out.append("")
                continue
            t = (v - lo) / (hi - lo)
            t = t if col.name in _HIGHER else 1 - t
            r, g, b = (int(T.ACCENT.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
            out.append(f"background-color: rgba({r},{g},{b},{0.06 + 0.34 * t:.2f})")
        return out
    fmt = {c: "{:.2f}" for c in df.columns if c.endswith("%")}
    fmt.update({"Complaints": "{:,.0f}", "Score": "{:.0f}", "Assets $B": "{:,.1f}"})
    return df.style.apply(shade, axis=0).format(fmt, na_rep="N/A")


def _full_table(result: PipelineResult, banks: list[str]) -> pd.DataFrame:
    cmp_, mort, sc = (complaints_by_bank(result, banks), mortgage_by_bank(result, banks),
                      score_by_bank(result, banks))
    inst = {b: next((i for i in result.institutions if match(b, i.name)), None) for b in banks}
    rows = []
    for b in banks:
        c, m, s, i = cmp_.get(b), mort.get(b), sc.get(b), inst[b]
        rows.append({
            "Institution": b,
            "Grade": s.grade if s else None,
            "Score": round(s.overall_score) if s else None,
            "Savings APY %": BANK_SAVINGS_RATES.get(b),
            "12-mo CD %": BANK_CD_12MO_RATES.get(b),
            "Card APR %": BANK_CC_RATES.get(b),
            "Complaints": c["total"] if c else None,
            "Relief %": round(c["relief"], 1) if c else None,
            "Timely %": round(c["timely"], 1) if c else None,
            "Mortgage approval %": m.approval_rate if m else None,
            "Avg mortgage rate %": m.avg_interest_rate if m else None,
            "Tier 1 capital %": i.tier1_capital_ratio if i else None,
            "Assets $B": round(i.asset_size / 1e6, 1) if i and i.asset_size else None,
        })
    return pd.DataFrame(rows)


def render(result: PipelineResult):
    banks = result.selected_banks
    T.page_title("Drill-down", "Pick a bank, choose a dimension, then inspect the underlying records.")
    if not banks:
        st.info("Select at least one bank in the sidebar.")
        return

    bank = st.selectbox("Bank", banks, label_visibility="collapsed")
    cmp_ = complaints_by_bank(result, [bank]).get(bank)
    mort = mortgage_by_bank(result, [bank]).get(bank)
    sc = score_by_bank(result, [bank]).get(bank)

    # ── Level 1: summary ─────────────────────────────────────────────────
    cols = st.columns(5, gap="medium")
    with cols[0]:
        T.kpi("Overall", f"{sc.grade} · {sc.overall_score:.0f}" if sc else "—", "composite score")
    with cols[1]:
        v = BANK_SAVINGS_RATES.get(bank)
        T.kpi("Savings APY", f"{v:.2f}%" if v is not None else "—")
    with cols[2]:
        T.kpi("Complaints", f"{cmp_['total']:,}" if cmp_ else "—",
              f"{cmp_['timely']:.1f}% timely" if cmp_ else "",
              ("alert" if cmp_['timely'] < THRESH['timely_alert'] else "good") if cmp_ else "neutral")
    with cols[3]:
        T.kpi("Mortgage approval", f"{mort.approval_rate:.1f}%" if mort else "—",
              "", "warn" if mort and mort.approval_rate < THRESH["approval_warn"] else "neutral")
    with cols[4]:
        i = next((i for i in result.institutions if match(bank, i.name)), None)
        t1 = i.tier1_capital_ratio if i else None
        T.kpi("Tier 1 capital", f"{t1:.1f}%" if t1 else "—",
              "" if t1 is None else ("below 10% threshold" if t1 < THRESH["tier1_warn"] else "well capitalised"),
              "neutral" if t1 is None else ("warn" if t1 < THRESH["tier1_warn"] else "good"))

    # ── Level 2: breakdown ───────────────────────────────────────────────
    T.section("Breakdown")
    dim = st.segmented_control("Dimension", ["Complaints by product", "Mortgage denials", "Score components"],
                               default="Complaints by product", label_visibility="collapsed")

    if dim == "Complaints by product":
        rows = [x for x in result.complaint_summaries if match(bank, x.institution_name)]
        if rows:
            tot = sum(x.total_complaints for x in rows)
            worst = max(rows, key=lambda x: x.total_complaints)
            T.section(f"Where {bank}'s complaints come from",
                      f"{worst.product} is {worst.total_complaints / tot:.0%} of its {tot:,} complaints. "
                      "Each bar is one bank's mix, so shares are comparable.")
            shares = {}
            for b in [bank] + [x for x in banks if x != bank]:
                parts = {}
                for x in result.complaint_summaries:
                    if match(b, x.institution_name):
                        parts[x.product] = parts.get(x.product, 0) + x.total_complaints
                if parts:
                    shares[short(b, 20)] = parts
            T.show(T.stacked_share(shares))
            df = pd.DataFrame([{"Product": x.product, "Complaints": x.total_complaints,
                                "Relief %": x.relief_rate, "Timely %": x.timely_response_rate,
                                "Top issues": ", ".join(x.top_issues[:3])} for x in rows])
            st.dataframe(df, hide_index=True, width="stretch")
        else:
            st.caption("No complaint data for this bank.")
    elif dim == "Mortgage denials":
        if mort and mort.denial_reasons:
            tot = sum(mort.denial_reasons.values())
            top = max(mort.denial_reasons, key=mort.denial_reasons.get)
            T.section("Why mortgage applications are denied",
                      f"{top} is the leading reason ({mort.denial_reasons[top] / tot:.0%} of {bank}'s recorded denials).")
            shares = {}
            for b in [bank] + [x for x in banks if x != bank]:
                m = mortgage_by_bank(result, [b]).get(b)
                if m and m.denial_reasons:
                    shares[short(b, 20)] = dict(m.denial_reasons)
            T.show(T.stacked_share(shares))
        else:
            st.caption("No denial data for this bank.")
    else:
        if sc:
            parts = {"Rates": sc.rate_score, "Complaints": sc.complaint_score,
                     "Safety": sc.safety_score, "Fairness": sc.fairness_score}
            weakest = min(parts, key=parts.get)
            T.section("What drives the score", f"{weakest} is the weakest component ({parts[weakest]:.0f}/100).")
            st.plotly_chart(T.ranked_bar(list(parts), list(parts.values()), fmt="{:.0f}", axis_max=120,
                                         benchmark=60, benchmark_label="60"),
                            width="stretch", config=_CFG)
            if sc.verdict:
                st.caption(sc.verdict)
        else:
            st.caption("No score for this bank.")

    # ── Level 3: records ─────────────────────────────────────────────────
    T.section("Underlying records", "Individual complaint records available for this bank.")
    raw = [c for c in result.raw_complaints if match(bank, c.institution_name)]
    if raw:
        st.dataframe(pd.DataFrame([c.model_dump() for c in raw]), hide_index=True, width="stretch")
    else:
        st.caption("No record-level complaints loaded for this bank. Summaries above come from the CFPB annual report.")

    # ── Export ───────────────────────────────────────────────────────────
    T.section("All selected banks", "Full comparison table. Export for your own analysis.")
    df = _full_table(result, banks)
    st.dataframe(_styled(df), hide_index=True, width="stretch")
    st.caption("Blue intensity shows how good a value is within its column (darker is better; for APR, volume and rate, lower is darker).")
    st.download_button("Download CSV", df.to_csv(index=False).encode(), "bank_comparison.csv", "text/csv")
