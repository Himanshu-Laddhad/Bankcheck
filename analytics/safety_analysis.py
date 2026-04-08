"""Bank safety and credit union comparison charts."""
from typing import List
import pandas as pd
import plotly.graph_objects as go
from models.schemas import Institution, BankScore, CreditUnion
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CC_RATES
from processing.aggregator import BANK_CD_12MO_RATES

COLORS = {
    "primary": "#4F8EF7", "green": "#10B981", "red": "#F43F5E",
    "amber": "#F59E0B", "purple": "#8B5CF6", "bg": "#111827",
    "card": "#1F2937", "text": "#E5E7EB", "subtext": "#9CA3AF",
}
PLOT_LAYOUT = dict(
    paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["card"],
    font=dict(color=COLORS["text"], family="Inter, sans-serif"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

GRADE_COLOR = {"A+": "#10B981", "A": "#10B981", "B": "#4F8EF7",
               "C": "#F59E0B", "D": "#F97316", "F": "#F43F5E", "N/A": "#6B7280"}


def build_score_gauge_row(scores: List[BankScore]) -> go.Figure:
    if not scores:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No score data")

    n = len(scores)
    fig = go.Figure()

    for i, s in enumerate(scores):
        color = GRADE_COLOR.get(s.grade, COLORS["primary"])
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=s.overall_score,
            title={"text": f"<b>{s.institution_name}</b><br><span style='font-size:1.4em;color:{color}'>{s.grade}</span>",
                   "font": {"color": COLORS["text"], "size": 13}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": COLORS["subtext"]},
                "bar": {"color": color},
                "bgcolor": COLORS["card"],
                "bordercolor": "#374151",
                "steps": [
                    {"range": [0, 50], "color": "#1a0a0a"},
                    {"range": [50, 70], "color": "#1a150a"},
                    {"range": [70, 100], "color": "#0a1a0f"},
                ],
                "threshold": {"line": {"color": COLORS["amber"], "width": 2}, "thickness": 0.75, "value": 70},
            },
            domain={"row": 0, "column": i},
        ))

    fig.update_layout(
        **{**PLOT_LAYOUT, "margin": dict(l=10, r=10, t=60, b=10)},
        grid={"rows": 1, "columns": n, "pattern": "independent"},
        height=250,
    )
    return fig


def build_score_breakdown_bar(scores: List[BankScore]) -> go.Figure:
    if not scores:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No score data")

    categories = ["Rate Score", "Complaint Score", "Safety Score", "Fairness Score"]
    weights = [0.35, 0.35, 0.20, 0.10]
    palette = [COLORS["primary"], COLORS["red"], COLORS["green"], COLORS["amber"]]

    fig = go.Figure()
    for i, (cat, w, col) in enumerate(zip(categories, weights, palette)):
        attr = ["rate_score", "complaint_score", "safety_score", "fairness_score"][i]
        fig.add_trace(go.Bar(
            name=f"{cat} ({int(w*100)}%)",
            x=[s.institution_name for s in scores],
            y=[getattr(s, attr) * w for s in scores],
            marker_color=col,
            hovertemplate=f"<b>%{{x}}</b><br>{cat}: %{{customdata:.1f}}/100<extra></extra>",
            customdata=[getattr(s, attr) for s in scores],
        ))

    fig.update_layout(
        **PLOT_LAYOUT,
        title="Score Breakdown by Category",
        barmode="stack",
        xaxis_title="",
        yaxis_title="Weighted Score (0–100)",
        yaxis=dict(gridcolor="#374151", range=[0, 100]),
        xaxis=dict(gridcolor="#374151"),
        height=380,
    )
    return fig


def build_cu_vs_bank_comparison(credit_unions: List[CreditUnion], selected_banks: List[str]) -> go.Figure:
    from processing.aggregator import BANK_SAVINGS_RATES

    cu_data = [(cu.name, cu.savings_rate) for cu in credit_unions if cu.savings_rate is not None]
    bank_data = [(b, BANK_SAVINGS_RATES.get(b)) for b in selected_banks if BANK_SAVINGS_RATES.get(b) is not None]

    if not cu_data and not bank_data:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No comparison data available")

    fig = go.Figure()
    if cu_data:
        names, rates = zip(*cu_data)
        fig.add_trace(go.Bar(
            name="Credit Unions", x=list(names), y=list(rates),
            marker_color=COLORS["green"],
            hovertemplate="<b>%{x}</b><br>Savings APY: %{y:.2f}%<extra></extra>",
        ))
    if bank_data:
        names, rates = zip(*bank_data)
        fig.add_trace(go.Bar(
            name="Banks", x=list(names), y=list(rates),
            marker_color=COLORS["primary"],
            hovertemplate="<b>%{x}</b><br>Savings APY: %{y:.2f}%<extra></extra>",
        ))

    fig.update_layout(
        **PLOT_LAYOUT,
        title="Savings APY — Credit Unions vs Banks",
        yaxis_title="APY (%)",
        xaxis=dict(tickangle=-30),
        yaxis=dict(gridcolor="#374151"),
        barmode="group",
        height=420,
    )
    return fig


def build_safety_table(institutions: List[Institution], selected_banks: List[str]) -> pd.DataFrame:
    filtered = [i for i in institutions if not selected_banks or
                any(b.lower() in i.name.lower() for b in selected_banks)]
    rows = []
    for inst in filtered:
        tier1 = inst.tier1_capital_ratio
        if tier1 is not None:
            if tier1 >= 10: safety = "Well Capitalised"
            elif tier1 >= 8: safety = "Adequately Capitalised"
            elif tier1 >= 6: safety = "Minimum Required"
            else: safety = "Under-Capitalised"
        else:
            safety = "N/A"

        rows.append({
            "Institution": inst.name,
            "State": inst.state or "N/A",
            "Total Assets ($B)": f"${inst.asset_size / 1e6:.1f}B" if inst.asset_size else "N/A",
            "Tier 1 Capital Ratio": f"{tier1:.1f}%" if tier1 else "N/A",
            "Safety Status": safety,
            "Net Interest Margin": f"{inst.net_interest_margin:.2f}%" if inst.net_interest_margin else "N/A",
            "ROA": f"{inst.return_on_assets:.2f}%" if inst.return_on_assets else "N/A",
            "Branches": f"{inst.branch_count:,}" if inst.branch_count else "N/A",
            "FDIC Insured": "Yes" if inst.is_fdic_insured else "No",
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def build_score_table(scores: List[BankScore]) -> pd.DataFrame:
    rows = []
    for s in scores:
        rows.append({
            "Institution": s.institution_name,
            "Grade": s.grade,
            "Overall Score": f"{s.overall_score:.0f}/100",
            "Rate Score": f"{s.rate_score:.0f}/100",
            "Complaint Score": f"{s.complaint_score:.0f}/100",
            "Safety Score": f"{s.safety_score:.0f}/100",
            "Fairness Score": f"{s.fairness_score:.0f}/100",
            "Verdict": s.verdict or "",
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame()
