# Non-Technical Onboarding Guide

This guide is for agents helping founders, sales operators, or account executives use the B2G GTM Toolkit without touching the terminal.

## What The User Should Experience

The user should be able to say:

> "Connect this to Notion and try the toolkit."

The agent should then guide them through only the external actions that cannot be done locally:

- creating or reusing a Notion integration;
- sharing the target Notion page with that integration;
- providing the Notion page URL and integration token;
- confirming whether to create the GTM workspace databases.

Everything else is agent work.

## Plain-Language Notion Setup

### Step 1: Reuse Existing Project Access If Available

Ask:

> Did someone on your team already create a Notion integration for this project?

If yes, ask for the existing project `.env` or these values:

- Notion integration token.
- Notion page URL for the workspace page.

The page URL is enough. The agent extracts the page ID.

### Step 2: Create An Integration Only If Needed

If no integration exists, guide the user:

1. Open Notion's integrations page.
2. Create a new internal integration.
3. Name it something recognizable, such as `B2G GTM Toolkit`.
4. Give it permission to read, insert, and update content.
5. Copy the integration token.

Do not ask the user to understand API terminology.

### Step 3: Share The Workspace Page

Ask the user to create or choose one Notion page, for example `GovBridge HQ` or `B2G GTM`.

Then ask them to:

1. Open that page in Notion.
2. Click `Share`.
3. Invite or connect the integration.
4. Copy the page URL.

If setup fails with missing access, the most likely cause is that the page was not shared with the integration.

### Step 4: Agent Configures Locally

The agent should save the token and page ID in `.env`.

The user does not need to understand the file. The important promise is:

- it stays local;
- it is ignored by git;
- the agent will not print the token back.

### Step 5: Agent Creates Or Verifies The Workspace

The agent checks whether the required GTM databases exist. If they are missing and the user agrees, the agent creates them.

The expected databases are:

- B2G Business Profiles
- B2G ICPs
- B2G Target Accounts
- B2G SECOP Research
- B2G Opportunities
- B2G GTM Outputs
- B2G Owners
- B2G Signals

The agent should report:

> Notion is connected and the GTM workspace structure is ready.

Only say this after verification succeeds.

## Trial Run

For a first trial, the agent may use sample data included with the repo. Say it plainly:

> I used sample data included with the project so we can verify the flow safely.

If Notion sync is configured and authorized, the agent may write sample SECOP research records to Notion. The report should include:

- how many records were created;
- how many were updated;
- whether this was sample data or real SECOP data.

Do not say data was mounted in Notion unless a real write succeeded.

## Recommended Agent Report

Use this shape:

```text
Notion is connected.
The GTM workspace structure is ready.
I ran a sample SECOP research flow and synced 6 records to Notion.
Running the sync again updated the same 6 records, so it is not duplicating them.
Next business step: replace the sample company/opportunity inputs with your real company context.
```

## What Not To Show The User By Default

Avoid showing:

- terminal commands;
- Python virtual environment details;
- dependency package names;
- raw stack traces;
- Notion data source internals;
- local run IDs unless needed to debug.

Show these only if the user asks for technical details or if a developer is debugging.
