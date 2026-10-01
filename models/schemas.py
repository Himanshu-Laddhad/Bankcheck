from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ── Institution ──────────────────────────────────────────────────────────────

class Institution(BaseModel):
    cert: str                              # FDIC certificate number (unique ID)
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    asset_size: Optional[float] = None    # Total assets in $thousands
    deposits: Optional[float] = None      # Total deposits in $thousands
    tier1_capital_ratio: Optional[float] = None
    net_interest_margin: Optional[float] = None
    efficiency_ratio: Optional[float] = None
    return_on_assets: Optional[float] = None
    branch_count: Optional[int] = None
    is_fdic_insured: bool = True
    institution_type: str = "bank"        # bank | credit_union | online_bank


# ── Rates ─────────────────────────────────────────────────────────────────────

class RateRecord(BaseModel):
    institution_name: str
    product: str                          # savings | cd_3mo | cd_6mo | cd_12mo | cd_24mo | mortgage_30yr | auto_48mo | personal_loan | credit_card
    rate: float                           # APY or APR as percentage
    as_of_date: str
    source: str = "fred"


class FedRate(BaseModel):
    series_id: str
    name: str
    rate: float
    as_of_date: str


# ── Complaints ────────────────────────────────────────────────────────────────

class Complaint(BaseModel):
    complaint_id: str
    institution_name: str
    product: str                          # credit_card | mortgage | checking | savings | personal_loan | auto_loan | student_loan | money_transfer
    issue: str
    resolution: str                       # closed_with_relief | closed_without_relief | closed_with_explanation | in_progress
    submitted_date: str
    state: Optional[str] = None
    timely_response: bool = True


class ComplaintSummary(BaseModel):
    institution_name: str
    product: str
    total_complaints: int
    relief_rate: float                    # % closed with monetary relief
    timely_response_rate: float
    top_issues: List[str] = []


# ── Mortgage / HMDA ───────────────────────────────────────────────────────────

class MortgageRecord(BaseModel):
    institution_name: str
    lei: Optional[str] = None            # Legal Entity Identifier
    action_type: str                     # originated | denied | approved_not_accepted | withdrawn
    loan_purpose: str                    # home_purchase | refinancing | home_improvement
    loan_amount: Optional[float] = None
    income: Optional[float] = None
    interest_rate: Optional[float] = None
    state: Optional[str] = None
    year: int = 2023


class MortgageSummary(BaseModel):
    institution_name: str
    approval_rate: float
    avg_interest_rate: Optional[float] = None
    total_applications: int
    denial_reasons: Dict[str, int] = {}


# ── Credit Union ──────────────────────────────────────────────────────────────

class CreditUnion(BaseModel):
    cu_number: str
    name: str
    state: Optional[str] = None
    total_assets: Optional[float] = None
    membership_type: Optional[str] = None   # community | employer | association
    savings_rate: Optional[float] = None
    loan_rate: Optional[float] = None
    is_ncua_insured: bool = True


# ── Composite Score ───────────────────────────────────────────────────────────

class BankScore(BaseModel):
    institution_name: str
    cert: Optional[str] = None
    overall_score: float = 0.0            # 0–100
    grade: str = "N/A"                   # A+ A B C D F
    rate_score: float = 0.0
    complaint_score: float = 0.0
    safety_score: float = 0.0
    fairness_score: float = 0.0
    rate_detail: Optional[str] = None
    complaint_detail: Optional[str] = None
    safety_detail: Optional[str] = None
    verdict: Optional[str] = None


# ── Source Health ─────────────────────────────────────────────────────────────

class SourceHealth(BaseModel):
    source: str
    is_healthy: bool
    record_count: int = 0
    last_checked: str = ""
    error: Optional[str] = None


# ── Pipeline Result ───────────────────────────────────────────────────────────

class PipelineResult(BaseModel):
    institutions: List[Institution] = []
    rates: List[RateRecord] = []
    fed_rates: List[FedRate] = []
    fed_history: List[Dict[str, object]] = []   # [{'date': 'YYYY-MM-DD', 'value': float}], ascending
    complaint_summaries: List[ComplaintSummary] = []
    raw_complaints: List[Complaint] = []
    mortgage_summaries: List[MortgageSummary] = []
    credit_unions: List[CreditUnion] = []
    scores: List[BankScore] = []
    health: List[SourceHealth] = []
    selected_banks: List[str] = []
    as_of: str = ""
