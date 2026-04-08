"""Find Your Bank — quiz and savings calculator."""
import streamlit as st
from models.schemas import PipelineResult
from ui.interactive import savings_calculator, bank_matcher_quiz


def render(result: PipelineResult):
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#1E1B4B,#312E81);
                    border-radius:16px;padding:1.75rem 2rem;margin-bottom:1.5rem;
                    border:1px solid rgba(99,102,241,0.3);">
            <h1 style="color:#E5E7EB;font-size:1.75rem;font-weight:800;margin:0 0 0.4rem;">
                Find Your Ideal Bank
            </h1>
            <p style="color:#A5B4FC;font-size:0.95rem;margin:0;">
                Answer a few quick questions to get a personalised recommendation —
                or use the calculator to see exactly how much you could save.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_q, col_c = st.columns([1, 1], gap="large")
    with col_q:
        bank_matcher_quiz()
    with col_c:
        savings_calculator(result)
