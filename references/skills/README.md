# Vendored Skills

This folder is for optional skill snapshots that may be shipped together with `more-news-briefing`.

## Why this folder exists

Sometimes you want a user to install only this skill repository and still have a few optional accelerators available locally.

This folder supports that use case without changing the skill's main boundary:

1. `more-news-briefing` remains standalone-first
2. Vendored skills remain optional adapters
3. Contract resolution, ranking, evidence judgment, and final writing still belong to `more-news-briefing`

## What may go here

Good candidates:

1. Search-expansion helpers
2. Small formatting helpers
3. Narrow topic adapters
4. Read-only reference snapshots

Avoid placing these here unless you are intentionally forking and maintaining them:

1. Large general-purpose skills
2. Whole multi-skill bundles
3. Anything with unclear license status
4. Anything that would become a hidden hard dependency

## Required metadata

Every vendored skill snapshot should be listed in `vendor-manifest.json`.

For each entry, record:

1. `name`
2. `source_path`
3. `snapshot_path`
4. `bundled`
5. `role`
6. `required_by_default`
7. `license_note`
8. `update_policy`

Do not keep secrets, local `.env` files, caches, or machine-specific state inside vendored snapshots.

## Operating rule

If a vendored skill disappears, `more-news-briefing` should still run.

If a vendored skill is present, it may help with:

1. broader recall
2. faster extraction
3. lighter polish

It must not silently replace the built-in contract, ranking, evidence, or digest logic.

## Current bundled snapshots

At the moment this repository bundles snapshots for:

1. `anysearch`
2. `deep-research`
3. `humanizer-zh`
