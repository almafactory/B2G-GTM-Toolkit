# Feature Specification: Notion-First GTM Workflows

## User Scenarios & Testing

### User Story 1 - Notion is the canonical input (Priority: P1)

An agent preparing research, outreach, meeting prep, or proposal work reads the current account, opportunity, evidence, status, and prior outputs from Notion. Local files are never used as the canonical source for business decisions once the workspace is connected.

**Why this priority**: If the user sees one version of the data in Notion while the agent reads another version from local files, the product becomes unreliable. The same system must be both the user-visible workspace and the agent-visible source of truth.

**Independent Test**: Given a Notion workspace with an updated opportunity and an older local file with conflicting fields, when the agent generates an output, then the output uses the Notion values and ignores the stale local file unless the user explicitly requested a local import or preview.

**Acceptance Scenarios**:

- Given Notion is configured, when an agent needs account, opportunity, research, or output context, then it reads from Notion through the configured Notion access layer.
- Given local files exist with conflicting values, when a real workflow runs, then the local files are not used as business input.
- Given Notion is not configured, when the user asks for a real workflow, then the agent asks to connect Notion instead of falling back silently to local data.
- Given a local file must be used for migration or import, when the workflow completes, then the imported result is written to Notion before it becomes eligible as future input.

### User Story 2 - Outputs live in Notion (Priority: P1)

An Account Executive asks the agent to generate outreach, meeting prep, or a proposal brief for a researched opportunity. The final deliverable is created as a page in the GTM Outputs database in Notion, with useful classification properties and links back to the opportunity, account, and evidence records.

**Why this priority**: GTM outputs are the user-facing artifact. If they remain local files, the workflow feels fragmented and the AE cannot review, classify, approve, or reuse them from the GTM operating system.

**Independent Test**: Given a verified Notion workspace and a valid researched opportunity, when the agent generates an output and applies the write, then a GTM Output page exists in Notion with the rendered content, type, approval status, and relations to the source records.

**Acceptance Scenarios**:

- Given a researched opportunity exists in Notion, when an outreach output is generated, then Notion contains a new or updated GTM Output page of type `outreach`.
- Given an equivalent output already exists for the same opportunity and type, when the output is regenerated, then the existing Notion page is updated instead of duplicated.
- Given Notion is not configured, when the user requests a real output, then the agent explains that Notion must be connected before the result can be stored as the source of truth.

### User Story 3 - Research runs are visible from Notion (Priority: P1)

A GTM user wants to understand what research was performed, when it was performed, and which records came from it without opening local folders. Research execution metadata and SECOP evidence records are available in Notion.

**Why this priority**: Outputs depend on evidence. Notion needs both the evidence records and the research context so downstream outputs can be audited.

**Independent Test**: Given a completed SECOP research workflow, when sync is applied, then Notion shows the individual SECOP records and enough run-level metadata to audit the source, status, and counts.

**Acceptance Scenarios**:

- Given a research workflow completes, when Notion sync is applied, then SECOP records are upserted by source platform and source record ID.
- Given the same research workflow is synced twice, when the second sync runs, then records are updated idempotently and not duplicated.
- Given a user views a synced record in Notion, then they can see the source URL or source identifiers and the related target account when available.

### User Story 4 - Local files are not reusable GTM state (Priority: P2)

A non-technical user should not need to know that the toolkit uses local files internally. Local files may exist for a single command's temporary work, developer tests, or explicit migration/import, but they must not become reusable GTM state.

**Why this priority**: A durable local cache can drift from Notion and create invisible inconsistencies. If local artifacts exist, their lifetime and purpose must be narrow enough that agents cannot accidentally treat them as truth.

**Independent Test**: Given a real workflow has completed, deleting local generated artifacts does not change what the agent will use next time, because the next workflow reads from Notion.

**Acceptance Scenarios**:

- Given a real workflow succeeds, when the agent reports the outcome, then it says whether Notion was written and how many pages were created or updated.
- Given local temporary artifacts are created, when the command finishes successfully, then those artifacts are not required for future business workflows.
- Given Notion write fails after research succeeds, then the agent clearly reports that research completed but Notion was not updated.
- Given Notion write fails, then the agent does not treat any local fallback artifact as canonical input for future real workflows.

### User Story 5 - Outputs are classifiable and reviewable (Priority: P2)

Sales and leadership users can filter GTM outputs by type, account, opportunity, approval status, owner, stage, and recency inside Notion.

**Why this priority**: Storing markdown in Notion is not enough. The output must behave like a managed GTM object.

**Independent Test**: Given multiple generated outputs, when a user filters the GTM Outputs database in Notion, then they can find outputs by business-relevant properties.

**Acceptance Scenarios**:

- Given a generated output, then it has a type, title, approval status, generated timestamp, and source summary.
- Given the output is tied to an opportunity, then the Notion page relates to that opportunity and target account.
- Given the output used SECOP evidence, then the output page relates to the SECOP Research pages used as evidence where those pages exist.

## Requirements

### Functional Requirements

- FR-001: The system MUST support creating GTM Output pages in Notion for outreach, meeting prep, proposal brief, and business case outputs.
- FR-002: The system MUST render the full output content into the Notion page body or an equivalent readable page area, not only into a short property.
- FR-003: The system MUST set classification properties for output type, approval status, source summary, target account, opportunity, related research records, created time, and updated time when available.
- FR-004: The system MUST deduplicate generated outputs by a stable key such as output type plus opportunity plus target account plus source evidence hash.
- FR-005: The system MUST continue to support preview behavior when the user has not authorized a Notion write, but the preview must be clearly labeled as not written to Notion.
- FR-006: The system MUST sync SECOP research records to Notion idempotently before linking outputs to research evidence.
- FR-007: The system MUST not claim a workflow is stored in Notion unless a real Notion write succeeded.
- FR-008: The system MUST keep secrets out of generated pages, logs, and user-facing reports.
- FR-009: The system MUST use Notion as the canonical input for real agent workflows once Notion is configured.
- FR-010: The system MUST NOT use local generated artifacts as reusable GTM state after a successful Notion write.
- FR-011: The system MUST provide a migration path for existing local research runs and output files into Notion before they can be used as canonical input.
- FR-012: The system SHOULD preserve deterministic builders so output content remains testable and reproducible.
- FR-013: The system SHOULD use the Notion MCP layer for agent-side reads/writes when available, while toolkit internals may use the Notion API client behind a compatible abstraction.
- FR-014: The system SHOULD avoid persistent local audit copies unless they serve a concrete maintainer need that Notion cannot satisfy.

### Non-Goals

- NG-001: This feature does not require removing all local files from tests, developer workflows, one-command temporary work, or explicit import/export utilities.
- NG-002: This feature does not require a new web UI.
- NG-003: This feature does not require automatic Slack or email notifications.
- NG-004: This feature does not require LLM-generated content; existing deterministic output builders can remain the first implementation path.

## Success Criteria

- SC-001: A real output generation workflow creates or updates exactly one Notion GTM Output page per output type and opportunity.
- SC-002: Running the same Notion output workflow twice produces zero duplicate GTM Output pages.
- SC-003: A user can review the generated output content directly inside Notion without opening a local file.
- SC-004: A workflow with conflicting local and Notion data uses Notion values for the generated output.
- SC-005: At least 90% of normal user-facing completion reports reference Notion outcomes rather than local file paths.
- SC-006: Existing unit and integration tests pass, with added coverage for Notion input resolution, GTM Output mapping, and idempotent output upsert behavior.

## Open Questions

- OQ-001: Should research run metadata live in a new `B2G Research Runs` database, or should run metadata remain as properties on SECOP Research records and related GTM Outputs?
- OQ-002: Should generated output content be stored only in the Notion page body, or duplicated into a `Content` property for search/export convenience?
- OQ-003: Which local artifacts, if any, are still justified for maintainer diagnostics after Notion becomes canonical?
- OQ-004: Should output generation start from a Notion Opportunity page ID, a Notion database filter, or both?
