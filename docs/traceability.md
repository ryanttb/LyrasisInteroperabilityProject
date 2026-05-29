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
| F1 | F1, D1, D2 | All five CSTs | Integration repository & documentation | [#58](https://github.com/lyrasisorghome/InteroperabilityProject/issues/58) | [`specs/F1-integration-scenario-registry.md`](../specs/F1-integration-scenario-registry.md) | Draft v0.1 | **In progress** — see gaps below; parent tracking [#57](https://github.com/lyrasisorghome/InteroperabilityProject/issues/57) |
| V1 | V1 | VIVO, DSpace | SWORD deposit | [#54](https://github.com/lyrasisorghome/InteroperabilityProject/issues/54) | [`specs/V1-vivo-sword-deposit.md`](../specs/V1-vivo-sword-deposit.md) | Draft v0.1 | **In progress** — see gaps below |
| V2 | V2 | VIVO, DSpace | COAR Notify | [#55](https://github.com/lyrasisorghome/InteroperabilityProject/issues/55) | — | — | Not started |

**Legend — Scenario ↔ spec**: `Not started` | `In progress` | `Aligned` | `Gap` (spec exists but does not cover scenario) | `N/A`

---

## CST coverage (RFP)

| CST | Scenarios | Spec documents (repo) | RFP workflow covered? |
|-----|-----------|-------------------------|------------------------|
| ArchivesSpace | A1, A2, A3, A4, C2, C3, F1 | [`A1-bidirectional-linking-as-ds`](../specs/A1-bidirectional-linking-as-ds.md) | **Partial** (A1, A2 only) |
| CollectionSpace | C1, C2, C3, F1 | [`C1-cs-oai-pmh`](../specs/C1-cs-oai-pmh.md) | **Partial** (C1 only) |
| DSpace | A1–A4, F1, V1, D1*, D2* | [`A1-bidirectional-linking-as-ds`](../specs/A1-bidirectional-linking-as-ds.md), [`V1-vivo-sword-deposit`](../specs/V1-vivo-sword-deposit.md) | **Partial** (A1/A2, V1) |
| Fedora | F1 | [`F1-integration-scenario-registry`](../specs/F1-integration-scenario-registry.md) | Pending (likely via F1) |
| VIVO | V1, V2, F1 | [`V1-vivo-sword-deposit`](../specs/V1-vivo-sword-deposit.md) | **Partial** (V1 only) |

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

## A1 validation snapshot

*Last reviewed against `specs/A1-bidirectional-linking-as-ds.md` (synced 2026-05-27) and [issue #7](https://github.com/lyrasisorghome/InteroperabilityProject/issues/7).*

### Behavior scenario steps

| ID | In GitHub #7 | In spec v0.2 | Notes |
|----|--------------|--------------|-------|
| BS01 | Config at System > Manage Repositories | BS-01 (Configuration section) | Aligned; spec adds field-level detail |
| BS02 | Search from Instances > Digital Object > Browse | BS-02 heading only; detail in BS-03 table | Spec splits entry points; BS-02 body empty |
| BS03 | Search from File Versions > Browse | BS-04 | Aligned |
| BS04 | Autocomplete from Instances > Digital Object | Not explicit | Spec uses dedicated search screen + Search button (addresses Bridget's autocomplete concern) |
| BS05 | Autocomplete from File Versions | Not explicit | Same as BS04 |
| BS06 | Link → new Digital Object + PATCH DSpace | BS-11 | Aligned; spec names metadata source option |
| BS07 | Link → new File Version + PATCH DSpace | BS-10 | Aligned |
| ES01 | Browse disabled when config inactive | Not in ES section | **Gap** — add ES scenario or reference config toggle |
| ES02 | DSpace search API fails | ES-02 heading only | **Gap** — body empty in spec |

### Open gaps (from spec)

| Gap ID | Topic | Blocks |
|--------|--------|--------|
| G-02 | Multiple DSpace repos per AS instance | BS01 config model, admin UX |
| G-10 | Multi-field search operators | BS-06–BS-09 search behavior tests |
| G-12 | Publish vs Save distinct flows | BS-08/BS-09 button behavior |
| G-14 | Configurable search fields | Search UI acceptance criteria |
| G-15 | Configurable result display fields | Result list assertions |

### Suggested validation artifacts (not yet in repo)

- [ ] Example DSpace Discover API search request/response (JSON fixtures under `examples/a1-dspace-search/`)
- [ ] Example PATCH payload for bidirectional URI write-back
- [ ] Matrix: spec BS-02–BS-11 ↔ GitHub BS02–BS07 entry points

---

## A2 validation snapshot

*Last reviewed against `specs/A1-bidirectional-linking-as-ds.md` (synced 2026-05-27) and [issue #44](https://github.com/lyrasisorghome/InteroperabilityProject/issues/44). A2 shares the A1 spec document (bulk/collection linking section).*

### Behavior scenario steps

| ID | In GitHub #44 | In spec v0.2 | Notes |
|----|---------------|--------------|-------|
| BS01 | Add Digital Collection → DOs for each DSpace item + PATCH each | BS-12 | Partially aligned; spec covers link-existing-collection path only |
| BS02 | Create DSpace items from AS children + append File Versions | Not specified | **Major gap** — open questions in issue; spec G-06 |
| BS03 | Config (refs #7) | BS-01 (shared with A1) | Aligned via A1 |
| ES01 | Add Digital Collection button inactive | Not in ES section | **Gap** |
| ES02 | Missing date on AS record (DSpace requires year) | ES-04 heading only | **Gap** — body empty; A2-specific |

### Open gaps (from spec)

| Gap ID | Topic | Blocks |
|--------|--------|--------|
| G-06 | Bulk linking scenarios and many-to-many matching | BS01/BS02 coverage for A2 |
| G-19 | Confirmation before bulk DO creation | BS-12 UX and safety tests |
| G-06 (issue) | Match DSpace collection items to AS digital objects | Core A2 workflow design |

### Suggested validation artifacts (not yet in repo)

- [ ] Collection-with-N-items fixture: expected N AS digital objects + N PATCH calls
- [ ] Decision doc: link-existing vs create-in-DSpace paths (issue BS01 vs BS02)
- [ ] Field mapping for AS → DSpace item creation (date handling per issue ES02)

---

## V1 validation snapshot

*Last reviewed against `specs/V1-vivo-sword-deposit.md` (synced 2026-05-27) and [issue #54](https://github.com/lyrasisorghome/InteroperabilityProject/issues/54).*

### Behavior scenario steps

| ID | In GitHub #54 | In spec v0.1 | Notes |
|----|---------------|--------------|-------|
| BS01 | Deposit file + link on profile (SWORD v3 flow) | BS01 config + BS02 deposit (mixed v2/v3) | Spec reframes as admin config + researcher wizard; issue still has v3 inline questions |
| BS02 | Retrieve metadata from Object (SWORD 3.2) | BS03 heading only | **Gap** — link-existing-IR path not written |
| BS03 | Complete in-progress deposit (SWORD 8) | Not in spec | **Gap** — out of scope for v0.1? |
| BS04 | Delete object (SWORD 6.4) | Not in spec | **Gap** — issue has draft; spec omits |
| ES (401/403/405/412) | Listed in issue | ES01–ES05 headings only | **Gap** — error tables empty |

### Open gaps (from spec)

| Gap ID | Topic | Blocks |
|--------|--------|--------|
| G-01 | Auth model per SWORD version (Basic vs OAuth) | BS02 deposit flow, security review |
| G-03 | Per-researcher vs shared IR credentials | End-to-end deposit tests |
| G-04 | SWORD package format (Zip/SAF vs Atom) | DSpace PoC validation |
| G-06 | VIVO file upload / attachment model | BS02 UI and data path |
| G-07 | VIVO ontology → IR metadata mapping | Deposit wizard pre-population |
| G-11 | Required VIVO permission values | Admin configuration docs |

### Cross-cutting issue (GitHub #54 comments)

- **SWORD v2 vs v3**: Issue drafted against v3; DSpace and most IRs deploy v2. Spec acknowledges both but PoC targets DSpace SWORD v2 — align BS02 HTTP steps to v2 AtomPub for validation work.
- **Collection selection**: Brian Lowe asked about multi-collection choice within a repo; spec BS01 mentions default collection but not per-deposit override — confirm in G-05 scope.

### Suggested validation artifacts (not yet in repo)

- [ ] SWORD v2 Service Document + deposit request/response examples (`examples/v1-sword-v2/`)
- [ ] Metadata mapping table: VIVO publication RDF → DSpace SAF/dublin_core
- [ ] Auth flow diagram (shared service account vs per-user OAuth)

---

## Spec inventory

| File | Scenarios | Version | Source |
|------|-----------|---------|--------|
| [`specs/A1-bidirectional-linking-as-ds.md`](../specs/A1-bidirectional-linking-as-ds.md) | A1, A2 | 0.2 draft | [Google Doc](https://docs.google.com/document/d/1GVP7IgAcK4kcJyl27Fobm_EuDJZTnh_IbUl5C61jNYw) |
| [`specs/C1-cs-oai-pmh.md`](../specs/C1-cs-oai-pmh.md) | C1 (C2 may overlap) | 0.2 draft | [Google Doc](https://docs.google.com/document/d/1TuCEufv8ekB6XgZT3aEr8g7ciW4d-xPvLh7T8tLswO4) |
| [`specs/F1-integration-scenario-registry.md`](../specs/F1-integration-scenario-registry.md) | F1, D1, D2 | 0.1 draft | [Google Doc](https://docs.google.com/document/d/1_ecWifpqfNN5PrmN3ZnqcjlgAqrYTbtNMWLDi5x6y1s) |
| [`specs/V1-vivo-sword-deposit.md`](../specs/V1-vivo-sword-deposit.md) | V1 | 0.1 draft | [Google Doc](https://docs.google.com/document/d/1YWPMBOrjoQC3e_cQUTZu3BKsgVw0TH0cqh7-o_UNV8U) |

---

## How to update

1. Export or sync spec → `specs/<id>-<short-name>.md` with YAML front matter (`source`, `issue`, `last_synced`).
2. Set **Spec status** and **Scenario ↔ spec** in the master matrix.
3. For active specs, add a validation snapshot section (copy the C1 template above).
4. Keep [`scenarios/README.md`](../scenarios/README.md) issue links in sync when adding specs.
