"""Shared UI components for BankCheck dashboard."""
import streamlit as st
from models.schemas import BankScore, SourceHealth

GRADE_COLOR = {
    "A+": "#10B981", "A": "#10B981", "B": "#4F8EF7",
    "C": "#F59E0B", "D": "#F97316", "F": "#F43F5E", "N/A": "#6B7280",
}


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <div style="height:3px;background:linear-gradient(90deg,#4F8EF7,#8B5CF6,#10B981);border-radius:2px;margin-bottom:0.75rem;"></div>
        <h1 style="margin:0;font-size:1.75rem;font-weight:700;color:#E5E7EB;">{title}</h1>
        {f'<p style="margin:0.25rem 0 0;color:#9CA3AF;font-size:0.9rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, delta: str = "", delta_good: bool = True):
    delta_color = "#10B981" if delta_good else "#F43F5E"
    delta_html = f'<span style="font-size:0.8rem;color:{delta_color};">{delta}</span>' if delta else ""
    st.markdown(f"""
    <div style="background:#1F2937;border:1px solid #374151;border-radius:12px;padding:1rem 1.25rem;
                text-align:center;min-height:90px;display:flex;flex-direction:column;justify-content:center;">
        <div style="color:#9CA3AF;font-size:0.75rem;font-weight:600;text-transform:uppercase;
                    letter-spacing:0.05em;margin-bottom:0.4rem;">{label}</div>
        <div style="color:#E5E7EB;font-size:1.5rem;font-weight:700;line-height:1.2;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def score_card(score: BankScore):
    color = GRADE_COLOR.get(score.grade, "#6B7280")
    bar_pct = score.overall_score
    st.markdown(f"""
    <div style="background:#1F2937;border:1px solid #374151;border-radius:12px;
                padding:1.25rem;margin-bottom:0.75rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
            <span style="color:#E5E7EB;font-weight:600;font-size:1rem;">{score.institution_name}</span>
            <span style="background:{color}22;color:{color};font-weight:700;font-size:1.1rem;
                         padding:0.2rem 0.6rem;border-radius:6px;border:1px solid {color}44;">{score.grade}</span>
        </div>
        <div style="background:#374151;border-radius:4px;height:8px;margin-bottom:0.75rem;">
            <div style="background:{color};width:{bar_pct}%;height:100%;border-radius:4px;
                        transition:width 0.5s ease;"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;font-size:0.8rem;color:#9CA3AF;">
            <span>Rate: <b style="color:#E5E7EB;">{score.rate_score:.0f}/100</b></span>
            <span>Complaints: <b style="color:#E5E7EB;">{score.complaint_score:.0f}/100</b></span>
            <span>Safety: <b style="color:#E5E7EB;">{score.safety_score:.0f}/100</b></span>
            <span>Fairness: <b style="color:#E5E7EB;">{score.fairness_score:.0f}/100</b></span>
        </div>
        <div style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid #374151;
                    font-size:0.82rem;color:#9CA3AF;">{score.verdict or ""}</div>
    </div>
    """, unsafe_allow_html=True)


def alert_card(message: str, level: str = "info"):
    colors = {"info": "#4F8EF7", "warning": "#F59E0B", "error": "#F43F5E", "success": "#10B981"}
    icons  = {"info": "ℹ️", "warning": "⚠️", "error": "🔴", "success": "✅"}
    color = colors.get(level, colors["info"])
    icon  = icons.get(level, "ℹ️")
    st.markdown(f"""
    <div style="background:{color}15;border-left:3px solid {color};border-radius:0 8px 8px 0;
                padding:0.75rem 1rem;margin-bottom:0.5rem;font-size:0.88rem;color:#E5E7EB;">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)


def source_health_row(health_records: list):
    cols = st.columns(len(health_records))
    for col, h in zip(cols, health_records):
        color = "#10B981" if h.is_healthy else "#F43F5E"
        icon  = "●" if h.is_healthy else "○"
        label = "Live" if h.is_healthy else "Down"
        with col:
            st.markdown(f"""
            <div style="background:#1F2937;border:1px solid #374151;border-radius:8px;
                        padding:0.6rem;text-align:center;font-size:0.78rem;">
                <div style="color:{color};font-weight:700;">{icon} {h.source.upper()}</div>
                <div style="color:#9CA3AF;">{label} · {h.record_count} records</div>
            </div>
            """, unsafe_allow_html=True)


def section_divider(label: str = ""):
    if label:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.75rem;margin:1.5rem 0 1rem;">
            <div style="flex:1;height:1px;background:#374151;"></div>
            <span style="color:#6B7280;font-size:0.78rem;font-weight:600;
                         text-transform:uppercase;letter-spacing:0.1em;">{label}</span>
            <div style="flex:1;height:1px;background:#374151;"></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<hr style="border:none;border-top:1px solid #374151;margin:1.5rem 0;">', unsafe_allow_html=True)


def badge(text: str, color: str = "#4F8EF7"):
    st.markdown(f"""
    <span style="background:{color}22;color:{color};border:1px solid {color}44;
                 border-radius:12px;padding:0.2rem 0.6rem;font-size:0.75rem;font-weight:600;">
        {text}
    </span>
    """, unsafe_allow_html=True)
