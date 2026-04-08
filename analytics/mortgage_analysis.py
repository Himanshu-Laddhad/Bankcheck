"""Mortgage & lending intelligence charts."""
from typing import List
import pandas as pd
import plotly.graph_objects as go
from models.schemas import MortgageSummary

COLORS = {
    "primary": "#4F8EF7", "green": "#10B981", "red": "#F43F5E",
    "amber": "#F59E0B", "purple": "#8B5CF6", "bg": "#111827",
    "card": "#1F2937", "text": "#E5E7EB",
}
PLOT_LAYOUT = dict(
    paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["card"],
    font=dict(color=COLORS["text"], family="Inter, sans-serif"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def build_approval_rate_scatter(summaries: List[MortgageSummary]) -> go.Figure:
    if not summaries:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No mortgage data available")

    df = pd.DataFrame([{
        "Institution": s.institution_name,
        "Approval Rate (%)": s.approval_rate,
        "Avg Interest Rate (%)": s.avg_interest_rate or 0,
        "Applications": s.total_applications,
    } for s in summaries if s.total_applications > 10])

    if df.empty:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="Insufficient mortgage data")

    colors = [COLORS["green"] if r >= 70 else COLORS["amber"] if r >= 50 else COLORS["red"]
              for r in df["Approval Rate (%)"]]

    fig = go.Figure(go.Scatter(
        x=df["Approval Rate (%)"],
        y=df["Avg Interest Rate (%)"],
        mode="markers+text",
        text=df["Institution"],
        textposition="top center",
        marker=dict(
            size=[max(10, min(40, a / 100)) for a in df["Applications"]],
            color=colors,
            opacity=0.85,
            line=dict(color="#374151", width=1),
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Approval Rate: %{x:.1f}%<br>"
            "Avg Rate: %{y:.2f}%<extra></extra>"
        ),
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title="Mortgage Lenders — Approval Rate vs Interest Rate Offered",
        xaxis_title="Approval Rate (%) — Higher is Better",
        yaxis_title="Avg Interest Rate (%) — Lower is Better",
        xaxis=dict(gridcolor="#374151"),
        yaxis=dict(gridcolor="#374151"),
        height=450,
    )
    return fig


def build_denial_reasons_bar(summaries: List[MortgageSummary], selected_banks: List[str]) -> go.Figure:
    filtered = [s for s in summaries if not selected_banks or
                any(b.lower() in s.institution_name.lower() for b in selected_banks)]

    if not filtered or all(not s.denial_reasons for s in filtered):
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No denial reason data available")

    all_reasons: dict = {}
    for s in filtered:
        for reason, count in s.denial_reasons.items():
            all_reasons[reason] = all_reasons.get(reason, 0) + count

    df = pd.DataFrame(list(all_reasons.items()), columns=["Reason", "Count"])
    df = df.sort_values("Count", ascending=True)

    fig = go.Figure(go.Bar(
        y=df["Reason"], x=df["Count"],
        orientation="h",
        marker_color=COLORS["red"],
        hovertemplate="%{y}<br>Count: %{x:,}<extra></extra>",
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title="Top Mortgage Denial Reasons",
        xaxis_title="Number of Denials",
        height=max(300, len(df) * 50 + 80),
        xaxis=dict(gridcolor="#374151"),
        yaxis=dict(gridcolor="#374151"),
    )
    return fig


def build_approval_rate_bar(summaries: List[MortgageSummary], selected_banks: List[str]) -> go.Figure:
    filtered = [s for s in summaries if not selected_banks or
                any(b.lower() in s.institution_name.lower() for b in selected_banks)]

    if not filtered:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No data for selected banks")

    df = pd.DataFrame([{"Institution": s.institution_name, "Approval Rate (%)": s.approval_rate}
                       for s in filtered]).sort_values("Approval Rate (%)", ascending=True)

    colors = [COLORS["green"] if r >= 70 else COLORS["amber"] if r >= 50 else COLORS["red"]
              for r in df["Approval Rate (%)"]]

    fig = go.Figure(go.Bar(
        y=df["Institution"], x=df["Approval Rate (%)"],
        orientation="h", marker_color=colors,
        text=[f"{r:.1f}%" for r in df["Approval Rate (%)"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Approval Rate: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title="Mortgage Approval Rates by Lender",
        xaxis_title="Approval Rate (%)",
        xaxis=dict(gridcolor="#374151", range=[0, 110]),
        yaxis=dict(gridcolor="#374151"),
        height=max(300, len(df) * 50 + 80),
    )
    return fig


def build_mortgage_table(summaries: List[MortgageSummary]) -> pd.DataFrame:
    rows = []
    for s in summaries:
        rows.append({
            "Institution": s.institution_name,
            "Approval Rate": f"{s.approval_rate:.1f}%",
            "Avg Rate Offered": f"{s.avg_interest_rate:.2f}%" if s.avg_interest_rate else "N/A",
            "Total Applications": f"{s.total_applications:,}",
            "Top Denial Reason": max(s.denial_reasons, key=s.denial_reasons.get) if s.denial_reasons else "N/A",  # empty dict is falsy, safe
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame()
