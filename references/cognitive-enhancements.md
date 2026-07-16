# Cognitive Enhancement Layer

Use this reference when a briefing should do more than summarize events. Keep the layer optional, portable, and subordinate to the evidence workflow.

## Configuration

Set `cognitive_features` to a comma-separated subset of:

1. `interrogate`: challenge causal leaps, unsupported certainty, missing counterevidence, and weak sourcing
2. `sprout`: connect verified events to mechanisms, precedents, adjacent domains, or plausible consequences
3. `commentary`: identify the few signals that best explain the period
4. `continuity`: emit explicit questions and indicators for the next run

Default to `interrogate`. Use `off` to disable the layer. Enable `sprout`, `commentary`, or `continuity` only when the user requests more interpretation, uses an analyst-oriented format, or configures them for a recurring briefing.

Example:

```text
cognitive_features=interrogate,sprout,continuity
```

## Evidence Boundary

Never edit a verified event claim to make an extension more interesting. Keep these fields distinct:

1. `what`: sourced event claim
2. `why`: evidence-grounded importance
3. `signal_commentary`: editorial synthesis across retained items
4. `insight_extensions`: explicitly inferred connections
5. `continuity`: next-cycle monitoring instruction

Every visible extension must state both its basis and that it is an inference. Do not create an extension from a rumor, a `待确认` item, or a source-free claim. Absence of an extension is better than a generic connection.

Recommended item fields:

```json
{
  "signal_commentary": "政策与资本开支正在同向变化。",
  "insight_extensions": [
    {
      "insight": "采购周期可能先于收入确认改善",
      "basis": "招标量上升且交付周期缩短"
    }
  ],
  "continuity": "下期检查中标公告与交付指引是否同步上调",
  "causal_claim": false,
  "causal_basis": "",
  "counterevidence_checked": true
}
```

## Interrogate Gate

Before acceptance, ask:

1. Is correlation written as causation?
2. Is a forecast presented as a reported fact?
3. Does the headline claim more than the sources support?
4. Is a high-impact item supported by only one independent source?
5. Was material counterevidence ignored?
6. Would the conclusion change if the weakest source were removed?

Move unresolved event claims to `继续跟踪`. Keep unresolved interpretation out of the visible cognitive sections.

## Sprout Selection

Retain at most three extensions in a standard digest. Prefer one of these useful connection types:

1. Mechanism: what process could connect the event to an outcome
2. Precedent: what comparable event clarifies the likely path
3. Cross-domain link: what adjacent field changes the interpretation
4. Scenario: what observable condition would make a consequence more or less likely

Avoid trivia, generic analogies, motivational quotations, and connections that cannot name their basis.

## Commentary And Continuity

`commentary` should compress the period into one to three discriminating signals, not praise individual stories. `continuity` should produce a reusable handoff containing concrete entities, indicators, unresolved questions, and a time horizon.

The skill does not own a global user profile or hidden persistent memory. For portable GitHub use, continuity state must be supplied by the caller, a prior digest, a watchlist file, or an external automation layer.
