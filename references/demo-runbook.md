# Demo Runbook

Use this runbook when you want a concrete execution path for a one-off briefing.

## Success standard

A run counts as successful only if all of these are true:

1. The contract is resolved before search begins
2. At least one retained item uses `首选证据`
3. Duplicate stories are merged instead of repeated
4. The final output matches one of the built-in templates
5. Any weakly sourced item is moved to `继续跟踪` instead of presented as confirmed

## Default sample run

Use this sample when testing the skill end to end:

```text
time_window: last_7d
cadence: one_off
topic_mix: AI, politics, business, culture, sports, specialty
specialty: user-priority domain if known
depth: standard
format: standard_digest
audience: research
mode: standard
```

## Operator sequence

1. Resolve the contract with `input-contract.md`
2. Pick topic buckets and draft 2 to 4 queries per bucket from `query-playbook.md`
3. Run the `recent-scan pattern` first
4. Run the `broad-search pattern` only after new items are isolated
5. Merge duplicate events into canonical items
6. Rank with `editorial-rubric.md`
7. Verify high-impact items with `source-ladder.md`
8. Draft with `output-templates.md`
9. Run the final pass against `acceptance-checklist.md`

## Stop conditions

Stop searching and move to synthesis when one of these becomes true:

1. You already have 5 to 12 retained items with adequate coverage
2. New search results are mostly duplicates or commentary
3. The remaining uncovered bucket is low-priority and weakly sourced

If a critical bucket is still empty, say so explicitly instead of padding it with weak items.

## Anti-patterns

Do not do these during a run:

1. Dump raw search results into the final digest
2. Treat repeated syndication as multiple confirmations
3. Keep a top item without a clear evidence level
4. Inflate sports or entertainment items just to satisfy coverage symmetry
5. Hide missing assumptions

## Minimal test prompt

Use this prompt for a quick manual test:

```text
Use $more-news-briefing in standard mode. Build a one-off standard digest for the last 7 days in concise Chinese. Cover AI, politics, business, culture, sports, plus one specialty bucket if the user has a known domain interest. Include sources, 来源级别, and 证据状态. State any inferred assumptions.
```
