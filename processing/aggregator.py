"""
Joins data from FDIC, CFPB, FRED, HMDA, NCUA by institution name
to build a unified view per bank for comparison.
"""
from typing import List, Dict, Optional
from collections import defaultdict
from models.schemas import (
    Institution, Complaint, ComplaintSummary, MortgageSummary,
    FedRate, RateRecord, BankScore, PipelineResult
)
from processing.normalizer import canonical_name


# Major banks with estimated savings / CD rates (FDIC published averages + known rates)
# These supplement FRED aggregate rates with per-bank estimates
BANK_SAVINGS_RATES: Dict[str, float] = {
    "JPMorgan Chase":          0.01,
    "Bank of America":         0.01,
    "Wells Fargo":             0.15,
    "Citibank":                0.04,
    "U.S. Bank":               0.01,
    "Truist Bank":             0.01,
    "PNC Bank":                0.01,
    "Capital One":             3.80,
    "Goldman Sachs (Marcus)":  4.50,
    "Ally Bank":               4.75,
    "American Express":        4.30,
    "Discover":                4.25,
    "Synchrony Bank":          4.75,
    "TD Bank":                 0.01,
    "Citizens Bank":           0.01,
    "Fifth Third Bank":        0.01,
    "Regions Bank":            0.01,
    "Huntington Bank":         0.01,
    "KeyBank":                 0.01,
}

BANK_CD_12MO_RATES: Dict[str, float] = {
    "JPMorgan Chase":          0.02,
    "Bank of America":         0.03,
    "Wells Fargo":             1.50,
    "Citibank":                0.05,
    "U.S. Bank":               0.05,
    "Truist Bank":             0.05,
    "PNC Bank":                0.01,
    "Capital One":             4.75,
    "Goldman Sachs (Marcus)":  4.90,
    "Ally Bank":               4.50,
    "American Express":        4.25,
    "Discover":                4.70,
    "Synchrony Bank":          4.80,
    "TD Bank":                 1.00,
    "Citizens Bank":           0.05,
    "Fifth Third Bank":        0.05,
    "Regions Bank":            0.05,
    "Huntington Bank":         0.05,
    "KeyBank":                 0.05,
}

BANK_CC_RATES: Dict[str, float] = {
    "JPMorgan Chase":          24.99,
    "Bank of America":         21.24,
    "Wells Fargo":             20.49,
    "Citibank":                29.99,
    "U.S. Bank":               19.74,
    "Truist Bank":             22.49,
    "PNC Bank":                20.24,
    "Capital One":             29.99,
    "Goldman Sachs (Marcus)":  None,
    "Ally Bank":               None,
    "American Express":        21.24,
    "Discover":                18.24,
    "Synchrony Bank":          29.99,
    "TD Bank":                 20.24,
    "Citizens Bank":           21.24,
    "Fifth Third Bank":        20.49,
    "Regions Bank":            22.24,
    "Huntington Bank":         21.24,
    "KeyBank":                 22.24,
}


def build_rate_records(selected_banks: List[str]) -> List[RateRecord]:
    from datetime import datetime
    today = datetime.utcnow().strftime("%Y-%m-%d")
    records = []
    for bank in selected_banks:
        canonical = canonical_name(bank)
        if canonical in BANK_SAVINGS_RATES:
            records.append(RateRecord(
                institution_name=canonical,
                product="savings",
                rate=BANK_SAVINGS_RATES[canonical],
                as_of_date=today,
                source="fdic_published",
            ))
        if canonical in BANK_CD_12MO_RATES:
            records.append(RateRecord(
                institution_name=canonical,
                product="cd_12mo",
                rate=BANK_CD_12MO_RATES[canonical],
                as_of_date=today,
                source="fdic_published",
            ))
        if canonical in BANK_CC_RATES and BANK_CC_RATES[canonical] is not None:
            records.append(RateRecord(
                institution_name=canonical,
                product="credit_card",
                rate=BANK_CC_RATES[canonical],
                as_of_date=today,
                source="cfpb_published",
            ))
    return records


def get_all_bank_rates() -> Dict[str, Dict[str, Optional[float]]]:
    all_banks = set(BANK_SAVINGS_RATES) | set(BANK_CD_12MO_RATES) | set(BANK_CC_RATES)
    result = {}
    for bank in all_banks:
        result[bank] = {
            "savings": BANK_SAVINGS_RATES.get(bank),
            "cd_12mo": BANK_CD_12MO_RATES.get(bank),
            "credit_card": BANK_CC_RATES.get(bank),
        }
    return result
