# Traceability matrix

Maps **approved use cases** and **behavior scenarios** to **technical specifications**, protocols, and validation status. Update this document when specs are exported into [`specs/`](../specs/) or when scenario issues change materially.

**Milestones** (from [project updates](index.md)): draft specifications by **April 30, 2026**; final specifications and implementation package by **June 30, 2026**.

**RFP constraint**: each of the five CSTs (ArchivesSpace, CollectionSpace, DSpace, Fedora, VIVO) must appear in at least one integration-workflow specification. Confirm with Lyrasis whether the F1 integration repository alone satisfies Fedora/D1/D2-style documentation use cases.

---

## Master matrix

| Scenario | Use case IDs | CSTs | Protocol / focus | Behavior scenario issue | Spec document | Spec status | Scenario ↔ spec |
|----------|--------------|------|------------------|-------------------------|---------------|-------------|------------------|
| A1 | A1 | ArchivesSpace, DSpace | DSpace Search API; one-time link | [#7](https://github.com/lyrasisorghome/InteroperabilityProject/issues/7) | [`specs/A1-bidirectional-linking-as-ds.md`](../specs/A1-bidirectional-linking-as-ds.md) | Draft v0.2 | **In progress** — see gaps below |
| A2 | A2 | ArchivesSpace, DSpace | DSpace Search API; one-time link | [#44](https://github.com/lyrasisorghome/InteroperabilityProject/issues/44) | [`specs/A1-bidirectional-linking-as-ds.md`](../specs/A1-bidirectional-linking-as-ds.md) | Draft v0.2 | **In progress** — see gaps below |
| A3 | A3 | ArchivesSpace, DSpace | SWORD deposit + AS digital object | [#45](https://github.com/lyrasisorghome/InteroperabilityProject/issues/45) | — | — | Not started |
| A4 | A4 | ArchivesSpace, DSpace | SWORD batch deposit | [#52](https://github.com/lyrasisorghome/InteroperabilityProject/issues/52) | — | — | Not started |
| C1 | C1 | CollectionSpace | OAI-PMH 2.0 provider | [#46](https://github.com/lyrasisorghome/InteroperabilityProject/issues/46) | [`specs/C1-cs-oai-pmh.md`](../specs/C1-cs-oai-pmh.md) | Draft v0.2 | **In progress** — see gaps below |
| C2 | C2 | CollectionSpace, ArchivesSpace | OAI-PMH (CS) + shared discovery | [#47](https://github.com/lyrasisorghome/InteroperabilityProject/issues/47) | — (may extend C1 spec) | — | Not started |
| C3 | C3 | CollectionSpace, ArchivesSpace | Cross-system search / field mapping | [#51](https://github.com/lyrasisorghome/InteroperabilityProject/issues/51) | — | — | Not started |
| F1 | F1, D1, D2 | All five CSTs | Integration repository & documentation | [#58](https://github.com/lyrasisorghome/InteroperabilityProject/issues/58) | [`specs/F1-integration-scenario-registry.md`](../specs/F1-integration-scenario-registry.md) | Draft v0.2 | **In progress** — see gaps below; parent tracking [#57](https://github.com/lyrasisorghome/InteroperabilityProject/issues/57) |
| V1 | V1 | VIVO, DSpace | SWORD deposit | [#54](https://github.com/lyrasisorghome/InteroperabilityProject/issues/54) | [`specs/A1-bidirectional-linking-as-ds.md`](../specs/A1-bidirectional-linking-as-ds.md) | Draft v0.1 | **In progress** — see gaps below |
| V2 | V2 | VIVO, DSpace | COAR Notify | [#55](https://github.com/lyrasisorghome/InteroperabilityProject/issues/55) | — | — | Not started |

**Legend — Scenario ↔ spec**: `Not started` | `In progress` | `Aligned` | `Gap` (spec exists but does not cover scenario) | `N/A`

---

## CST coverage (RFP)

| CST | Scenarios | Spec documents (repo) | RFP workflow covered? |
|-----|-----------|-------------------------|------------------------|
| ArchivesSpace | A1, A2, A3, A4, C2, C3, F1 | A1 | **Partial** (A1, A2 only) |
| CollectionSpace | C1, C2, C3, F1 | C1 | **Partial** (C1 only) |
| DSpace | A1–A4, F1, V1, D1*, D2* | — | Pending specs |
| Fedora | F1 | F1 | Pending (likely via F1) |
| VIVO | V1, V2, F2 | V1 | **Partial** (V1 only) |

\*D1/D2 documented via integration repository (F1), not separate behavior-scenario issues.

---

## C1 validation snapshot

*Last reviewed against `specs/C1-cs-oai-pmh.md` (synced 2026-05-27) and [issue #46](https://github.com/lyrasisorghome/InteroperabilityProject/issues/46).*

### Behavior scenario steps

| ID | In GitHub #46 | In spec v0.2 | Notes |
|----|---------------|----------------|-------|
| BS01 | Partial (`>>> ??` navigation) | Partial (G-05 placeholder) | Align navigation path with ArchivesSpace OAI UI mirror |
| BS02 | Staff publish / harvest | Split across BS03, duplicate BS02 headings | Spec has duplicate/misnumbered BS02–BS04 blocks; needs editorial pass |
| BS03 | Discovery harvester config | BS04 in spec | Discovery UI correctly out of scope in spec |
| ES01–ES02 | Stubs | ES01–ES05 headings; ES01 body started | Complete error tables |
| — | OAI verb-level detail | Multiple BS02 verb sections | Good direction; tie each to testable XML examples |

### Open gaps (from spec)

Track resolution in the spec’s “Open Questions and Specification Gaps” section; high-priority items for validation:

| Gap ID | Topic | Blocks |
|--------|--------|--------|
| G-05 | OAI-PMH Settings navigation path | BS01 UI tests, admin docs |
| G-08 | Digital object exposure in OAI records | BS02 harvest assertions |
| G-10 | Endpoint authentication model | Security review, harvester config |

### Suggested validation artifacts (not yet in repo)

- [ ] Example `Identify`, `ListMetadataFormats`, `ListRecords` XML (fixture files under `examples/c1-oai-pmh/`)
- [ ] Curl or script checklist mapping each OAI verb to BS02 sections
- [ ] Field-mapping golden record (one CollectionSpace object → expected `oai_dc`)

---

## Spec inventory

| File | Scenarios | Version | Source |
|------|-----------|---------|--------|
| [`specs/C1-cs-oai-pmh.md`](../specs/C1-cs-oai-pmh.md) | C1 (C2 may overlap) | 0.2 draft | [Google Doc](https://docs.google.com/document/d/1TuCEufv8ekB6XgZT3aEr8g7ciW4d-xPvLh7T8tLswO4) |

*Redstart reported four feature specs in Google Docs; add rows here as each is exported.*

---

## How to update

1. Export or sync spec → `specs/<id>-<short-name>.md` with YAML front matter (`source`, `issue`, `last_synced`).
2. Set **Spec status** and **Scenario ↔ spec** in the master matrix.
3. For active specs, add a validation snapshot section (copy the C1 template above).
4. Keep [`scenarios/README.md`](../scenarios/README.md) issue links in sync when adding specs.
