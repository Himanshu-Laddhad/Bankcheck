"""Interactive engagement components for BankCheck dashboard."""
import streamlit as st
from typing import Dict, List, Optional
from models.schemas import PipelineResult, BankScore
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CC_RATES
from config import FEDERAL_FUNDS_RATE


# ── Color Palette ──────────────────────────────────────────────────────────
COLORS = {
    'positive': '#10B981',
    'negative': '#EF4444',
    'action': '#6366F1',
    'highlight': '#F59E0B',
    'neutral': '#6B7280',
    'accent': '#8B5CF6',
}


# ── Hero Section with Interactive Bank Picker ─────────────────────────────
def hero_section():
    """Engaging hero section with quick bank finder."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px; padding: 2.5rem 2rem; text-align: center;
                margin-bottom: 2rem; box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);">
        <h1 style="color: white; font-size: 2.5rem; margin: 0 0 0.5rem 0; font-weight: 800;">
            Find Your Perfect Bank in 30 Seconds
        </h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0 0 1.5rem 0;">
            Compare rates, safety, and customer satisfaction across major US banks
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick pick cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 Best Savings\nHighest APY", key="quick_savings", width="stretch"):
            st.session_state.quick_pick = "savings"
    
    with col2:
        if st.button("🏠 Best Mortgage\nTop Approval Rate", key="quick_mortgage", width="stretch"):
            st.session_state.quick_pick = "mortgage"
    
    with col3:
        if st.button("💳 Best Credit Card\nLowest APR", key="quick_card", width="stretch"):
            st.session_state.quick_pick = "credit_card"


# ── Quick Picks Display ───────────────────────────────────────────────────
def show_quick_picks(result: PipelineResult):
    """Show top 3 banks based on user's quick pick selection."""
    if 'quick_pick' not in st.session_state:
        return
    
    pick_type = st.session_state.quick_pick
    
    st.markdown(f"""
    <div style="margin: 2rem 0 1rem 0;">
        <h2 style="color: #E5E7EB; font-size: 1.5rem; font-weight: 700;">
            🏆 Top Picks for {pick_type.replace('_', ' ').title()}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    if pick_type == "savings":
        # Sort by savings APY
        sorted_banks = sorted(
            BANK_SAVINGS_RATES.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        cols = st.columns(3)
        for i, (bank, rate) in enumerate(sorted_banks):
            with cols[i]:
                medal = ["🥇", "🥈", "🥉"][i]
                vs_avg = rate - 0.64
                _quick_pick_card(
                    medal=medal,
                    bank=bank,
                    rate=f"{rate:.2f}% APY",
                    subtitle=f"+{vs_avg:.2f}% vs national avg",
                    color=COLORS['positive']
                )
    
    elif pick_type == "credit_card":
        # Sort by lowest credit card APR
        sorted_banks = sorted(
            [(k, v) for k, v in BANK_CC_RATES.items() if v is not None],
            key=lambda x: x[1]
        )[:3]
        
        cols = st.columns(3)
        for i, (bank, rate) in enumerate(sorted_banks):
            with cols[i]:
                medal = ["🥇", "🥈", "🥉"][i]
                vs_avg = 21.47 - rate
                _quick_pick_card(
                    medal=medal,
                    bank=bank,
                    rate=f"{rate:.2f}% APR",
                    subtitle=f"-{vs_avg:.2f}% below avg",
                    color=COLORS['positive']
                )
    
    elif pick_type == "mortgage" and not result.mortgage_summaries:
        st.info("No mortgage data loaded yet. Select banks in the sidebar and click Refresh.")
    elif pick_type == "mortgage":
        # Sort by approval rate
        sorted_banks = sorted(
            result.mortgage_summaries,
            key=lambda x: x.approval_rate,
            reverse=True
        )[:3]
        
        cols = st.columns(3)
        for i, summary in enumerate(sorted_banks):
            with cols[i]:
                medal = ["🥇", "🥈", "🥉"][i]
                _quick_pick_card(
                    medal=medal,
                    bank=summary.institution_name,
                    rate=f"{summary.approval_rate:.1f}% Approved",
                    subtitle=f"{summary.total_applications:,} applications",
                    color=COLORS['positive']
                )


def _quick_pick_card(medal: str, bank: str, rate: str, subtitle: str, color: str):
    """Individual quick pick card with animation."""
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                cursor: pointer;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">{medal}</div>
        <div style="color: #E5E7EB; font-weight: 600; font-size: 1rem; margin-bottom: 0.5rem;">
            {bank}
        </div>
        <div style="color: {color}; font-size: 1.8rem; font-weight: 800; margin-bottom: 0.25rem;">
            {rate}
        </div>
        <div style="color: #9CA3AF; font-size: 0.85rem;">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Interactive Savings Calculator ────────────────────────────────────────
def savings_calculator(result: PipelineResult):
    """What-if calculator showing potential savings."""
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h2 style="color: #E5E7EB; font-size: 1.5rem; font-weight: 700;">
            💰 How Much More Could You Earn?
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        amount = st.slider(
            "Your savings balance",
            min_value=1000,
            max_value=100000,
            value=10000,
            step=1000,
            format="$%d"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            current_bank = st.selectbox(
                "Current bank",
                options=list(BANK_SAVINGS_RATES.keys()),
                index=0
            )
        with col_b:
            top_banks = sorted(
                BANK_SAVINGS_RATES.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            switch_bank = st.selectbox(
                "Switch to",
                options=[b[0] for b in top_banks],
                index=0
            )

        # Calculate earnings
        current_rate = BANK_SAVINGS_RATES.get(current_bank, 0)
        new_rate = BANK_SAVINGS_RATES.get(switch_bank, 0)

        current_earnings = amount * current_rate / 100
        new_earnings = amount * new_rate / 100
        difference = new_earnings - current_earnings

        # Results card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['positive']}22, {COLORS['accent']}22);
                    border: 2px solid {COLORS['positive']}44;
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    margin-top: 1rem;">
            <div style="color: #9CA3AF; font-size: 0.85rem; text-transform: uppercase;
                        letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                You'd Earn
            </div>
            <div style="color: {COLORS['positive']}; font-size: 2.5rem; font-weight: 800;
                        margin-bottom: 0.25rem;">
                ${difference:.2f}
            </div>
            <div style="color: #E5E7EB; font-size: 0.9rem; margin-bottom: 1rem;">
                MORE per year
            </div>
            <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 8px;
                        font-size: 0.85rem; color: #D1D5DB;">
                <div style="margin-bottom: 0.25rem;">
                    5 years: <strong style="color: {COLORS['highlight']};">${difference * 5:,.2f}</strong>
                </div>
                <div>
                    10 years: <strong style="color: {COLORS['highlight']};">${difference * 10:,.2f}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Visual comparison
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Current Bank',
        x=[current_bank],
        y=[current_earnings],
        marker_color='#EF4444',
        text=[f'${current_earnings:.2f}'],
        textposition='outside',
    ))
    
    fig.add_trace(go.Bar(
        name='New Bank',
        x=[switch_bank],
        y=[new_earnings],
        marker_color='#10B981',
        text=[f'${new_earnings:.2f}'],
        textposition='outside',
    ))
    
    fig.update_layout(
        title="Annual Interest Earnings Comparison",
        yaxis_title="Annual Earnings ($)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E5E7EB'),
        showlegend=True,
        height=350,
        bargap=0.3,
    )
    
    st.plotly_chart(fig, width="stretch")


# ── Bank Matcher Quiz ─────────────────────────────────────────────────────
def bank_matcher_quiz():
    """Interactive quiz to match users with ideal banks."""
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h2 style="color: #E5E7EB; font-size: 1.5rem; font-weight: 700;">
            🎯 Find Your Ideal Bank in 4 Questions
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        # Initialize quiz state
        if 'quiz_responses' not in st.session_state:
            st.session_state.quiz_responses = {}
        
        # Question 1: Priority
        st.markdown("**1. What matters most to you?**")
        priority = st.radio(
            "Priority",
            options=["Highest savings rates", "Lowest fees", "Best customer service", "Most branches"],
            key="q1_priority",
            label_visibility="collapsed"
        )
        st.session_state.quiz_responses['priority'] = priority
        
        # Question 2: Balance
        st.markdown("**2. How much do you plan to save?**")
        balance = st.select_slider(
            "Balance",
            options=["$0-$1k", "$1k-$5k", "$5k-$25k", "$25k-$100k", "$100k+"],
            value="$5k-$25k",
            key="q2_balance",
            label_visibility="collapsed"
        )
        st.session_state.quiz_responses['balance'] = balance
        
        # Question 3: Branches
        st.markdown("**3. Do you need physical branches?**")
        branches = st.radio(
            "Branches",
            options=["Yes, definitely", "No, online only is fine", "Doesn't matter"],
            key="q3_branches",
            label_visibility="collapsed"
        )
        st.session_state.quiz_responses['branches'] = branches
        
        # Question 4: Products
        st.markdown("**4. Which products do you need?**")
        products = st.multiselect(
            "Products",
            options=["Checking", "Savings", "Credit Card", "Mortgage", "Auto Loan"],
            default=["Checking", "Savings"],
            key="q4_products",
            label_visibility="collapsed"
        )
        st.session_state.quiz_responses['products'] = products
        
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        
        if st.button("🎯 Show My Matches", type="primary", width="stretch"):
            st.session_state.show_quiz_results = True
    
    # Show results if quiz completed
    if st.session_state.get('show_quiz_results', False):
        _show_quiz_results(st.session_state.quiz_responses)


def _show_quiz_results(responses: Dict):
    """Display personalized bank recommendations based on quiz."""
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h3 style="color: #E5E7EB; font-size: 1.3rem; font-weight: 700;">
            ✨ Your Personalized Recommendations
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple matching logic
    recommendations = []
    
    if responses.get('priority') == "Highest savings rates":
        # Recommend high-yield banks
        recommendations = [
            ("Ally Bank", "4.75% APY", "Best overall rate", COLORS['positive']),
            ("Synchrony Bank", "4.75% APY", "Competitive online rate", COLORS['positive']),
            ("Goldman Sachs (Marcus)", "4.50% APY", "Strong brand, great rate", COLORS['accent']),
        ]
    elif responses.get('priority') == "Best customer service":
        recommendations = [
            ("American Express", "4.30% APY", "Excellent service reputation", COLORS['accent']),
            ("Discover", "4.25% APY", "Award-winning support", COLORS['positive']),
            ("Capital One", "3.80% APY", "Strong mobile app", COLORS['highlight']),
        ]
    elif responses.get('priority') == "Most branches":
        recommendations = [
            ("JPMorgan Chase", "0.01% APY", "5,000+ branches nationwide", COLORS['neutral']),
            ("Bank of America", "0.01% APY", "4,000+ branches", COLORS['neutral']),
            ("Wells Fargo", "0.15% APY", "4,700+ branches", COLORS['neutral']),
        ]
    else:
        # Default to balanced options
        recommendations = [
            ("Capital One", "3.80% APY", "Good balance of rate & service", COLORS['positive']),
            ("Discover", "4.25% APY", "No fees, great rate", COLORS['positive']),
            ("Ally Bank", "4.75% APY", "Top online bank", COLORS['accent']),
        ]
    
    cols = st.columns(3)
    for i, (bank, rate, reason, color) in enumerate(recommendations):
        with cols[i]:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05);
                        border: 2px solid {color}44;
                        border-radius: 12px;
                        padding: 1.5rem;
                        text-align: center;
                        min-height: 180px;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">
                    {'🏆' if i == 0 else '⭐' if i == 1 else '✨'}
                </div>
                <div style="color: #E5E7EB; font-weight: 700; font-size: 1.1rem;
                            margin-bottom: 0.5rem;">
                    {bank}
                </div>
                <div style="color: {color}; font-size: 1.3rem; font-weight: 800;
                            margin-bottom: 0.5rem;">
                    {rate}
                </div>
                <div style="color: #9CA3AF; font-size: 0.85rem; line-height: 1.4;">
                    {reason}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── Achievement Badges ────────────────────────────────────────────────────
def achievement_badge(text: str, icon: str, color: str = None):
    """Display an achievement badge."""
    color = color or COLORS['highlight']
    st.markdown(f"""
    <div style="display: inline-block;
                background: linear-gradient(135deg, {color}22, {color}11);
                border: 2px solid {color}44;
                border-radius: 20px;
                padding: 0.5rem 1rem;
                margin: 0.25rem;
                font-size: 0.85rem;
                font-weight: 600;">
        <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
        <span style="color: {color};">{text}</span>
    </div>
    """, unsafe_allow_html=True)


# ── Animated Score Card ───────────────────────────────────────────────────
def animated_score_card(score: BankScore, rank: int = None):
    """Enhanced score card with animations and badges."""
    from ui.components import GRADE_COLOR
    import re

    color = GRADE_COLOR.get(score.grade, "#6B7280")
    bar_pct = score.overall_score
    # Unique animation name per card so each bar fills to its own target width
    anim_id = re.sub(r"[^a-zA-Z0-9]", "", score.institution_name)
    
    # Determine achievements
    badges = []
    if score.rate_score >= 90:
        badges.append(("🏆 Rate Leader", COLORS['positive']))
    if score.complaint_score >= 85:
        badges.append(("💎 Customer Favorite", COLORS['accent']))
    if score.safety_score >= 90:
        badges.append(("🛡️ Safety Champion", COLORS['positive']))
    if score.overall_score >= 85:
        badges.append(("⭐ Top Pick", COLORS['highlight']))
    
    rank_badge = f"""
    <div style="position: absolute; top: -10px; right: -10px;
                background: linear-gradient(135deg, {COLORS['highlight']}, {COLORS['accent']});
                color: white; font-weight: 800; font-size: 0.9rem;
                width: 36px; height: 36px; border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        #{rank}
    </div>
    """ if rank else ""
    
    badges_html = "".join([
        f'<span style="background:{c}22;color:{c};border:1px solid {c}44;'
        f'border-radius:12px;padding:0.2rem 0.5rem;font-size:0.7rem;'
        f'font-weight:600;margin-right:0.25rem;">{b}</span>'
        for b, c in badges
    ])
    
    st.markdown(f"""
    <div style="position: relative;
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid {color}44;
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
        {rank_badge}
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
            <span style="color:#E5E7EB;font-weight:700;font-size:1.1rem;">{score.institution_name}</span>
            <span style="background:{color};color:white;font-weight:800;font-size:1.3rem;
                         padding:0.4rem 0.8rem;border-radius:8px;
                         box-shadow: 0 2px 8px {color}66;">{score.grade}</span>
        </div>
        <div style="background:#374151;border-radius:6px;height:10px;margin-bottom:1rem;
                    overflow: hidden;">
            <div style="background: linear-gradient(90deg, {color}, {color}88);
                        width:{bar_pct}%;height:100%;border-radius:6px;
                        animation: fillBar_{anim_id} 1s ease-out;"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;
                    margin-bottom:1rem;font-size:0.85rem;">
            <div style="background:rgba(0,0,0,0.2);padding:0.5rem;border-radius:6px;">
                <span style="color:#9CA3AF;">Rate:</span>
                <strong style="color:#E5E7EB;margin-left:0.5rem;">{score.rate_score:.0f}/100</strong>
            </div>
            <div style="background:rgba(0,0,0,0.2);padding:0.5rem;border-radius:6px;">
                <span style="color:#9CA3AF;">Complaints:</span>
                <strong style="color:#E5E7EB;margin-left:0.5rem;">{score.complaint_score:.0f}/100</strong>
            </div>
            <div style="background:rgba(0,0,0,0.2);padding:0.5rem;border-radius:6px;">
                <span style="color:#9CA3AF;">Safety:</span>
                <strong style="color:#E5E7EB;margin-left:0.5rem;">{score.safety_score:.0f}/100</strong>
            </div>
            <div style="background:rgba(0,0,0,0.2);padding:0.5rem;border-radius:6px;">
                <span style="color:#9CA3AF;">Fairness:</span>
                <strong style="color:#E5E7EB;margin-left:0.5rem;">{score.fairness_score:.0f}/100</strong>
            </div>
        </div>
        <div style="margin-bottom:0.75rem;">
            {badges_html}
        </div>
        <div style="padding-top:0.75rem;border-top:1px solid #374151;
                    font-size:0.85rem;color:#D1D5DB;line-height:1.5;">
            {score.verdict or ""}
        </div>
    </div>
    <style>
    @keyframes fillBar_{anim_id} {{
        from {{ width: 0%; }}
        to {{ width: {bar_pct}%; }}
    }}
    </style>
    """, unsafe_allow_html=True)


# ── Live Rankings Leaderboard ─────────────────────────────────────────────
def live_rankings_leaderboard():
    """Display a leaderboard-style ranking of banks."""
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h2 style="color: #E5E7EB; font-size: 1.5rem; font-weight: 700;">
            🏆 Today's Top Performers
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    sorted_banks = sorted(
        BANK_SAVINGS_RATES.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    for i, (bank, rate) in enumerate(sorted_banks):
        medal = ["🥇", "🥈", "🥉", "🔸", "🔸"][i]
        badge_text = "⚡ Hot" if i == 0 else ""
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 1rem 1.5rem;
                    margin-bottom: 0.75rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: transform 0.2s ease;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.5rem;">{medal}</span>
                <span style="color: #E5E7EB; font-weight: 600; font-size: 1rem;">
                    {i+1}. {bank}
                </span>
                {f'<span style="background:#F59E0B22;color:#F59E0B;border:1px solid #F59E0B44;border-radius:8px;padding:0.2rem 0.5rem;font-size:0.7rem;font-weight:700;margin-left:0.5rem;">{badge_text}</span>' if badge_text else ''}
            </div>
            <span style="color: {COLORS['positive']}; font-weight: 800; font-size: 1.2rem;">
                {rate:.2f}% APY
            </span>
        </div>
        """, unsafe_allow_html=True)
