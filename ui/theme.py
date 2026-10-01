"""Design tokens, CSS and shared chart helpers (light and dark).

Colour rules
  * ACCENT (blue) has exactly one meaning: "look here" (leader / selected bank).
  * WARN (orange) = watch, ALERT (red) = act. There is no green: blue/orange stays
    distinguishable for red-green colour blindness, and status also carries a symbol or label.
  * NEUTRAL (gray) = everything that is context. All pairs meet WCAG contrast (3:1 graphics, 4.5:1 text).
  * Gap-to-benchmark uses a diverging pair: blue = above, orange = below, gray axis = zero.

Chart-type rules
  * Ranking / one point in time ........ horizontal bar (ranked_bar)
  * Tight ranges, peer context ......... dot plot with truncated axis (dot_plot)
  * Parts of a whole ................... 100% stacked bar (stacked_share)
  * Two-metric relationship ............ labelled scatter (labelled_scatter)
  * Above / below a benchmark .......... diverging bar (diverging_bar)
  * Trend over time .................... line (trend_line)
"""
from __future__ import annotations
import streamlit as st

_LIGHT = dict(
    BG="#F6F8FB", PANEL="#FFFFFF", LINE="#DDE3EC", TEXT="#172033", MUTED="#556075", FAINT="#667289",
    ACCENT="#2563EB", WARN="#C96A00", WARN_TEXT="#B45309", ALERT="#DC2626", NEUTRAL="#7B879C",
    RAMP=["#1D4ED8", "#3B6FE0", "#6C93EA", "#9DB7F2", "#C7D6F8"],
)
_DARK = dict(
    BG="#0E1525", PANEL="#151E31", LINE="#2A3552", TEXT="#E6EAF2", MUTED="#A3AEC2", FAINT="#8F9BB2",
    ACCENT="#6AA0FF", WARN="#F5A524", WARN_TEXT="#F5A524", ALERT="#F87171", NEUTRAL="#6B7792",
    RAMP=["#6AA0FF", "#5183E0", "#3C68BE", "#2E5199", "#264278"],
)

# Active tokens (rebound by set_mode(); always read via `T.NAME` at call time)
MODE = "light"
BG = PANEL = LINE = TEXT = MUTED = FAINT = ACCENT = WARN = WARN_TEXT = ALERT = NEUTRAL = ""
RAMP: list[str] = []


def set_mode(mode: str = "light") -> str:
    """Rebind the active tokens. Charts and HTML snippets read them at call time."""
    global MODE
    MODE = "dark" if mode == "dark" else "light"
    globals().update(_DARK if MODE == "dark" else _LIGHT)
    return MODE


set_mode("light")


def inject_css() -> None:
    """Call once at the top of main.py. Mode comes from the sidebar toggle (session_state['dark_mode'])."""
    set_mode("dark" if st.session_state.get("dark_mode") else "light")
    dark_css = f"""
header[data-testid="stHeader"] {{ background:{BG}; }}
h1,h2,h3,h4,h5,h6,p,label,span,li,[data-testid="stMarkdownContainer"] {{ color:{TEXT}; }}
[data-baseweb="select"] > div, [data-baseweb="input"] > div, .stNumberInput input, .stTextInput input
    {{ background:{PANEL} !important; color:{TEXT} !important; border-color:{LINE} !important; }}
[data-baseweb="popover"] *, [data-baseweb="menu"] {{ background:{PANEL}; color:{TEXT}; }}
[data-testid="stDataFrame"] {{ filter:invert(1) hue-rotate(180deg); }}
[data-testid="stDownloadButton"] button {{ background:transparent; color:{TEXT}; border:1px solid {LINE}; }}
.stButton > button:hover, [data-testid="stDownloadButton"] button:hover {{ color:{ACCENT}; border-color:{ACCENT}; }}
[data-testid="stPills"] button, [data-testid="stSegmentedControl"] button {{ color:{TEXT}; }}
""" if MODE == "dark" else ""
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family:'Inter',sans-serif !important; }}
.stApp {{ background:{BG}; color:{TEXT}; }}
.block-container {{ padding-top:2rem; padding-bottom:3rem; max-width:1280px; }}

section[data-testid="stSidebar"] {{ background:{PANEL}; border-right:1px solid {LINE}; }}
.sb-label {{ color:{MUTED}; font-size:.7rem; font-weight:600; letter-spacing:.08em;
            text-transform:uppercase; margin:1rem 0 .35rem; }}

.stButton > button {{ background:transparent; color:{TEXT}; border:1px solid {LINE};
    border-radius:8px; font-weight:500; box-shadow:none; }}
.stButton > button:hover {{ border-color:{ACCENT}; color:{ACCENT}; }}

.stTabs [data-baseweb="tab-list"] {{ gap:1.5rem; border-bottom:1px solid {LINE}; background:transparent; }}
.stTabs [data-baseweb="tab"] {{ color:{MUTED}; font-weight:500; padding:.6rem 0; background:transparent; }}
.stTabs [aria-selected="true"] {{ color:{TEXT} !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background:{ACCENT}; }}

[data-testid="stDataFrame"] {{ border:1px solid {LINE}; border-radius:8px; }}

.h-title {{ color:{TEXT}; font-size:1.6rem; font-weight:700; margin:0; }}
.h-sub   {{ color:{MUTED}; font-size:.95rem; margin:.25rem 0 1.25rem; }}
.sec     {{ color:{TEXT}; font-size:1.05rem; font-weight:600; margin:2rem 0 .1rem; }}
.sec-sub {{ color:{MUTED}; font-size:.85rem; margin:0 0 .75rem; }}

.ns-label {{ color:{MUTED}; font-size:.78rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase; }}
.ns-value {{ color:{TEXT}; font-size:72px; font-weight:800; line-height:1.05; letter-spacing:-.02em; }}
.ns-unit  {{ font-size:28px; color:{MUTED}; font-weight:600; }}
.ns-note  {{ color:{MUTED}; font-size:.95rem; margin-top:.35rem; }}

.kpi {{ border-left:2px solid {LINE}; padding:.1rem 0 .1rem .9rem; }}
.kpi-label {{ color:{MUTED}; font-size:.72rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }}
.kpi-value {{ color:{TEXT}; font-size:28px; font-weight:700; line-height:1.15; font-variant-numeric:tabular-nums; }}
.kpi-note  {{ font-size:.8rem; margin-top:.1rem; }}

.exc {{ border-left:3px solid var(--c); background:{PANEL}; border-radius:0 8px 8px 0;
        padding:.65rem .9rem; margin-bottom:.5rem; color:{TEXT}; font-size:.9rem; }}
.exc b.tag {{ color:var(--t); font-size:.7rem; letter-spacing:.08em; margin-right:.5rem; }}
.exc .act {{ color:{MUTED}; font-size:.82rem; display:block; margin-top:.15rem; }}
.ok-line {{ color:{MUTED}; font-size:.9rem; }}

.footnote {{ color:{FAINT}; font-size:.75rem; margin-top:2.5rem; }}
{dark_css}
</style>
""", unsafe_allow_html=True)


# ── HTML snippets ─────────────────────────────────────────────────────────
def page_title(title: str, subtitle: str = "") -> None:
    st.markdown(f'<p class="h-title">{title}</p><p class="h-sub">{subtitle}</p>', unsafe_allow_html=True)


def section(title: str, insight: str = "") -> None:
    """Section heading + one-line insight (the 'subtitle states the takeaway' rule)."""
    st.markdown(f'<p class="sec">{title}</p><p class="sec-sub">{insight}</p>', unsafe_allow_html=True)


def north_star(label: str, value: str, unit: str, note: str) -> None:
    st.markdown(
        f'<div class="ns-label">{label}</div>'
        f'<div class="ns-value">{value}<span class="ns-unit"> {unit}</span></div>'
        f'<div class="ns-note">{note}</div>',
        unsafe_allow_html=True,
    )


def kpi(label: str, value: str, note: str = "", status: str = "neutral") -> None:
    """status: good (blue ▲) | warn (orange ●) | alert (red ▼) | neutral."""
    color = {"good": ACCENT, "warn": WARN_TEXT, "alert": ALERT, "neutral": MUTED}[status]
    sym   = {"good": "▲ ", "warn": "● ", "alert": "▼ ", "neutral": ""}[status]
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-note" style="color:{color}">{sym}{note}</div></div>',
        unsafe_allow_html=True,
    )


def exception(level: str, message: str, action: str = "") -> None:
    c = {"alert": ALERT, "warn": WARN, "info": ACCENT}[level]
    t = {"alert": ALERT, "warn": WARN_TEXT, "info": ACCENT}[level]
    tag = {"alert": "ACT NOW", "warn": "WATCH", "info": "NOTE"}[level]
    act = f'<span class="act">→ {action}</span>' if action else ""
    st.markdown(f'<div class="exc" style="--c:{c};--t:{t}"><b class="tag">{tag}</b>{message}{act}</div>',
                unsafe_allow_html=True)


def footnote(text: str) -> None:
    st.markdown(f'<p class="footnote">{text}</p>', unsafe_allow_html=True)


# ── Plotly helpers ────────────────────────────────────────────────────────
def base_layout(height: int = 320, title: str = "") -> dict:
    return dict(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="Inter, sans-serif", size=12),
        title=dict(text=title, font=dict(size=13, color=MUTED), x=0, xanchor="left"),
        margin=dict(l=0, r=40, t=36 if title else 8, b=8),
        showlegend=False,
        hoverlabel=dict(bgcolor=PANEL, bordercolor=LINE, font=dict(color=TEXT)),
    )


def show(fig) -> None:
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def _hex_rgba(h: str, a: float) -> str:
    h = h.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def _lum(h: str) -> float:
    h = h.lstrip("#")
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _on(bg: str) -> str:
    """Text colour (white or near-black) with the higher contrast on `bg`."""
    dark, light = "#0E1525", "#FFFFFF"
    cr = lambda a, b: (max(_lum(a), _lum(b)) + 0.05) / (min(_lum(a), _lum(b)) + 0.05)
    return dark if cr(bg, dark) >= cr(bg, light) else light


def ranked_bar(
    labels: list[str], values: list[float], *, fmt: str = "{:.2f}%",
    higher_is_better: bool = True, benchmark: float | None = None,
    benchmark_label: str = "", title: str = "", highlight: int = 1,
    axis_max: float | None = None,
):
    """Horizontal bars, best first. Top `highlight` bars are ACCENT, the rest NEUTRAL (one encoding only).
    The benchmark is a dotted reference line, never a second bar colour."""
    import plotly.graph_objects as go

    pairs = sorted(zip(labels, values), key=lambda p: p[1], reverse=higher_is_better)
    labels, values = [p[0] for p in pairs], [p[1] for p in pairs]
    colors = [ACCENT if i < highlight else NEUTRAL for i in range(len(values))]

    fig = go.Figure(go.Bar(
        y=labels, x=values, orientation="h", marker_color=colors,
        text=[fmt.format(v) for v in values], textposition="outside",
        textfont=dict(color=TEXT, size=12), cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
    ))
    if benchmark is not None:
        fig.add_vline(x=benchmark, line_dash="dot", line_color=MUTED, line_width=1,
                      annotation_text=benchmark_label, annotation_position="top",
                      annotation_font=dict(color=MUTED, size=11))
    top = axis_max or (max(max(values), benchmark or 0) * 1.18 if values else 1)
    fig.update_layout(
        **base_layout(max(160, 34 * len(labels) + 50), title),
        xaxis=dict(visible=False, range=[0, top]),
        yaxis=dict(autorange="reversed", showgrid=False, linecolor=LINE, tickfont=dict(color=TEXT, size=12)),
        bargap=0.35,
    )
    return fig


def dot_plot(
    peers: dict[str, float], selected: list[str], *, fmt: str = "{:.1f}%", title: str = "",
    higher_is_better: bool = True, benchmark: float | None = None, benchmark_label: str = "",
):
    """One row per selected bank. Gray dots = every tracked bank (peer context), blue dot = the bank.
    The axis is truncated on purpose (tight ranges), so it is labelled as such."""
    import plotly.graph_objects as go

    rows = sorted([b for b in selected if b in peers], key=lambda b: peers[b], reverse=higher_is_better)
    fig = go.Figure()
    if not rows:
        fig.update_layout(**base_layout(120, title))
        return fig
    px_, py_, pt_ = [], [], []
    for b in rows:
        for name, v in peers.items():
            if name not in selected:
                px_.append(v); py_.append(b); pt_.append(name)
    fig.add_trace(go.Scatter(
        x=px_, y=py_, mode="markers", marker=dict(size=7, color=_hex_rgba(NEUTRAL, 0.55)),
        customdata=pt_, hovertemplate="%{customdata}: %{x:.1f}<extra>peer</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[peers[b] for b in rows], y=rows, mode="markers+text",
        marker=dict(size=14, color=ACCENT, line=dict(color=PANEL, width=2)),
        text=[fmt.format(peers[b]) for b in rows], textposition="middle right",
        textfont=dict(color=TEXT, size=12), cliponaxis=False,
        hovertemplate="<b>%{y}</b>: %{text}<extra></extra>",
    ))
    if benchmark is not None:
        fig.add_vline(x=benchmark, line_dash="dot", line_color=MUTED, line_width=1,
                      annotation_text=benchmark_label, annotation_position="top",
                      annotation_font=dict(color=MUTED, size=11))
    vals = list(peers.values())
    pad = (max(vals) - min(vals)) * 0.12 or 1
    fig.update_layout(
        **base_layout(max(170, 42 * len(rows) + 70), title),
        xaxis=dict(range=[min(vals) - pad, max(vals) + pad * 2.2], showgrid=True, gridcolor=LINE,
                   zeroline=False, tickfont=dict(color=MUTED, size=11), title=None),
        yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(color=TEXT, size=12)),
    )
    fig.add_annotation(xref="paper", yref="paper", x=1, y=-0.02, yanchor="top", xanchor="right", showarrow=False,
                       text="Axis does not start at zero · gray = all tracked banks",
                       font=dict(color=FAINT, size=10))
    fig.update_layout(margin=dict(l=0, r=40, t=36 if title else 8, b=26))
    return fig


def stacked_share(
    shares: dict[str, dict[str, float]], *, title: str = "", max_parts: int = 5, order: list[str] | None = None,
):
    """100% horizontal stacked bar per row. Single-hue ramp (largest part darkest), small parts grouped as Other."""
    import plotly.graph_objects as go

    totals: dict[str, float] = {}
    for parts in shares.values():
        for k, v in parts.items():
            totals[k] = totals.get(k, 0) + v
    keep = [k for k, _ in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:max_parts]]
    rows = order or list(shares)
    fig = go.Figure()
    cats = keep + (["Other"] if len(totals) > max_parts else [])
    for i, cat in enumerate(cats):
        vals = []
        for r in rows:
            parts = shares[r]
            tot = sum(parts.values()) or 1
            v = parts.get(cat, 0) if cat != "Other" else sum(x for k, x in parts.items() if k not in keep)
            vals.append(v / tot * 100)
        color = RAMP[i] if i < len(RAMP) else NEUTRAL
        fig.add_trace(go.Bar(
            y=rows, x=vals, name=cat, orientation="h", marker_color=color,
            text=[f"{v:.0f}%" if v >= 7 else "" for v in vals], textposition="inside", insidetextanchor="middle",
            textfont=dict(color=_on(color), size=11),
            hovertemplate="<b>%{y}</b><br>" + cat + ": %{x:.1f}%<extra></extra>",
        ))
    fig.update_layout(
        **{**base_layout(max(150, 48 * len(rows) + 90), title), "showlegend": True},
        barmode="stack", bargap=0.35,
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, font=dict(size=11, color=MUTED)),
        xaxis=dict(visible=False, range=[0, 100]),
        yaxis=dict(autorange="reversed", tickfont=dict(color=TEXT, size=12)),
    )
    fig.update_layout(margin=dict(l=0, r=10, t=56 if title else 30, b=8))
    return fig


def labelled_scatter(
    points: dict[str, tuple[float, float]], selected: list[str], *, x_title: str, y_title: str,
    x_fmt: str = "{:.2f}", y_fmt: str = "{:.2f}", x_higher_better: bool = True, y_higher_better: bool = True,
    title: str = "", best_label: str = "Best zone",
):
    """Every tracked bank is a gray dot; selected banks are blue and labelled. Axes are oriented so that
    'better' is always top-right, with dotted median lines for context."""
    import plotly.graph_objects as go
    import statistics as st_

    fig = go.Figure()
    others = {k: v for k, v in points.items() if k not in selected}
    chosen = {k: v for k, v in points.items() if k in selected}
    fig.add_trace(go.Scatter(
        x=[v[0] for v in others.values()], y=[v[1] for v in others.values()], mode="markers",
        marker=dict(size=8, color=_hex_rgba(NEUTRAL, 0.6)), customdata=list(others),
        hovertemplate="<b>%{customdata}</b><br>x %{x:.2f} · y %{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[v[0] for v in chosen.values()], y=[v[1] for v in chosen.values()], mode="markers+text",
        text=list(chosen), textposition="top center", textfont=dict(color=TEXT, size=11),
        marker=dict(size=14, color=ACCENT, line=dict(color=PANEL, width=2)),
        hovertemplate="<b>%{text}</b><br>x %{x:.2f} · y %{y:.2f}<extra></extra>",
    ))
    if len(points) >= 3:
        fig.add_vline(x=statistics_median([v[0] for v in points.values()]), line_dash="dot",
                      line_color=LINE, line_width=1)
        fig.add_hline(y=statistics_median([v[1] for v in points.values()]), line_dash="dot",
                      line_color=LINE, line_width=1)
    fig.update_layout(
        **base_layout(380, title),
        xaxis=dict(title=dict(text=x_title + (" →" if x_higher_better else " ←"), font=dict(color=MUTED, size=11)),
                   autorange=True if x_higher_better else "reversed", showgrid=False, zeroline=False,
                   tickfont=dict(color=MUTED, size=11), linecolor=LINE),
        yaxis=dict(title=dict(text=y_title + (" ↑" if y_higher_better else " ↓ (lower is better)"),
                              font=dict(color=MUTED, size=11)),
                   autorange=True if y_higher_better else "reversed", showgrid=False, zeroline=False,
                   tickfont=dict(color=MUTED, size=11), linecolor=LINE),
    )
    fig.add_annotation(xref="paper", yref="paper", x=0.99, y=0.99, xanchor="right", yanchor="top",
                       text=f"{best_label} ↗", showarrow=False, font=dict(color=ACCENT, size=11))
    return fig


def statistics_median(vals: list[float]) -> float:
    import statistics
    return statistics.median(vals)


def diverging_bar(labels: list[str], gaps: list[float], *, title: str = "", unit: str = " pts"):
    """Bars around zero: blue = above the benchmark, orange = below. Sorted high to low."""
    import plotly.graph_objects as go

    pairs = sorted(zip(labels, gaps), key=lambda p: p[1], reverse=True)
    labels, gaps = [p[0] for p in pairs], [p[1] for p in pairs]
    fig = go.Figure(go.Bar(
        y=labels, x=gaps, orientation="h",
        marker_color=[ACCENT if g >= 0 else WARN for g in gaps],
        text=[f"{g:+.2f}{unit}" for g in gaps], textposition="outside", cliponaxis=False,
        textfont=dict(color=TEXT, size=12),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
    ))
    span = max(abs(g) for g in gaps) if gaps else 1
    fig.add_vline(x=0, line_color=MUTED, line_width=1)
    fig.update_layout(
        **base_layout(max(160, 34 * len(labels) + 50), title),
        xaxis=dict(visible=False, range=[-span * 1.45, span * 1.45]),
        yaxis=dict(autorange="reversed", showgrid=False, tickfont=dict(color=TEXT, size=12)),
        bargap=0.35,
    )
    return fig


def trend_line(
    dates: list[str], values: list[float], *, name: str, title: str = "", unit: str = "%",
    reference: float | None = None, reference_label: str = "", annotate_changes: bool = True,
):
    """Single line, direct end-label, annotated step changes, optional dotted reference."""
    import plotly.graph_objects as go

    fig = go.Figure(go.Scatter(
        x=dates, y=values, mode="lines", line=dict(color=ACCENT, width=3, shape="hv"),
        hovertemplate="%{x}: %{y:.2f}" + unit + "<extra>" + name + "</extra>",
    ))
    if values:
        fig.add_trace(go.Scatter(
            x=[dates[-1]], y=[values[-1]], mode="markers+text", marker=dict(size=9, color=ACCENT),
            text=[f"{values[-1]:.2f}{unit}"], textposition="top left", textfont=dict(color=TEXT, size=12),
            hoverinfo="skip",
        ))
    if annotate_changes and len(values) > 2:
        biggest = max(range(1, len(values)), key=lambda i: abs(values[i] - values[i - 1]))
        d = values[biggest] - values[biggest - 1]
        if abs(d) >= 0.2:
            fig.add_annotation(x=dates[biggest], y=values[biggest], ax=0, ay=-34, showarrow=True,
                               arrowcolor=MUTED, arrowwidth=1, arrowhead=0,
                               text=f"{'Cut' if d < 0 else 'Hike'} {abs(d):.2f} pts",
                               font=dict(color=TEXT, size=11), bgcolor=PANEL, bordercolor=LINE)
    if reference is not None:
        fig.add_hline(y=reference, line_dash="dot", line_color=MUTED, line_width=1,
                      annotation_text=reference_label, annotation_position="bottom right",
                      annotation_font=dict(color=MUTED, size=11))
    lo = min(values + ([reference] if reference is not None else [])) if values else 0
    hi = max(values + ([reference] if reference is not None else [])) if values else 1
    pad = (hi - lo) * 0.15 or 0.5
    fig.update_layout(
        **base_layout(300, title),
        xaxis=dict(showgrid=False, linecolor=LINE, tickfont=dict(color=MUTED, size=11)),
        yaxis=dict(range=[max(0, lo - pad), hi + pad], showgrid=True, gridcolor=LINE, zeroline=False,
                   ticksuffix=unit, tickfont=dict(color=MUTED, size=11)),
    )
    return fig
