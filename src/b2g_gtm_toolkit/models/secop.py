from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SourcePlatform(str, Enum):
    SECOP_I = "SECOP_I"
    SECOP_II = "SECOP_II"
    TVEC = "TVEC"
    SECOP_INTEGRATED = "SECOP_INTEGRATED"
    OCDS_JSON = "OCDS_JSON"


class ResearchTaskType(str, Enum):
    account_research = "account_research"
    opportunity_discovery = "opportunity_discovery"
    purchase_history = "purchase_history"
    supplier_discovery = "supplier_discovery"
    bid_shortlist = "bid_shortlist"


class SecopResearchInput(BaseModel):
    task_type: ResearchTaskType
    entity_names: List[str] = Field(default_factory=list)
    entity_nits: List[str] = Field(default_factory=list)
    municipalities: List[str] = Field(default_factory=list)
    departments: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    unspsc_codes: List[str] = Field(default_factory=list)
    modalities: List[str] = Field(default_factory=list)
    statuses: List[str] = Field(default_factory=list)
    suppliers: List[str] = Field(default_factory=list)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    min_value: Optional[float] = Field(default=None, ge=0)
    max_value: Optional[float] = Field(default=None, ge=0)
    datasets: List[str] = Field(default_factory=list)
    result_limit: int = Field(default=50, ge=1, le=10000)
    page_size: int = Field(default=200, ge=1, le=1000)
    target_account_ref: Optional[str] = None
    icp_ref: Optional[str] = None


class Provenance(BaseModel):
    source_dataset: str = Field(min_length=1)
    source_url: Optional[str] = None
    retrieved_at: datetime
    raw_payload_hash: str = Field(min_length=1)
    query: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class SecopRawRecord(BaseModel):
    source_platform: SourcePlatform
    source_dataset: str
    source_record_id: str
    payload: Dict[str, Any]
    fetched_at: datetime


class RelevanceScore(BaseModel):
    score: float = Field(ge=0, le=100)
    rationale: str = Field(min_length=1)
    recommended_action: Optional[str] = None


class SecopNormalizedRecord(BaseModel):
    source_platform: SourcePlatform
    source_dataset: str
    source_record_id: str
    source_url: Optional[str] = None
    process_id: Optional[str] = None
    contract_id: Optional[str] = None
    buyer_name: str = Field(min_length=1)
    buyer_nit: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_nit: Optional[str] = None
    object: str = Field(min_length=1)
    modality: Optional[str] = None
    status: Optional[str] = None
    contract_value: Optional[float] = None
    currency: str = "COP"
    publication_date: Optional[date] = None
    award_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    deadline: Optional[datetime] = None
    unspsc_codes: List[str] = Field(default_factory=list)
    matched_account_id: Optional[str] = None
    relevance: Optional[RelevanceScore] = None
    provenance: Provenance
    run_id: Optional[str] = None
