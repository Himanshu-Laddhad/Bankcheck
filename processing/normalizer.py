"""
Standardises institution names across FDIC, CFPB, HMDA, and NCUA so that
all sources can be joined by a single canonical bank name.
"""
import re
from typing import List, Dict
from models.schemas import Institution, Complaint, MortgageSummary


# Canonical name aliases — maps variations to a single display name
NAME_ALIASES: Dict[str, str] = {
    # JPMorgan Chase
    "jpmorgan chase bank": "JPMorgan Chase",
    "jpmorgan chase": "JPMorgan Chase",
    "jp morgan chase": "JPMorgan Chase",
    "chase bank": "JPMorgan Chase",
    # Bank of America
    "bank of america": "Bank of America",
    "bank of america, n.a.": "Bank of America",
    "boa": "Bank of America",
    # Wells Fargo
    "wells fargo bank": "Wells Fargo",
    "wells fargo": "Wells Fargo",
    "wells fargo bank, n.a.": "Wells Fargo",
    # Citibank / Citi
    "citibank": "Citibank",
    "citibank, n.a.": "Citibank",
    "citi": "Citibank",
    "citicorp": "Citibank",
    # US Bank
    "u.s. bank": "U.S. Bank",
    "us bank": "U.S. Bank",
    "u.s. bank national association": "U.S. Bank",
    # Truist
    "truist bank": "Truist Bank",
    "truist": "Truist Bank",
    # PNC
    "pnc bank": "PNC Bank",
    "pnc bank, national association": "PNC Bank",
    # Capital One
    "capital one": "Capital One",
    "capital one bank": "Capital One",
    "capital one, n.a.": "Capital One",
    # Goldman Sachs / Marcus
    "goldman sachs bank usa": "Goldman Sachs (Marcus)",
    "goldman sachs": "Goldman Sachs (Marcus)",
    "marcus by goldman sachs": "Goldman Sachs (Marcus)",
    # Ally
    "ally bank": "Ally Bank",
    "ally financial": "Ally Bank",
    # American Express
    "american express": "American Express",
    "american express national bank": "American Express",
    # Discover
    "discover bank": "Discover",
    "discover financial": "Discover",
    "discover": "Discover",
    # Synchrony
    "synchrony bank": "Synchrony Bank",
    "synchrony financial": "Synchrony Bank",
    # TD Bank
    "td bank": "TD Bank",
    "td bank, n.a.": "TD Bank",
    # Citizens
    "citizens bank": "Citizens Bank",
    "citizens bank, n.a.": "Citizens Bank",
    # Fifth Third
    "fifth third bank": "Fifth Third Bank",
    "fifth third bank, national association": "Fifth Third Bank",
    # Regions
    "regions bank": "Regions Bank",
    # Huntington
    "huntington national bank": "Huntington Bank",
    "huntington bank": "Huntington Bank",
    # KeyBank
    "keybank": "KeyBank",
    "keybank national association": "KeyBank",
}

# Suffixes to strip before matching
_STRIP = re.compile(
    r"\b(national association|n\.a\.|na|fsb|federal savings bank|"
    r"bank usa|financial|corp|inc|llc|ltd|co)\b\.?",
    re.IGNORECASE,
)


def canonical_name(raw: str | None) -> str:
    if not raw:
        return "Unknown"
    cleaned = _STRIP.sub("", raw).strip().rstrip(",").strip().lower()
    return NAME_ALIASES.get(cleaned, raw.title())


def normalise_institutions(institutions: List[Institution]) -> List[Institution]:
    seen = {}
    for inst in institutions:
        inst.name = canonical_name(inst.name)
        # cert is the stable unique key; fall back to canonical name for keyless institutions
        key = inst.cert if inst.cert else inst.name
        if key not in seen:
            seen[key] = inst
    return list(seen.values())


def normalise_complaints(complaints: List[Complaint]) -> List[Complaint]:
    for c in complaints:
        c.institution_name = canonical_name(c.institution_name)
    return complaints


def normalise_mortgage_summaries(summaries: List[MortgageSummary]) -> List[MortgageSummary]:
    for s in summaries:
        s.institution_name = canonical_name(s.institution_name)
    return summaries
