# Tasks: Agent-Guided UX for Non-Technical B2G Users

**Feature ID**: `002-agent-guided-ux`
**Prerequisites**: `spec.md`, `plan.md`

## Format

```text
- [ ] T001 [P] [US1] Description with file path
```

- `[P]`: Can run in parallel after dependencies are satisfied.
- `[US#]`: Task belongs to a user story from `spec.md`.

---

## Phase 1: Setup

**Purpose**: Establish the SDD documentation scaffold for the guided UX initiative.

- [X] T001 Create `.sdd/specs/002-agent-guided-ux/spec.md`.
- [X] T002 Create `.sdd/specs/002-agent-guided-ux/plan.md`.
- [X] T003 Create `.sdd/specs/002-agent-guided-ux/tasks.md`.
- [X] T004 Create `.sdd/specs/002-agent-guided-ux/checklists/requirements.md`.

**Checkpoint**: The feature has SDD spec, plan, tasks, and checklist files.

---

## Phase 2: Foundational Agent Guidance

**Purpose**: Give future agents a clear operating contract so they stop treating non-technical users like CLI operators.

- [X] T005 [P] [US3] Create root `CLAUDE.md` with agent behavior rules for non-technical onboarding.
- [X] T006 [P] [US2] Create `docs/ux-friction-log.md` documenting observed setup friction and future fixes.
- [X] T007 [P] [US1] Create `docs/non-technical-onboarding.md` with plain-language Notion setup guidance.
- [X] T008 [US3] Update `docs/agent-usage.md` to distinguish agent-facing internals from user-facing guidance.

**Checkpoint**: A future agent can read repo docs and know to run setup internally, explain simply, and avoid exposing commands by default.

---

## Phase 3: User Story 1 - Guided Notion Onboarding (P1)

**Goal**: Make Notion setup feel like a guided product flow, not a CLI tutorial.

**Independent Test**: Start with no `.env`, an empty Notion page, and a non-technical user. The agent obtains the token/page URL, configures `.env`, verifies access, applies setup, and reports success plainly.

- [X] T009 [US1] Document the user action sequence for Notion integration creation and page sharing in `docs/non-technical-onboarding.md`.
- [X] T010 [US1] Document agent handling for pasted Notion URLs, token secrecy, and token rotation in `CLAUDE.md`.
- [X] T011 [US1] Add or update tests covering `.env` loading by the CLI.
- [X] T012 [US1] Add tests covering Notion data source verification and property mapping with a fake client.
- [X] T013 [US1] Update `skills/b2g-notion-gtm-os/SKILL.md` so it reflects real setup/sync behavior instead of saying writes are blocked.

**Checkpoint**: The agent can connect and verify Notion without making the user understand page IDs or commands.

---

## Phase 4: User Story 2 - One-Click Trial Run (P1)

**Goal**: Make "try the toolkit" produce a clear and trustworthy result.

**Independent Test**: Ask the agent to try the toolkit. It runs the sample workflow, fixes safe setup issues, syncs to Notion if configured, and reports sample versus real outputs.

- [X] T014 [US2] Document preferred language for sample data, local test runs, dry-runs, and dependencies in `CLAUDE.md`.
- [X] T015 [US2] Update `README.md` to avoid making the first-use path sound like the user must operate the terminal.
- [X] T016 [US2] Add an agent-facing checklist for trial runs in `docs/non-technical-onboarding.md`.
- [X] T017 [US2] Add tests or snapshots proving repeated Notion sync updates existing SECOP records instead of duplicating them.

**Checkpoint**: Trial reports are understandable and do not overclaim what was written to Notion.

---

## Phase 5: User Story 3 - Agent-First Operating Model (P1)

**Goal**: Make natural-language business outcomes the primary interface.

**Independent Test**: Ask for a business outcome, not a command. The agent chooses the workflow, asks for missing inputs, runs internals, stores outputs, and reports next business steps.

- [X] T018 [US3] Add examples to `CLAUDE.md` for good and bad explanations.
- [X] T019 [US3] Update skill docs to instruct agents to ask one user action at a time when external permissions are needed.
- [X] T020 [US3] Define an agent status-report format that avoids command dumps and focuses on outcomes.
- [X] T021 [US3] Decide whether to add a single `guided setup` CLI command for agents and capture the decision in this spec folder.

**Checkpoint**: Future agents have concrete examples of how to behave in this repo.

---

## Phase 6: Polish & Cross-Cutting

- [X] T022 Run `pytest` after implementation changes.
- [X] T023 Check lints for edited Python files.
- [X] T024 Review `.env.example` and `.gitignore` to ensure secrets remain safe.
- [X] T025 Update this `tasks.md` as implementation progresses.
