"""Top Lists — Spotify-style billboard rankings. No bar charts."""
import streamlit as st
from models.schemas import PipelineResult
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CD_12MO_RATES, BANK_CC_RATES
from config import FEDERAL_FUNDS_RATE

_RANK = [
    {"num_color": "#FFD700", "bg": "rgba(255,215,0,0.09)", "border": "rgba(255,215,0,0.32)"},
    {"num_color": "#C0C0C0", "bg": "rgba(192,192,192,0.07)", "border": "rgba(192,192,192,0.25)"},
    {"num_color": "#CD7F32", "bg": "rgba(205,127,50,0.07)", "border": "rgba(205,127,50,0.25)"},
    {"num_color": "#6B7280", "bg": "rgba(255,255,255,0.03)", "border": "rgba(255,255,255,0.09)"},
    {"num_color": "#6B7280", "bg": "rgba(255,255,255,0.03)", "border": "rgba(255,255,255,0.09)"},
    {"num_color": "#6B7280", "bg": "rgba(255,255,255,0.03)", "border": "rgba(255,255,255,0.09)"},
    {"num_color": "#6B7280", "bg": "rgba(255,255,255,0.03)", "border": "rgba(255,255,255,0.09)"},
    {"num_color": "#6B7280", "bg": "rgba(255,255,255,0.03)", "border": "rgba(255,255,255,0.09)"},
]


def _bar_gradient(value: float, max_val: float, good_high: bool = True) -> str:
    """Return a CSS gradient color based on how good the value is."""
    ratio = value / max_val if max_val else 0
    if not good_high:
        ratio = 1 - ratio
    if ratio >= 0.70:
        return "linear-gradient(90deg,#10B981,#6EE7B7)"
    if ratio >= 0.40:
        return "linear-gradient(90deg,#F59E0B,#FDE68A)"
    return "linear-gradient(90deg,#EF4444,#FCA5A5)"


def _billboard(
    title: str,
    subtitle: str,
    accent: str,
    items: list,          # list of (label, display_str, float_val)
    unit: str = "",
    good_high: bool = True,
    benchmark: float = None,
):
    """Render a Spotify-style ranked billboard section."""
    if not items:
        return

    max_val = max(v for _, _, v in items)

    header_html = (
        f'<div style="border-left:4px solid {accent};'
        f'padding:0.55rem 0.85rem;margin-bottom:0.7rem;'
        f'background:rgba(0,0,0,0.18);border-radius:0 8px 8px 0;">'
        f'<div style="color:{accent};font-size:0.9rem;font-weight:800;'
        f'letter-spacing:0.05em;">{title}</div>'
        f'<div style="color:#6B7280;font-size:0.68rem;margin-top:0.1rem;">{subtitle}</div>'
        f'</div>'
    )

    cards = []
    for rank, (label, disp, val) in enumerate(items):
        s = _RANK[min(rank, len(_RANK) - 1)]
        bar_w = max(4, int((val / max_val) * 100)) if good_high else max(4, int((1 - val / max_val) * 100))
        grad = _bar_gradient(val, max_val, good_high)

        bench_html = ""
        if benchmark is not None and good_high:
            diff = val - benchmark
            if diff >= 0:
                bench_html = (
                    f'<span style="background:rgba(16,185,129,0.18);color:#10B981;'
                    f'font-size:0.58rem;padding:1px 5px;border-radius:10px;margin-left:5px;">'
                    f'+{diff:.2f}% Fed</span>'
                )
            else:
                bench_html = (
                    f'<span style="background:rgba(239,68,68,0.15);color:#F87171;'
                    f'font-size:0.58rem;padding:1px 5px;border-radius:10px;margin-left:5px;">'
                    f'{diff:.2f}% Fed</span>'
                )

        card = (
            f'<div style="display:flex;align-items:center;gap:0.7rem;'
            f'background:{s["bg"]};border:1px solid {s["border"]};'
            f'border-radius:10px;padding:0.6rem 0.85rem;margin:0.28rem 0;">'
            f'  <span style="font-size:1.35rem;font-weight:900;color:{s["num_color"]};'
            f'  min-width:34px;text-align:center;font-variant-numeric:tabular-nums;">#{rank+1}</span>'
            f'  <div style="flex:1;min-width:0;">'
            f'    <div style="color:#E5E7EB;font-weight:600;font-size:0.82rem;'
            f'    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
            f'      {label}{bench_html}</div>'
            f'    <div style="background:rgba(255,255,255,0.08);height:3px;'
            f'    border-radius:2px;margin-top:0.32rem;">'
            f'      <div style="background:{grad};width:{bar_w}%;height:3px;border-radius:2px;"></div>'
            f'    </div>'
            f'  </div>'
            f'  <div style="text-align:right;min-width:50px;">'
            f'    <div style="color:{s["num_color"]};font-size:1.1rem;font-weight:800;line-height:1.1;">'
            f'      {disp}</div>'
            f'    <div style="color:#4B5563;font-size:0.6rem;">{unit}</div>'
            f'  </div>'
            f'</div>'
        )
        cards.append(card)

    st.markdown(header_html + "".join(cards), unsafe_allow_html=True)


def _divider():
    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,transparent,'
        'rgba(99,102,241,0.35),transparent);margin:1.25rem 0;"></div>',
        unsafe_allow_html=True,
    )


def render(result: PipelineResult):
    st.markdown(
        '<h1 style="color:#E5E7EB;font-size:1.6rem;font-weight:800;margin:0 0 0.2rem;">🏆 Top Lists</h1>'
        '<p style="color:#6B7280;font-size:0.83rem;margin:0 0 1.25rem;">'
        'Government-data rankings · zero affiliate influence.</p>',
        unsafe_allow_html=True,
    )

    # ── Row 1: Savings  +  CD ────────────────────────────────────────────
    c1, c2 = st.columns(2, gap="large")

    with c1:
        sv_items = sorted(BANK_SAVINGS_RATES.items(), key=lambda x: x[1], reverse=True)[:8]
        _billboard(
            "💰 BEST SAVINGS APY",
            "Annual Percentage Yield · Higher = more money for you",
            "#FFD700",
            [(k, f"{v:.2f}%", v) for k, v in sv_items],
            unit="APY",
            good_high=True,
            benchmark=FEDERAL_FUNDS_RATE,
        )

    with c2:
        cd_items = sorted(BANK_CD_12MO_RATES.items(), key=lambda x: x[1], reverse=True)[:8]
        _billboard(
            "🏦 BEST 12-MONTH CD",
            "Certificate of Deposit APY · Higher = better for you",
            "#A78BFA",
            [(k, f"{v:.2f}%", v) for k, v in cd_items],
            unit="APY",
            good_high=True,
        )

    _divider()

    # ── Row 2: Credit Card  +  Mortgage ──────────────────────────────────
    c3, c4 = st.columns(2, gap="large")

    with c3:
        cc_items = sorted(
            [(k, v) for k, v in BANK_CC_RATES.items() if v is not None],
            key=lambda x: x[1],
        )[:8]
        _billboard(
            "💳 LOWEST CREDIT CARD APR",
            "Annual Percentage Rate · Lower = costs you less",
            "#F472B6",
            [(k, f"{v:.1f}%", v) for k, v in cc_items],
            unit="APR",
            good_high=False,
        )

    with c4:
        if result.mortgage_summaries:
            mort_items = sorted(
                result.mortgage_summaries, key=lambda s: s.approval_rate, reverse=True
            )[:8]
            _billboard(
                "🏠 HIGHEST MORTGAGE APPROVAL",
                "Approval rate from HMDA data · Higher = easier to qualify",
                "#34D399",
                [(s.institution_name, f"{s.approval_rate:.1f}%", s.approval_rate)
                 for s in mort_items],
                unit="Approval",
                good_high=True,
            )
        else:
            st.info("Mortgage data loading — select banks & refresh.")

    # ── Credit Unions ────────────────────────────────────────────────────
    if result.credit_unions:
        _divider()
        st.markdown(
            '<h2 style="color:#E5E7EB;font-size:1.05rem;font-weight:700;margin:0 0 0.75rem;">'
            '🏛️ Credit Union Spotlight</h2>',
            unsafe_allow_html=True,
        )
        c5, c6 = st.columns(2, gap="large")

        with c5:
            cu_sv = sorted(
                [(cu.name, cu.savings_rate) for cu in result.credit_unions if cu.savings_rate],
                key=lambda x: x[1], reverse=True,
            )[:5]
            if cu_sv:
                _billboard(
                    "💰 CU SAVINGS RATES",
                    "Credit Union Annual Percentage Yields",
                    "#60A5FA",
                    [(k, f"{v:.2f}%", v) for k, v in cu_sv],
                    unit="APY",
                )

        with c6:
            cu_loan = sorted(
                [(cu.name, cu.loan_rate) for cu in result.credit_unions if cu.loan_rate],
                key=lambda x: x[1],
            )[:5]
            if cu_loan:
                _billboard(
                    "🚗 LOWEST CU AUTO LOANS",
                    "Credit Union loan rates · Lower = better for you",
                    "#FB923C",
                    [(k, f"{v:.2f}%", v) for k, v in cu_loan],
                    unit="Rate",
                    good_high=False,
                )

    st.markdown(
        '<p style="color:#374151;font-size:0.68rem;text-align:center;margin-top:1.5rem;">'
        'Data: FDIC · CFPB · FRED · HMDA · NCUA · No sponsored rankings.</p>',
        unsafe_allow_html=True,
    )
