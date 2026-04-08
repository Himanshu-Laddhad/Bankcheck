from __future__ import annotations

"""
Composite scoring engine — assigns A–F grade to each institution based on:
  rate_score      (35%) — savings APY vs Fed benchmark
  complaint_score (35%) — CFPB complaint rate + resolution rate
  safety_score    (20%) — FDIC Tier 1 capital ratio
  fairness_score  (10%) — HMDA approval equity
"""
from typing import List, Dict, Optional
from models.schemas import BankScore, Institution, ComplaintSummary, MortgageSummary
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CC_RATES
from config import FEDERAL_FUNDS_RATE


FED_FUNDS_RATE = FEDERAL_FUNDS_RATE  # Single source of truth in config.py
MIN_TIER1 = 6.0         # Regulatory minimum
WELL_CAPITALISED = 10.0


def score_to_grade(score: float) -> str:
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B"
    if score >= 60: return "C"
    if score >= 50: return "D"
    return "F"


def compute_rate_score(bank_name: str, savings_rate: Optional[float] = None) -> tuple[float, str]:
    rate = savings_rate if savings_rate is not None else BANK_SAVINGS_RATES.get(bank_name)
    if rate is None:
        return 50.0, "No rate data available"

    # Score: how close to Fed benchmark (5.33%)
    # 4.5%+ → 100, 3%+ → 80, 1%+ → 60, 0.5%+ → 40, <0.5% → 20
    if rate >= 4.5:
        score = 100.0
        detail = f"Excellent — {rate:.2f}% APY (near Fed benchmark)"
    elif rate >= 3.0:
        score = 80.0
        detail = f"Good — {rate:.2f}% APY"
    elif rate >= 1.0:
        score = 55.0
        detail = f"Below average — {rate:.2f}% APY (national avg 0.64%)"
    elif rate >= 0.5:
        score = 35.0
        detail = f"Poor — only {rate:.2f}% APY"
    else:
        score = 15.0
        detail = f"Very poor — {rate:.2f}% APY (losing {FED_FUNDS_RATE - rate:.2f}% vs Fed benchmark)"

    return score, detail


def compute_complaint_score(summaries: List[ComplaintSummary], bank_name: str) -> tuple[float, str]:
    bank_summaries = [s for s in summaries if bank_name.lower() in s.institution_name.lower()]
    if not bank_summaries:
        return 60.0, "No complaint data found"

    total = sum(s.total_complaints for s in bank_summaries)
    avg_relief = sum(s.relief_rate for s in bank_summaries) / len(bank_summaries)
    avg_timely = sum(s.timely_response_rate for s in bank_summaries) / len(bank_summaries)

    # Score: weighted combo of resolution rate and complaint volume (lower = better)
    relief_score = min(avg_relief * 1.5, 60.0)        # up to 60 pts for resolution rate
    timely_score = min(avg_timely * 0.4, 40.0)        # up to 40 pts for timeliness

    raw_score = relief_score + timely_score

    # Penalty for very high complaint volume (>5000 in period = concerning)
    if total > 10000:
        raw_score = max(raw_score - 20, 10)
    elif total > 5000:
        raw_score = max(raw_score - 10, 10)

    detail = (
        f"{total:,} complaints — {avg_relief:.0f}% resolved with relief, "
        f"{avg_timely:.0f}% responded on time"
    )
    return round(raw_score, 1), detail


def compute_safety_score(institutions: List[Institution], bank_name: str) -> tuple[float, str]:
    matches = [i for i in institutions if bank_name.lower() in i.name.lower()]
    if not matches:
        return 65.0, "No FDIC data found — assumed adequately capitalised"

    inst = matches[0]
    tier1 = inst.tier1_capital_ratio

    if tier1 is None:
        return 65.0, "Capital ratio not reported"

    if tier1 >= WELL_CAPITALISED:
        score = 100.0
        detail = f"Well capitalised — Tier 1 ratio {tier1:.1f}% (min {MIN_TIER1:.0f}%)"
    elif tier1 >= 8.0:
        score = 75.0
        detail = f"Adequately capitalised — Tier 1 ratio {tier1:.1f}%"
    elif tier1 >= MIN_TIER1:
        score = 50.0
        detail = f"Minimum capitalised — Tier 1 ratio {tier1:.1f}% (watch closely)"
    else:
        score = 20.0
        detail = f"Under-capitalised — Tier 1 ratio {tier1:.1f}% (below regulatory minimum)"

    return score, detail


def compute_fairness_score(mortgage_summaries: List[MortgageSummary], bank_name: str) -> tuple[float, str]:
    matches = [m for m in mortgage_summaries if bank_name.lower() in m.institution_name.lower()]
    if not matches:
        return 60.0, "No HMDA mortgage data available"

    m = matches[0]
    rate = m.approval_rate

    if rate >= 75:
        score = 100.0
        detail = f"High approval rate — {rate:.0f}% of applicants approved"
    elif rate >= 60:
        score = 75.0
        detail = f"Average approval rate — {rate:.0f}%"
    elif rate >= 45:
        score = 50.0
        detail = f"Below average approval rate — {rate:.0f}%"
    else:
        score = 25.0
        detail = f"Low approval rate — {rate:.0f}% (restrictive lending)"

    return score, detail


def score_all(
    bank_names: List[str],
    institutions: List[Institution],
    complaint_summaries: List[ComplaintSummary],
    mortgage_summaries: List[MortgageSummary],
) -> List[BankScore]:
    # Build cert lookup once — O(n) instead of O(n*m) in the loop
    cert_lookup = {i.name: i.cert for i in institutions if i.cert}

    scores = []
    for name in bank_names:
        r_score, r_detail = compute_rate_score(name)
        c_score, c_detail = compute_complaint_score(complaint_summaries, name)
        s_score, s_detail = compute_safety_score(institutions, name)
        f_score, f_detail = compute_fairness_score(mortgage_summaries, name)

        overall = (
            r_score * 0.35 +
            c_score * 0.35 +
            s_score * 0.20 +
            f_score * 0.10
        )
        grade = score_to_grade(overall)

        if overall >= 80:
            verdict = "Strong performer — recommended"
        elif overall >= 65:
            verdict = "Average — acceptable with caveats"
        elif overall >= 50:
            verdict = "Below average — consider alternatives"
        else:
            verdict = "Poor — avoid if possible"

        scores.append(BankScore(
            institution_name=name,
            cert=cert_lookup.get(name),
            overall_score=round(overall, 1),
            grade=grade,
            rate_score=r_score,
            complaint_score=c_score,
            safety_score=s_score,
            fairness_score=f_score,
            rate_detail=r_detail,
            complaint_detail=c_detail,
            safety_detail=s_detail,
            verdict=verdict,
        ))

    return sorted(scores, key=lambda x: -x.overall_score)
