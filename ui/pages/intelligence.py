"""Intelligence Dashboard — diverse chart types for selected banks only."""
from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from collections import defaultdict
from typing import List

from models.schemas import PipelineResult
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CD_12MO_RATES, BANK_CC_RATES
from config import FEDERAL_FUNDS_RATE

# ── Shared style tokens ───────────────────────────────────────────────────────
_P = "rgba(0,0,0,0)"           # transparent paper bg
_C = "rgba(17,24,39,0.88)"     # dark plot bg
_G = "#374151"                  # grid color
_T = "#E5E7EB"                  # tick / text color
_SUB = "#9CA3AF"

_PAL = [
    "#6366F1", "#10B981", "#F59E0B", "#EF4444",
    "#8B5CF6", "#EC4899", "#14B8A6", "#F97316",
    "#3B82F6", "#A3E635", "#F43F5E", "#0EA5E9",
]

_BASE = dict(
    paper_bgcolor=_P, plot_bgcolor=_C,
    font=dict(color=_T, family="Inter, sans-serif", size=11),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
    margin=dict(l=10, r=20, t=42, b=12),
    height=300,
)


def _h(height: int = 300) -> dict:
    return {**_BASE, "height": height}


def _section(label: str, icon: str = ""):
    st.markdown(
        f'<div style="height:1px;background:linear-gradient(90deg,transparent,'
        f'rgba(99,102,241,0.4),transparent);margin:1.6rem 0 0.8rem;"></div>'
        f'<h2 style="color:{_T};font-size:1.1rem;font-weight:700;margin:0 0 0.6rem;">'
        f'{icon} {label}</h2>',
        unsafe_allow_html=True,
    )


def _hex_rgba(hex_col: str, alpha: float = 0.18) -> str:
    h = hex_col.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ════════════════════════════════════════════════════════════════════════════
# RATE CHARTS
# ════════════════════════════════════════════════════════════════════════════

def _radar_chart(banks: List[str]) -> go.Figure:
    """Radar: each axis = one rate metric, normalized 0–100."""
    cats = ["Savings APY", "12-Mo CD", "Low CC APR", "Rate Pass-Through"]
    fig = go.Figure()

    for i, bank in enumerate(banks[:9]):
        sv = BANK_SAVINGS_RATES.get(bank, 0)
        cd = BANK_CD_12MO_RATES.get(bank, 0)
        cc = BANK_CC_RATES.get(bank) or 30.0
        pt = min((sv / FEDERAL_FUNDS_RATE) * 100, 100) if FEDERAL_FUNDS_RATE > 0 else 0

        scores = [
            min(sv / 5.0 * 100, 100),
            min(cd / 5.5 * 100, 100),
            max(0.0, (35 - cc) / 20 * 100),
            pt,
        ]
        col = _PAL[i % len(_PAL)]
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=cats + [cats[0]],
            fill="toself",
            name=bank,
            line=dict(color=col, width=2),
            fillcolor=_hex_rgba(col, 0.12),
            hovertemplate="<b>%{theta}</b><br>Score: %{r:.0f}/100<extra>" + bank + "</extra>",
        ))

    fig.update_layout(
        polar=dict(
            bgcolor=_C,
            radialaxis=dict(
                visible=True, range=[0, 100], gridcolor=_G,
                tickfont=dict(color=_SUB, size=8), ticksuffix="",
            ),
            angularaxis=dict(gridcolor=_G, tickfont=dict(color=_T, size=9)),
        ),
        paper_bgcolor=_P,
        font=dict(color=_T, family="Inter, sans-serif", size=10),
        title=dict(text="Rate Profile — Normalized 0–100 (higher = better for you)", font=dict(size=12)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9), x=1.05),
        height=340,
        margin=dict(l=20, r=100, t=48, b=20),
    )
    return fig


def _bubble_savings_vs_cc(banks: List[str]) -> go.Figure:
    """Scatter bubble: x=Savings APY, y=CC APR (lower Y = better), bubble = CD rate."""
    fig = go.Figure()
    for i, bank in enumerate(banks):
        sv = BANK_SAVINGS_RATES.get(bank)
        cc = BANK_CC_RATES.get(bank)
        cd = BANK_CD_12MO_RATES.get(bank, 1.0)
        if sv is None or cc is None:
            continue
        col = _PAL[i % len(_PAL)]
        fig.add_trace(go.Scatter(
            x=[sv], y=[cc],
            mode="markers+text",
            text=[bank.split()[0]],
            textposition="top center",
            textfont=dict(size=8, color=_SUB),
            marker=dict(
                size=max(14, cd * 8),
                color=col,
                opacity=0.82,
                line=dict(color="rgba(255,255,255,0.25)", width=1),
            ),
            name=bank,
            hovertemplate=(
                f"<b>{bank}</b><br>"
                f"Savings APY: {sv:.2f}%<br>"
                f"CC APR: {cc:.1f}%<br>"
                f"CD APY: {cd:.2f}% (bubble size)"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    # "best zone" annotation
    fig.add_annotation(
        xref="paper", yref="paper", x=0.95, y=0.05,
        text="🏆 Best zone →<br>high savings, low CC",
        showarrow=False, font=dict(color="#10B981", size=8),
        bgcolor="rgba(16,185,129,0.08)", bordercolor="#10B981", borderwidth=1,
    )
    fig.update_layout(
        **_h(340),
        title="Savings APY vs Credit Card APR — bubble = CD rate",
        xaxis=dict(title="Savings APY (%) →  higher = better", gridcolor=_G, zeroline=False),
        yaxis=dict(
            title="CC APR (%) →  lower = better", gridcolor=_G, zeroline=False,
            autorange="reversed",
        ),
    )
    return fig


def _rate_heatmap(banks: List[str]) -> go.Figure:
    """Heatmap: banks × rate categories, colour = normalized score 0–100."""
    metrics = ["Savings APY", "12-Mo CD APY", "CC APR (inv.)"]
    z_vals, texts = [], []
    for bank in banks:
        sv = BANK_SAVINGS_RATES.get(bank, 0)
        cd = BANK_CD_12MO_RATES.get(bank, 0)
        cc = BANK_CC_RATES.get(bank) or 30.0
        row = [
            round(min(sv / 5.0 * 100, 100), 1),
            round(min(cd / 5.5 * 100, 100), 1),
            round(max(0.0, (35 - cc) / 20 * 100), 1),
        ]
        z_vals.append(row)
        texts.append([f"{v:.0f}" for v in row])

    fig = go.Figure(go.Heatmap(
        z=z_vals, x=metrics, y=banks,
        colorscale=[[0, "#1F2937"], [0.3, "#B45309"], [0.65, "#F59E0B"], [1, "#10B981"]],
        text=texts, texttemplate="%{text}",
        hovertemplate="<b>%{y}</b> — %{x}<br>Score: %{z:.0f}/100<extra></extra>",
        colorbar=dict(
            title=dict(text="Score/100", font=dict(color=_SUB)),
            tickfont=dict(color=_SUB), len=0.85,
        ),
        zmin=0, zmax=100,
    ))
    fig.update_layout(
        **{**_h(max(240, len(banks) * 32 + 80)), "margin": dict(l=10, r=20, t=64, b=12)},
        title=dict(text="Rate Scorecard Heatmap — score 0–100 (higher = better for you)", pad=dict(t=12)),
        xaxis=dict(side="top", gridcolor=_G),
        yaxis=dict(autorange="reversed", gridcolor=_G),
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════
# COMPLAINT CHARTS
# ════════════════════════════════════════════════════════════════════════════

_PROD_MAP = {
    "Credit card": "Credit Card",
    "Checking or savings account": "Checking/Savings",
    "Mortgage": "Mortgage",
    "Personal loan": "Personal Loan",
    "Vehicle loan or lease": "Auto Loan",
    "Student loan": "Student Loan",
    "Money transfer, virtual currency, or money service": "Money Transfer",
    "Debt collection": "Debt Collection",
    "Credit reporting": "Credit Reporting",
}


def _abbr(name: str, n: int = 11) -> str:
    return name[:n] + ("…" if len(name) > n else "")


def _complaint_sunburst(raw_complaints, banks: List[str]) -> go.Figure:
    """Sunburst: bank → product category → complaint count."""
    agg: dict = defaultdict(lambda: defaultdict(int))
    for c in raw_complaints:
        b = c.institution_name
        if banks and not any(bk.lower() in b.lower() for bk in banks):
            continue
        prod = _PROD_MAP.get(c.product, c.product[:20] if c.product else "Other")
        agg[b][prod] += 1

    if not agg:
        fig = go.Figure()
        fig.update_layout(**_h(), title="No complaint data for selected banks")
        return fig

    labels: list = ["All Complaints"]
    parents: list = [""]
    values: list = [0]
    colors: list = ["rgba(0,0,0,0)"]

    bank_pal = _PAL.copy()
    for bi, (bank, prods) in enumerate(agg.items()):
        bkey = _abbr(bank)
        bcol = bank_pal[bi % len(bank_pal)]
        labels.append(bkey)
        parents.append("All Complaints")
        values.append(sum(prods.values()))
        colors.append(bcol)
        for pi, (prod, cnt) in enumerate(prods.items()):
            labels.append(f"{bkey}/{_abbr(prod, 8)}")
            parents.append(bkey)
            values.append(cnt)
            colors.append(_hex_rgba(bcol, 0.55 + pi * 0.05))

    fig = go.Figure(go.Sunburst(
        labels=labels, parents=parents, values=values,
        branchvalues="total",
        marker=dict(colors=colors),
        hovertemplate="<b>%{label}</b><br>Complaints: %{value:,}<extra></extra>",
        insidetextorientation="radial",
    ))
    fig.update_layout(
        paper_bgcolor=_P,
        font=dict(color=_T, family="Inter, sans-serif", size=10),
        title=dict(text="Complaint Volume — Bank  ▸  Product", font=dict(size=12)),
        height=340,
        margin=dict(l=10, r=10, t=48, b=10),
    )
    return fig


def _resolution_bar(summaries, banks: List[str]) -> go.Figure:
    """Grouped horizontal bar: relief rate vs timely response per bank."""
    agg: dict = defaultdict(lambda: {"relief": [], "timely": []})
    for s in summaries:
        if banks and not any(b.lower() in s.institution_name.lower() for b in banks):
            continue
        agg[s.institution_name]["relief"].append(s.relief_rate)
        agg[s.institution_name]["timely"].append(s.timely_response_rate)

    if not agg:
        fig = go.Figure()
        fig.update_layout(**_h(), title="No resolution data for selected banks")
        return fig

    bnames = list(agg.keys())
    relief = [sum(v["relief"]) / len(v["relief"]) for v in agg.values()]
    timely = [sum(v["timely"]) / len(v["timely"]) for v in agg.values()]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=bnames, x=relief, name="Resolved with Relief", orientation="h",
        marker_color="#10B981",
        text=[f"{r:.0f}%" for r in relief], textposition="outside",
        hovertemplate="<b>%{y}</b><br>Relief: %{x:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=bnames, x=timely, name="Timely Response", orientation="h",
        marker_color="#6366F1",
        text=[f"{r:.0f}%" for r in timely], textposition="outside",
        hovertemplate="<b>%{y}</b><br>Timely: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **_h(max(280, len(bnames) * 52 + 80)),
        title="Complaint Resolution — Higher is Better",
        barmode="group",
        xaxis=dict(title="%", gridcolor=_G, range=[0, 125]),
        yaxis=dict(gridcolor=_G),
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════
# MORTGAGE CHARTS
# ════════════════════════════════════════════════════════════════════════════

def _mortgage_scatter(summaries, banks: List[str]) -> go.Figure:
    """Bubble scatter: x=approval rate, y=avg rate, size=# applications."""
    filtered = [
        s for s in summaries
        if (not banks or any(b.lower() in s.institution_name.lower() for b in banks))
        and s.total_applications > 5
    ]
    if not filtered:
        fig = go.Figure()
        fig.update_layout(**_h(), title="No mortgage data for selected banks")
        return fig

    avg_appr = sum(s.approval_rate for s in filtered) / len(filtered)
    fig = go.Figure()

    for i, s in enumerate(filtered):
        col = _PAL[i % len(_PAL)]
        size = max(12, min(52, s.total_applications / 40))
        fig.add_trace(go.Scatter(
            x=[s.approval_rate],
            y=[s.avg_interest_rate or 0],
            mode="markers+text",
            text=[_abbr(s.institution_name, 9)],
            textposition="top center",
            textfont=dict(size=8, color=_SUB),
            marker=dict(
                size=size, color=col, opacity=0.82,
                line=dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            name=s.institution_name,
            hovertemplate=(
                f"<b>{s.institution_name}</b><br>"
                f"Approval Rate: {s.approval_rate:.1f}%<br>"
                f"Avg Interest Rate: {s.avg_interest_rate:.2f}%<br>"
                f"Applications: {s.total_applications:,}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.add_vline(
        x=avg_appr, line_dash="dash", line_color="#F59E0B",
        annotation_text=f"Avg {avg_appr:.0f}%", annotation_font_color="#F59E0B",
        annotation_position="top right",
    )
    fig.update_layout(
        **_h(340),
        title="Mortgage: Approval Rate vs Interest Rate (size = applications)",
        xaxis=dict(title="Approval Rate (%) →  higher = easier", gridcolor=_G, zeroline=False),
        yaxis=dict(title="Avg Interest Rate (%) →  lower = better", gridcolor=_G, zeroline=False),
    )
    return fig


def _denial_stacked(summaries, banks: List[str]) -> go.Figure:
    """Stacked horizontal bar: denial reasons per bank."""
    filtered = [
        s for s in summaries
        if (not banks or any(b.lower() in s.institution_name.lower() for b in banks))
        and s.denial_reasons
    ]
    if not filtered:
        fig = go.Figure()
        fig.update_layout(**_h(), title="No denial reason data for selected banks")
        return fig

    all_reasons = sorted({r for s in filtered for r in s.denial_reasons})
    bnames = [s.institution_name for s in filtered]
    pal = px.colors.qualitative.Set2

    fig = go.Figure()
    for j, reason in enumerate(all_reasons[:7]):
        vals = [s.denial_reasons.get(reason, 0) for s in filtered]
        if sum(vals) == 0:
            continue
        fig.add_trace(go.Bar(
            y=bnames, x=vals, name=reason[:22], orientation="h",
            marker_color=pal[j % len(pal)],
            hovertemplate=f"<b>%{{y}}</b><br>{reason}: %{{x:,}}<extra></extra>",
        ))

    fig.update_layout(
        **_h(max(280, len(bnames) * 45 + 80)),
        title="Mortgage Denial Reasons — Stacked",
        barmode="stack",
        xaxis=dict(title="Number of Denials", gridcolor=_G),
        yaxis=dict(gridcolor=_G),
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════
# DETAILS TABLE
# ════════════════════════════════════════════════════════════════════════════

def _details_table(result: PipelineResult, banks: List[str]):
    cmp_agg: dict = defaultdict(lambda: {"total": 0, "relief": [], "timely": []})
    for s in result.complaint_summaries:
        n = s.institution_name
        if any(b.lower() in n.lower() for b in banks):
            cmp_agg[n]["total"] += s.total_complaints
            cmp_agg[n]["relief"].append(s.relief_rate)
            cmp_agg[n]["timely"].append(s.timely_response_rate)

    mort_map = {s.institution_name: s for s in result.mortgage_summaries}
    inst_map = {i.name: i for i in result.institutions}
    score_map = {s.institution_name: s for s in result.scores}

    rows = []
    for bank in banks:
        row: dict = {"Institution": bank}
        sv = BANK_SAVINGS_RATES.get(bank)
        cd = BANK_CD_12MO_RATES.get(bank)
        cc = BANK_CC_RATES.get(bank)
        row["Savings APY"] = f"{sv:.2f}%" if sv is not None else "N/A"
        row["12-Mo CD"] = f"{cd:.2f}%" if cd is not None else "N/A"
        row["CC APR"] = f"{cc:.2f}%" if cc is not None else "N/A"

        cmp = next((v for k, v in cmp_agg.items() if bank.lower() in k.lower()), None)
        if cmp and cmp["total"] > 0:
            row["Complaints"] = f"{cmp['total']:,}"
            row["Relief"] = f"{sum(cmp['relief'])/len(cmp['relief']):.1f}%"
            row["Timely"] = f"{sum(cmp['timely'])/len(cmp['timely']):.1f}%"
        else:
            row["Complaints"] = row["Relief"] = row["Timely"] = "N/A"

        mort = next((v for k, v in mort_map.items() if bank.lower() in k.lower()), None)
        if mort:
            row["Mortg. Approval"] = f"{mort.approval_rate:.1f}%"
            row["Avg Rate"] = f"{mort.avg_interest_rate:.2f}%" if mort.avg_interest_rate else "N/A"
        else:
            row["Mortg. Approval"] = row["Avg Rate"] = "N/A"

        inst = next((v for k, v in inst_map.items() if bank.lower() in k.lower()), None)
        if inst:
            row["Tier1 Cap."] = f"{inst.tier1_capital_ratio:.1f}%" if inst.tier1_capital_ratio else "N/A"
            row["Assets"] = f"${inst.asset_size/1e9:.1f}B" if inst.asset_size else "N/A"
        else:
            row["Tier1 Cap."] = row["Assets"] = "N/A"

        score = next((v for k, v in score_map.items() if bank.lower() in k.lower()), None)
        if score:
            row["Grade"] = score.grade
            row["Score"] = f"{score.overall_score:.0f}/100"
        else:
            row["Grade"] = row["Score"] = "N/A"

        rows.append(row)

    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.info("No data for selected banks.")


# ════════════════════════════════════════════════════════════════════════════
# MAIN RENDER
# ════════════════════════════════════════════════════════════════════════════

def render(result: PipelineResult):
    banks = result.selected_banks

    st.markdown(
        '<h1 style="color:#E5E7EB;font-size:1.6rem;font-weight:800;margin:0 0 0.2rem;">'
        'Intelligence Dashboard</h1>'
        '<p style="color:#6B7280;font-size:0.83rem;margin:0 0 0.5rem;">'
        'All charts are filtered to your selected banks.</p>',
        unsafe_allow_html=True,
    )

    if not banks:
        st.info("Select banks in the sidebar to load the dashboard.")
        return

    # ── RATE INTELLIGENCE ────────────────────────────────────────────────
    _section("Rate Intelligence")
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.plotly_chart(_radar_chart(banks), width="stretch")
    with c2:
        st.plotly_chart(_bubble_savings_vs_cc(banks), width="stretch")
    # Heatmap spans full width — spacer prevents title overlapping chart above
    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)
    st.plotly_chart(_rate_heatmap(banks), width="stretch")

    # ── COMPLAINT INTELLIGENCE ───────────────────────────────────────────
    _section("Complaint Intelligence")
    st.plotly_chart(
        _resolution_bar(result.complaint_summaries, banks),
        width="stretch",
    )

    # ── MORTGAGE & LENDING ───────────────────────────────────────────────
    _section("Mortgage & Lending")
    if result.mortgage_summaries:
        c5, c6 = st.columns(2, gap="medium")
        with c5:
            st.plotly_chart(
                _mortgage_scatter(result.mortgage_summaries, banks),
                width="stretch",
            )
        with c6:
            st.plotly_chart(
                _denial_stacked(result.mortgage_summaries, banks),
                width="stretch",
            )
    else:
        st.info("No mortgage data available for selected banks.")

    # ── DETAILS TABLE ────────────────────────────────────────────────────
    _section("Details Table")
    _details_table(result, banks)
