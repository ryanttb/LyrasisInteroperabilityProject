# Behavior scenarios

Canonical **discussion and draft BDD** for each scenario live on GitHub ([`lyrasisorghome/InteroperabilityProject`](https://github.com/lyrasisorghome/InteroperabilityProject/issues)). This index is the stable lookup table for validation work in this repo.

| ID | Title | GitHub issue | CST labels | Spec in repo |
|----|-------|--------------|------------|--------------|
| [A1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/7) | Link one item record in DSpace to one digital object record in ArchivesSpace | [#7](https://github.com/lyrasisorghome/InteroperabilityProject/issues/7) | ArchivesSpace, DSpace | [`specs/A1-bidirectional-linking-as-ds.md`](../specs/A1-bidirectional-linking-as-ds.md) |
| [A2](https://github.com/lyrasisorghome/InteroperabilityProject/issues/44) | Link a collection in DSpace to many digital object records in ArchivesSpace | [#44](https://github.com/lyrasisorghome/InteroperabilityProject/issues/44) | ArchivesSpace, DSpace | [`specs/A1-bidirectional-linking-as-ds.md`](../specs/A1-bidirectional-linking-as-ds.md) |
| [A3](https://github.com/lyrasisorghome/InteroperabilityProject/issues/45) | Deposit a file to a SWORD-compliant repository and link to it in ArchivesSpace | [#45](https://github.com/lyrasisorghome/InteroperabilityProject/issues/45) | ArchivesSpace, DSpace | — |
| [A4](https://github.com/lyrasisorghome/InteroperabilityProject/issues/52) | Deposit many files to a SWORD-compliant repository and link them in ArchivesSpace | [#52](https://github.com/lyrasisorghome/InteroperabilityProject/issues/52) | ArchivesSpace | — |
| [C1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/46) | Enabling discovery of a CollectionSpace object in an OAI-PMH enabled discovery repository | [#46](https://github.com/lyrasisorghome/InteroperabilityProject/issues/46) | CollectionSpace | [`specs/C1-cs-oai-pmh.md`](../specs/C1-cs-oai-pmh.md) |
| [C2](https://github.com/lyrasisorghome/InteroperabilityProject/issues/47) | Configure a search interface for CollectionSpace and ArchivesSpace | [#47](https://github.com/lyrasisorghome/InteroperabilityProject/issues/47) | ArchivesSpace, CollectionSpace | — |
| [C3](https://github.com/lyrasisorghome/InteroperabilityProject/issues/51) | Search CollectionSpace and ArchivesSpace records from one interface | [#51](https://github.com/lyrasisorghome/InteroperabilityProject/issues/51) | ArchivesSpace, CollectionSpace | — |
| [F1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/58) | Lyrasis Interoperability Database | [#58](https://github.com/lyrasisorghome/InteroperabilityProject/issues/58) | ArchivesSpace, CollectionSpace, DSpace, Fedora, VIVO | [`specs/F1-integration-scenario-registry.md`](../specs/F1-integration-scenario-registry.md), [`specs/F1-dev-integration-registry-platform.md`](../specs/F1-dev-integration-registry-platform.md), [`registry/`](../registry/) |
| [V1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/54) | Deposit to DSpace using SWORD | [#54](https://github.com/lyrasisorghome/InteroperabilityProject/issues/54) | DSpace, VIVO | [`specs/V1-vivo-sword-deposit.md`](../specs/V1-vivo-sword-deposit.md) |
| [V2](https://github.com/lyrasisorghome/InteroperabilityProject/issues/55) | Sync metadata between VIVO and a COAR Notify-compliant repository | [#55](https://github.com/lyrasisorghome/InteroperabilityProject/issues/55) | VIVO | — |

## Related use cases (not separate behavior-scenario issues)

These appear in the [March 2026 use-case table](https://lyrasisorghome.github.io/InteroperabilityProject/) and are expected to be covered by the **integration repository / documentation** work (see F1 and [#57](https://github.com/lyrasisorghome/InteroperabilityProject/issues/57)) rather than standalone behavior-scenario issues:

| ID | Summary | Notes |
|----|---------|--------|
| D1 | LMS → DSpace deposit | Tracked under integration repository |
| D2 | DSpace → OJS manuscript update | Tracked under integration repository |

## Optional local mirrors

You do **not** need to copy issue bodies into this repo for me to work from issue URLs. If a scenario stabilizes, you may add `scenarios/<ID>.md` (e.g. `scenarios/C1.md`) with the same front matter pattern as specs:

```yaml
---
issue: https://github.com/lyrasisorghome/InteroperabilityProject/issues/46
last_synced: YYYY-MM-DD
---
```

## Refreshing this index

Issue titles and numbers can be regenerated from GitHub:

```bash
curl -s 'https://api.github.com/search/issues?q=repo:lyrasisorghome/InteroperabilityProject+Behavior+Scenario+in:title&per_page=20' \
  -o /tmp/scenarios.json
python3 scripts/parse_scenarios.py /tmp/scenarios.json
```

See also [`docs/traceability.md`](../docs/traceability.md) for scenario ↔ spec ↔ protocol coverage.
