"""Data shaping shared by the dashboard views."""
from __future__ import annotations
from collections import defaultdict
from models.schemas import PipelineResult
from processing.aggregator import BANK_SAVINGS_RATES, BANK_CD_12MO_RATES, BANK_CC_RATES
from config import FEDERAL_FUNDS_RATE

# ── Explicit thresholds (single source of truth for every status colour) ──
THRESH = {
    "savings_gap_warn": 1.0,       # savings APY more than 1 pt under Fed funds -> watch
    "savings_gap_alert": 2.0,      # more than 2 pts under -> act
    "timely_warn": 97.0,           # % complaints answered on time
    "timely_alert": 95.0,
    "relief_warn": 10.0,           # % closed with relief (low = customers rarely helped)
    "approval_warn": 60.0,         # mortgage approval %
    "cc_apr_warn": 25.0,           # credit-card APR
    "tier1_warn": 10.0,            # capital ratio %
}


def match(bank: str, name: str) -> bool:
    return bank.lower() in name.lower() or name.lower() in bank.lower()


def complaints_by_bank(result: PipelineResult, banks: list[str]) -> dict:
    """{bank: {total, relief, timely}} with complaint-weighted averages."""
    out = {}
    for b in banks:
        rows = [s for s in result.complaint_summaries if match(b, s.institution_name)]
        total = sum(s.total_complaints for s in rows)
        if total:
            out[b] = {
                "total": total,
                "relief": sum(s.relief_rate * s.total_complaints for s in rows) / total,
                "timely": sum(s.timely_response_rate * s.total_complaints for s in rows) / total,
            }
    return out


def mortgage_by_bank(result: PipelineResult, banks: list[str]) -> dict:
    out = {}
    for b in banks:
        m = next((s for s in result.mortgage_summaries if match(b, s.institution_name)), None)
        if m:
            out[b] = m
    return out


def score_by_bank(result: PipelineResult, banks: list[str]) -> dict:
    out = {}
    for b in banks:
        s = next((s for s in result.scores if match(b, s.institution_name)), None)
        if s:
            out[b] = s
    return out


def rates_for(banks: list[str]) -> dict:
    return {
        "savings": {b: BANK_SAVINGS_RATES[b] for b in banks if b in BANK_SAVINGS_RATES},
        "cd": {b: BANK_CD_12MO_RATES[b] for b in banks if b in BANK_CD_12MO_RATES},
        "cc": {b: BANK_CC_RATES[b] for b in banks if BANK_CC_RATES.get(b) is not None},
    }


def short(name: str, n: int = 22) -> str:
    return name if len(name) <= n else name[: n - 1] + "…"


ALL_BANKS = sorted(BANK_SAVINGS_RATES)


def fed_rate(result: PipelineResult) -> float:
    """Latest effective Fed funds rate from FRED when available, else the config constant."""
    if result.fed_history:
        return float(result.fed_history[-1]["value"])
    for r in result.fed_rates:
        if r.series_id in ("DFF", "FEDFUNDS"):
            return r.rate
    return FEDERAL_FUNDS_RATE


def savings_status(gap_pts: float) -> str:
    """gap_pts = rate - fed (negative = below). One rule for KPI colour AND exceptions."""
    if gap_pts < -THRESH["savings_gap_alert"]:
        return "alert"
    if gap_pts < -THRESH["savings_gap_warn"]:
        return "warn"
    return "good"
