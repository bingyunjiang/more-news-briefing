# Standalone Operation

Use this reference when `more-news-briefing` must complete the workflow without relying on any external skill.

## Standalone principle

Complete the job with:

1. Native retrieval available in the current environment
2. User-provided links, documents, screenshots, or source lists
3. User-assisted login to account-gated or institution-gated sources when needed
4. Internal ranking, deduplication, verification, and formatting rules

## Standalone collection paths

Choose the lightest sufficient path:

1. `open web path`: public news, official statements, public reports, exchange announcements
2. `user-supplied source path`: the user gives links, PDFs, copied excerpts, or screenshots
3. `logged-in browser path`: the user signs in and the agent works from the accessible session
4. `institution-assisted path`: the user uses campus, enterprise, or subscribed access and shares the accessible materials

## User-assisted login flow

When a useful source is account-gated:

1. Tell the user what source is needed and why
2. Ask the user to log in through their own browser or available session
3. Read only the content the session makes accessible
4. Prefer direct login over asking the user to paste secrets into chat
5. If login is impossible, ask for exported files, copied abstracts, screenshots, or equivalent open sources

## Institution-gated sources

This is especially relevant for:

1. Academic databases
2. Paid industry intelligence
3. Exchange and filing systems with better logged-in access
4. Enterprise research platforms

If the user has legitimate access, guide them to:

1. Open the relevant result page
2. Download or export permitted materials
3. Share links, PDFs, copied abstracts, filing screenshots, or notes

Then continue with internal extraction, ranking, and formatting.

## No-external-skill workflow

When fully standalone, use this sequence:

1. Build queries from `query-playbook.md`
2. Run a recent-scan pass
3. Merge and deduplicate candidate items
4. Escalate important items into deep verification
5. Preserve source lines for every retained top item
6. Format with the built-in templates

## Evidence hierarchy

When external skills are absent, rank evidence like this:

1. Official statements and primary documents
2. Regulator, exchange, ministry, or institution releases
3. Reputable direct reporting
4. Secondary aggregation
5. Commentary

Prefer a thinner briefing with stronger evidence over a wider briefing built on weak sourcing.
