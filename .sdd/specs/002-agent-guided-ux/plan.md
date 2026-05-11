# Implementation Plan: Agent-Guided UX for Non-Technical B2G Users
**Feature ID**: `002-agent-guided-ux`
**Date**: 2026-05-10
**Spec**: `spec.md`
## Summary
Improve the toolkit from a developer-operated CLI into an agent-operated workflow for non-technical B2G users. The first deliverable is not a new UI; it is a clear operating contract for agents plus SDD-backed documentation of the friction observed during the first real Notion setup. The agent should own setup, verification, dependency repair, Notion sync, and business output generation while the user only supplies business context and necessary external permissions.
The plan preserves the CLI as the internal execution layer, but user-facing docs and agent responses should avoid exposing terminal commands unless the user asks. Future implementation can add a single guided command or web UI, but the immediate improvement is to make agents reliably guide users end-to-end.

## Technical Context
- **Language/Version**: Python 3.11+ for toolkit automation; Markdown for SDD docs, agent instructions, and user-facing guidance.
- **Primary Dependencies**: Typer, Pydantic, `email-validator`, Notion client, python-dotenv, pytest.
- **Storage**: Local `.env` for secrets and resolved Notion IDs; Notion databases/data sources for GTM records; local `data/runs/` for audit logs.
- **Testing**: pytest for CLI behavior and Notion adapters/fakes; manual acceptance checks against a real Notion page when credentials are available.
- **Target Runtime**: Cursor/agent environment on Windows first, with cross-platform command handling where possible.

## Decisions
### Agent-first documentation
Create `CLAUDE.md` at the repo root as the primary operating guide for agents. It should define:
- what the user experience should feel like;
- which technical terms to hide or translate;
- how to handle secrets and Notion setup;
- when to run internal CLI commands without exposing them;
- how to report sample versus real data.
This is separate from `README.md`. The README can remain a developer reference, while `CLAUDE.md` tells the agent how to act for non-technical users.

### Friction log
Create a dedicated friction log under `docs/ux-friction-log.md`. It should capture:
- what confused the user;
- what the agent assumed incorrectly;
- how to explain it better;
- product/doc improvements needed.
This log becomes input for future specs and prevents repeating the same onboarding failures.

### User-facing setup guide
Create `docs/non-technical-onboarding.md` as the plain-language guide the agent can paraphrase. It should avoid commands and technical jargon, but still describe what the user must do in Notion UI terms.
### CLI remains internal
Keep `b2g-gtm` as the execution layer for now. Agents may run commands internally, but should not make the user copy commands unless the user explicitly asks to operate manually.

### Notion API reality
Document that recent Notion API versions use databases plus data sources. This is an implementation detail for maintainers, not a user-facing concept.
## Project Structure
```text
CLAUDE.md
docs/
  non-technical-onboarding.md
  ux-friction-log.md
.sdd/specs/002-agent-guided-ux/
  spec.md
  plan.md
  tasks.md
  checklists/
    requirements.md
```


## Implementation Phases
### Phase 1: Documentation foundation
- Create the SDD spec, implementation plan, requirements checklist, and tasks.
- Add `CLAUDE.md` as the agent operating contract.
- Add user-facing onboarding guidance.
- Add friction log from the first live setup.
### Phase 2: Skill and README alignment
- Update relevant skills so they match the real behavior: setup can apply real Notion changes when authorized, sync can write real records, and agents should not present dry-run as complete setup.
- Keep README accurate, but move terminal-heavy walkthroughs away from the non-technical path.
### Phase 3: Automation hardening
- Add tests around `.env` loading, Notion data source adapter behavior, idempotent setup, and idempotent sync.
- Consider a single guided setup command for agents, but keep the user experience conversational.
### Phase 4: Product UX
- Evaluate whether the next step should be a local guided wizard, lightweight web UI, or Cursor Canvas for onboarding/status.
- Define the minimum UI that removes terminal exposure entirely.

## Risks
- **Secret exposure**: users may paste tokens in chat. Mitigation: never echo secrets, keep `.env` ignored, recommend rotation after exposure.
- **Notion API drift**: database/data-source behavior may change again. Mitigation: isolate Notion adapter behavior and test with fakes plus documented live checks.
- **Duplicate workspaces**: repeated setup can create duplicate bases if ID resolution fails. Mitigation: persist data source IDs and verify before creating.
- **Over-documentation**: user-facing docs can become too technical. Mitigation: split agent/maintainer docs from user-facing onboarding.
## Open Questions
- Should there be a single `guided setup` CLI command for agents, or should the agent orchestrate existing commands?
- Should non-technical users ever see the README, or should README become a developer-only reference?
- Should we build a small local UI/canvas for setup status and Notion verification?
- How should real SECOP API credentials be obtained and explained without exposing datos.gov.co implementation details?
