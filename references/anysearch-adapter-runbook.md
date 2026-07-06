# AnySearch Adapter Runbook

Use this runbook when `more-news-briefing` chooses `anysearch` as the first-pass collector for a broad news digest.

## Goal

Use `anysearch` to improve first-pass recall without outsourcing ranking, evidence judgment, or final writing.

A successful run means:

1. `anysearch` is used only for discovery and page extraction
2. Search is organized by topic bucket instead of ad hoc one-off queries
3. Shortlisted items are re-checked with stronger sources before entering the main digest
4. Final deduplication and ranking still happen inside `more-news-briefing`

## Before you start

Resolve the briefing contract first with `input-contract.md`.

Then choose this runbook only if at least one of these is true:

1. The digest spans 3 or more topic buckets
2. Native search snippets are too shallow
3. You need parallel first-pass search
4. You expect to extract article pages after discovery

## Local preflight

Run these checks before the first networked search:

1. Confirm the skill exists at `/Users/Bing/.codex/skills/anysearch`
2. Run the offline interface spec once:

```bash
python3 /Users/Bing/.codex/skills/anysearch/scripts/anysearch_cli.py doc
```

3. Optionally inspect command help if needed:

```bash
python3 /Users/Bing/.codex/skills/anysearch/scripts/anysearch_cli.py search --help
python3 /Users/Bing/.codex/skills/anysearch/scripts/anysearch_cli.py batch_search --help
python3 /Users/Bing/.codex/skills/anysearch/scripts/anysearch_cli.py extract --help
```

If Python is unavailable, fall back to the Node or shell CLI described in the `anysearch` skill.

## Query design rule

For broad briefings, use one first-pass query per topic bucket, not one query per possible story.

For daily briefings, default to a rolling `last_7d` retrieval window. The final ranking should still favor the most recent high-consequence items, but the search window should be wide enough to avoid thin days.

Default bucket set:

1. AI and technology
2. Politics and policy
3. Business and markets
4. Culture and society
5. Sports
6. One specialty bucket if the user has a stable domain interest

For each bucket:

1. Start with one broad `news` query
2. Add freshness at the CLI level instead of overstuffing the text query
3. Keep the query headline-like, not essay-like
4. Prefer event-bearing nouns for politics and culture, not abstract category words

Use these default first-pass phrasings:

1. AI: `AI model launch regulation funding`
2. Politics: `official statement policy sanctions summit law`
3. Business: `earnings investment tariff deal market`
4. Culture: `festival release platform controversy education survey`
5. Sports: `championship transfer injury roster final`
6. Specialty: use the strongest domain nouns, such as `V2G fast charging energy storage tender`

## First-pass collection pattern

Use `batch_search` for 2 to 5 buckets at a time.

Recommended default:

1. Batch A: AI, politics, business
2. Batch B: culture, sports, specialty

This keeps each call readable while still using parallel retrieval.

### Batch A example

```bash
python3 /Users/Bing/.codex/skills/anysearch/scripts/anysearch_cli.py batch_search \
  --queries '[
    {"query":"AI model launch regulation funding","content_types":"news","freshness":"week","max_results":5},
    {"query":"official statement policy sanctions summit law","content_types":"news","freshness":"week","max_results":5},
    {"query":"earnings investment tariff deal market","content_types":"news","freshness":"week","max_results":5}
  ]'
```

### Batch B example

```bash
python3 /Users/Bing/.codex/skills/anysearch/scripts/anysearch_cli.py batch_search \
  --queries '[
    {"query":"festival release platform controversy education survey","content_types":"news","freshness":"week","max_results":5},
    {"query":"championship transfer injury roster final","content_types":"news","freshness":"week","max_results":5},
    {"query":"V2G fast charging energy storage tender","content_types":"news","freshness":"week","max_results":5}
  ]'
```

If the politics bucket is weak after one batch, run one tighter second-pass query instead of broadening randomly:

```bash
python3 /Users/Bing/.codex/skills/anysearch/scripts/anysearch_cli.py search "official statement ministry white house european commission law" --content_types news --freshness week --max_results 5
```

If the culture bucket is weak, run one event-led second pass:

```bash
python3 /Users/Bing/.codex/skills/anysearch/scripts/anysearch_cli.py search "festival release platform controversy survey" --content_types news --freshness week --max_results 5
```

## What to keep from first-pass results

Keep candidate items, not finished claims.

Retain only results that appear to have at least one of these:

1. High consequence
2. Strong recency
3. Likely official or direct-reporting follow-up path
4. Clear match to the user's specialty topic

Drop or downrank results that are:

1. Obvious commentary
2. Rewritten aggregation
3. Duplicate headlines about the same event
4. Thin clickbait without a clear verification path

## Extraction handoff

Use `extract` only for shortlisted results, not for every hit.

Good triggers for extraction:

1. The snippet is too vague
2. The article likely contains numbers or dates you need
3. You need the body text before deciding whether to keep the event

Example:

```bash
python3 /Users/Bing/.codex/skills/anysearch/scripts/anysearch_cli.py extract "https://example.com/news/article"
```

Limit extraction to the top 1 to 3 URLs per bucket during first pass. If an item still looks important after extraction, verify it with stronger sources.

## Verification handoff

After `anysearch` discovery, switch back to `more-news-briefing` rules:

1. Merge duplicates into canonical events
2. Classify evidence with `source-ladder.md`
3. For high-impact items, find at least one `首选证据`
4. Move unresolved items to `继续跟踪`

`anysearch` results alone are not enough for the final top block when the item is policy, financial, safety-related, or technically material.

## Stop conditions

Stop first-pass search when one of these is true:

1. You have 8 to 20 candidate items across the requested buckets
2. New hits are mostly duplicates
3. Every major bucket already has at least one viable candidate

Then move to ranking and verification. Do not keep widening search just because the tool can.

## Suggested command sequence

Use this sequence for a standard broad digest:

1. `doc` once for local interface reference
2. `batch_search` for Batch A
3. `batch_search` for Batch B
4. `extract` for the top shortlisted URLs
5. Verification with official or primary sources
6. Final ranking and drafting inside `more-news-briefing`

## Minimal test path

Use this when validating the adapter itself:

```text
1. Resolve a one-off, last-7-days, standard digest contract
2. Run one AnySearch batch for AI, politics, and business
3. Shortlist 3 to 5 candidate items
4. Extract at least one URL
5. Confirm the shortlisted items can be mapped into `来源级别` and `证据状态`
```

## Anti-patterns

Do not do these:

1. Run one huge batch with every imaginable query
2. Extract every result URL
3. Treat snippet text as final evidence
4. Let `anysearch` determine final story priority
5. Keep weak culture or sports filler only to satisfy symmetry
