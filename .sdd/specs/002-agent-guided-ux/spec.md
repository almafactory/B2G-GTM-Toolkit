# Feature Specification: Agent-Guided UX for Non-Technical B2G Users

**Feature ID**: `002-agent-guided-ux`
**Created**: 2026-05-10
**Status**: Draft

## User Scenarios & Testing

### User Story 1 - Guided Notion Onboarding (Priority: P1)

A non-technical user wants the toolkit connected to Notion without knowing what an integration token, page ID, terminal command, virtual environment, fixture, dry-run, or data source is. The agent explains only the business action needed, helps the user obtain the required Notion access, configures the local environment, verifies the workspace, creates the required GTM databases when authorized, and reports the outcome in plain language.

**Why this priority**: Notion is the durable GTM system of record. If setup feels technical, the product fails before users get value.

**Independent Test**: Start from a repo with no `.env` and an empty Notion page. A tester who has never used the CLI should be able to follow agent prompts and end with all required Notion databases verified.

**Acceptance Scenarios**:

1. **Given** the user has no `.env`, **when** they ask to connect Notion, **then** the agent asks for or guides them to obtain only the Notion integration token and Notion page URL.
2. **Given** the user provides a Notion page URL, **when** setup begins, **then** the agent extracts the page ID without asking the user to understand URL structure.
3. **Given** valid Notion credentials and an accessible page, **when** setup runs, **then** the agent creates or verifies the workspace and summarizes the created bases without exposing implementation details.
4. **Given** Notion rejects access, **when** setup fails, **then** the agent explains the likely permission issue and gives the smallest next action in Notion UI terms.

---

### User Story 2 - One-Click Trial Run (Priority: P1)

A user wants to "try the toolkit" and see useful output without learning commands, local test data jargon, or Python dependency details. The agent runs the smallest safe trial, distinguishes sample data from real SECOP/Notion data in plain language, and offers the next meaningful business step.

**Why this priority**: The first trial should build trust. Terms like "fixtures", "offline", or "email-validator" confuse users and hide what actually happened.

**Independent Test**: Ask the agent to try the toolkit from a fresh clone. The agent should install missing dependencies, run sample validation/research, sync to Notion if configured, and report what was real versus sample.

**Acceptance Scenarios**:

1. **Given** dependencies are missing, **when** the agent runs the trial, **then** it fixes setup silently where safe and only reports user-impacting outcomes.
2. **Given** the trial uses sample data, **when** reporting results, **then** the agent says "sample data included with the repo" instead of "fixtures" or "sin red".
3. **Given** Notion is not configured, **when** a trial needs Notion, **then** the agent guides connection before claiming data was mounted.
4. **Given** Notion is configured, **when** sample SECOP data is synced, **then** the agent confirms exactly how many records were created or updated.

---

### User Story 3 - Agent-First Operating Model (Priority: P1)

A user interacts only with the coding agent in natural language. The agent chooses the right skill, CLI operation, setup repair, verification, and output generation without teaching the user command syntax unless explicitly requested.

**Why this priority**: The desired product experience is agent-operated, not terminal-operated. Documentation should teach agents how to behave, not force users to become operators.

**Independent Test**: Give the agent a natural-language goal such as "quiero preparar outreach para esta oportunidad". The agent should collect missing business inputs, run the needed workflow, store outputs, and produce a concise human result without listing commands.

**Acceptance Scenarios**:

1. **Given** a user asks for a business outcome, **when** a CLI command is needed, **then** the agent runs it and summarizes the result without exposing command syntax by default.
2. **Given** the user is blocked by missing credentials or permissions, **when** the agent needs user action, **then** it asks for one concrete action at a time.
3. **Given** multiple setup steps are required, **when** the agent reports progress, **then** it groups them by user-visible outcome, not by internal tools.
4. **Given** the agent encounters a dependency or API-version issue, **when** it fixes it, **then** it documents the friction and updates guidance so future agents do not repeat the mistake.

---

### User Story 4 - Low-Friction Future Setup (Priority: P2)

A team wants onboarding to become progressively easier across sessions: fewer manual IDs, fewer ambiguous docs, safer credential handling, and clearer automation boundaries.

**Why this priority**: The current flow can work, but the product should become resilient enough that a new user can onboard with minimal agent babysitting.

**Independent Test**: Reset local configuration and onboard again using only a Notion page URL and token. The second run should be faster, idempotent, and less error-prone than the initial manual setup.

**Acceptance Scenarios**:

1. **Given** an existing Notion workspace, **when** setup runs again, **then** it detects existing databases and does not create duplicates.
2. **Given** data already synced, **when** sync runs again, **then** it updates existing records instead of duplicating them.
3. **Given** credentials are present in local config, **when** the agent reports status, **then** it never prints secrets.
4. **Given** setup docs mention technical concepts, **when** they are user-facing, **then** they define or hide those concepts.

## Requirements

### Functional Requirements

- FR-001: The system MUST provide an agent-facing onboarding guide that prioritizes natural-language user outcomes over CLI instructions.
- FR-002: The system MUST document the exact Notion setup flow for non-technical users, including integration creation, page sharing, page URL capture, and permission troubleshooting.
- FR-003: The system MUST maintain a friction log of confusing terms, failed assumptions, and required product/doc improvements discovered during real trials.
- FR-004: The system MUST instruct agents not to claim data is in Notion unless a real Notion sync has succeeded.
- FR-005: The system MUST instruct agents to avoid unexplained terms such as "fixture", "offline", "dry-run", "stub", and dependency package names in user-facing summaries.
- FR-006: The system MUST define how agents should handle secrets: do not print them back, keep them in ignored local config, and recommend rotation when secrets appear in chat.
- FR-007: The system MUST distinguish sample-data trials from real SECOP/Notion runs in plain language.
- FR-008: The system MUST make Notion setup idempotent: existing databases should be reused where possible and repeated syncs should not duplicate records.
- FR-009: The system MUST include testable tasks for improving setup automation, docs, and agent behavior.
- FR-010: The system SHOULD provide a single agent-operated "guided setup" flow in a future implementation so users do not need to know individual commands.

### Non-Functional Requirements

- NFR-001: User-facing explanations MUST be understandable to a non-technical founder or sales operator.
- NFR-002: Agent-facing docs MAY include commands, schemas, and implementation details, but must label them as internal.
- NFR-003: Setup must be safe by default: no destructive Notion writes, no credential commits, and no duplicate data on repeated sync.
- NFR-004: The flow should minimize context switching between Cursor, terminal, browser, and Notion UI.

## Success Criteria

- SC-001: A first-time user can connect Notion with agent guidance in under 10 minutes after obtaining workspace access.
- SC-002: A trial run report states clearly whether it used sample data, real SECOP data, and/or real Notion writes.
- SC-003: Future agents can read `CLAUDE.md` and perform setup without asking the user to run terminal commands.
- SC-004: Re-running setup and sync does not create duplicate Notion databases or duplicate SECOP research records.
- SC-005: No user-facing onboarding document requires understanding Python virtual environments, CLI syntax, package dependencies, fixtures, stubs, dry-runs, or data source API internals.
