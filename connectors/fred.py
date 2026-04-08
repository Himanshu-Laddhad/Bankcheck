"""
FRED API (Federal Reserve Economic Data) — https://fred.stlouisfed.org/docs/api/
Free API key required: https://fred.stlouisfed.org/docs/api/api_key.html
Returns benchmark rates and consumer credit rates (G.19, H.15 releases).
Falls back to NCUA/FDIC published averages if no key provided.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
from connectors.base import BaseConnector
from models.schemas import FedRate, RateRecord, SourceHealth
from config import settings


FRED_BASE = "https://api.stlouisfed.org/fred"

# Series IDs → human label → product category
RATE_SERIES = {
    "FEDFUNDS":      ("Federal Funds Rate",                        "fed_funds"),
    "DFF":           ("Fed Funds Effective Rate (Daily)",           "fed_funds_daily"),
    "TERMCBCCALLNS": ("Credit Card Interest Rate (All Accounts)",   "credit_card"),
    # TERMCBCCALLAN returns 400 — series ID is invalid on current FRED
    "TERMCBPER24NS": ("Personal Loan Rate (24-month)",              "personal_loan"),
    "TERMCBAUTO48NS": ("Auto Loan Rate (48-month)",                 "auto_loan"),
    "MORTGAGE30US":  ("30-Year Fixed Mortgage Rate",                "mortgage_30yr"),
    "MORTGAGE15US":  ("15-Year Fixed Mortgage Rate",                "mortgage_15yr"),
    # CD and money-market series (CD6NRNBW, CD1NRNBW, MMNRNBW) were discontinued
    # by the Fed in 2022 — no current replacements; static fallbacks used instead.
}

# Fallback national averages (FDIC/NCUA published, updated quarterly)
FALLBACK_RATES = {
    "fed_funds":    5.33,
    "credit_card":  21.47,
    "credit_card_new": 24.37,
    "personal_loan": 12.35,
    "auto_loan":    7.68,
    "mortgage_30yr": 6.82,
    "mortgage_15yr": 6.06,
    "cd_6mo":       1.79,
    "cd_12mo":      1.86,
    "money_market": 0.64,
}


class FREDConnector(BaseConnector):
    source_name = "fred"

    def fetch(self, series_ids: Optional[List[str]] = None) -> List[FedRate]:
        if not settings.has_fred:
            logger.warning("FRED_API_KEY not set — using fallback national averages")
            return self._fallback_rates()

        ids = series_ids or list(RATE_SERIES.keys())
        rates = []
        for sid in ids:
            rate = self._fetch_series(sid)
            if rate:
                rates.append(rate)
        return rates

    def _fetch_series(self, series_id: str) -> Optional[FedRate]:
        label, _ = RATE_SERIES.get(series_id, (series_id, series_id))
        try:
            date_from = (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d")
            data = self._get(f"{FRED_BASE}/series/observations", params={
                "series_id": series_id,
                "api_key": settings.fred_api_key,
                "file_type": "json",
                "observation_start": date_from,
                "sort_order": "desc",
                "limit": 1,
            })
            obs = data.get("observations", [])
            if obs and obs[0].get("value") not in (".", None, ""):
                return FedRate(
                    series_id=series_id,
                    name=label,
                    rate=float(obs[0]["value"]),
                    as_of_date=obs[0]["date"],
                )
        except Exception as e:
            logger.warning(f"FRED series {series_id} failed: {e}")
        return None

    def _fallback_rates(self) -> List[FedRate]:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        result = []
        for sid, (label, product) in RATE_SERIES.items():
            if product in FALLBACK_RATES:
                result.append(FedRate(
                    series_id=sid,
                    name=f"{label} (national avg)",
                    rate=FALLBACK_RATES[product],
                    as_of_date=today,
                ))
        return result

    def get_benchmark(self) -> float:
        rates = self.fetch(["FEDFUNDS"])
        if rates:
            return rates[0].rate
        return FALLBACK_RATES["fed_funds"]

    def health_check(self) -> SourceHealth:
        if not settings.has_fred:
            # Explicitly mark as degraded — data is national averages, not live FRED
            return SourceHealth(
                source=self.source_name,
                is_healthy=False,
                record_count=len(FALLBACK_RATES),
                last_checked=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                error="No FRED_API_KEY — showing static national averages (Q4 2024)",
            )
        try:
            data = self._get(f"{FRED_BASE}/series/observations", params={
                "series_id": "FEDFUNDS",
                "api_key": settings.fred_api_key,
                "file_type": "json",
                "limit": 1,
            })
            ok = bool(data.get("observations"))
            return SourceHealth(source=self.source_name, is_healthy=ok, record_count=1 if ok else 0,
                                last_checked=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
        except Exception as e:
            return SourceHealth(source=self.source_name, is_healthy=False, error=str(e),
                                last_checked=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
