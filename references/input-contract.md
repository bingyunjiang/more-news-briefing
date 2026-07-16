# Input Contract

Use this reference to turn a vague news request into a repeatable briefing job before retrieval starts.

## Minimum viable contract

Resolve these fields for every run:

1. `time_window`: `today`, `last_24h`, `last_3d`, `last_7d`, or explicit dates
2. `cadence`: `one_off`, `daily`, `weekly`, or `custom`
3. `topic_mix`: default buckets or named priorities
4. `depth`: `quick`, `standard`, or `analyst`
5. `format`: `quick_brief`, `standard_digest`, `analyst_watch`, or `long_message`
6. `audience`: `personal`, `executive`, `research`, or `public`
7. `mode`: `full`, `standard`, or `minimal`
8. `source_roles`: preferred mix of `discovery`, `verification`, `context`, and `watch`
9. `company_watchlist`: named companies, operators, labs, projects, or tickers if recurring monitoring matters
10. `institution_watchlist`: named regulators, ministries, standards bodies, exchanges, or associations if recurring monitoring matters
11. `community_watchlist`: named communities, repos, forums, channels, or discussion sources if practitioner signal matters
12. `cognitive_features`: comma-separated subset of `interrogate`, `sprout`, `commentary`, and `continuity`; default `interrogate`, or `off`

If the user leaves fields blank, fill them with the smallest reasonable defaults and declare them in the output.

## First-use topic intake rule

If this appears to be the user's first use of the skill, or the first time they are asking for a specialty watch topic, resolve topic design before retrieval starts.

Read [onboarding-template.md](./onboarding-template.md) before asking the intake questions. Prefer the multiple-choice prompt there, and only fall back to free-form follow-up when the user's selections still leave the specialty topic too broad.

Read [topic-enums.md](./topic-enums.md) when you need to classify the user's choices into default broad buckets versus specialty monitoring buckets.

Read [source-family-catalog.md](./source-family-catalog.md) when you need to translate the user's preferences into source-role choices or recurring watchlists.
Read [watchlist-template.md](./watchlist-template.md) when the user wants a recurring specialty briefing and needs a recommended starting watchlist for companies, institutions, and communities.

Use a two-step first-use policy:

1. First show a compact gate: `直接开始` / `快速自定义` / `深度自定义`
2. Then ask only the minimum number of follow-up questions needed for the chosen path

Do not silently treat an empty first-use request as consent to skip customization forever. At most, treat it as permission to run this one briefing with defaults and remind the user that a lightweight customization path exists.

Use a compact intake with two layers:

1. Choose the briefing shape: broad default mix, focused multi-topic mix, or specialty-only monitoring
2. If a specialty topic is included, define it well enough to search repeatedly
3. If the user cares about repeatability, resolve source preferences and watchlists at the same time

For `快速自定义`, stop after these fields unless the user volunteers more:

1. `topic_mix`
2. `specialty_label` or `specialty_scope` if relevant
3. `specialty_geography`
4. `specialty_priority`

For `深度自定义`, continue into `source_roles`, exclusions, and watchlists.

For a specialty topic, try to resolve these fields:

1. `specialty_label`: short name for the watch topic
2. `specialty_scope`: technology, policy, company, project, product, or market slice
3. `specialty_keywords`: Chinese and English keywords, aliases, abbreviations, and brand names
4. `specialty_geography`: global or named markets
5. `specialty_priority`: policy, product, financing, safety, standards, bids, deployments, or research
6. `specialty_exclusions`: nearby topics to filter out unless clearly relevant

Prefer a two-layer specialty definition for public use:

1. first layer: broad public-friendly sector or technology bucket
2. second layer: narrower professional subtopic

Good public first-layer examples:

1. energy and power
2. automotive and mobility
3. advanced manufacturing
4. semiconductors and electronics
5. AI and robotics
6. simulation and digital twin
7. thermal management
8. test methods and validation

For recurring or specialty monitoring, also try to resolve these fields:

1. `source_roles`: whether the user wants more hotlist discovery, more official verification, more community context, or more recurring watch sources
2. `company_watchlist`: specific companies, operators, labs, projects, repos, or tickers to keep warm every run
3. `institution_watchlist`: specific ministries, regulators, standards bodies, exchanges, or associations to keep warm every run
4. `community_watchlist`: specific communities, forums, repositories, channels, or discussion venues to keep warm every run

If the user chooses a source-family shortcut during onboarding, map it like this:

1. `偏热点` -> emphasize `discovery`
2. `偏官方` -> emphasize `verification`
3. `偏社区` -> emphasize `context`
4. `偏产业` -> emphasize `watch` plus domain-specific discovery
5. `平衡默认` -> balanced `discovery + verification`

If the user does not care, use the smallest reasonable defaults:

1. broad digest: balanced `discovery + verification`
2. technical specialty digest: `discovery + verification + context + watch`
3. no watchlist: leave the watchlist fields blank instead of inventing names

If the user gives only a loose label such as `储能`, `充电`, or `机器人`, do not treat that as a complete specialty definition. Offer a more concrete candidate formulation and get confirmation before retrieval.

If the user chose `直接开始`, you may skip this follow-up for the current run only, but the output should record that the specialty dimension was not customized.

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
7. `mode`: `full`
8. `source_roles`: balanced `discovery + verification`
9. `company_watchlist`: blank unless known
10. `institution_watchlist`: blank unless known
11. `community_watchlist`: blank unless known
12. `cognitive_features`: `interrogate`

If the user says `日报` or clearly wants a repeatable daily run, change only this field set:

1. `time_window`: `last_7d`
2. `cadence`: `daily`
3. Keep the remaining defaults unchanged

If this is also their first use, still show the compact first-use gate before locking these defaults in.

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
mode: full
source_roles: discovery + verification
company_watchlist: blank
institution_watchlist: blank
community_watchlist: blank
cognitive_features: interrogate
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
mode: full
source_roles: discovery + verification + context + watch
company_watchlist: CATL, BYD, Sungrow, Tesla Energy if relevant
institution_watchlist: NEA, NDRC, MIIT if relevant
community_watchlist: OCPP / ISO 15118 repos or engineering communities if relevant
cognitive_features: interrogate, sprout, continuity
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
mode: full
source_roles: discovery + verification, plus watch if specialty is stable
company_watchlist: known names only
institution_watchlist: known names only
community_watchlist: known names only
cognitive_features: interrogate
```

## Output note

Put the resolved assumptions near the top or bottom of the final digest whenever they were inferred instead of explicitly provided.

For first-use default runs, explicitly label the assumptions as `本次按默认口径执行` so the user can tell the run was not yet customized.
