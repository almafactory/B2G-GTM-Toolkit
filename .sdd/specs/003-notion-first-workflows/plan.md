# Implementation Plan: Notion-First GTM Workflows

## Summary

Move the default GTM workflow from local-file-centered execution to Notion-canonical execution. Notion becomes both the place users see GTM data and the place agents read GTM input from. Local files may still exist for tests, explicit import/export, or temporary command internals, but they must not become reusable GTM state.

The first implementation slice should establish canonical Notion reads for opportunities, accounts, evidence, and prior outputs. The output writer should then create or update `B2G GTM Outputs` pages from that Notion input. Local JSON source files should move to a developer/import path, not the default agent path.

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**: Typer, Pydantic, Notion client, python-dotenv, pytest
- **Storage**: Notion databases/data sources as canonical GTM system; local files only for tests, explicit import/export, or temporary command internals
- **Testing**: pytest unit tests for mapping/dedupe; integration tests with fake Notion client; live verification when credentials are configured
- **Current State**:
  - SECOP research writes `data/runs/<run-id>/secop-research.jsonl` and `manifest.json`.
  - `notion sync --run <run-id> --apply` can upsert SECOP research records into Notion.
  - `output create` renders markdown from a local source JSON and can write a local markdown file.
  - `B2G GTM Outputs` exists in the Notion schema, but there is no writer path for GTM outputs yet.
  - There is no Notion reader path for output generation yet, which is the core drift risk.

## Guiding Decisions

### Notion is the canonical source of truth

For real workflows, the agent should read input from Notion and report Notion outcomes. If Notion and local files disagree, Notion wins. Local paths should be reserved for maintainer/debug context and should not be used as future business input.

### Local persistence should be exceptional

Persistent local copies are more dangerous than useful if they can drift from Notion. The preferred default is no durable local business state. Acceptable local uses are:

- test fixtures;
- explicit import/export requested by a maintainer;
- temporary files inside one command execution;
- failure diagnostics that are clearly marked as not canonical and not eligible as future input.

### Keep deterministic builders

The existing output builders should remain pure functions. The Notion layer should wrap their result by rendering markdown, mapping properties, and writing a Notion page. This keeps snapshot tests useful and avoids mixing business content generation with persistence.

### Page body stores the readable artifact

The full outreach, meeting prep, or proposal should be stored in the Notion page body. A short `Content` property can remain for summary/search, but rich content should not be squeezed into a property.

### Idempotency is mandatory

Research records and generated outputs must be upserted. Re-running the same workflow should update existing Notion pages, not create duplicates.

## Proposed User Experience

1. User asks: "Genera outreach para esta oportunidad."
2. Agent verifies Notion configuration and required databases.
3. Agent resolves the source opportunity and related evidence from Notion.
4. Agent generates the output using the existing deterministic builder.
5. Agent writes or updates a page in `B2G GTM Outputs`.
6. Agent reports:
   - whether Notion was written;
   - output type and title;
   - created/updated count;
   - what the AE should do next.

If Notion is unavailable, the agent should ask to connect Notion before claiming a real workflow. A preview can be offered only as a clearly labeled preview. That preview must not become future input until imported into Notion.

## Project Structure

```text
src/b2g_gtm_toolkit/
  cli.py
  notion/
    write.py
    read.py                   # new: canonical Notion opportunity/evidence input
    output_mapper.py          # new: GtmOutput -> Notion properties/body/dedupe
  outputs/
    outreach.py
    meeting_prep.py
    proposal_brief.py
    render.py
tests/
  unit/
    test_notion_output_mapper.py
    test_outputs.py
  integration/
    test_notion_output_sync.py
.sdd/specs/003-notion-first-workflows/
  spec.md
  plan.md
  data-model.md
  tasks.md
```

## Implementation Phases

### Phase 1: Canonical Notion read path

- Add a Notion reader abstraction for agent/toolkit workflows.
- Resolve Opportunity, Target Account, SECOP Research, and prior GTM Outputs from Notion.
- Convert Notion pages into the existing output builder context shape.
- Add tests proving stale local files are ignored when Notion is configured.

### Phase 2: GTM Output write path

- Add a Notion mapping function for `GtmOutput`.
- Add dedupe logic for generated outputs.
- Extend the Notion writer protocol to support page body children when creating/updating pages.
- Add CLI support for Notion-native output generation from a Notion opportunity/page identifier.
- Keep local source preview behavior available for developer/import use, but not as the recommended agent path.

### Phase 3: Research write-through to Notion

- Make SECOP research write to Notion as the durable result.
- Avoid leaving durable local `data/runs` as the normal next-step input.
- If an intermediate local file is needed, mark it temporary/non-canonical and clean it up or quarantine it after a successful write.

### Phase 4: Research run visibility

- Decide whether to add a `B2G Research Runs` database.
- If added, write run metadata to Notion and relate SECOP Research records to the run page.
- If not added, improve run-level fields on SECOP Research and GTM Outputs.
- Update user-facing reports so local run IDs are internal unless needed for support.

### Phase 5: Migration and cleanup

- Add a migration command for existing local outputs and research runs.
- Update skills and docs so generated outputs are expected to land in Notion.
- Make local artifact creation exceptional and explicit in developer docs.
- Add regression tests for idempotent re-runs and no duplicate output pages.

## Data Flow

```text
Notion Opportunity + Target Account + SECOP Research
              ↓
      output builder context
              ↓
 deterministic markdown render
              ↓
       GtmOutput model
              ↓
 Notion properties + page body + dedupe key
              ↓
 B2G GTM Outputs page
```

## CLI/API Shape

Initial Notion-canonical CLI:

```text
b2g-gtm output create --type outreach --opportunity-page <notion-page-id> --to-notion --apply
```

Developer/import preview path:

```text
b2g-gtm output preview --type outreach --source examples/opportunity.json
```

Agent-facing behavior should hide these commands unless the user asks for technical detail.

## Risks

- **Notion body rendering complexity**: Markdown must be converted to Notion blocks. Mitigation: start with headings, paragraphs, bullets, numbered lists, and links; keep advanced formatting for later.
- **Relation resolution**: Imported or newly synced records may not have page IDs immediately available. Mitigation: write to Notion first, then query by stable IDs before generating downstream outputs.
- **Duplicate outputs**: Weak dedupe keys can create clutter. Mitigation: include type, opportunity, target account, and source evidence hash.
- **Property length limits**: Full content may exceed rich text property limits. Mitigation: store full content in page body, summary in property.
- **User trust**: Agents may overstate completion. Mitigation: reports must distinguish preview from real Notion write.
- **Local drift**: Persistent local artifacts can contradict Notion. Mitigation: do not use them as canonical input; force import into Notion first.

## Open Decisions

- Add `B2G Research Runs` now, or defer until scheduled/recurring research exists?
- Store markdown source as an attachment-like code block in the page body, or only store rendered Notion blocks?
- Should `--out` remain on `output create`, or move to an explicit `output preview/export` command later so output generation stays Notion-canonical by default?
