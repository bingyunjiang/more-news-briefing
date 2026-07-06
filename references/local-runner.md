# Local Runner

Use this reference when you want the skill's core orchestration to stay fully local to this repository.

## Purpose

The local runner is intentionally small.

It owns only the parts this skill should own directly:

1. Contract normalization
2. Topic-bucket query planning
3. Final digest rendering from retained items

It does not try to replace live retrieval, browser access, or general-purpose search tooling.

## Command set

All commands use only Python standard library:

```bash
python3 scripts/standalone_runner.py contract
python3 scripts/standalone_runner.py adapters
python3 scripts/standalone_runner.py route
python3 scripts/standalone_runner.py queries --topic-mix default
python3 scripts/standalone_runner.py digest --items-file items.json
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
  --specialty-keywords "V2G, fast charging, BESS, bidirectional charging" \
  --specialty-geography "China, EU" \
  --specialty-priority "policy"
```

### `queries`

Emit the default query pack by bucket.

Example:

```bash
python3 scripts/standalone_runner.py queries --topic-mix default --specialty "charging / V2G / BESS"
```

By default this emits grouped query packs with `core`, `news`, `institutional`, and `community` sections.

Use `--flat` if a downstream tool wants a single flat list per bucket.

The output now also includes `adapter_discovery`, so a caller can see which vendored adapters are locally available before choosing a retrieval route.

It now also includes `route_recommendation`, so a caller can get grouped queries and the recommended adapter path in one call.

### `adapters`

Read `references/skills/vendor-manifest.json` and report which vendored adapters are present in this repository.

Examples:

```bash
python3 scripts/standalone_runner.py adapters
python3 scripts/standalone_runner.py adapters --available-only
```

This is the runtime discovery path for bundled optional adapters such as vendored `anysearch`, `deep-research`, and `humanizer-zh`.

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

### `digest`

Render a standard digest from retained items stored in JSON.

Expected item fields:

1. `title`
2. `what`
3. `why`
4. `bucket`
5. `source_level`
6. `evidence_status`
7. `sources`
8. optional `time_window`
9. optional `follow_up`

Example:

```bash
python3 scripts/standalone_runner.py digest --items-file items.json --specialty "charging / V2G / BESS"
```

Template selection is now parameterized:

```bash
python3 scripts/standalone_runner.py digest --items-file items.json --format quick_brief
python3 scripts/standalone_runner.py digest --items-file items.json --format analyst_watch
python3 scripts/standalone_runner.py digest --items-file items.json --format long_message
python3 scripts/standalone_runner.py digest --items-file items.json --audience executive
```

Supported rendering rules include:

1. `quick_brief`
2. `standard_digest`
3. `analyst_watch`
4. `long_message`
5. `long_message_exec`

If `--format` is omitted, the runner infers a default from `depth` and `audience`.

The `contract` output now also includes `adapter_discovery`, so downstream callers can resolve the briefing contract and inspect local adapter availability in one call.

## Ownership rule

If you are tempted to add a new external dependency here, stop and ask:

1. Is this core to `more-news-briefing` itself?
2. Can this be done with the standard library and existing references?
3. Would copying a whole other skill create drift or blur responsibilities?

If the answer to the third question is yes, keep it out of the local runner.
