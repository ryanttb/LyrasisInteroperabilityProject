# Integration Scenario Registry (F1 prototype)

Lightweight **GitHub-native registry** for real-world CST integration records. Each record is one YAML file; CI validates schema and keeps `index.json` in sync for search UI / API consumers.

**Spec:** [`specs/F1-dev-integration-registry-platform.md`](../specs/F1-dev-integration-registry-platform.md)

## Layout

| Path | Purpose |
|------|---------|
| `schema.json` | JSON Schema for scenario records |
| `vocabularies.yaml` | Controlled lists (systems, protocols, statuses) |
| `scenarios/{uuid}.yaml` | One integration record per file |
| `index.json` | Built index for read-only clients (commit after editing YAML) |
| `requirements.txt` | Python deps for validation scripts |

## Add or edit a record

1. Generate a UUID (e.g. `uuidgen` on macOS/Linux, or [uuidgenerator.net](https://www.uuidgenerator.net/)).
2. Create `scenarios/{uuid}.yaml` using an existing file as a template.
3. Ensure `id` in the file **matches the filename**.
4. From the repo root:

   ```powershell
   pip install -r registry/requirements.txt
   python scripts/validate_registry.py
   python scripts/build_registry_index.py
   ```

5. Commit both the YAML file and the updated `index.json`.
6. Open a pull request (see `.github/PULL_REQUEST_TEMPLATE/registry-record.md`).

Records with status `Retired` or `Recalled` are excluded from `index.json` but remain in the repo for audit history.

## Local validation

```powershell
python scripts/validate_registry.py          # errors only
python scripts/validate_registry.py --strict # duplicate advisories fail too
python scripts/build_registry_index.py --check  # verify index.json is current
```

## GitHub Actions

Workflow: [`.github/workflows/registry-validate.yml`](../.github/workflows/registry-validate.yml)

On every pull request (and push to `main`) that touches `registry/**`:

1. **Checkout** — Actions clones your branch.
2. **Setup Python** — Installs Python 3.12 and caches pip packages.
3. **Validate** — Runs `validate_registry.py` (schema, filename, duplicate warnings).
4. **Index check** — Runs `build_registry_index.py --check` so YAML and `index.json` cannot drift.

If validation fails, the PR shows a red ✗ on the **Checks** tab; expand **Registry validate** for log output.

Contributors without Actions experience: you do not configure anything on GitHub—the workflow runs automatically when the YAML file is present on the default branch or in a PR.

## Submit without editing YAML

Use the issue form **Registry submission** (`.github/ISSUE_TEMPLATE/registry-submission.yml`). A maintainer converts approved submissions into a YAML file + PR.

## Phase II API

`index.json` shape:

```json
{
  "meta": { "generated_at": "…", "total": 3 },
  "vocabularies": { "systems": ["ArchivesSpace", "…"] },
  "data": [ { "id": "…", "title": "…", "source_system": ["…"], … } ]
}
```

A future static site or Cloudflare Worker can expose `GET /api/v1/scenarios` by filtering this file—no schema change required.
