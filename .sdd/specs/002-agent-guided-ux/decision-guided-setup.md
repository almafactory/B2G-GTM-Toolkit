# Decision: Guided Setup CLI Command

**Status**: Deferred
**Date**: 2026-05-10

## Decision

Do not add a single `guided setup` CLI command in Phase 5. Keep the current CLI commands as the internal execution layer and let the agent orchestrate them behind a conversational setup flow.

## Rationale

- Phase 5 is docs-focused; adding a new command would require Python implementation and tests.
- The existing commands already cover verification, setup planning, setup apply, research, and sync.
- The user experience problem can be solved immediately by agent guidance: ask for one external permission at a time, run internals directly, and report outcomes instead of commands.
- A single command is still valuable later, but it needs design around secrets, Notion permission failures, idempotent setup, and safe reporting.

## Future Shape

A future `guided setup` command should be agent-operated, not user-facing by default. It should:

- detect existing local configuration;
- accept or derive the Notion page ID from a page URL;
- verify access before planning writes;
- show a preview before creating or updating Notion databases;
- require explicit authorization before writing;
- verify again after writing;
- report using the outcome-focused agent status format in `CLAUDE.md` and `AGENTS.md`.

## Revisit When

Revisit this decision when repeated onboarding sessions show that agents are reimplementing the same setup sequence manually, or when a tested implementation slice can cover idempotency, permission errors, and secret-safe reporting.
