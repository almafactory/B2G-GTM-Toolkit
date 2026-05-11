# Agent Operating Guide

This repo is meant to be operated by an agent for non-technical B2G users. Treat the CLI, Python environment, Notion API details, and local files as internal machinery. The user should experience a guided business workflow.

## Core Principle

Default to doing the work for the user. Do not ask the user to run commands, inspect files, understand package dependencies, or decode Notion URLs unless they explicitly ask to operate manually.

Good default:

- Ask for the business goal.
- Ask for one missing external permission or credential at a time.
- Configure local files safely.
- Run internal validation/setup/sync steps yourself.
- Report business-visible results in plain language.

Bad default:

- Dump CLI commands as the main answer.
- Say "offline", "fixtures", "stub", "dry-run", "venv", or package names without explanation.
- Claim data is in Notion before a real Notion write has succeeded.
- Echo secrets back to the user.

## User-Facing Language

Translate technical terms:

- "fixtures" -> "sample data included with the repo"
- "offline" -> "using local sample data, not contacting external services"
- "dry-run" -> "preview only; nothing was written"
- "stub" -> "local placeholder, not real Notion"
- "email-validator" -> "a Python package used to check whether owner email fields are valid"
- "run id" -> "the saved research run"
- "data source" -> do not mention unless debugging for a developer

If a technical term matters, explain why it matters to the user. If it does not matter, omit it.

## Notion Setup Behavior

When the user wants to connect Notion:

1. Ask whether someone already created a Notion integration for this project.
2. If yes, ask for the existing `.env` values or the token plus Notion page URL.
3. If no, guide them to create an internal Notion integration in the Notion UI.
4. Ask them to share the target Notion page with the integration.
5. Extract `NOTION_PARENT_PAGE_ID` from the page URL yourself.
6. Save credentials in local `.env`, which is ignored by git.
7. Run Notion verification internally.
8. If the workspace is missing databases and the user has authorized setup, run setup internally.
9. Verify again and report the result.

Never print the token back. If the token appears in chat or logs, recommend rotating it before production use.

## Trial Run Behavior

When the user says "try it", "ensayemos", "probemos", or similar:

1. Read the README and relevant skills internally.
2. Install missing dependencies if safe.
3. If Notion is not configured, explain that the trial can either use sample local outputs or first connect Notion.
4. If using sample data, say so plainly.
5. Run validation/research internally.
6. Sync to Notion only if real credentials are configured and setup is verified.
7. Report:
   - whether sample or real data was used;
   - whether Notion was actually written;
   - how many records were created/updated;
   - the next business step.

Do not present commands unless the user asks for commands.

## Agent Status Reports

When reporting setup, trial, research, or sync progress, use short outcome-focused updates instead of command dumps:

- `Outcome`: what is true now in business terms.
- `Evidence`: the verification result, record counts, or concrete artifact created.
- `User action needed`: one concrete external action, only when the agent is blocked.
- `Next business step`: the next useful GTM action.

If external permissions are missing, ask for one user action at a time and wait for the result before asking for the next one. Do not bundle several browser, Notion, credential, or sharing steps into one request unless the user explicitly asks for a full checklist.

Do not include terminal commands, raw logs, stack traces, package names, run IDs, or Notion internals by default. If something failed, explain the user-visible impact and the next action the agent will take or the one action needed from the user.

## Current Notion Implementation Notes

Recent Notion API versions expose database properties through data sources. The toolkit adapter must use `data_sources.retrieve`, `data_sources.update`, `data_sources.query`, and page creation with `parent={"data_source_id": ...}`.

This is an internal maintainer detail. Do not explain it to non-technical users unless it is the root cause of a failure and they need a short status update.

## Secrets And Git Safety

- `.env` is ignored by git; use it for local secrets.
- Do not commit `.env`, tokens, exported Notion zips, or local run outputs.
- If a secret is pasted in chat, do not repeat it in the final answer.
- Recommend rotation after exposure.
- Before committing, inspect changes and ensure only intended source/docs files are staged.

## Response Style For This Project

Use Spanish if the user writes in Spanish. Be direct and plain.

For non-technical users:

- Explain outcomes, not implementation details.
- Use one next action at a time.
- Avoid long command blocks.
- Say when something was only a preview.
- Say when something was actually written to Notion.

For maintainers:

- It is okay to mention file paths, commands, tests, and API details.
- Keep user-facing docs separate from agent/maintainer docs.

## Verification Expectations

After changing Python behavior:

- Run tests with `pytest`.
- Check lints on edited Python files.
- For Notion changes, verify idempotency: setup should not duplicate databases, sync should update existing records.

After changing docs only:

- Read the changed docs once for consistency with this guide.
- Ensure non-technical docs avoid unexplained jargon.
