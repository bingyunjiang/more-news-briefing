# Embedded Enhancements

This reference internalizes the most useful working patterns that were previously outsourced to other skills.

## 1. Recent-scan pattern

Purpose: quickly isolate what is genuinely new in the current cycle.

Use this sequence:

1. Define the time window first: last 24 hours, last 3 days, last 7 days, or user-specified
2. Run narrow queries focused on recency before broad thematic searches
3. Group results into: clearly new, likely follow-up, and background-only
4. Drop items that are only reheated commentary unless they changed the underlying picture

Use this pattern whenever the user asks for "today", "recent", "latest", "this week", or "hot topics".

## 2. Broad-search pattern

Purpose: widen coverage without losing structure.

Use this sequence:

1. Create 2 to 3 keyword variants per topic bucket
2. Mix general and topic-specific source types
3. Search major themes separately before merging
4. Merge duplicates into canonical events instead of preserving source-level duplicates

For broad briefings, search in buckets:

1. AI and technology
2. Politics and policy
3. Business and markets
4. Culture and society
5. Sports
6. User-priority specialty topics

## 3. Deep-verify pattern

Purpose: spend extra effort only where it matters.

Escalate an item into deep verification when one or more are true:

1. It has high policy, market, or geopolitical impact
2. Sources disagree
3. The story is moving quickly
4. One source is being copied widely without enough original reporting
5. The user needs decision-grade confidence

Deep verification means:

1. Read beyond snippets
2. Prefer primary or official documents when available
3. Cross-check at least two distinct credible sources
4. Flag unresolved conflicts instead of smoothing them over

## 4. Final-polish pattern

Purpose: make the briefing readable without weakening the evidence chain.

Apply this after ranking is stable:

1. Remove padded openings and transitions
2. Replace vague claims with source-backed specifics
3. Keep "why it matters" shorter than "what happened"
4. Preserve source lines
5. Keep the tone calm, compact, and evidence-first

If the prose starts sounding like stitched search notes, rewrite for rhythm and clarity, but do not remove supporting attribution.

## 5. Mapping to optional external skills

If the environment includes related skills, map them like this:

1. `Last30Days` maps to the `recent-scan pattern`
2. `anysearch` maps to the `broad-search pattern`
3. `deep-research` maps to the `deep-verify pattern`
4. `humanizer-zh` maps to the `final-polish pattern`

These are accelerators, not mandatory dependencies.
