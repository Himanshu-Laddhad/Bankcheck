"""Rate intelligence charts and tables."""
from typing import List, Optional
import pandas as pd
import plotly.graph_objects as go
from models.schemas import RateRecord, FedRate
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CD_12MO_RATES, BANK_CC_RATES
from config import FEDERAL_FUNDS_RATE

COLORS = {
    "primary": "#4F8EF7",
    "green":   "#10B981",
    "red":     "#F43F5E",
    "amber":   "#F59E0B",
    "purple":  "#8B5CF6",
    "gray":    "#6B7280",
    "bg":      "#111827",
    "card":    "#1F2937",
    "text":    "#E5E7EB",
    "subtext": "#9CA3AF",
}

PLOT_LAYOUT = dict(
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor=COLORS["card"],
    font=dict(color=COLORS["text"], family="Inter, sans-serif"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
)


def _rate_color(rate: float, product: str, benchmark: float = 5.33) -> str:
    if product in ("savings", "cd_12mo", "cd_6mo"):
        if rate >= 4.0: return COLORS["green"]
        if rate >= 1.0: return COLORS["amber"]
        return COLORS["red"]
    else:
        if rate <= 15.0: return COLORS["green"]
        if rate <= 22.0: return COLORS["amber"]
        return COLORS["red"]


def build_savings_rate_bar(selected_banks: List[str], fed_rate: float = 5.33) -> go.Figure:
    data = []
    for bank in selected_banks:
        rate = BANK_SAVINGS_RATES.get(bank)
        if rate is not None:
            data.append({"Bank": bank, "APY (%)": rate, "Gap vs Fed": round(fed_rate - rate, 2)})

    if not data:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No savings rate data available")

    df = pd.DataFrame(data).sort_values("APY (%)", ascending=True)
    colors = [_rate_color(r, "savings") for r in df["APY (%)"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Bank"], x=df["APY (%)"],
        orientation="h",
        marker_color=colors,
        text=[f"{r:.2f}%" for r in df["APY (%)"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>APY: %{x:.2f}%<extra></extra>",
    ))
    fig.add_vline(x=fed_rate, line_dash="dash", line_color=COLORS["amber"],
                  annotation_text=f"Fed Rate {fed_rate:.2f}%", annotation_font_color=COLORS["amber"])
    fig.update_layout(
        **PLOT_LAYOUT,
        title="Savings Account APY vs Federal Funds Rate",
        xaxis_title="APY (%)",
        yaxis_title="",
        height=max(300, len(data) * 50 + 80),
        xaxis=dict(gridcolor="#374151", range=[0, max(fed_rate + 0.5, df["APY (%)"].max() + 0.5)]),
        yaxis=dict(gridcolor="#374151"),
    )
    return fig


def build_rate_comparison_table(selected_banks: List[str]) -> pd.DataFrame:
    rows = []
    for bank in selected_banks:
        savings = BANK_SAVINGS_RATES.get(bank)
        cd = BANK_CD_12MO_RATES.get(bank)
        cc = BANK_CC_RATES.get(bank)
        rows.append({
            "Institution": bank,
            "Savings APY": f"{savings:.2f}%" if savings is not None else "N/A",
            "12-Mo CD APY": f"{cd:.2f}%" if cd is not None else "N/A",
            "Credit Card APR": f"{cc:.2f}%" if cc is not None else "N/A",
            "Savings vs Fed Gap": f"-{5.33 - savings:.2f}%" if savings is not None else "N/A",
        })
    return pd.DataFrame(rows)


def build_cd_rate_bar(selected_banks: List[str]) -> go.Figure:
    data = []
    for bank in selected_banks:
        rate = BANK_CD_12MO_RATES.get(bank)
        if rate is not None:
            data.append({"Bank": bank, "APY (%)": rate})

    if not data:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No CD rate data available")

    df = pd.DataFrame(data).sort_values("APY (%)", ascending=True)
    colors = [_rate_color(r, "cd_12mo") for r in df["APY (%)"]]

    fig = go.Figure(go.Bar(
        y=df["Bank"], x=df["APY (%)"],
        orientation="h",
        marker_color=colors,
        text=[f"{r:.2f}%" for r in df["APY (%)"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>12-Mo CD APY: %{x:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title="12-Month CD Rates",
        xaxis_title="APY (%)",
        height=max(300, len(data) * 50 + 80),
        xaxis=dict(gridcolor="#374151"),
        yaxis=dict(gridcolor="#374151"),
    )
    return fig


def build_credit_card_apr_bar(selected_banks: List[str], fed_rate: float = 5.33) -> go.Figure:
    data = []
    for bank in selected_banks:
        rate = BANK_CC_RATES.get(bank)
        if rate is not None:
            data.append({"Bank": bank, "APR (%)": rate})

    if not data:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No credit card rate data available")

    df = pd.DataFrame(data).sort_values("APR (%)", ascending=False)
    colors = [_rate_color(r, "credit_card") for r in df["APR (%)"]]

    fig = go.Figure(go.Bar(
        y=df["Bank"], x=df["APR (%)"],
        orientation="h",
        marker_color=colors,
        text=[f"{r:.2f}%" for r in df["APR (%)"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Credit Card APR: %{x:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title="Credit Card APR — Lower is Better for Consumers",
        xaxis_title="APR (%)",
        height=max(300, len(data) * 50 + 80),
        xaxis=dict(gridcolor="#374151"),
        yaxis=dict(gridcolor="#374151"),
    )
    return fig


def build_rate_pass_through_chart(fed_rate: float = 5.33, selected_banks: list = None) -> go.Figure:
    all_banks = selected_banks if selected_banks else list(BANK_SAVINGS_RATES.keys())
    data = []
    for bank in all_banks:
        rate = BANK_SAVINGS_RATES[bank]
        gap = round(fed_rate - rate, 2)
        pct_passed = round((rate / fed_rate) * 100, 1) if fed_rate > 0 else 0
        data.append({"Bank": bank, "Savings APY": rate, "Gap to Fed": gap, "% Passed to Customer": pct_passed})

    df = pd.DataFrame(data).sort_values("% Passed to Customer", ascending=True)
    colors = [COLORS["green"] if p >= 70 else COLORS["amber"] if p >= 30 else COLORS["red"]
              for p in df["% Passed to Customer"]]

    fig = go.Figure(go.Bar(
        y=df["Bank"], x=df["% Passed to Customer"],
        orientation="h",
        marker_color=colors,
        text=[f"{p:.0f}%" for p in df["% Passed to Customer"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Passes %{x:.0f}% of Fed rate to customers<extra></extra>",
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title=f"Rate Pass-Through — % of Fed Rate ({fed_rate}%) Passed to Savers",
        xaxis_title="% of Fed Rate Passed to Customers",
        height=max(500, len(all_banks) * 40 + 80),
        xaxis=dict(gridcolor="#374151", range=[0, 110]),
        yaxis=dict(gridcolor="#374151"),
    )
    return fig
