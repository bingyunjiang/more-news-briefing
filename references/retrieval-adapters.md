# Retrieval Adapters

Use this reference when the core weakness is not writing or ranking, but getting a stronger candidate pool.

## Design rule

This file describes optional adapters, not mandatory dependencies.

Borrow retrieval capability in layers only after confirming the built-in route is insufficient:

1. `native web` for default broad coverage
2. `hotlist or structured feed` for faster discovery
3. `search expansion skill` for higher recall
4. `topic-specific retrieval skill` for specialty buckets
5. `deep verification skill` only after ranking

Do not replace the whole workflow with another skill. Borrow collection strength, then return to this skill's ranking, evidence, and formatting rules.

## Recommended routing

### Route 1: default broad news

Use this route first:

1. Native web search or browsing for broad headlines
2. Official or primary-source follow-up for retained items
3. Internal deduplication and ranking

Use when:

1. The digest is broad
2. Coverage matters more than niche depth
3. No specialized retrieval skill is clearly better

### Route 2: AnySearch for recall expansion

Use `anysearch` when:

1. You need multiple topic buckets searched in parallel
2. Native search snippets are too shallow
3. You want page extraction after discovery

Borrow from `anysearch`:

1. Parallel batch search
2. General web recall
3. URL content extraction for shortlisted items

Do not borrow from `anysearch`:

1. Final ranking logic
2. Final digest structure
3. Final evidence labeling

### Route 3: hotlist and structured-feed collectors

Use a hotlist-like collector when you need fast discovery rather than final proof.

Read [borrowed-source-catalog.md](./borrowed-source-catalog.md) before choosing a concrete collector. Start with public and keyless routes such as media channel pages, Google News RSS, GDELT, Hacker News, RSS/Atom, GitHub, or OSS Insight. Use provider-, token-, subscription-, or login-dependent routes only when they materially improve a priority bucket.

Good examples:

1. Hacker News for builder attention
2. GitHub Trending or release feeds for open-source momentum
3. social or portal hotlists for China-topic awareness
4. finance fast-news streams for market-moving headlines

Borrow from them:

1. speed of discovery
2. stable field structure
3. engagement signals such as score, rank, or comment count

Do not borrow from them:

1. final factual authority
2. policy or safety proof
3. capital-markets confirmation

Keep a source-specific fallback route. Examples include channel feed to public page, RSS to linked HTML, Reddit old-web to JSON/RSS, GitHub API to release page, and OpenBB to filing or company investor relations.

If a stronger structured source needs login, it is acceptable to use it after asking the user to sign in.

### Route 4: specialty-topic retrieval

Use a niche retrieval skill when the user's stable interest is more important than broad coverage.

Good examples:

1. Charging / energy-storage hotspot search skills
2. Sector-specific search prompts with strong keyword priors
3. Narrow scrapers with stable source scope

Rule:

1. Treat topic-specific output as candidate generation, not final truth
2. Re-check retained claims with `source-ladder.md`
3. Keep vendor or hype-heavy items out of the top block unless stronger evidence exists
4. If the best specialty route is account-gated, tell the user why it is worth using and ask them to log in before relying on it

### Route 5: HN-style structured scraper

Use a structured scraper such as `hackernews-frontpage` only for a narrow bucket like AI builder chatter or developer attention.

Borrow from it:

1. Deterministic JSON-like extraction
2. Stable field structure
3. Tight source scope

Do not use it as:

1. A general news source
2. A politics or business source
3. Evidence for policy, financial, or safety claims

## Known local skills

### `anysearch`

Best use:

1. Broad candidate generation
2. Parallel queries across multiple buckets
3. Reading shortlisted pages after search

Execution path:

1. Follow [anysearch-adapter-runbook.md](./anysearch-adapter-runbook.md) for preflight, batch query layout, and extraction handoff

### `充电桩行业热点搜索`

Best use:

1. Charging infrastructure specialty bucket
2. Fast initial idea list for policy, technology, and market subthemes

Limits:

1. Its example query is narrow and dated
2. It should be refreshed before direct reuse
3. It needs evidence re-checking before main-digest retention

### `hackernews-frontpage`

Best use:

1. Developer-attention side signal
2. AI tooling chatter
3. Open-source product momentum

Limits:

1. It is not a substitute for mainstream reporting
2. It is best kept in `专项关注` or `继续跟踪`

### `Last30Days`

Do not use for news retrieval.

Reason:

1. It tracks coding activity, not current events
2. Its name sounds relevant but its function is unrelated

## Integration pattern

For each bucket, choose one collector and one verifier:

1. Collector: native web or borrowed retrieval skill
2. Verifier: official source, primary document, or reputable direct reporting

Example:

1. AI bucket: HN-style or `anysearch` collector, official company blog or repo release as verifier
2. Politics bucket: native web or hotlist collector, government release as verifier
3. Charging bucket: specialty charging collector, regulator or company release as verifier
4. Market bucket: fast-news collector, filing or exchange disclosure as verifier

## Minimal adoption path

If you only make one upgrade, make it this:

1. Use `anysearch` for first-pass multi-bucket retrieval
2. Keep all ranking and evidence rules inside `more-news-briefing`

That is the highest-return optional upgrade with the lowest workflow distortion.
