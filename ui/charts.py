"""Enhanced chart components with animations and interactivity."""
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
import pandas as pd


# ── Chart Theme ───────────────────────────────────────────────────────────
CHART_THEME = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font': {'color': '#E5E7EB', 'family': 'Inter, sans-serif'},
    'title': {'font': {'size': 18, 'color': '#E5E7EB'}},
    'xaxis': {
        'gridcolor': '#374151',
        'linecolor': '#374151',
        'zerolinecolor': '#374151',
    },
    'yaxis': {
        'gridcolor': '#374151',
        'linecolor': '#374151',
        'zerolinecolor': '#374151',
    },
}

COLOR_SCALE = [
    '#10B981',  # Green
    '#6366F1',  # Purple
    '#F59E0B',  # Orange
    '#EF4444',  # Red
    '#8B5CF6',  # Violet
    '#3B82F6',  # Blue
]


def animated_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color_col: str = None,
    sort_by: str = None,
    show_values: bool = True,
) -> go.Figure:
    """Create an animated bar chart with smooth transitions."""
    
    if sort_by:
        data = data.sort_values(by=sort_by, ascending=False)
    
    fig = px.bar(
        data,
        x=x,
        y=y,
        title=title,
        color=color_col,
        color_discrete_sequence=COLOR_SCALE,
        text=y if show_values else None,
    )
    
    fig.update_traces(
        texttemplate='%{text:.2f}',
        textposition='outside',
        marker_line_width=0,
        hovertemplate='<b>%{x}</b><br>%{y:.2f}<extra></extra>',
    )
    
    fig.update_layout(
        **CHART_THEME,
        height=500,
        showlegend=False,
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        hoverlabel=dict(
            bgcolor="#1F2937",
            font_size=13,
            font_family="Inter",
        ),
        margin=dict(t=60, b=80, l=60, r=20),
    )
    
    return fig


def interactive_line_chart(
    data: pd.DataFrame,
    x: str,
    y_columns: List[str],
    title: str,
    labels: Dict[str, str] = None,
) -> go.Figure:
    """Create an interactive line chart with range selector."""
    
    fig = go.Figure()
    
    for i, col in enumerate(y_columns):
        fig.add_trace(go.Scatter(
            x=data[x],
            y=data[col],
            name=labels.get(col, col) if labels else col,
            mode='lines+markers',
            line=dict(color=COLOR_SCALE[i % len(COLOR_SCALE)], width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{y:.2f}%</b><br>%{x}<extra></extra>',
        ))
    
    fig.update_layout(
        **CHART_THEME,
        title=title,
        height=450,
        hovermode='x unified',
        xaxis=dict(
            rangeslider=dict(visible=True, bgcolor='#1F2937'),
            rangeselector=dict(
                buttons=[
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ],
                bgcolor='#374151',
                activecolor='#6366F1',
                font=dict(color='#E5E7EB'),
            ),
        ),
        margin=dict(t=60, b=100, l=60, r=20),
    )
    
    return fig


def bubble_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    size: str,
    color: str,
    hover_name: str,
    title: str,
) -> go.Figure:
    """Create an animated bubble chart for bank comparison."""
    
    fig = px.scatter(
        data,
        x=x,
        y=y,
        size=size,
        color=color,
        hover_name=hover_name,
        color_continuous_scale='Viridis',
        size_max=60,
        title=title,
    )
    
    fig.update_traces(
        marker=dict(
            line=dict(width=2, color='#E5E7EB'),
            opacity=0.8,
        ),
        hovertemplate='<b>%{hovertext}</b><br>' +
                      f'{x}: %{{x:.2f}}<br>' +
                      f'{y}: %{{y:.2f}}<extra></extra>',
    )
    
    fig.update_layout(
        **CHART_THEME,
        height=500,
        margin=dict(t=60, b=60, l=60, r=60),
    )
    
    return fig


def radar_chart(
    categories: List[str],
    values_dict: Dict[str, List[float]],
    title: str,
) -> go.Figure:
    """Create a radar chart for multi-dimensional comparison."""
    
    fig = go.Figure()
    
    for i, (name, values) in enumerate(values_dict.items()):
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=name,
            line_color=COLOR_SCALE[i % len(COLOR_SCALE)],
            fillcolor=COLOR_SCALE[i % len(COLOR_SCALE)],
            opacity=0.4,
            hovertemplate='<b>%{theta}</b><br>Score: %{r:.0f}<extra></extra>',
        ))
    
    fig.update_layout(
        **CHART_THEME,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='#374151',
                linecolor='#374151',
            ),
            angularaxis=dict(
                gridcolor='#374151',
                linecolor='#374151',
            ),
            bgcolor='rgba(0,0,0,0)',
        ),
        title=title,
        height=500,
        showlegend=True,
        legend=dict(
            bgcolor='#1F2937',
            bordercolor='#374151',
            borderwidth=1,
        ),
        margin=dict(t=80, b=60, l=60, r=60),
    )
    
    return fig


def heatmap_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    values: str,
    title: str,
    color_scale: str = 'RdYlGn',
) -> go.Figure:
    """Create an interactive heatmap."""
    
    pivot_data = data.pivot(index=y, columns=x, values=values)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale=color_scale,
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>%{x}<br>Value: %{z:.2f}<extra></extra>',
        colorbar=dict(
            title="Value",
            titleside="right",
            tickfont=dict(color='#E5E7EB'),
            titlefont=dict(color='#E5E7EB'),
        ),
    ))
    
    fig.update_layout(
        **CHART_THEME,
        title=title,
        height=500,
        xaxis=dict(side='bottom'),
        margin=dict(t=60, b=100, l=120, r=60),
    )
    
    return fig


def comparison_bar_with_benchmark(
    data: pd.DataFrame,
    institutions: str,
    values: str,
    benchmark: float,
    benchmark_label: str,
    title: str,
    value_format: str = '%.2f%%',
) -> go.Figure:
    """Bar chart with benchmark line overlay."""
    
    fig = go.Figure()
    
    # Add bars
    colors = [COLOR_SCALE[0] if v >= benchmark else '#EF4444' 
              for v in data[values]]
    
    fig.add_trace(go.Bar(
        x=data[institutions],
        y=data[values],
        marker_color=colors,
        text=data[values],
        texttemplate=value_format,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>%{y:.2f}%<extra></extra>',
        name='Bank Rate',
    ))
    
    # Add benchmark line
    fig.add_hline(
        y=benchmark,
        line_dash="dash",
        line_color="#F59E0B",
        line_width=3,
        annotation_text=benchmark_label,
        annotation_position="right",
        annotation_font=dict(size=12, color='#F59E0B'),
    )
    
    fig.update_layout(
        **CHART_THEME,
        title=title,
        height=500,
        showlegend=False,
        yaxis_title="Rate (%)",
        margin=dict(t=60, b=100, l=60, r=20),
    )
    
    return fig


def sparkline_chart(values: List[float], color: str = '#10B981') -> go.Figure:
    """Create a small sparkline chart for inline metrics."""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=values,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'{color}33',
        hovertemplate='%{y:.2f}<extra></extra>',
    ))
    
    fig.update_layout(
        showlegend=False,
        height=60,
        margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x',
    )
    
    return fig


def gauge_chart(value: float, title: str, max_value: float = 100) -> go.Figure:
    """Create a gauge chart for single metric display."""
    
    # Determine color based on value
    if value >= 80:
        color = '#10B981'
    elif value >= 60:
        color = '#F59E0B'
    else:
        color = '#EF4444'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#E5E7EB'}},
        number={'suffix': '%', 'font': {'size': 32, 'color': '#E5E7EB'}},
        gauge={
            'axis': {'range': [None, max_value], 'tickcolor': '#E5E7EB'},
            'bar': {'color': color},
            'bgcolor': '#1F2937',
            'borderwidth': 2,
            'bordercolor': '#374151',
            'steps': [
                {'range': [0, 50], 'color': '#37415133'},
                {'range': [50, 80], 'color': '#37415166'},
                {'range': [80, 100], 'color': '#37415199'},
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        **CHART_THEME,
        height=300,
        margin=dict(t=40, b=20, l=20, r=20),
    )
    
    return fig


def funnel_chart(
    stages: List[str],
    values: List[int],
    title: str,
) -> go.Figure:
    """Create a funnel chart for process visualization."""
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(
            color=COLOR_SCALE[:len(stages)],
            line=dict(width=2, color='#E5E7EB')
        ),
        connector=dict(line=dict(color='#6B7280', dash='dot', width=3)),
        hovertemplate='<b>%{y}</b><br>Count: %{x:,}<extra></extra>',
    ))
    
    fig.update_layout(
        **CHART_THEME,
        title=title,
        height=450,
        margin=dict(t=60, b=40, l=20, r=20),
    )
    
    return fig
