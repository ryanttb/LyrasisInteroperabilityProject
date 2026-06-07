#!/usr/bin/env python3
"""
Build registry/index.json from registry/scenarios/*.yaml.

The index is the Phase I read API: static JSON consumed by GitHub Pages UI or
machine clients. Omits records whose status is in vocabularies.yaml index_exclude_statuses.

Usage:
  python scripts/build_registry_index.py
  python scripts/build_registry_index.py --check   # exit 1 if index would change
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = ROOT / "registry" / "scenarios"
VOCAB_PATH = ROOT / "registry" / "vocabularies.yaml"
INDEX_PATH = ROOT / "registry" / "index.json"
SCHEMA_PATH = ROOT / "registry" / "schema.json"


def load_vocab() -> dict:
    with VOCAB_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_scenarios() -> list[dict]:
    records = []
    for path in sorted(SCENARIOS_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            record = yaml.safe_load(f)
        records.append(record)
    return records


def build_index() -> dict:
    vocab = load_vocab()
    exclude = set(vocab.get("index_exclude_statuses") or [])

    records = [r for r in load_scenarios() if r.get("status") not in exclude]
    records.sort(key=lambda r: (r.get("updated_date") or r.get("submitted_date") or "", r["title"]))

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total": len(records),
            "schema_url": "registry/schema.json",
            "vocabularies_url": "registry/vocabularies.yaml",
        },
        "vocabularies": {
            "systems": vocab.get("systems", []),
            "integration_types": vocab.get("integration_types", []),
            "protocols": vocab.get("protocols", []),
            "statuses": vocab.get("statuses", []),
        },
        "data": records,
    }


def serialize_index(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def comparable_payload(payload: dict) -> dict:
    """Copy payload without volatile meta.generated_at for --check diffs."""
    copy = json.loads(json.dumps(payload))
    copy.get("meta", {}).pop("generated_at", None)
    return copy


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; fail if registry/index.json is out of date",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=INDEX_PATH,
        help=f"Output path (default: {INDEX_PATH.relative_to(ROOT)})",
    )
    args = parser.parse_args()

    if not SCENARIOS_DIR.is_dir():
        print(f"ERROR: missing {SCENARIOS_DIR}", file=sys.stderr)
        return 1

    payload = build_index()
    content = serialize_index(payload)

    if args.check:
        if not args.output.is_file():
            print(f"ERROR: {args.output} does not exist; run build_registry_index.py", file=sys.stderr)
            return 1
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        if comparable_payload(existing) != comparable_payload(payload):
            print(
                "ERROR: registry/index.json is out of date. "
                "Run: python scripts/build_registry_index.py",
                file=sys.stderr,
            )
            return 1
        print("OK: registry/index.json is up to date")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(f"Wrote {args.output} ({payload['meta']['total']} records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
