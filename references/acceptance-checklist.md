# Acceptance Checklist

Use this checklist as a pass/fail gate before delivering a briefing.

## Contract

Pass only if:

1. `time_window` is explicit
2. `topic_mix` is explicit
3. `depth`, `format`, and `audience` are either user-provided or declared as assumptions

## Coverage

Pass only if:

1. The requested priority topic is covered
2. Broad briefings include the major requested buckets without obvious gaps
3. The final item count matches the chosen depth

Default count targets:

1. `quick`: 3 to 7 retained items
2. `standard`: 5 to 12 retained items
3. `analyst`: 5+ retained items plus open questions or watchlist notes

## Evidence

Pass only if:

1. Each retained top item has a source line unless the user explicitly asked for a source-free executive style
2. High-impact items have at least one `首选证据`
3. Weakly sourced or unresolved items are labeled and moved to `继续跟踪`
4. Dates and numbers are consistent across retained claims

The runner treats missing/placeholder title, event text, importance, bucket, sources, or invalid evidence enums as blocking issues. Such items do not enter the main digest.

## Writing

Pass only if:

1. The output uses a built-in section order or a user-requested variant
2. Item field order is consistent
3. `为什么重要` is shorter than or equal in weight to `发生了什么`
4. The text reads like a briefing, not search notes

## Cognitive layer

Pass only if:

1. `interrogate` flags single-source high-impact claims, unsupported causality, and unchecked counterevidence
2. `sprout` uses only retained, evidence-backed items
3. Every visible extension states `依据` and `性质：推断`
4. Editorial commentary and future tracking are not presented as reported facts
5. Disabling cognitive features leaves the core digest unchanged
6. `continuity` can be exported as explicit JSON when the next run needs state

## Reusability

Pass only if:

1. The digest structure is stable enough to repeat next cycle
2. Inferred assumptions are visible
3. Another operator could rerun the same briefing from the stated contract
4. A writable run produces a UTF-8 `.md` artifact unless the user requested chat-only output
5. The default artifact follows `daily-news-YYYY-MM-DD.md`, or uses the explicit output path supplied by the caller
6. The final response exposes the saved artifact path
7. If a continuity artifact is produced, it is user-visible and portable

## Machine report

`finalize` emits `acceptance_report` with `passed`, `blocking_issues`, `warnings`, retained count, follow-up count, and `cognitive_review`. It also emits `acceptance_summary` with compact counts for warnings, blocking issues, retained items, follow-up items, single-source high-impact items, and evidence gaps. Blocking issues prevent the Markdown artifact from being written; count shortfalls, high-impact evidence gaps, and interrogation findings remain visible warnings for operator review.
