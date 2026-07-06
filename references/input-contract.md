# Input Contract

Use this reference to turn a vague news request into a repeatable briefing job before retrieval starts.

## Minimum viable contract

Set these six fields for every run:

1. `time_window`: `today`, `last_24h`, `last_3d`, `last_7d`, or explicit dates
2. `cadence`: `one_off`, `daily`, `weekly`, or `custom`
3. `topic_mix`: default buckets or named priorities
4. `depth`: `quick`, `standard`, or `analyst`
5. `format`: `quick_brief`, `standard_digest`, `analyst_watch`, or `long_message`
6. `audience`: `personal`, `executive`, `research`, or `public`

If the user leaves fields blank, fill them with the smallest reasonable defaults and declare them in the output.

## Rolling-window rule

For recurring or quasi-recurring news work, prefer a rolling window over a strict same-day cutoff.

Default rule:

1. `daily` digest: use `last_7d` as the retrieval window, then rank by consequence first and recency second
2. `weekly` digest: use `last_7d` or explicit calendar dates
3. `today` or `last_24h` only when the user explicitly wants a hot-take style update or breaking-news scan

This avoids thin briefings on slow news days and supports stable daily monitoring.

## Default assumptions

Use these defaults when the user says only things like "测试下", "做个简报", or "来一版今天的新闻":

1. `time_window`: `last_7d`
2. `cadence`: `one_off`
3. `topic_mix`: AI, politics, business, culture, sports, plus one user-priority specialty bucket if known
4. `depth`: `standard`
5. `format`: `standard_digest`
6. `audience`: `research`

If the user says `日报` or clearly wants a repeatable daily run, change only this field set:

1. `time_window`: `last_7d`
2. `cadence`: `daily`
3. Keep the remaining defaults unchanged

## Specialty-topic rule

If the user has a stable domain interest, add one specialty bucket by default. Examples:

1. Charging / V2G / fast charging
2. Energy storage / BESS / fire safety
3. Power electronics / SiC / GaN
4. Power market reform / EMS / grid operations

If no specialty is known, do not invent one.

## Contract examples

### Example 1: minimal user request

User request:

```text
做个今天的热点简报
```

Resolved contract:

```text
time_window: last_7d
cadence: one_off
topic_mix: default broad mix
depth: quick
format: quick_brief
audience: personal
```

### Example 2: research-oriented request

User request:

```text
给我做一版储能和充电方向的本周监测
```

Resolved contract:

```text
time_window: last_7d
cadence: one_off
topic_mix: energy storage, charging, policy, business
depth: analyst
format: analyst_watch
audience: research
```

### Example 3: daily rolling briefing

User request:

```text
给我做日报
```

Resolved contract:

```text
time_window: last_7d
cadence: daily
topic_mix: default broad mix plus known specialty bucket
depth: standard
format: standard_digest
audience: research
```

## Output note

Put the resolved assumptions near the top or bottom of the final digest whenever they were inferred instead of explicitly provided.
