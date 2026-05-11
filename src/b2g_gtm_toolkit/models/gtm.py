from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from ..utils.ids import stable_id
from .business import ApprovalStatus


class ResearchStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    stale = "stale"


class OpportunityStatus(str, Enum):
    draft = "draft"
    open = "open"
    in_evaluation = "in_evaluation"
    awarded = "awarded"
    closed = "closed"
    cancelled = "cancelled"


class OpportunityModality(str, Enum):
    licitacion_publica = "licitacion_publica"
    seleccion_abreviada = "seleccion_abreviada"
    concurso_meritos = "concurso_meritos"
    minima_cuantia = "minima_cuantia"
    contratacion_directa = "contratacion_directa"
    acuerdo_marco = "acuerdo_marco"
    otro = "otro"


class GtmOutputType(str, Enum):
    outreach = "outreach"
    meeting_prep = "meeting_prep"
    proposal_brief = "proposal_brief"
    business_case = "business_case"


class SignalType(str, Enum):
    new_opportunity = "new_opportunity"
    contract_awarded = "contract_awarded"
    leadership_change = "leadership_change"
    budget_publication = "budget_publication"
    regulatory_change = "regulatory_change"
    other = "other"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class NotificationPreference(str, Enum):
    none = "none"
    email = "email"
    slack = "slack"
    both = "both"


class ActionStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"
    dismissed = "dismissed"


class NotificationStatus(str, Enum):
    not_sent = "not_sent"
    queued = "queued"
    sent = "sent"
    failed = "failed"
    suppressed = "suppressed"


class NotificationPreferences(BaseModel):
    slack: bool = False
    email: bool = False


class Owner(BaseModel):
    name: str = Field(min_length=1)
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    slack_id: Optional[str] = None
    notification_preference: NotificationPreference = NotificationPreference.none
    notification_preferences: NotificationPreferences = Field(default_factory=NotificationPreferences)
    active: bool = True


class TargetAccount(BaseModel):
    id: Optional[str] = None
    name: str = Field(min_length=1)
    normalized_name: Optional[str] = None
    entity_type: Optional[str] = None
    nit: Optional[str] = None
    department: Optional[str] = None
    municipality: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    identifiers: Dict[str, str] = Field(default_factory=dict)
    fit_score: Optional[float] = Field(default=None, ge=0, le=100)
    fit_rationale: Optional[str] = None
    research_status: ResearchStatus = ResearchStatus.not_started
    next_research_step: Optional[str] = None
    owner: Optional[str] = None
    owner_ref: Optional[str] = None
    icp_ref: Optional[str] = None
    last_researched_at: Optional[datetime] = None

    def compute_stable_id(self) -> str:
        if self.id:
            return self.id
        location = self.location or self.municipality or self.department or ""
        return stable_id(self.name, self.entity_type or "", location)


class TargetAccountList(BaseModel):
    icp_id: Optional[str] = None
    generated_at: Optional[datetime] = None
    source: Optional[str] = None
    count: Optional[int] = None
    accounts: List[TargetAccount] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_accounts(self) -> "TargetAccountList":
        if not self.accounts:
            raise ValueError("TargetAccountList requires at least one account")

        seen_ids: Dict[str, int] = {}
        for idx, account in enumerate(self.accounts):
            if account.fit_score is not None and not (0 <= account.fit_score <= 100):
                raise ValueError(
                    f"Account at index {idx} has fit_score={account.fit_score}; must be between 0 and 100"
                )
            sid = account.compute_stable_id()
            if sid in seen_ids:
                raise ValueError(
                    f"Duplicate target account stable id '{sid}' at indices {seen_ids[sid]} and {idx}"
                )
            seen_ids[sid] = idx

        if self.count is not None and self.count != len(self.accounts):
            raise ValueError(
                f"count metadata ({self.count}) does not match number of accounts ({len(self.accounts)})"
            )
        return self


class Opportunity(BaseModel):
    title: str = Field(min_length=1)
    summary: Optional[str] = None
    status: OpportunityStatus = OpportunityStatus.draft
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    estimated_value: Optional[float] = Field(default=None, ge=0)
    deadline: Optional[datetime] = None
    modality: Optional[OpportunityModality] = None
    requirements_summary: Optional[str] = None
    fit_score: Optional[float] = Field(default=None, ge=0, le=100)
    fit_rationale: Optional[str] = None
    pursuit_recommendation: Optional[str] = None
    next_action: Optional[str] = None
    approval_status: ApprovalStatus = ApprovalStatus.draft
    target_account_ref: Optional[str] = None
    research_record_refs: List[str] = Field(default_factory=list)


class Signal(BaseModel):
    type: SignalType
    priority: Priority = Priority.medium
    summary: str = Field(min_length=1)
    source: Optional[str] = None
    source_url: Optional[str] = None
    detected_at: Optional[datetime] = None
    recommended_action: Optional[str] = None
    notification_status: NotificationStatus = NotificationStatus.not_sent
    action_status: ActionStatus = ActionStatus.pending
    target_account_ref: Optional[str] = None
    opportunity_ref: Optional[str] = None
    owner_ref: Optional[str] = None


class GtmOutput(BaseModel):
    type: GtmOutputType
    title: str = Field(min_length=1)
    content: str
    output_key: Optional[str] = None
    source_evidence_hash: Optional[str] = None
    stage: Optional[str] = None
    channel: Optional[str] = None
    source_summary: Optional[str] = None
    approval_status: ApprovalStatus = ApprovalStatus.draft
    created_for: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    owner_ref: Optional[str] = None
    target_account_ref: Optional[str] = None
    opportunity_ref: Optional[str] = None
    research_record_refs: List[str] = Field(default_factory=list)
