"""Complaint intelligence charts and tables."""
from typing import List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from models.schemas import Complaint, ComplaintSummary
from collections import defaultdict

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

PRODUCT_LABELS = {
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


def _clean_product(product: str) -> str:
    return PRODUCT_LABELS.get(product, product[:30] if product else "Other")


def build_complaint_heatmap(complaints: List[Complaint], selected_banks: List[str]) -> go.Figure:
    if not complaints:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No complaint data available")

    bank_product: dict = defaultdict(lambda: defaultdict(int))
    for c in complaints:
        bank = c.institution_name
        if not selected_banks or any(b.lower() in bank.lower() for b in selected_banks):
            prod = _clean_product(c.product)
            bank_product[bank][prod] += 1

    if not bank_product:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No data for selected banks")

    banks = sorted(bank_product.keys())
    products = sorted({p for b in bank_product.values() for p in b})
    z = [[bank_product[b].get(p, 0) for p in products] for b in banks]

    fig = go.Figure(go.Heatmap(
        z=z, x=products, y=banks,
        colorscale=[[0, "#111827"], [0.3, "#F59E0B"], [1, "#F43F5E"]],
        hovertemplate="<b>%{y}</b><br>%{x}<br>Complaints: %{z:,}<extra></extra>",
        colorbar=dict(title="Complaints", tickfont=dict(color=COLORS["text"])),
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title="Complaint Volume by Bank × Product",
        xaxis=dict(tickangle=-30),
        height=max(350, len(banks) * 50 + 100),
    )
    return fig


def build_resolution_rate_bar(summaries: List[ComplaintSummary], selected_banks: List[str]) -> go.Figure:
    filtered = [s for s in summaries if not selected_banks or
                any(b.lower() in s.institution_name.lower() for b in selected_banks)]

    if not filtered:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No resolution data available")

    agg: dict = defaultdict(lambda: {"relief": 0, "total": 0, "timely": 0, "count": 0})
    for s in filtered:
        b = s.institution_name
        agg[b]["relief"] += s.relief_rate
        agg[b]["timely"] += s.timely_response_rate
        agg[b]["count"] += 1

    rows = []
    for bank, vals in agg.items():
        n = vals["count"]
        rows.append({
            "Bank": bank,
            "Relief Rate (%)": round(vals["relief"] / n, 1),
            "Timely Response (%)": round(vals["timely"] / n, 1),
        })

    df = pd.DataFrame(rows).sort_values("Relief Rate (%)", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Bank"], x=df["Relief Rate (%)"],
        name="Resolved with Relief", orientation="h",
        marker_color=COLORS["green"],
        hovertemplate="<b>%{y}</b><br>Relief Rate: %{x:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=df["Bank"], x=df["Timely Response (%)"],
        name="Timely Response", orientation="h",
        marker_color=COLORS["primary"],
        hovertemplate="<b>%{y}</b><br>Timely: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title="Complaint Resolution Rate — Higher is Better for Consumers",
        barmode="group",
        xaxis_title="Percentage (%)",
        height=max(350, len(rows) * 60 + 80),
        xaxis=dict(gridcolor="#374151"),
        yaxis=dict(gridcolor="#374151"),
    )
    return fig


def build_complaint_trend(complaints: List[Complaint], selected_banks: List[str]) -> go.Figure:
    if not complaints:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No trend data available")

    monthly: dict = defaultdict(lambda: defaultdict(int))
    for c in complaints:
        if not c.submitted_date:
            continue
        bank = c.institution_name
        if selected_banks and not any(b.lower() in bank.lower() for b in selected_banks):
            continue
        try:
            month = c.submitted_date[:7]  # YYYY-MM
            monthly[bank][month] += 1
        except Exception:
            continue

    if not monthly:
        return go.Figure().update_layout(**PLOT_LAYOUT, title="No trend data for selection")

    fig = go.Figure()
    palette = [COLORS["primary"], COLORS["red"], COLORS["green"], COLORS["amber"], COLORS["purple"]]
    for i, (bank, months) in enumerate(monthly.items()):
        sorted_months = sorted(months.items())
        fig.add_trace(go.Scatter(
            x=[m[0] for m in sorted_months],
            y=[m[1] for m in sorted_months],
            name=bank,
            mode="lines+markers",
            line=dict(color=palette[i % len(palette)], width=2),
            hovertemplate=f"<b>{bank}</b><br>Month: %{{x}}<br>Complaints: %{{y}}<extra></extra>",
        ))

    fig.update_layout(
        **PLOT_LAYOUT,
        title="Monthly Complaint Trend",
        xaxis_title="Month",
        yaxis_title="Complaints",
        xaxis=dict(gridcolor="#374151"),
        yaxis=dict(gridcolor="#374151"),
        height=380,
    )
    return fig


def build_complaint_summary_table(summaries: List[ComplaintSummary], selected_banks: List[str]) -> pd.DataFrame:
    filtered = [s for s in summaries if not selected_banks or
                any(b.lower() in s.institution_name.lower() for b in selected_banks)]
    rows = []
    for s in filtered:
        rows.append({
            "Institution": s.institution_name,
            "Product": _clean_product(s.product),
            "Total Complaints": s.total_complaints,
            "Relief Rate": f"{s.relief_rate:.1f}%",
            "Timely Response": f"{s.timely_response_rate:.1f}%",
            "Top Issue": s.top_issues[0] if s.top_issues else "N/A",
        })
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Institution", "Product", "Total Complaints", "Relief Rate", "Timely Response", "Top Issue"])
    return df.sort_values("Total Complaints", ascending=False) if not df.empty else df
