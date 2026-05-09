# Feature Specification: B2G-GTM-Toolkit

**Feature ID**: `001-b2g-gtm-toolkit`
**Created**: 2026-05-09
**Status**: Draft

## User Scenarios & Testing

### User Story 1 - Define a B2G ICP From Real Customer Context (Priority: P1)

A B2G contractor or GTM team member provides baseline business context, current clients, competitors, offer details, best customers, poor-fit customers, and market assumptions. The toolkit guides the agent through the right questions, uses the existing GTM skills as the baseline methodology, and produces a practical Ideal Customer Profile for Colombian public-sector buyers.

**Why this priority**: The ICP is the foundation for every downstream workflow. If the system does not identify which public entities are worth pursuing, SECOP research, outreach, proposals, and meeting preparation will produce generic or low-value outputs.

**Independent Test**: Provide a sample contractor profile with 5-10 clients and verify that the toolkit produces an ICP with target entity types, fit criteria, disqualifiers, buying triggers, target roles, and confidence level.

**Acceptance Scenarios**:

1. **Given** a user with partial but usable customer and offer context, **When** they start the ICP workflow, **Then** the toolkit asks for missing baseline inputs before producing the ICP.
2. **Given** a user with prior clients such as alcaldias or gobernaciones, **When** the ICP workflow completes, **Then** the output identifies target public-entity segments and explains why they are a good fit.
3. **Given** weak or insufficient customer evidence, **When** the toolkit produces the ICP, **Then** it labels the ICP as a hypothesis and lists the evidence still needed to validate it.

---

### User Story 2 - Build a Target Account List From the ICP (Priority: P1)

A GTM user takes the ICP output and asks the toolkit to identify public entities and accounts that match the target profile. The toolkit turns ICP criteria into a structured target-account list that can guide SECOP research and commercial prioritization.

**Why this priority**: Users need an actionable list before they can research contracts, buying history, upcoming opportunities, and account-specific messages.

**Independent Test**: Use a completed ICP and verify that the toolkit returns a prioritized account list with fit rationale, account type, region/category when available, and next research action.

**Acceptance Scenarios**:

1. **Given** a completed ICP, **When** the user starts prospecting, **Then** the toolkit produces accounts grouped or ranked by fit.
2. **Given** a target account candidate, **When** the account lacks enough evidence to match the ICP, **Then** the toolkit marks it as uncertain instead of treating it as qualified.
3. **Given** target-account criteria involving public-entity type, geography, category, or buying pattern, **When** the list is created, **Then** each account includes the reason it belongs in the list.

---

### User Story 3 - Research SECOP Opportunities and Buying History (Priority: P1)

A contractor wants to find tenders, contracts, and opportunities in SECOP that are relevant to their ICP and offer. The toolkit helps run repeatable research against SECOP data, captures historical deals and current opportunities, and transforms the findings into structured account and opportunity intelligence.

**Why this priority**: The core value of the product is reducing manual SECOP research and helping contractors identify more relevant public-sector opportunities each month.

**Independent Test**: Provide a target account or ICP search criteria and verify that the toolkit produces structured research outputs for contracts, opportunities, buyers, suppliers, dates, values, relevance rationale, and recommended next action.

**Acceptance Scenarios**:

1. **Given** a target-account list, **When** SECOP research runs, **Then** the toolkit records relevant historical contracts and active or recent opportunities for each account where data exists.
2. **Given** an opportunity found in SECOP, **When** the toolkit evaluates it, **Then** it summarizes why it is relevant or not relevant to the user's offer.
3. **Given** repeated research needs, **When** a user provides the same inputs over time, **Then** the toolkit supports repeatable collection without requiring the agent to manually browse and copy SECOP data.

---

### User Story 4 - Store GTM Intelligence in Notion (Priority: P1)

A team wants a persistent GTM operating system where ICPs, accounts, SECOP findings, opportunities, buying signals, outreach plans, meeting briefs, proposals, and ownership are stored in structured Notion databases.

**Why this priority**: The output must be reusable by sales teams, entrepreneurs, and account executives. Without structured storage, the toolkit only creates one-off documents and cannot support recurring workflows.

**Independent Test**: Run the workflow for one ICP and three accounts, then verify that the resulting records can be found in the expected Notion databases with linked account, opportunity, and research data.

**Acceptance Scenarios**:

1. **Given** a workspace without the required Notion structure, **When** the user starts a workflow that needs storage, **Then** the toolkit verifies whether the required databases exist before saving research.
2. **Given** researched SECOP data, **When** the data is stored, **Then** it is linked to the relevant ICP, target account, opportunity, and responsible person when known.
3. **Given** duplicate or previously researched records, **When** the toolkit saves new findings, **Then** it avoids creating confusing duplicate records and preserves the latest known status.

---

### User Story 5 - Generate Account Executive Work Products (Priority: P2)

An account executive uses saved account and opportunity intelligence to create outreach campaigns, meeting preparation briefs, proposal briefs, and business cases for public-sector opportunities.

**Why this priority**: After research is captured, the next value comes from converting that intelligence into sales execution assets that save time and improve quality.

**Independent Test**: Select one researched opportunity and verify that the toolkit creates an outreach sequence, a meeting prep brief, and a proposal/business-case brief using the stored research as source material.

**Acceptance Scenarios**:

1. **Given** an account with SECOP buying history, **When** the user asks for outreach, **Then** the toolkit creates a campaign tied to the account's needs, historical purchasing behavior, and likely buying triggers.
2. **Given** an upcoming meeting, **When** the user asks for preparation, **Then** the toolkit produces a concise brief with account context, opportunity context, key questions, likely objections, and recommended ask.
3. **Given** a relevant tender opportunity, **When** the user asks for proposal support, **Then** the toolkit produces a brief that helps evaluate fit, requirements, positioning, and next steps.

---

### User Story 6 - Monitor Buying Signals and Notify Owners (Priority: P2)

A GTM team wants ongoing enrichment of leads, detection of buying signals, and notifications to the responsible owner when a relevant opportunity or account signal appears.

**Why this priority**: B2G opportunities are time-sensitive. The toolkit should help teams act on signals instead of relying only on manual periodic research.

**Independent Test**: Configure a sample target account and responsible owner, simulate or detect a new relevant signal, and verify that the system records the signal and notifies the owner with recommended action.

**Acceptance Scenarios**:

1. **Given** target accounts with owners, **When** new relevant SECOP opportunities or buying signals appear, **Then** the toolkit creates a signal record and identifies the responsible owner.
2. **Given** a signal with weak relevance, **When** it is evaluated, **Then** the toolkit marks it lower priority or suppresses unnecessary notification.
3. **Given** recurring enrichment, **When** the toolkit updates account data, **Then** it preserves past research and highlights what changed.

---

### Edge Cases

- The user has no existing clients and can only provide dream accounts or assumptions.
- The user's best customers do not map cleanly to public-sector entity categories.
- SECOP data is incomplete, duplicated, stale, or inconsistent across records.
- Multiple opportunities appear relevant but have conflicting timelines, requirements, or budget signals.
- A Notion workspace is missing required databases or has a similar but incompatible schema.
- The same public entity appears under different names or spellings.
- A lead owner is missing, inactive, or responsible for too many accounts.
- A tender is relevant commercially but impossible to pursue because of timing, eligibility, documentation, or qualification constraints.

## Requirements

### Functional Requirements

- **FR-001**: System MUST guide users through baseline GTM inputs required to define an ICP, including offer, current clients, best customers, worst customers, competitors, target market assumptions, and company stage.
- **FR-002**: System MUST use the methodology represented by the sales skills in `E:\skills\ventas` as the baseline for ICP definition, prospecting, account research, qualification, outreach, meeting preparation, and signal-based outbound.
- **FR-003**: System MUST produce an ICP briefing that includes firmographic/public-entity fit criteria, situational criteria, buying triggers, buying committee roles, disqualifiers, observable signals, and confidence level.
- **FR-004**: System MUST convert the ICP into a target-account list of public-sector entities or account segments relevant to Colombian B2G sales.
- **FR-005**: System MUST support research workflows that collect SECOP buying history, contracts, suppliers, opportunity details, dates, values, and relevance rationale for target accounts and opportunities.
- **FR-006**: System MUST distinguish between active opportunities, historical contracts, account-level intelligence, and buying signals.
- **FR-007**: System MUST structure research outputs so they can be reused by account executives for outreach, meetings, proposals, and business cases.
- **FR-008**: System MUST verify that required Notion databases and relationships exist before saving structured GTM intelligence.
- **FR-009**: System MUST store or update ICPs, accounts, opportunities, SECOP research records, signals, outreach assets, meeting briefs, proposal briefs, and responsible owners in Notion.
- **FR-010**: System MUST detect and handle duplicate accounts, duplicate opportunities, or repeated SECOP findings in a way that keeps the workspace understandable.
- **FR-011**: System MUST generate outreach campaign outputs from stored account, opportunity, and signal intelligence.
- **FR-012**: System MUST generate meeting preparation briefs from stored account and opportunity intelligence.
- **FR-013**: System MUST generate proposal or business-case briefs for selected SECOP opportunities.
- **FR-014**: System MUST support recurring enrichment of lead and account data.
- **FR-015**: System MUST support recurring buying-signal detection and notify the responsible owner when a relevant signal is found.
- **FR-016**: System MUST label uncertain, incomplete, or low-confidence outputs instead of presenting them as validated facts.
- **FR-017**: System MUST preserve source references or provenance for SECOP-derived findings so users can trace why an opportunity or account was recommended.
- **FR-018**: System MUST allow the user to review and approve key outputs before they are used for downstream workflows.
- **FR-019**: System MUST support Spanish-language B2G workflows and outputs, with English support where useful for tool commands or technical setup.
- **FR-020**: System MUST provide a toolkit-style setup that can be installed or reused locally by AI coding agents such as Codex or Claude Code.
- **FR-021**: System MUST [NEEDS CLARIFICATION: define which Notion workspace/database naming conventions should be created by default].
- **FR-022**: System MUST [NEEDS CLARIFICATION: define the exact notification channels for responsible owners, such as Notion mentions, email, Slack, or another channel].
- **FR-023**: System MUST [NEEDS CLARIFICATION: define whether the first release targets only Colombia SECOP data or should support other public procurement sources later].

### Key Entities

- **Business Profile**: The contractor or B2G company using the toolkit, including what it sells, current customers, competitors, strengths, constraints, and market assumptions.
- **ICP**: The ideal public-sector customer profile derived from customer context and research, including target entity types, fit rules, disqualifiers, buying triggers, and confidence level.
- **Target Account**: A public entity or account segment that matches the ICP and should be researched or pursued.
- **SECOP Research Record**: A structured finding from SECOP, including contract or opportunity information, source reference, relevance rationale, and relationship to an account.
- **Opportunity**: A specific tender, procurement process, contract opportunity, or actionable commercial event that may justify outreach or proposal work.
- **Buying Signal**: A relevant change or event indicating a target account may be worth contacting or monitoring.
- **Responsible Owner**: The person accountable for acting on an account, opportunity, or signal.
- **Outreach Campaign**: A planned set of messages or actions based on account intelligence and buying signals.
- **Meeting Prep Brief**: A concise preparation artifact for an account or opportunity meeting.
- **Proposal / Business Case Brief**: A structured artifact that helps evaluate, position, and prepare for a public-sector opportunity.
- **Notion GTM Workspace**: The linked database system where toolkit outputs are stored, related, and updated.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A user can complete the baseline ICP workflow and receive an ICP briefing without manually deciding which GTM questions to ask.
- **SC-002**: The toolkit can transform one ICP into a prioritized account list with clear fit rationale.
- **SC-003**: For a selected target account or opportunity, the toolkit can produce structured SECOP research records that are reusable in later workflows.
- **SC-004**: Required Notion databases can be verified or prepared before research outputs are stored.
- **SC-005**: A saved opportunity can be used to generate at least three account-executive outputs: outreach, meeting prep, and proposal/business-case brief.
- **SC-006**: Recurring enrichment can identify a new or changed signal and route it to a responsible owner.
- **SC-007**: Users can process more relevant B2G opportunities per month than they could with fully manual SECOP research and document preparation.
- **SC-008**: Users can trace each recommended account, opportunity, or signal back to its underlying evidence or source rationale.
