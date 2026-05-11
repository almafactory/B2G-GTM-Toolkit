# Tasks: Notion-First GTM Workflows

## Phase 1: Setup

- [ ] T001 Review current Notion writer protocol and fake client coverage in `src/b2g_gtm_toolkit/notion/write.py` and `tests/`.
- [ ] T002 Review current GTM Output schema in `src/b2g_gtm_toolkit/models/gtm.py` and Notion manifest in `src/b2g_gtm_toolkit/models/notion.py`.
- [ ] T003 Decide whether `B2G Research Runs` is in-scope for the first implementation slice.
- [ ] T004 Decide the agent/tool boundary: Notion MCP for agent-side canonical operations where available, toolkit Notion API client for internal CLI operations behind the same conceptual contract.

## Phase 2: Canonical Notion Input

- [ ] T005 Add a Notion reader abstraction for retrieving pages and related records from the GTM databases.
- [ ] T006 Add support for reading an Opportunity page and its related Target Account.
- [ ] T007 Add support for reading related SECOP Research evidence records.
- [ ] T008 Add support for reading prior GTM Outputs related to the same Opportunity or Target Account.
- [ ] T009 Convert retrieved Notion pages into the existing output builder context shape.
- [ ] T010 Add tests proving that when Notion is configured, stale/conflicting local files are ignored for real workflows.

## Phase 3: Foundational Notion Output Mapping

- [ ] T011 [P] Add or extend `GtmOutput` fields needed for stable output identity, channel, owner, and stage in `src/b2g_gtm_toolkit/models/gtm.py`.
- [ ] T012 [P] Update `B2G GTM Outputs` Notion schema with dedupe and classification properties in `src/b2g_gtm_toolkit/models/notion.py`.
- [ ] T013 Add `gtm_output_properties()` mapper in a new `src/b2g_gtm_toolkit/notion/output_mapper.py`.
- [ ] T014 Add `dedupe_filter_for_gtm_output()` in `src/b2g_gtm_toolkit/notion/output_mapper.py`.
- [ ] T015 Extend Notion writer support for page body blocks if current client wrapper only writes properties.
- [ ] T016 Add unit tests for output property mapping, dedupe key generation, and body block conversion.

## Phase 4: User Story 1 - Notion Is Canonical Input (P1)

- [ ] T017 Add CLI input option for `--opportunity-page` or equivalent Notion-native opportunity selector.
- [ ] T018 Make the Notion-native path the agent-recommended path for real output generation.
- [ ] T019 Keep local `--source` JSON support only for tests, previews, or explicit import/migration.
- [ ] T020 If Notion is configured and local source data is supplied for a real workflow, require importing/syncing it into Notion first.
- [ ] T021 Add integration tests for Notion page input to output generation.

## Phase 5: User Story 2 - Outputs Live In Notion (P1)

- [ ] T022 Update `b2g-gtm output create` to build a `GtmOutput` object after rendering markdown.
- [ ] T023 Add CLI flags for Notion output persistence, such as `--to-notion` and `--apply`.
- [ ] T024 In preview mode, report that the output was generated but not written to Notion and is not canonical.
- [ ] T025 In apply mode, verify Notion configuration and locate `B2G GTM Outputs`.
- [ ] T026 In apply mode, upsert the GTM Output page by stable output key.
- [ ] T027 Ensure a repeated output generation updates the existing Notion page instead of creating a duplicate.
- [ ] T028 Add integration tests with a fake Notion client for create and update behavior.

## Phase 6: User Story 3 - Research Runs Visible From Notion (P1)

- [ ] T029 Confirm current SECOP research sync remains idempotent by Source Platform and Source Record ID.
- [ ] T030 Make SECOP research write-through to Notion the real workflow result, not a local run folder.
- [ ] T031 Add relation resolution from synced SECOP Research pages to generated GTM Outputs.
- [ ] T032 If `B2G Research Runs` is accepted, add its Notion schema and mapper.
- [ ] T033 If `B2G Research Runs` is accepted, write run metadata during research sync.
- [ ] T034 Add tests proving synced evidence can be linked to a GTM Output page.

## Phase 7: User Story 4 - Local Files Are Not Reusable GTM State (P2)

- [X] T035 Update agent-facing skills so real workflows describe Notion outcomes and canonical Notion input.
- [X] T036 Update README developer path to explain local files as tests/import/export/temporary diagnostics only.
- [X] T037 Update non-technical docs to say generated deliverables and future inputs live in Notion after a real write.
- [ ] T038 Adjust CLI success messages so user-facing agent reports avoid local paths by default.
- [ ] T039 Add an explicit developer/debug option for exporting local markdown if needed.
- [X] T040 Add tests or docs proving local artifacts are not required after a successful Notion write.

## Phase 8: User Story 5 - Outputs Are Classifiable And Reviewable (P2)

- [ ] T041 Add Stage, Channel, Output Key, Source Evidence Hash, and Owner properties to `B2G GTM Outputs` if approved.
- [ ] T042 Map output type to a practical default channel: outreach to email/linkedin, meeting prep to meeting, proposal brief/business case to proposal.
- [ ] T043 Ensure Approval Status remains human-controlled after draft generation.
- [ ] T044 Add tests for classification fields and default values.

## Phase 9: Migration

- [X] T045 Add a migration command for existing local output markdown files into `B2G GTM Outputs`.
- [ ] T046 Add a migration command or documented internal path for existing `data/runs` research folders.
- [X] T047 Ensure migration can run in preview mode and apply mode.
- [ ] T048 After migration, ensure future workflows read the imported Notion records rather than the original local files.
- [X] T049 Add migration tests for no duplicate pages on repeated runs.

## Phase 10: Verification And Release

- [ ] T050 Run full pytest suite.
- [ ] T051 Run lints on edited Python files.
- [ ] T052 Run Notion verification after schema changes.
- [ ] T053 Perform one live output write to Notion with real credentials, if authorized.
- [ ] T054 Confirm user-facing report includes Notion input source, Notion write result, created/updated counts, and next business step.
