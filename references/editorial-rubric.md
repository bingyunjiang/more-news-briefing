# Editorial Rubric

Use this reference when the briefing spans multiple topic areas or when the user asks for a repeatable digest format.

## Ranking rubric

Score each candidate item informally across these dimensions:

1. Impact: Does it change policy, regulation, markets, conflict, platforms, culture, or public attention in a meaningful way?
2. Urgency: Does the reader need to know it now?
3. Breadth: Is it relevant to many readers or only a niche audience?
4. Persistence: Will it still matter in the next cycle?
5. Reader fit: Does it match the user's recurring interests or explicit watch topics?

Keep items that score high on impact plus at least one of urgency, breadth, or reader fit.

## Source balance

Prefer at least two distinct sources for major claims when possible.

For sensitive topics, give extra weight to:

1. Official statements
2. Primary documents
3. Reputable outlets with direct reporting

Do not inflate an item just because many sites syndicate the same wire copy.

## Topic quotas

Default quota for a standard digest:

1. AI and technology: 2 items
2. Politics and policy: 2 items
3. Business and markets: 2 items
4. Culture and society: 1 item
5. Sports: 1 item
6. User-priority specialty topics: 1 to 3 items depending on request

Adjust quotas when the user names a priority domain. A named domain outranks the default mix.

## Output templates

### Push summary

Use when the channel is chat-first:

```text
Today's briefing: [one-sentence overview]

1. [Title] - [what happened]. [why it matters].
2. [Title] - [what happened]. [why it matters].
3. [Title] - [what happened]. [why it matters].
```

### Standard digest

Use when the reader wants a cleaner roundup:

```text
Top line
[2-4 sentence overview]

Top developments
1. [Title]
[what happened]
[why it matters]

2. [Title]
[what happened]
[why it matters]
```

### Analyst watch

Use when the reader cares about monitoring:

```text
Overview
[summary]

Priority items
[ranked items]

Watch next
- [emerging item]
- [emerging item]
```

## Editing notes

Before polish, run the configured `interrogate` review: challenge causal wording, forecasts written as facts, overclaimed headlines, single-source high-impact items, and missing counterevidence. Keep these findings in the machine report unless the reader needs an analyst-style open-question section.

Use `humanizer-zh` for the final pass when the digest sounds too templated, too padded, or too much like stitched search output.
