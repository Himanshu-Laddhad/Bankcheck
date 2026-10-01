"""Consumer view: simple, jargon-free. Savings calculator + short bank matcher."""
from __future__ import annotations
import streamlit as st
from models.schemas import PipelineResult
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CC_RATES
from ui import theme as T


def _calculator():
    T.section("How much more could you earn?", "Move a balance from your current bank to a higher-paying one.")
    amount = st.slider("Savings balance", 1_000, 100_000, 10_000, 1_000, format="$%d")
    ranked = sorted(BANK_SAVINGS_RATES.items(), key=lambda kv: kv[1], reverse=True)
    c1, c2 = st.columns(2)
    with c1:
        cur = st.selectbox("Current bank", list(BANK_SAVINGS_RATES), index=0)
    with c2:
        new = st.selectbox("Switch to", [b for b, _ in ranked[:5]], index=0)

    cur_e = amount * BANK_SAVINGS_RATES[cur] / 100
    new_e = amount * BANK_SAVINGS_RATES[new] / 100
    diff = new_e - cur_e

    T.north_star("You would earn", f"${diff:,.0f}", "more per year",
                 f"{cur} {BANK_SAVINGS_RATES[cur]:.2f}% → {new} {BANK_SAVINGS_RATES[new]:.2f}% on ${amount:,}. "
                 f"Over 5 years: ${diff * 5:,.0f}.")
    st.plotly_chart(
        T.ranked_bar([cur, new], [cur_e, new_e], fmt="${:,.0f}", title="Annual interest earned"),
        width="stretch", config={"displayModeBar": False},
    )


def _quiz(result: PipelineResult):
    T.section("Find your match", "Four questions. Rankings use the same public data as the rest of the dashboard.")
    priority = st.radio("What matters most?",
                        ["Highest savings rate", "Lowest card APR", "Easiest mortgage approval"], horizontal=False)
    branches = st.radio("Do you need physical branches?", ["No, online is fine", "Yes"], horizontal=True)
    products = st.multiselect("Products you need", ["Savings", "Credit card", "Mortgage"], default=["Savings"])

    online_only = {"Ally Bank", "Synchrony Bank", "Goldman Sachs (Marcus)", "Discover", "American Express", "Capital One"}
    if priority == "Highest savings rate":
        pool = [(b, v, f"{v:.2f}% APY", True) for b, v in BANK_SAVINGS_RATES.items()]
    elif priority == "Lowest card APR":
        pool = [(b, v, f"{v:.1f}% APR", False) for b, v in BANK_CC_RATES.items() if v is not None]
    else:
        pool = [(m.institution_name, m.approval_rate, f"{m.approval_rate:.1f}% approved", True)
                for m in result.mortgage_summaries]
    if branches == "Yes":
        pool = [p for p in pool if p[0] not in online_only] or pool
    if not pool:
        st.caption("No data for that combination.")
        return

    higher = pool[0][3]
    pool = sorted(pool, key=lambda p: p[1], reverse=higher)[:3]
    T.section("Your top 3", f"Ranked by {priority.lower()}." + (" Filtered to banks with branches." if branches == "Yes" else ""))
    st.plotly_chart(
        T.ranked_bar([p[0] for p in pool], [p[1] for p in pool], fmt="{:.2f}", higher_is_better=higher,
                     title=priority),
        width="stretch", config={"displayModeBar": False},
    )
    for name, _, label, _ in pool:
        st.markdown(f"**{name}** — {label}")


def render(result: PipelineResult):
    T.page_title("Find your bank", "Plain answers from government data. No affiliate links, no sponsored results.")
    left, right = st.columns(2, gap="large")
    with left:
        _calculator()
    with right:
        _quiz(result)
