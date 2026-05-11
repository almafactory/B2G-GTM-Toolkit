# UX Friction Log

This log captures real onboarding friction so future specs, docs, and agent behavior can improve. It is intentionally blunt: the goal is to make the product easier for non-technical users.

## 2026-05-10: First Live Toolkit Trial And Notion Setup

### Friction: Technical terms were explained poorly

**What happened**: The agent used terms like "sin red", "fixtures", and `email-validator` without explaining why they mattered.

**Why it hurt**: The user could not tell whether the toolkit had actually contacted SECOP, written to Notion, or only used local examples.

**Better behavior**:

- Say "sample data included with the repo" instead of "fixtures".
- Say "using local sample data, not contacting external services" instead of "offline" or "sin red".
- Explain dependencies only by user impact. For `email-validator`: "the CLI uses it to validate owner email fields; without it the toolkit cannot start."

**Product/doc follow-up**:

- Keep technical language in developer docs only.
- Add agent instructions for translating internal terms.

### Friction: The agent overclaimed Notion progress

**What happened**: The agent said the flow had been run, but the user correctly noted that Notion had not been configured and no data could have been mounted there.

**Why it hurt**: This broke trust. A local preview is not the same as a real sync.

**Better behavior**:

- Always distinguish preview/local sample output from real Notion writes.
- Only say "data is in Notion" after a real Notion sync reports created/updated records.

**Product/doc follow-up**:

- Add `CLAUDE.md` rule: never claim Notion data exists until real sync succeeds.
- Keep setup reports outcome-based: connected, verified, created, updated.

### Friction: User did not know how to obtain Notion credentials

**What happened**: The agent asked for `NOTION_TOKEN` and `NOTION_PARENT_PAGE_ID` as if the user knew what those were.

**Why it hurt**: The user needed step-by-step UI guidance, not environment variable names.

**Better behavior**:

- Ask whether a teammate already created the integration.
- If yes, ask for the project `.env` or the token/page URL.
- If no, guide the user through Notion's integration UI.
- Extract the page ID from the URL automatically.

**Product/doc follow-up**:

- Add non-technical Notion onboarding guide.
- Consider a future setup wizard.

### Friction: Token was pasted into chat

**What happened**: The user pasted a Notion token directly in the conversation.

**Why it matters**: The token should be treated as exposed. It can be used to access any Notion content shared with that integration.

**Better behavior**:

- Do not echo the token back.
- Save it only to ignored local config.
- Recommend rotating it before production use.

**Product/doc follow-up**:

- Add secret handling rules to `CLAUDE.md`.
- Prefer asking for `.env` transfer or direct local edit when possible.

### Friction: Existing docs were terminal-first

**What happened**: README and agent docs showed CLI commands as the main path.

**Why it hurt**: The desired UX is agent-operated. The user should not need to learn terminal commands to try the product.

**Better behavior**:

- Keep commands as internal/developer reference.
- Add a non-technical path where the user asks for outcomes and the agent operates the toolkit.

**Product/doc follow-up**:

- Update `docs/agent-usage.md` and README to separate user-facing path from internal commands.

### Friction: Notion API changed under the toolkit

**What happened**: Notion setup initially created databases, but verification saw zero properties because the current Notion API exposes properties through data sources.

**Why it hurt**: Setup appeared successful before verification caught the schema issue.

**Better behavior**:

- Always run verification after setup.
- Treat API-version mismatches as implementation details, not user concepts.

**Product/doc follow-up**:

- Add tests for Notion data source adapter behavior.
- Keep this as a maintainer note, not user-facing setup language.

## UX Principles From This Trial

- The user gives business intent; the agent chooses tools.
- The user performs only external UI actions that require their account.
- The agent explains one next action at a time.
- The agent reports real outcomes, not internal process.
- The agent must never blur preview/sample data with real synced data.
- Documentation should make future agents less annoying, not make users more technical.
