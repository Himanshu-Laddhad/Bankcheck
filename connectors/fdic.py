"""
FDIC BankFind Suite API — https://banks.data.fdic.gov/docs/
No API key required.
- /api/institutions  → name, assets, deposits, branch count
- /api/financials    → Tier 1 capital, NIM ratio, efficiency ratio, ROA (separate endpoint)
"""
from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from loguru import logger
from connectors.base import BaseConnector
from models.schemas import Institution, SourceHealth


BASE = "https://banks.data.fdic.gov/api"

# Institutions endpoint — NAME (not NAMEFULL, renamed in 2024 API update)
INST_FIELDS = "CERT,NAME,CITY,STALP,ASSET,DEP,OFFICES"

# Financials endpoint — ratios reported separately from institution profile
FIN_FIELDS = "CERT,REPDTE,RBCRWAJ,NIM,EEFFR,ROA"

# Canonical name → FDIC certificate number.
# The FDIC text search is unreliable (returns 0 results for major banks).
# Cert-based lookup is the authoritative approach — verified 2025-04-02.
# Note: Discover Bank (cert 5649) is INACTIVE — acquired by Capital One in 2024.
CERT_LOOKUP: dict[str, str] = {
    "JPMorgan Chase":         "628",
    "Bank of America":        "3510",
    "Wells Fargo":            "3511",
    "Citibank":               "7213",
    "U.S. Bank":              "6548",
    "Capital One":            "4297",
    "Goldman Sachs (Marcus)": "33124",
    "PNC Bank":               "6384",
    "Truist Bank":            "9846",
    "TD Bank":                "18409",
    "Citizens Bank":          "57957",
    "Huntington Bank":        "6560",
    "Fifth Third Bank":       "6672",
    "American Express":       "27471",
    "Ally Bank":              "57803",
    "KeyBank":                "17534",
    "Regions Bank":           "12368",
    "Synchrony Bank":         "27314",
    # Discover acquired by Capital One 2024 — no active FDIC entry
}


class FDICConnector(BaseConnector):
    source_name = "fdic"

    def fetch(self, bank_names: Optional[List[str]] = None, limit: int = 100) -> List[Institution]:
        institutions: List[Institution] = []
        try:
            if bank_names:
                # Resolve canonical names to certs; fall back to top-assets fetch for unknowns
                certs = [CERT_LOOKUP[n] for n in bank_names if n in CERT_LOOKUP]
                if certs:
                    institutions = self._fetch_by_certs(certs)
                    # For any requested bank not in CERT_LOOKUP, log a warning
                    missing = [n for n in bank_names if n not in CERT_LOOKUP]
                    for m in missing:
                        logger.warning(f"FDIC: no cert mapping for '{m}' — excluded from FDIC data")
                else:
                    institutions = self._fetch_top_banks(limit)
            else:
                institutions = self._fetch_top_banks(limit)

            institutions = self._enrich_financials(institutions)
        except Exception as e:
            logger.error(f"FDIC fetch error: {e}")
        return institutions

    def _fetch_by_certs(self, certs: List[str]) -> List[Institution]:
        """Fetch institutions by their FDIC certificate numbers — the only reliable lookup method."""
        cert_filter = " OR ".join(f"CERT:{c}" for c in certs)
        try:
            data = self._get(f"{BASE}/institutions", params={
                "filters": cert_filter,
                "fields": INST_FIELDS,
                "limit": len(certs),
                "output": "json",
            })
            return [self._parse_inst(r["data"]) for r in data.get("data", []) if r.get("data")]
        except Exception as e:
            logger.warning(f"FDIC cert fetch failed: {e}")
            return []

    def _fetch_top_banks(self, limit: int) -> List[Institution]:
        # Use known certs for the top banks we track — more reliable than filter query
        all_certs = list(CERT_LOOKUP.values())[:limit]
        return self._fetch_by_certs(all_certs)

    def _enrich_financials(self, institutions: List[Institution]) -> List[Institution]:
        """Fetch Tier1, NIM ratio, efficiency, ROA from the /financials endpoint."""
        if not institutions:
            return institutions

        cert_map = {str(inst.cert): inst for inst in institutions if inst.cert}
        if not cert_map:
            return institutions

        cert_filter = " OR ".join(f"CERT:{c}" for c in cert_map)
        try:
            data = self._get(f"{BASE}/financials", params={
                "filters": cert_filter,
                "fields": FIN_FIELDS,
                "limit": len(cert_map),
                "sort_by": "REPDTE",
                "sort_order": "DESC",
                "output": "json",
            })
            seen_certs: set = set()
            for r in data.get("data", []):
                d = r.get("data", {})
                cert = str(d.get("CERT", ""))
                if cert in cert_map and cert not in seen_certs:
                    seen_certs.add(cert)
                    inst = cert_map[cert]
                    inst.tier1_capital_ratio = self._pct(d.get("RBCRWAJ"))
                    # NIM in financials endpoint is dollar income; compute ratio from assets
                    nim_dollars = self._float(d.get("NIM"))
                    if nim_dollars is not None and inst.asset_size and inst.asset_size > 0:
                        inst.net_interest_margin = round(nim_dollars / inst.asset_size * 100, 2)
                    inst.efficiency_ratio = self._pct(d.get("EEFFR"))
                    inst.return_on_assets = self._pct(d.get("ROA"))
        except Exception as e:
            logger.warning(f"FDIC financials enrich failed: {e}")

        return institutions

    def _parse_inst(self, d: dict) -> Institution:
        return Institution(
            cert=str(d.get("CERT", "")),
            name=d.get("NAME", "Unknown"),   # field renamed from NAMEFULL in 2024
            city=d.get("CITY"),
            state=d.get("STALP"),
            asset_size=self._float(d.get("ASSET")),
            deposits=self._float(d.get("DEP")),
            branch_count=int(d["OFFICES"]) if d.get("OFFICES") else None,
            is_fdic_insured=True,
            institution_type="bank",
        )

    @staticmethod
    def _float(val) -> Optional[float]:
        try:
            return float(val) if val not in (None, "", "NA") else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _pct(val) -> Optional[float]:
        """Values from FDIC financials are already percentages — return as-is."""
        try:
            v = float(val)
            return round(v, 4) if val not in (None, "", "NA") else None
        except (ValueError, TypeError):
            return None

    def health_check(self) -> SourceHealth:
        try:
            data = self._get(f"{BASE}/institutions", params={
                "filters": "ACTIVE:1", "fields": "CERT,NAME", "limit": 1, "output": "json"
            })
            ok = bool(data.get("data"))
            return SourceHealth(
                source=self.source_name, is_healthy=ok,
                record_count=1 if ok else 0,
                last_checked=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            )
        except Exception as e:
            return SourceHealth(
                source=self.source_name, is_healthy=False, error=str(e),
                last_checked=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            )
