#!/usr/bin/env python3
"""
Validate integration scenario YAML files under registry/scenarios/.

Checks:
  - JSON Schema (registry/schema.json)
  - Filename matches record id ({uuid}.yaml)
  - Duplicate advisory (same submitter + systems + integration_type)
  - related_scenario_ids reference existing records

Usage:
  python scripts/validate_registry.py
  python scripts/validate_registry.py --strict   # warnings fail the run
"""

from __future__ import annotations

import argparse
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_DIR = ROOT / "registry" / "scenarios"
SCHEMA_PATH = ROOT / "registry" / "schema.json"
TITLE_SIMILARITY_THRESHOLD = 0.85


def load_schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def load_scenario(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping at top level")
    return data


def collect_scenarios() -> list[tuple[Path, dict]]:
    if not SCENARIOS_DIR.is_dir():
        return []
    files = sorted(SCENARIOS_DIR.glob("*.yaml"))
    return [(p, load_scenario(p)) for p in files]


def validate_filename(path: Path, record: dict, errors: list[str]) -> None:
    expected = f"{record['id']}.yaml"
    if path.name != expected:
        errors.append(
            f"{path}: filename must be {expected} (matches id field)"
        )


def validate_schema(
    record: dict, path: Path, schema: dict, validator: jsonschema.Draft202012Validator
) -> None:
    for error in sorted(validator.iter_errors(record), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in error.path) or "(root)"
        raise ValueError(f"{path}: schema error at {loc}: {error.message}")


def duplicate_key(record: dict) -> tuple:
    return (
        record.get("submitted_by", "").strip().lower(),
        tuple(sorted(record.get("source_system", []))),
        tuple(sorted(record.get("target_system", []))),
        record.get("integration_type"),
    )


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def check_duplicates(
    scenarios: list[tuple[Path, dict]], warnings: list[str]
) -> None:
    by_key: dict[tuple, list[tuple[Path, dict]]] = {}
    for path, record in scenarios:
        key = duplicate_key(record)
        by_key.setdefault(key, []).append((path, record))

    for key, group in by_key.items():
        if len(group) < 2:
            continue
        ids = ", ".join(r["id"] for _, r in group)
        warnings.append(
            f"Duplicate advisory: same submitted_by + source + target + "
            f"integration_type ({ids})"
        )

    active = [
        (p, r)
        for p, r in scenarios
        if r.get("status") in ("Active", "Experimental")
    ]
    for i, (path_a, rec_a) in enumerate(active):
        for path_b, rec_b in active[i + 1 :]:
            sim = title_similarity(rec_a["title"], rec_b["title"])
            if sim >= TITLE_SIMILARITY_THRESHOLD:
                warnings.append(
                    f"Duplicate advisory: similar titles ({sim:.0%}) "
                    f"{rec_a['id']} and {rec_b['id']}"
                )


def check_related_ids(
    scenarios: list[tuple[Path, dict]], errors: list[str]
) -> None:
    known = {r["id"] for _, r in scenarios}
    for path, record in scenarios:
        for ref in record.get("related_scenario_ids") or []:
            if ref not in known:
                errors.append(
                    f"{path}: related_scenario_ids references unknown id {ref}"
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat duplicate advisories as errors (exit 1)",
    )
    args = parser.parse_args()

    if not SCHEMA_PATH.is_file():
        print(f"ERROR: missing {SCHEMA_PATH}", file=sys.stderr)
        return 1

    schema = load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    scenarios = collect_scenarios()

    if not scenarios:
        print(f"WARNING: no scenario files in {SCENARIOS_DIR}")
        return 0

    errors: list[str] = []
    warnings: list[str] = []

    for path, record in scenarios:
        try:
            validate_schema(record, path, schema, validator)
            validate_filename(path, record, errors)
        except ValueError as exc:
            errors.append(str(exc))

    check_related_ids(scenarios, errors)
    check_duplicates(scenarios, warnings)

    for w in warnings:
        print(f"WARNING: {w}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if warnings and args.strict:
        print(
            f"ERROR: {len(warnings)} advisory warning(s) with --strict",
            file=sys.stderr,
        )
        return 1

    print(f"OK: validated {len(scenarios)} scenario record(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
