from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class CompanyStage(str, Enum):
    idea = "idea"
    early = "early"
    growth = "growth"
    scale = "scale"
    enterprise = "enterprise"


class ApprovalStatus(str, Enum):
    draft = "draft"
    needs_review = "needs_review"
    approved = "approved"
    rejected = "rejected"
    archived = "archived"


class ConfidenceLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class BusinessProfile(BaseModel):
    name: str = Field(min_length=1)
    offer_summary: str = Field(min_length=1)
    products_services: List[str] = Field(default_factory=list)
    current_customers: List[str] = Field(default_factory=list)
    best_customers: List[str] = Field(default_factory=list)
    poor_fit_customers: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    company_stage: CompanyStage = CompanyStage.early
    regions_served: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BuyingCommitteeRole(BaseModel):
    role: str = Field(min_length=1)
    typical_titles: List[str] = Field(default_factory=list)
    influence: Optional[str] = None


class ICP(BaseModel):
    name: str = Field(min_length=1)
    business_profile_ref: Optional[str] = None
    target_entity_types: List[str] = Field(default_factory=list)
    target_categories: List[str] = Field(default_factory=list)
    target_regions: List[str] = Field(default_factory=list)
    fit_criteria: List[str] = Field(default_factory=list)
    disqualifiers: List[str] = Field(default_factory=list)
    buying_triggers: List[str] = Field(default_factory=list)
    buying_committee_roles: List[BuyingCommitteeRole] = Field(default_factory=list)
    observable_signals: List[str] = Field(default_factory=list)
    confidence_level: ConfidenceLevel = ConfidenceLevel.low
    evidence_summary: Optional[str] = None
    approval_status: ApprovalStatus = ApprovalStatus.draft

    @model_validator(mode="after")
    def _require_some_fit_criteria(self) -> "ICP":
        if not self.target_entity_types and not self.fit_criteria:
            raise ValueError("ICP requires at least one target_entity_type or fit_criteria entry")
        return self
