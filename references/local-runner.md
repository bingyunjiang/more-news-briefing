# Local Runner

Use this reference when you want the skill's core orchestration to stay fully local to this repository.

## Purpose

The local runner owns the deterministic parts this skill should control directly:

1. Contract normalization
2. Topic-bucket query planning
3. Candidate normalization, stable IDs, deduplication, and ranking
4. Verification-result validation and overlay
5. Acceptance reporting and final digest rendering
6. Configurable cognitive review and section rendering

It does not try to replace live retrieval, browser access, or general-purpose search tooling.

## Command set

All commands use only Python standard library:

```bash
python3 scripts/standalone_runner.py contract
python3 scripts/standalone_runner.py adapters
python3 scripts/standalone_runner.py route
python3 scripts/standalone_runner.py collect
python3 scripts/standalone_runner.py verify --items-file items.json
python3 scripts/standalone_runner.py verify-results --items-file items.json
python3 scripts/standalone_runner.py polish --draft-file digest.txt
python3 scripts/standalone_runner.py pipeline --items-file items.json --draft-file digest.txt
python3 scripts/standalone_runner.py execute --items-file items.json --draft-file digest.txt
python3 scripts/standalone_runner.py prepare --items-file candidates.json --output-file items.json
python3 scripts/standalone_runner.py queries --topic-mix default
python3 scripts/standalone_runner.py digest --items-file items.json
python3 scripts/standalone_runner.py digest --items-file items.json --cognitive-features insight
python3 scripts/standalone_runner.py finalize --items-file items.json
python3 scripts/standalone_runner.py finalize --items-file items.json --continuity-file continuity.json
python3 scripts/standalone_runner.py demo --cognitive-features all --output-file demo.md --continuity-file demo.continuity.json
```

The runner now internalizes a subset of defaults from:

1. `input-contract.md`
2. `query-playbook.md`
3. `output-templates.md`

## Subcommands

### `contract`

Resolve the minimum viable contract with built-in defaults.

Example:

```bash
python3 scripts/standalone_runner.py contract --specialty "charging / V2G / BESS"
```

Useful optional flags:

```bash
python3 scripts/standalone_runner.py contract \
  --depth analyst \
  --audience research \
  --specialty "charging / V2G / BESS" \
  --specialty-scope "grid-scale storage and bidirectional charging" \
  --specialty-keywords "V2G, fast charging, BESS, bidirectional charging" \
  --specialty-exclusions "consumer battery, residential storage" \
  --specialty-geography "China, EU" \
  --specialty-priority "policy"
```

### `queries`

Emit the default query pack by bucket.

Example:

```bash
python3 scripts/standalone_runner.py queries --topic-mix default --specialty "charging / V2G / BESS"
```

By default this emits grouped query packs with `core`, `news`, `institutional`, `community`, and `watch` sections. Company, institution, and community watchlists create concrete watch queries. The response also includes `source_targets`, drawn from the concrete source catalog.

Use `--flat` if a downstream tool wants a single flat list per bucket.

The output now also includes `adapter_discovery`, so a caller can see which vendored adapters are locally available before choosing a retrieval route.

It now also includes `route_recommendation`, so a caller can get grouped queries and the recommended adapter path in one call.

### `adapters`

Read `references/skills/vendor-manifest.json` and report snapshot, entrypoint, credential, and license health.

Examples:

```bash
python3 scripts/standalone_runner.py adapters
python3 scripts/standalone_runner.py adapters --available-only
```

An adapter is routable only when its declared entrypoints exist, required credentials are available, and its license status is verified. Unresolved snapshots remain inspectable but are not selected automatically.

### `route`

Build a route recommendation from:

1. the resolved contract
2. current adapter availability
3. output format and depth

Examples:

```bash
python3 scripts/standalone_runner.py route --topic-mix default
python3 scripts/standalone_runner.py route --depth analyst --specialty "charging / V2G / BESS"
python3 scripts/standalone_runner.py route --audience executive --format long_message
```

The current route planner gives recommendations for:

1. `collect`
2. `verify`
3. `polish`

Typical behavior:

1. multi-topic broad coverage prefers vendored `anysearch` when available
2. analyst or specialty-heavy runs prefer vendored `deep-research` for retained-item verification when available
3. Chinese long-message output may prefer vendored `humanizer-zh` for final polish when available

### `collect`

Turn the `collect` route recommendation into an execution-ready plan.

Examples:

```bash
python3 scripts/standalone_runner.py collect --topic-mix default
python3 scripts/standalone_runner.py collect --depth analyst --specialty "charging / V2G / BESS"
```

When the collect route recommends vendored `anysearch`, the output now includes:

1. `execution_mode: anysearch_batch_search`
2. `anysearch_batches`
3. a ready-to-use `payload` for each batch
4. a shell-safe `command_argv` for the vendored `anysearch_cli.py`
5. a `command_hint` rendered with shell quoting for display only

Executors must run `command_argv` without a shell. Do not execute `command_hint` through `sh -c`, `shell=True`, or equivalent APIs.

When the collect route stays on the built-in path, the output falls back to:

1. `execution_mode: native_web_search`
2. `fallback_web_queries`

### `verify`

Turn retained items into a verification-stage execution plan.

Examples:

```bash
python3 scripts/standalone_runner.py verify --items-file items.json
python3 scripts/standalone_runner.py verify --items-file items.json --depth analyst --specialty "charging / V2G / BESS"
```

When the verify route recommends vendored `deep-research`, the output now includes:

1. `execution_mode: deep_research_fact_check_tasks`
2. `deep_research_tasks`
3. one task per retained item that should be verified
4. a `command_prompt` for fact-check style handoff
5. `verification_result_contract`
6. `verification_result_templates`

When the verify route stays on the built-in path, the output falls back to:

1. `execution_mode: built_in_verification`
2. `builtin_checks`

The verify plan exposes the stable result schema that downstream verification should write back into. `verdict` is always required, and each result must provide at least one identity field: `item_id`, `canonical_url`, or `title`.

Prefer `item_id`, then `canonical_url`, as the result identity. Title-only matching is retained only for backward compatibility when the title is unique.

### `prepare`

Normalize candidate objects, generate stable IDs, merge duplicates, rank retained items, and move structurally incomplete entries toward follow-up handling.

```bash
python3 scripts/standalone_runner.py prepare --items-file candidates.json --output-file items.json
```

### `verify-results`

Emit or normalize the stable verification result package between `verify` and `digest`.

Examples:

```bash
python3 scripts/standalone_runner.py verify-results --items-file items.json
python3 scripts/standalone_runner.py verify-results --items-file items.json --results-file verification-results.json
python3 scripts/standalone_runner.py verify-results --items-file items.json --output-file items.verification-results.json
python3 scripts/standalone_runner.py verify-results --items-file items.json --results-file reviewer-pass.json --output-file items.verification-results.json --merge
```

Use this command in two ways:

1. without `--results-file`, to generate result templates for the current verify candidates
2. with `--results-file`, to normalize deep-research or manual verification notes into a digest-ready package

It can also write directly to the shared verification artifact path:

1. `--output-file`: write the emitted package to disk
2. `--merge`: if `--output-file` already exists, merge incoming normalized results by `title` instead of overwriting

The output includes:

1. `result_contract`
2. `result_templates`
3. `results`
4. `verification_results`
5. `digest_overlay_ready_results`
6. optional `written_to`
7. optional `write_mode`

### `polish`

Turn the final-writing route into an execution-ready polish plan.

Examples:

```bash
python3 scripts/standalone_runner.py polish --draft-file digest.txt --format long_message
python3 scripts/standalone_runner.py polish --draft-file digest.txt --audience executive
python3 scripts/standalone_runner.py polish --items-file items.json --format standard_digest
```

When the polish route recommends vendored `humanizer-zh`, the output now includes:

1. `execution_mode: humanizer_zh_edit_task`
2. `humanizer_task`
3. `editing_goals`
4. `protected_invariants`
5. a `command_prompt` for the final revision pass

When the polish route stays on the built-in path, the output falls back to:

1. `execution_mode: built_in_polish`
2. `builtin_checks`

### `pipeline`

Build one combined artifact plan for:

1. `collect`
2. `normalize`
3. `rank`
4. `verify`
5. `render`
6. `cognition`
7. `acceptance`
8. `polish`

Examples:

```bash
python3 scripts/standalone_runner.py pipeline --items-file items.json --draft-file digest.txt
python3 scripts/standalone_runner.py pipeline --depth analyst --specialty "charging / V2G / BESS" --items-file items.json
```

Use this command when an upper-layer orchestrator wants one JSON object instead of composing three separate subcommands.

The `pipeline` output includes a `handoff_package` that normalizes the phases into one stable step list with:

1. `step`
2. `adapter`
3. `execution_mode`
4. `primary_inputs`
5. `artifacts`
6. `fallback`

### `execute`

Build a sequential execute-ready queue on top of `handoff_package`.

Examples:

```bash
python3 scripts/standalone_runner.py execute --items-file items.json --draft-file digest.txt
python3 scripts/standalone_runner.py execute --depth analyst --specialty "charging / V2G / BESS" --items-file items.json
```

Use this command when an upper-layer executor wants a flat ordered queue instead of nested plans.

The output includes:

1. `execute_queue.queue_length`
2. one ordered task per collection batch, local transformation, verification task, render, acceptance gate, and polish step
3. normalized fields: `order`, `phase`, `executor`, `action`, `target`, `command_argv`, `command`, `payload`
4. scheduling metadata: `requires_network`, `consumes_artifact`, `produces_artifact`, `success_signal`
5. `next_action_summary` for the first runnable queue item
6. `artifact_paths` with the shared output-path convention for later stages
7. `digest_command_hint` so the executor can hand the retained items and shared verify file straight into `digest`
8. `verification_results_init_command_hint` so the executor can initialize the shared verify file before appending judgments

Current path convention:

1. `items_file`: the retained-item JSON provided to `execute`
2. `verification_results_file`: `<items-file-stem>.verification-results.json`
3. `digest_output_file`: `daily-news-YYYY-MM-DD.md` in the items-file directory unless `--draft-file` is explicitly provided

Verify queue items now also expose `output_file`, so multiple verification tasks can append normalized results into the same shared `verification_results_file`.

Each verify queue item now also exposes:

1. `result_stub_file`
2. `merge_command_hint`

Use `merge_command_argv` when a verification task needs to append a normalized result. `merge_command_hint` is display-only.

### `digest`

Render a standard digest from retained items stored in JSON.

Expected item fields:

1. stable `item_id` or enough identity data to generate one
2. `title`, `what`, `why`, and `bucket`
3. enumerated `source_level` and `evidence_status`
4. non-empty `sources`
5. optional `canonical_url`, `time_window`, and `follow_up`
6. optional `signal_commentary`, `insight_extensions`, `continuity`, `causal_claim`, `causal_basis`, and `counterevidence_checked`

Example:

```bash
python3 scripts/standalone_runner.py digest --items-file items.json --specialty "charging / V2G / BESS"
python3 scripts/standalone_runner.py digest --items-file items.json --verification-results-file verification-results.json
```

Template selection is now parameterized:

```bash
python3 scripts/standalone_runner.py digest --items-file items.json --format quick_brief
python3 scripts/standalone_runner.py digest --items-file items.json --format analyst_watch
python3 scripts/standalone_runner.py digest --items-file items.json --format long_message
python3 scripts/standalone_runner.py digest --items-file items.json --audience executive
python3 scripts/standalone_runner.py digest --items-file items.json --cognitive-features analyst
python3 scripts/standalone_runner.py digest --items-file items.json --cognitive-features all
```

Supported rendering rules include:

1. `quick_brief`
2. `standard_digest`
3. `analyst_watch`
4. `long_message`
5. `long_message_exec`

If `--format` is omitted, the runner infers a default from `depth` and `audience`.

`--cognitive-features` accepts presets or explicit feature lists:

1. `compact`: `interrogate`
2. `insight`: `interrogate,sprout,commentary`
3. `analyst`: `interrogate,sprout,commentary,continuity`
4. `all`: `interrogate,sprout,commentary,continuity`
5. `off`: summary-only output
6. explicit comma-separated subsets such as `interrogate,sprout`

Visible extensions render only when their structured fields are present, and each sprout extension includes its basis plus `性质：推断`.

The `contract` output now also includes `adapter_discovery`, so downstream callers can resolve the briefing contract and inspect local adapter availability in one call.

If `--verification-results-file` is provided, the runner will overlay verify-stage decisions onto retained items before rendering the final digest.

Accepted verification result payload shapes:

1. a raw JSON array
2. an object with `results: [...]`
3. an object with `verification_results: [...]`

The full package emitted by `verify-results` is also accepted directly by `digest`, because it now includes `results` and `verification_results` aliases.

Per-result fields currently recognized:

1. `title`
2. `claim`
3. `why`
4. `source_level`
5. `evidence_status`
6. `sources`
7. `need_confirm`
8. `verdict`
9. `follow_up`

### `finalize`

Render the final digest artifact from retained items and the shared verification-results file.

Examples:

```bash
python3 scripts/standalone_runner.py finalize --items-file items.json
python3 scripts/standalone_runner.py finalize --items-file items.json --verification-results-file items.verification-results.json
python3 scripts/standalone_runner.py finalize --items-file items.json --verification-results-file items.verification-results.json --output-file custom-brief.md
python3 scripts/standalone_runner.py finalize --items-file items.json --continuity-file continuity.json
```

Use this command when you want one execution-facing step that:

1. reads retained items
2. optionally overlays verification results
3. renders the final digest
4. writes it as UTF-8 Markdown to `daily-news-YYYY-MM-DD.md` by default
5. uses `--output-file` when the caller needs a custom path or filename
6. uses `--continuity-file` when the caller wants explicit next-cycle tracking state as JSON

If `--verification-results-file` is omitted, `finalize` will try the standard shared path inferred from `items-file`.

The continuity file is portable state, not hidden memory. It includes the run date, enabled cognitive features, topic mix, follow-up topics, and item-level next-cycle checks.

Current `verdict` behavior:

1. `keep` / `confirm`: keep the item in the main digest and apply stronger fields if provided
2. `downgrade`: keep the item, but lower its evidence display using the supplied or default downgraded labels
3. `watch` / `move_to_watch` / `continue_tracking`: move the item into `继续跟踪` and preserve `follow_up` if provided

### `demo`

Render a built-in sample briefing that demonstrates visible cognitive sections.

Examples:

```bash
python3 scripts/standalone_runner.py demo
python3 scripts/standalone_runner.py demo --cognitive-features all
python3 scripts/standalone_runner.py demo --output-file demo.md --continuity-file demo.continuity.json
```

By default, `demo` enables `all` cognitive features so users can immediately see:

1. `本期信号点评`
2. `认知延伸`
3. `下期追踪`
4. an optional explicit continuity JSON artifact

## Ownership rule

If you are tempted to add a new external dependency here, stop and ask:

1. Is this core to `more-news-briefing` itself?
2. Can this be done with the standard library and existing references?
3. Would copying a whole other skill create drift or blur responsibilities?

If the answer to the third question is yes, keep it out of the local runner.
