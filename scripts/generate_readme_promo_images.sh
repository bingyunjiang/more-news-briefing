#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_GEN="${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/image_gen.py"
PROMPTS="$ROOT_DIR/tmp/imagegen/readme-promo-prompts.jsonl"
OUT_DIR="$ROOT_DIR/assets/readme-xiaohei-scenes"

if [[ ! -f "$IMAGE_GEN" ]]; then
  echo "image_gen.py not found: $IMAGE_GEN" >&2
  exit 1
fi

if [[ ! -f "$PROMPTS" ]]; then
  echo "Prompt file not found: $PROMPTS" >&2
  exit 1
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is not set." >&2
  echo "Export it in your trusted shell, then rerun this script." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

python3 "$IMAGE_GEN" generate-batch \
  --input "$PROMPTS" \
  --out-dir "$OUT_DIR" \
  --concurrency "${IMAGE_GEN_CONCURRENCY:-3}"
