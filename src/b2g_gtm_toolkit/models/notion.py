from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class NotionPropertyType(str, Enum):
    title = "title"
    rich_text = "rich_text"
    number = "number"
    select = "select"
    multi_select = "multi_select"
    date = "date"
    people = "people"
    files = "files"
    checkbox = "checkbox"
    url = "url"
    email = "email"
    phone_number = "phone_number"
    formula = "formula"
    relation = "relation"
    rollup = "rollup"
    created_time = "created_time"
    last_edited_time = "last_edited_time"
    status = "status"


class NotionPropertySpec(BaseModel):
    name: str = Field(min_length=1)
    type: NotionPropertyType
    required: bool = False
    options: List[str] = Field(default_factory=list)
    relation_database: Optional[str] = None
    description: Optional[str] = None


class NotionDatabaseSpec(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    properties: List[NotionPropertySpec] = Field(min_length=1)


class NotionWorkspaceManifest(BaseModel):
    version: str = "1.0.0"
    databases: List[NotionDatabaseSpec] = Field(min_length=1)


def default_workspace_manifest() -> NotionWorkspaceManifest:
    P = NotionPropertyType

    business_profiles = NotionDatabaseSpec(
        name="B2G Business Profiles",
        properties=[
            NotionPropertySpec(name="Name", type=P.title, required=True),
            NotionPropertySpec(name="Offer Summary", type=P.rich_text),
            NotionPropertySpec(name="Products Services", type=P.multi_select),
            NotionPropertySpec(name="Current Customers", type=P.multi_select),
            NotionPropertySpec(name="Best Customers", type=P.multi_select),
            NotionPropertySpec(name="Poor Fit Customers", type=P.multi_select),
            NotionPropertySpec(name="Competitors", type=P.multi_select),
            NotionPropertySpec(
                name="Company Stage",
                type=P.select,
                options=["idea", "early", "growth", "scale", "enterprise"],
            ),
            NotionPropertySpec(name="Regions Served", type=P.multi_select),
            NotionPropertySpec(name="Constraints", type=P.rich_text),
        ],
    )

    icps = NotionDatabaseSpec(
        name="B2G ICPs",
        properties=[
            NotionPropertySpec(name="Name", type=P.title, required=True),
            NotionPropertySpec(name="Business Profile", type=P.relation, relation_database="B2G Business Profiles"),
            NotionPropertySpec(name="Target Entity Types", type=P.multi_select),
            NotionPropertySpec(name="Target Categories", type=P.multi_select),
            NotionPropertySpec(name="Target Regions", type=P.multi_select),
            NotionPropertySpec(name="Fit Criteria", type=P.rich_text),
            NotionPropertySpec(name="Disqualifiers", type=P.rich_text),
            NotionPropertySpec(name="Buying Triggers", type=P.rich_text),
            NotionPropertySpec(name="Observable Signals", type=P.rich_text),
            NotionPropertySpec(
                name="Confidence Level",
                type=P.select,
                options=["low", "medium", "high"],
            ),
            NotionPropertySpec(name="Evidence Summary", type=P.rich_text),
            NotionPropertySpec(
                name="Approval Status",
                type=P.select,
                options=["draft", "needs_review", "approved", "rejected", "archived"],
            ),
        ],
    )

    target_accounts = NotionDatabaseSpec(
        name="B2G Target Accounts",
        properties=[
            NotionPropertySpec(name="Name", type=P.title, required=True),
            NotionPropertySpec(name="Normalized Name", type=P.rich_text),
            NotionPropertySpec(name="Entity Type", type=P.select),
            NotionPropertySpec(name="NIT", type=P.rich_text),
            NotionPropertySpec(name="Department", type=P.select),
            NotionPropertySpec(name="Municipality", type=P.rich_text),
            NotionPropertySpec(name="Category", type=P.select),
            NotionPropertySpec(name="Fit Score", type=P.number),
            NotionPropertySpec(name="Fit Rationale", type=P.rich_text),
            NotionPropertySpec(
                name="Research Status",
                type=P.select,
                options=["not_started", "in_progress", "completed", "stale"],
            ),
            NotionPropertySpec(name="Owner", type=P.relation, relation_database="B2G Owners"),
            NotionPropertySpec(name="ICP", type=P.relation, relation_database="B2G ICPs"),
            NotionPropertySpec(name="Last Researched At", type=P.date),
        ],
    )

    secop_research = NotionDatabaseSpec(
        name="B2G SECOP Research",
        properties=[
            NotionPropertySpec(name="Object", type=P.title, required=True),
            NotionPropertySpec(
                name="Source Platform",
                type=P.select,
                options=["SECOP_I", "SECOP_II", "TVEC", "SECOP_INTEGRATED", "OCDS_JSON"],
            ),
            NotionPropertySpec(name="Source Dataset", type=P.rich_text),
            NotionPropertySpec(name="Source Record ID", type=P.rich_text),
            NotionPropertySpec(name="Source URL", type=P.url),
            NotionPropertySpec(name="Process ID", type=P.rich_text),
            NotionPropertySpec(name="Contract ID", type=P.rich_text),
            NotionPropertySpec(name="Buyer Name", type=P.rich_text),
            NotionPropertySpec(name="Buyer NIT", type=P.rich_text),
            NotionPropertySpec(name="Supplier Name", type=P.rich_text),
            NotionPropertySpec(name="Supplier NIT", type=P.rich_text),
            NotionPropertySpec(name="Modality", type=P.select),
            NotionPropertySpec(name="Status", type=P.select),
            NotionPropertySpec(name="Contract Value", type=P.number),
            NotionPropertySpec(name="Currency", type=P.select, options=["COP", "USD"]),
            NotionPropertySpec(name="Publication Date", type=P.date),
            NotionPropertySpec(name="Award Date", type=P.date),
            NotionPropertySpec(name="Deadline", type=P.date),
            NotionPropertySpec(name="UNSPSC Codes", type=P.multi_select),
            NotionPropertySpec(name="Target Account", type=P.relation, relation_database="B2G Target Accounts"),
            NotionPropertySpec(name="Run ID", type=P.rich_text),
            NotionPropertySpec(name="Raw Payload Hash", type=P.rich_text),
        ],
    )

    opportunities = NotionDatabaseSpec(
        name="B2G Opportunities",
        properties=[
            NotionPropertySpec(name="Title", type=P.title, required=True),
            NotionPropertySpec(name="Summary", type=P.rich_text),
            NotionPropertySpec(
                name="Status",
                type=P.select,
                options=["draft", "open", "in_evaluation", "awarded", "closed", "cancelled"],
            ),
            NotionPropertySpec(name="Source Platform", type=P.select),
            NotionPropertySpec(name="Source URL", type=P.url),
            NotionPropertySpec(name="Estimated Value", type=P.number),
            NotionPropertySpec(name="Deadline", type=P.date),
            NotionPropertySpec(name="Modality", type=P.select),
            NotionPropertySpec(name="Requirements Summary", type=P.rich_text),
            NotionPropertySpec(name="Fit Score", type=P.number),
            NotionPropertySpec(name="Fit Rationale", type=P.rich_text),
            NotionPropertySpec(name="Pursuit Recommendation", type=P.rich_text),
            NotionPropertySpec(name="Next Action", type=P.rich_text),
            NotionPropertySpec(
                name="Approval Status",
                type=P.select,
                options=["draft", "needs_review", "approved", "rejected", "archived"],
            ),
            NotionPropertySpec(name="Target Account", type=P.relation, relation_database="B2G Target Accounts"),
            NotionPropertySpec(name="Research Records", type=P.relation, relation_database="B2G SECOP Research"),
        ],
    )

    gtm_outputs = NotionDatabaseSpec(
        name="B2G GTM Outputs",
        properties=[
            NotionPropertySpec(name="Title", type=P.title, required=True),
            NotionPropertySpec(
                name="Type",
                type=P.select,
                options=["outreach", "meeting_prep", "proposal_brief", "business_case"],
            ),
            NotionPropertySpec(name="Content", type=P.rich_text),
            NotionPropertySpec(name="Source Summary", type=P.rich_text),
            NotionPropertySpec(
                name="Approval Status",
                type=P.select,
                options=["draft", "needs_review", "approved", "rejected", "archived"],
            ),
            NotionPropertySpec(name="Target Account", type=P.relation, relation_database="B2G Target Accounts"),
            NotionPropertySpec(name="Opportunity", type=P.relation, relation_database="B2G Opportunities"),
            NotionPropertySpec(name="Research Records", type=P.relation, relation_database="B2G SECOP Research"),
            NotionPropertySpec(name="Created At", type=P.created_time),
            NotionPropertySpec(name="Updated At", type=P.last_edited_time),
        ],
    )

    owners = NotionDatabaseSpec(
        name="B2G Owners",
        properties=[
            NotionPropertySpec(name="Name", type=P.title, required=True),
            NotionPropertySpec(name="Role", type=P.rich_text),
            NotionPropertySpec(name="Email", type=P.email),
            NotionPropertySpec(name="Slack ID", type=P.rich_text),
            NotionPropertySpec(
                name="Notification Preference",
                type=P.select,
                options=["none", "email", "slack", "both"],
            ),
            NotionPropertySpec(name="Active", type=P.checkbox),
        ],
    )

    signals = NotionDatabaseSpec(
        name="B2G Signals",
        properties=[
            NotionPropertySpec(name="Summary", type=P.title, required=True),
            NotionPropertySpec(
                name="Type",
                type=P.select,
                options=[
                    "new_opportunity",
                    "contract_awarded",
                    "leadership_change",
                    "budget_publication",
                    "regulatory_change",
                    "other",
                ],
            ),
            NotionPropertySpec(
                name="Priority",
                type=P.select,
                options=["low", "medium", "high", "urgent"],
            ),
            NotionPropertySpec(name="Source", type=P.rich_text),
            NotionPropertySpec(name="Source URL", type=P.url),
            NotionPropertySpec(name="Detected At", type=P.date),
            NotionPropertySpec(name="Recommended Action", type=P.rich_text),
            NotionPropertySpec(
                name="Notification Status",
                type=P.select,
                options=["not_sent", "queued", "sent", "failed", "suppressed"],
            ),
            NotionPropertySpec(
                name="Action Status",
                type=P.select,
                options=["pending", "in_progress", "done", "dismissed"],
            ),
            NotionPropertySpec(name="Target Account", type=P.relation, relation_database="B2G Target Accounts"),
            NotionPropertySpec(name="Opportunity", type=P.relation, relation_database="B2G Opportunities"),
            NotionPropertySpec(name="Owner", type=P.relation, relation_database="B2G Owners"),
        ],
    )

    return NotionWorkspaceManifest(
        databases=[
            business_profiles,
            icps,
            target_accounts,
            secop_research,
            opportunities,
            gtm_outputs,
            owners,
            signals,
        ]
    )
