---
name: more-news-briefing
description: Create recurring multi-topic news briefings with customizable cadence, topic mix, ranking, verification, source-backed summaries, and optional claim interrogation, insight extension, signal commentary, and cross-run tracking. Use when Codex needs to collect, deduplicate, rank, verify, summarize, or prepare daily, weekly, or custom-cycle digests across general news, AI, politics, business, culture, sports, and user-defined subjects, including requests for deeper interpretation after the news. Default to full mode, which runs the complete collect-sort-verify-write workflow. On a user's first use, resolve the topic contract before search begins, and explicitly help the user choose broad themes or define specialty topics with enough scope, keywords, geography, and watch priorities to support repeatable monitoring. This skill should work as a standalone workflow by default, and only treat other installed skills as optional enhancements.
---

# More News Briefing

## Overview

Build a recurring news digest with an internal workflow for collection, filtering, ranking, verification, summarization, and formatting. Default to a broad briefing that covers major general-interest topics plus any user-priority themes, then adapt the scope, cadence, and output format to the request.

Before the first real retrieval pass, resolve whether this is the user's first use of the skill or the first time they are asking for a new specialty watchlist. If the topic mix is missing, vague, or only says things like `看下专项`, pause and complete the topic contract first.

When the user directly invokes the skill with a short request such as `做个简报`, `跑一下`, or `按默认来`, do not silently skip customization on the first turn. Give them a compact first-use gate that makes the choices visible:

1. `直接开始`: run once with the default broad mix
2. `快速自定义`: choose topic mix, specialty direction, geography, and priority lens
3. `深度自定义`: also define source style and recurring watchlists

If the user does not engage with the gate and still wants immediate output, proceed with the default broad mix for that run, but explicitly tell them that the skill supports a quick customization pass and show what was assumed.

## Default Operating Mode

If the user does not specify a cadence, ask only if scheduling is the main task. Otherwise assume a one-off run that is compatible with future automation.

Before collecting, normalize the request with the input contract in [input-contract.md](./references/input-contract.md). If the user gives a loose request like "做个今日简报", fill the missing fields with defaults and state those assumptions in the final output.

If this looks like the user's first use, or the request introduces a new specialty topic, do a short topic-intake interaction before retrieval. Keep the intake compact, but do not skip specialty-topic clarification when the topic definition is still too loose to search or rank well.

For first use, do not open with a long free-form questionnaire. Start with one compact gate that lets the user choose between default, quick customization, and deep customization. The goal is to surface customization early without increasing friction so much that the user abandons the skill.

If the user does not specify topics, use this default mix:

1. AI and technology
2. Politics and policy
3. Business and markets
4. Culture and society
5. Sports
6. User-priority specialty topics

If the user does not specify depth, produce a compact briefing:

1. One top-line summary
2. Five to twelve ranked items total
3. One or two sentences per item
4. A short "why it matters" note for the highest-priority items

## First-Use Topic Intake

Use a short guided intake the first time the skill is used, or whenever the user asks for a new specialty watchlist that is still underspecified.

Read [onboarding-template.md](./references/onboarding-template.md) before asking the first-use questions. Prefer the multiple-choice onboarding prompt there over free-form intake. Only ask for typed detail when the specialty topic is still too broad after the user makes selections.

Read [topic-enums.md](./references/topic-enums.md) when you need the canonical split between default recurring topics and specialty monitoring topics.

Cover these decisions in order:

1. Offer the first-use gate: default run, quick customization, or deep customization
2. Choose the briefing shape: broad default mix, focused multi-topic mix, or specialty-only monitoring
3. Confirm the primary themes the user wants tracked every run
4. If a specialty topic exists, refine it until the search space is operational

Treat `quick customization` as the preferred default branch for first-use users who seem willing to personalize but do not want a heavy setup. In that branch, prioritize four fields only:

1. Topic mix
2. Specialty subtopic if any
3. Geography
4. Priority lens

Only expand into source style, exclusions, and watchlists when the user explicitly chooses `deep customization`, asks for recurring monitoring, or shows strong domain specificity.

For specialty topics, explicitly collect enough detail to support stable retrieval and ranking:

1. Topic label: what the user wants to call this watch topic
2. Scope: devices, technology layer, policy track, market segment, companies, or projects
3. Keywords and aliases: Chinese and English terms, abbreviations, brand names, and technical synonyms
4. Geography: global, China, US, EU, or named markets
5. Priority lens: policy, products, financing, safety, standards, bids, deployments, or research
6. Exclusions: adjacent topics that should not be mixed in unless they become material

If the user only gives a broad domain like `储能` or `充电`, do not silently lock that in as the final specialty definition. Offer a more complete formulation and let the user confirm or adjust it before search begins.

## Capability Modes

Run this skill in one of three modes:

1. `full mode`: Run the complete built-in workflow first, then optionally borrow enhancement skills for better retrieval, validation, or polish
2. `standard mode`: Use only Codex's native retrieval and reasoning abilities
3. `minimal mode`: If retrieval is constrained, reorganize supplied material into a ranked, source-backed briefing

Default to `full mode`. In this skill, `full mode` still means the built-in workflow owns the result. External helpers may widen recall or improve polish, but they do not own the contract, ranking, evidence, or final draft. Only fall back to `standard mode` when the user explicitly asks for a lighter or faster run, or when the environment cannot support the complete retrieval and verification path. Use `minimal mode` only when search is constrained or the user mainly provided source material directly.

## Standalone Operation

This skill must be able to complete its core job without relying on any external skill.

Treat the following as part of the skill's owned core, not borrowed behavior:

1. Request normalization and assumption handling
2. Query planning and bucket layout
3. Candidate-item deduplication
4. Evidence labeling and retention rules
5. Output formatting and acceptance checks

If local code support is useful, use the built-in runner documented in [local-runner.md](./references/local-runner.md).

Treat the runner as an artifact-driven execution contract. Its complete phase order is `collect -> normalize/deduplicate -> rank/retain -> verify -> render -> cognition -> acceptance -> polish`; do not skip the acceptance gate or execute generated command strings through a shell.

When external skills are unavailable, use this standalone route:

1. Build queries from [query-playbook.md](./references/query-playbook.md)
2. Use native web retrieval or user-provided sources
3. Apply the built-in ranking, deduplication, verification, and formatting rules
4. Produce a source-backed digest with the internal templates

Treat external skills as accelerators, not prerequisites.

Account-gated or login-required sources are allowed when they materially improve the briefing. If a preferred source needs the user to log in, pause briefly, say why that source is worth using, and explicitly ask the user to complete login before continuing retrieval from that source.

When you need concrete retrieval routes instead of generic guidance, read [retrieval-adapters.md](./references/retrieval-adapters.md).

When the preferred retrieval route is `anysearch`, read [anysearch-adapter-runbook.md](./references/anysearch-adapter-runbook.md) for a directly executable first-pass collection workflow. This is an optional adapter, not the default dependency boundary for the skill.

## Internal Enhancement Patterns

This skill internally adopts five enhancement patterns. Use them whether or not the original source skills are installed:

1. `recent-scan pattern`: start with a short-horizon sweep for the last 24 hours to 7 days and identify what is actually new
2. `broad-search pattern`: widen coverage with multiple keyword variants, domain mixes, and topic buckets before ranking
3. `deep-verify pattern`: give high-impact or ambiguous items a second pass with fuller reading and cross-checking
4. `final-polish pattern`: compress, de-slop, and humanize the prose after the factual structure is stable
5. `cognitive-layer pattern`: optionally interrogate the draft, extend verified signals, and prepare next-cycle tracking without mixing inference into reported facts

Read [embedded-enhancements.md](./references/embedded-enhancements.md) before difficult collection or synthesis tasks.
Read [cognitive-enhancements.md](./references/cognitive-enhancements.md) when enabling any cognitive feature beyond the default `interrogate` review.

## External Skill Bridges

If these skills are installed, they can accelerate the internal patterns above:

1. `anysearch` can accelerate the `broad-search pattern`, especially for multi-query recall and page extraction
2. `deep-research` can accelerate the `deep-verify pattern`
3. `humanizer-zh` can accelerate the `final-polish pattern`
4. `automation-workflows` is only relevant when the task explicitly includes scheduling or delivery
5. Topic-specific retrieval skills can be used for specialty buckets if they are narrowly scoped and their evidence quality is checked before retention

Do not assume these skills exist. If one is unavailable, continue with the built-in pattern that serves the same purpose.

Do not bulk-import or conceptually merge another skill's whole codebase into this one during normal operation. Keep this skill's owned implementation compact and local, and use bridges only where the borrowed capability is clearly optional.

If you need zero-setup portability for a user environment, you may ship selected optional skill snapshots inside `references/skills/` together with a manifest and license notes. Treat those vendored snapshots as local optional adapters, not as the core of this skill.

Do not use `agent-reach` as the primary news collector. It can help find other agents, but it is not the main retrieval path for current affairs.

Do not use `Last30Days` for current-affairs retrieval. Despite the name, it is a coding-activity skill, not a news-recentness skill.

## Fallback Behavior

If an enhancement skill is unavailable, degrade gracefully:

1. Missing `anysearch`: use the best available web retrieval path and narrower topic queries
2. Missing `deep-research`: increase source cross-checking on the retained top items
3. Missing `humanizer-zh`: keep the draft concise and factual instead of adding stylistic polish
4. Missing a topic-specific retrieval skill: search that specialty bucket directly with the built-in query playbook
5. Missing all enhancement skills: still produce a source-backed digest from the best available retrieval path

If the user provides source material directly, skip search-heavy steps and focus on ranking, deduplication, and formatting.

Read [standalone-operation.md](./references/standalone-operation.md) when you need a no-external-skill path, including user-assisted login to account-gated or institution-gated sources.

## Workflow

## Quick Start

Use this sequence when you need a runnable path instead of a general description:

1. Normalize the request with [input-contract.md](./references/input-contract.md)
2. Follow the operator steps in [demo-runbook.md](./references/demo-runbook.md)
3. Pick the retrieval route in [retrieval-adapters.md](./references/retrieval-adapters.md)
4. If the route is `anysearch`, run [anysearch-adapter-runbook.md](./references/anysearch-adapter-runbook.md)
5. Format the digest with [output-templates.md](./references/output-templates.md)
6. Check completion with [acceptance-checklist.md](./references/acceptance-checklist.md)

### 1. Define the briefing contract

Lock down the core contract variables before collecting:

1. Cadence: one-off, daily, weekly, or custom
2. Topic mix: default mix or user-specified weights
3. Delivery format: plain digest, push-ready summary, or archive-friendly report
4. Audience: personal skim, executive scan, research watchlist, or public-facing copy
5. Mode: `full`, `standard`, or `minimal`
6. Source-role preference: discovery, verification, context, and watch balance when recurring monitoring matters
7. Watchlists: company, institution, and community watchlists when recurring monitoring matters
8. Cognitive features: default `interrogate`; use `all` for `interrogate,sprout,commentary,continuity`; or a user-selected subset

If one or more variables are missing, make the smallest reasonable assumption and state it in the final output.

Use the `minimum viable contract` in [input-contract.md](./references/input-contract.md) when you need to move quickly.

### 2. Collect candidate items

Collect more items than you plan to keep. Build a candidate pool by topic bucket, then merge.

Prefer a mixed source set:

1. Broad news sources for major events
2. Topic-specialized sources for depth
3. Official or primary sources when policy, regulation, or company announcements matter

If enhancement skills are available, use them to widen or verify the pool. If they are not, continue with direct retrieval and manual filtering. A briefing is not a dump of search results.

Apply the `recent-scan pattern` first, then the `broad-search pattern`, before deciding whether a `deep-verify pattern` pass is needed.

Read [query-playbook.md](./references/query-playbook.md) before building queries for broad news sweeps, niche technology monitoring, or mixed Chinese-English search workflows.

Read [source-ladder.md](./references/source-ladder.md) before deciding whether a source is strong enough to support a retained item.

Choose one source reference for the current problem instead of loading all of them: use [source-design-patterns.md](./references/source-design-patterns.md) for architecture, [source-family-catalog.md](./references/source-family-catalog.md) for source-role routing, or [borrowed-source-catalog.md](./references/borrowed-source-catalog.md) for exact sites, feeds, APIs, access requirements, and fallbacks. Prefer public and keyless routes by default.

Read [watchlist-template.md](./references/watchlist-template.md) when the user wants recurring specialty monitoring and would benefit from a suggested starter watchlist instead of naming every company, institution, or community from scratch.

### 3. Deduplicate and rank

Merge duplicate stories across sources before writing. Keep one canonical item with supporting sources rather than listing the same event multiple times.

Rank items with this priority order:

1. Consequence: policy, market, safety, geopolitical, platform, or cultural impact
2. Recency: newer items win when importance is similar
3. Attention: visible breakout coverage across credible sources
4. Relevance: explicit user interests or persistent watch topics
5. Novelty: genuine change beats routine commentary

Read [editorial-rubric.md](./references/editorial-rubric.md) before final ranking or when the topic mix is broad.

Read [source-ladder.md](./references/source-ladder.md) when a story is fast-moving, contested, technical, or financially material.

### 4. Write the digest

Write in layers, not as one flat list:

1. Headline summary: two to four sentences covering the biggest shifts
2. Ranked items: one short block per item
3. Optional watchlist: low-confidence or emerging stories worth checking next run

For each retained item, include:

1. A clear title
2. What happened
3. Why it matters
4. A timestamp or time window when relevant
5. One or more sources if the user asked for links or attribution

After the evidence-backed digest is stable, apply the configured cognitive layer. Keep `interrogate` as a non-visible review gate by default. Render `commentary`, `sprout`, or `continuity` only when enabled and supported by structured item fields. Label every visible extension as inference and state its basis.

If the user explicitly asks to test, demo, preview, or see the cognitive features in action, enable `interrogate,sprout,commentary,continuity` instead of using only the default `interrogate`.


Avoid filler transitions, generic optimism, and repetitive framing.

### 5. Prepare for push or repeat runs

If the task includes ongoing delivery and scheduling support is available, hand off the final structure to `automation-workflows`.

If scheduling support is unavailable, still produce a reusable digest format that another system can trigger later.

Store the workflow assumptions in the automation:

1. Cadence and trigger time
2. Topic mix
3. Depth target
4. Delivery channel
5. Maximum item count
6. Whether links, source notes, or a "watch next" section should be included
7. Enabled cognitive features and any prior-run continuity input

## Output Modes

Choose one of these patterns unless the user specifies another:

### Quick Brief

Use for mobile-friendly push summaries:

1. One short lead
2. Three to seven items
3. Minimal commentary

### Standard Digest

Use for daily or weekly roundup work:

1. One top-line overview
2. Five to twelve ranked items
3. Brief importance notes

### Analyst Watch

Use for research-heavy monitoring:

1. Topic-grouped sections
2. Explicit source comparison
3. Open questions and items to revisit next cycle

### Long Message Briefing

Use for WeChat, Feishu, or other chat surfaces where the digest should stay readable as one long message:

1. One concise title line
2. One short overview block
3. Three to six compact sections
4. Short paragraphs and list-like rhythm
5. No dense wall-of-text sections
6. Default to the high-density variant unless the user asks for a more executive style

## Output Format Rules

Treat formatting as part of the deliverable, not decoration. Keep the structure stable across runs so the digest is easy to scan and easy to automate later.

### Global formatting rules

1. Start with `一次刷尽近期热点，高效工作一整天` unless the user explicitly asks for a different opening
2. Render the final deliverable in Markdown by default so it stays readable in Feishu, WeChat, and similar chat surfaces
3. Put the highest-value summary first
4. Keep section titles short and consistent
5. Keep each news item in the same field order
6. Avoid long paragraphs; prefer compact blocks
7. Include source lines by default to preserve an evidence trail
8. Prefer mobile-friendly line lengths for chat delivery
9. Save the finished briefing as a UTF-8 Markdown file unless the user explicitly requests chat-only output
10. Use `daily-news-YYYY-MM-DD.md` as the default filename, based on the briefing date
11. Respect an explicit output path or filename when the user or calling workflow provides one
12. Return the saved file path with the final response so delivery systems such as Feishu bots can consume it directly

Use plain, portable Markdown only. Prefer headings, numbered lists, and flat bullets. Do not rely on HTML, complex tables, or formatting that breaks when pasted into chat tools.

### Required field order for each item

Unless the user asks for a lighter format, write each retained item in this order:

1. Title
2. What happened
3. Why it matters
4. Signal level or priority tag when useful
5. Source level or evidence status when the digest is source-backed
6. Sources or source count

### Chinese default style

Default to concise Chinese output with this tone:

1. Calm and information-dense
2. No marketing language
3. No exaggerated transitions
4. No fake objectivity language such as "业内人士表示" unless sourced
5. No filler ending paragraphs

### Section order

For a broad digest, use this section order unless the user overrides it:

1. 今日概览
2. 重点新闻
3. 分主题速览
4. 值得继续跟踪

If the digest is short, collapse "分主题速览" into "重点新闻".

### Preferred labels

Use these labels for Chinese briefings:

1. `今日概览`
2. `重点新闻`
3. `AI与科技`
4. `政治与政策`
5. `商业与市场`
6. `文化与社会`
7. `体育`
8. `专项关注`
9. `继续跟踪`

### Length targets

Use these defaults unless the user requests a different depth:

1. Overview: 2 to 4 sentences
2. Each ranked item: 2 to 5 lines
3. Each "why it matters" note: 1 short sentence
4. Each watchlist item: 1 line

### Long message rules

When writing for WeChat or Feishu long messages:

1. Keep each section to 2 to 4 items where possible
2. Keep each item to 3 short lines unless it is a top story
3. Avoid more than one dense explanatory paragraph in a row
4. Use visible section spacing so the reader can resume scanning after interruption
5. Put the most important stories before any topic-by-topic sweep
6. End with a short `继续跟踪` section instead of a long conclusion
7. Default to `信息密度高版`
8. Keep a source line on every retained top item unless the user explicitly requests a source-free executive style
9. Default to compact `来源级别` and `证据状态` labels on retained top items when evidence traceability matters

### Output examples

Read [output-templates.md](./references/output-templates.md) before drafting the final answer when the user asks for a fixed newsletter style, a chat-ready summary, or a reusable standard layout.

## Topic Expansion Rules

If the user asks for "comprehensive" coverage, expand breadth before depth. Add buckets in this order:

1. International affairs
2. China and domestic policy
3. AI and technology
4. Business and markets
5. Culture and society
6. Sports
7. Specialty topics named by the user

If the digest becomes too long, cut routine items first, then commentary, then low-impact repetition. Keep the top developments.

## Quality Bar

Before finishing, check that the digest:

1. Covers the requested or default topic mix
2. Avoids duplicate stories
3. Distinguishes important events from noisy chatter
4. Reads like a briefing, not search notes
5. Uses source strength labels consistently when the digest is source-backed
6. Can be reused by an external scheduler or automation layer without manual restructuring
7. Keeps reported facts, editorial synthesis, and inferred extensions visibly separate
8. Labels each visible cognitive extension with its basis and inference status

Read [acceptance-checklist.md](./references/acceptance-checklist.md) before delivering the final answer when you want a pass/fail check rather than a loose quality scan.
