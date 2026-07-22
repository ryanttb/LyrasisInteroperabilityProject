---
source: consultant draft (Ryan)
scenarios:
  - C1
issues:
  - https://github.com/lyrasisorghome/InteroperabilityProject/issues/46
related:
  - specs/C1-cs-oai-pmh.md
  - proposal/cs-meeting-notes.md
last_synced: 2026-06-23
---

# C1: OAI-PMH Provider for CollectionSpace - High-Level Feature Design

## Technical specification (architecture-first draft)

**Scenario:** [C1: Enabling discovery of a CollectionSpace object in an OAI-PMH enabled discovery repository](https://github.com/lyrasisorghome/InteroperabilityProject/issues/46)

**Status:** Draft v0.3:  high-level feature design; closes *where-in-the-codebase* gaps in [`C1-cs-oai-pmh.md`](C1-cs-oai-pmh.md)

**Systems:** CollectionSpace 8.x (Java services layer, Nuxeo, Elasticsearch), OAI-PMH 2.0 harvesters (external)

**Normative references:**

- [OAI-PMH 2.0](https://www.openarchives.org/OAI/openarchivesprotocol.html)
- [OAI-PMH Guidelines for Repository Implementers](https://www.openarchives.org/OAI/2.0/guidelines-repository.htm)
- [CollectionSpace for Developers](https://collectionspace.atlassian.net/wiki/spaces/cstd/pages/3570171905/CollectionSpace+for+Developers)
- [ArchivesSpace OAI-PMH architecture](https://docs.archivesspace.org/architecture/oai-pmh/) (behavioral reference; same LYRASIS ecosystem)
- [Dublin Core mapping (internal draft)](https://collectionspace.atlassian.net/wiki/spaces/CPD/pages/4081451009/Open+for+Internal+Comment+Dublin+Core+Mapping)
- Meeting notes: [`proposal/cs-meeting-notes.md`](../proposal/cs-meeting-notes.md)

---

## Purpose and scope

Define **how CollectionSpace would implement** native OAI-PMH 2.0 *provider* (repository) functionality so external discovery systems can harvest published collection-object metadata.

The parent spec [`C1-cs-oai-pmh.md`](C1-cs-oai-pmh.md) captures **requirements and behavior scenarios** but not **which Java modules, classes, configuration stores, or UI surfaces** would change. This document is the bridge to implementation planning.

This v0.1 draft covers:

1. **Deployment context** - where a running CollectionSpace instance lives and how HTTP traffic reaches it
2. **Existing components** to extend or reuse
3. **New components** (proposed packages, class names, responsibilities)
4. **Configuration and persistence** - tenant (.e.g, an institution or museum within an instance) bindings, optional harvest index, permissions
5. **Staff UI** touchpoints
6. **High-level request/data flows** with pseudocode sketches
7. **Open decisions** inherited from the parent spec and program-team meetings

Out of scope for v0.1 (defer to a lower-level design pass or client feedback):

- Full XML schema examples for every verb/error response
- Line-by-line Dublin Core mapping for every CollectionSpace profile
- Harvester-side configuration (discovery system UI)
- OAI **sets** hierarchy (deferred; `ListSets` returns `noSetHierarchy` - see meeting notes and Epic 5)
- Procedure/authority record harvesting
- Proof-of-concept GitHub repository (separate deliverable mentioned in meetings)

---

## Why the parent spec stalls

[`C1-cs-oai-pmh.md`](C1-cs-oai-pmh.md) defines **what** (verbs, roles, configuration table, DC mapping for Anthro) but leaves **how** open.

**Recommendation:** Treat **CollectionSpace services** as the primary implementation locus, mirror proven patterns from `PublicItemResource`, `ExportResource`, and `IndexResource`, and use **ArchivesSpace's OAI module** as a behavioral template, not a Java dependency.

---

## How "publishing" works in CollectionSpace

This is the central question raised in program-team feedback: *should OAI be a new "Publish To" target (a `Publish to OAI` option alongside `Publish to browser`), or simply a reuse of the existing public/not-public state?* Checked against the current codebase, the recommendation is **reuse the existing public state - do not add an `OAI-PMH` publish target.** This section documents the evidence so the decision is grounded in how the code actually behaves.

### There is no boolean "Publish" field

The parent behavior spec ([`C1-cs-oai-pmh.md`](C1-cs-oai-pmh.md)) refers to a *"'Publish' field"* that staff "toggle on" (BS03, and the Integration Architecture table). **No such field exists.** The real mechanism is **`Publish To`** (`publishTo`), a **repeating term-list field** backed by the `publishto` vocabulary. It is present on:

- Collection objects - `collectionobjects_common:publishToList/publishTo`
- Media - `media_common:publishToList/publishTo`
- Exhibitions - `exhibitions_common:publishToList/publishTo`

(See `cspace-ui.js` `src/plugins/recordTypes/{collectionobject,media,exhibition}/fields.js`; all use the term picker `source: 'publishto'`.)

### "Published" = a Publish To term with shortId `all` or `cspacepub`

A record is treated as publicly published when its `publishTo` list contains a term whose refName shortId is:

- `all` - label *"All"*
- `cspacepub` - label *"CollectionSpace Public Browser"*

This is the actual gate used today, in two independent places:

1. The Nuxeo -> Elasticsearch denormalizer that decides whether media/exhibition content is exposed (`services` `DefaultESDocumentWriter.isPublished`):

```java
String shortId = RefNameUtils.getItemShortId(value);
if (shortId.equals("all") || shortId.equals("cspacepub")) {
    isPublished = true;
    break;
}
```

2. The public gateway that fronts the public browser builds its Elasticsearch filter from configuration whose defaults are exactly these two shortids (`cspace-public-gateway` `application.yml`):

```yaml
es:
  allowedRecordTypes: CollectionObject
  recordTypes:
    CollectionObject:
      publishToField: collectionobjects_common:publishToList.shortid
    Media:
      publishToField: media_common:publishToList.shortid
  allowedPublishToValues: cspacepub,all
```

So the public browser's record set is precisely *collection objects whose `publishToList.shortid` is in `{all, cspacepub}`*. This is the same set the program team already said OAI should mirror ("Should support what is published now in the public browser," 2026-03-27 notes).

### Recommendation: reuse, don't extend

OAI harvest eligibility = the existing public-published state. Concretely:

- **No new `publishto` vocabulary term.** Remove `OAI-PMH` from the `publishto` picker and from every NXQL/ES predicate in this design.
- A record is harvestable when it is public (Publish To includes *All* or *CollectionSpace Public Browser*) - the same switch staff already use for the public browser.
- Which shortIds count is **configurable** (mirroring the gateway's `allowedPublishToValues`); default `all,cspacepub`. See `oai.harvestPublishToValues` below.

**Intended consequence (confirm with product):** OAI exposure becomes *coupled* to public-browser exposure - a record cannot be harvested via OAI without also being public in the browser, and vice-versa. The feedback explicitly asks for this single public/not-public switch, so the coupling is a feature, not an accident. If later work needs OAI-only or browser-only publishing, that is when a per-channel "Publish To" target would be reintroduced (the originally-drafted approach). The standing question in the parent spec's gap table - *"refactor Publish To... to a simple publish toggle?"* - is compatible with this: a single toggle would set/clear the public term.

---

## Assumptions

| ID | Assumption |
|----|------------|
| A-01 | Target CollectionSpace **8.x** on Tomcat; REST services WorkAuthority Resource (WAR) exposes `/cspace-services/...` per tenant. |
| A-02 | **Nuxeo** remains the system of record for collection objects and media metadata. |
| A-03 | **Elasticsearch** is already deployed (public browser / advanced search); may host a dedicated harvest index. |
| A-04 | Record eligibility **reuses the existing public-published state**: a record is harvestable when its **Publish To** (`publishto`) list includes a public term (refName shortId `all` or `cspacepub`) - the same state that drives the public browser. **No new `publishto` value is added.** (Revised per program-team feedback; supersedes the earlier "add an OAI-PMH value" direction. See *How "publishing" works*.) |
| A-05 | OAI **sets** are out of scope for this release; `ListSets` returns `noSetHierarchy`. |
| A-06 | Harvesters are **external**; CollectionSpace exposes an anonymous HTTP endpoint when the feature is enabled. |
| A-07 | A **scheduled refresh** (batch job + optional listener) prepares harvestable records; OAI verbs should not run heavy NXQL against live Nuxeo on every request (per meeting notes). |
| A-08 | Dublin Core mapping is **fixed in code** per profile (per meeting notes); configurable mapping is deferred (see Epic 5). |

---

## Actors and deployment context

```mermaid
flowchart TB
  subgraph External["External (out of scope)"]
    Harvester["OAI-PMH harvester\n(e.g. Blacklight, custom cron)"]
    EndUser["Discovery end user"]
  end

  subgraph CSDeploy["CollectionSpace deployment"]
    Gateway["cspace-public-gateway\n(optional reverse proxy)"]
    Services["services WAR\n/cspace-services/*"]
    UI["cspace-ui.js\nStaff UI"]
    ES["Elasticsearch"]
    Nuxeo["Nuxeo repository"]
    OAI["New: OAI-PMH endpoint\n/oai?verb=..."]
  end

  Staff["Staff / Admin"] --> UI
  Admin["System admin"] --> Services
  Harvester -->|"GET/POST OAI verbs"| OAI
  OAI --> Services
  Gateway -->|"public browser routes"| Services
  Gateway --> ES
  Services --> Nuxeo
  Services --> ES
  UI --> Services
  EndUser -.->|"uses harvested metadata"| Harvester
```

| Actor | Role |
|-------|------|
| **CollectionSpace System Administrator** | Enables feature at instance/tenant level via config files or tenant admin APIs not exposed in Staff UI. |
| **OAI-PMH Administrator** (new permission) | Enables/disables endpoint, edits repository name, admin email, harvest page size, etc. via Staff UI. |
| **Staff user** | Marks records harvestable via **Publish To**; may run bulk publish jobs. |
| **Harvester** | Calls OAI verbs on a schedule; handles resumption tokens and incremental `from`/`until`. |
| **OAI provider module** (new) | Serves XML responses from harvest index + config; enforces enabled/disabled state. |

### Typical URL shapes

Assume tenant `museum` and host `https://cs.example.edu`:

| Surface | Example URL | Notes |
|---------|-------------|-------|
| Services REST (authenticated) | `https://cs.example.edu/museum/cspace-services/collectionobjects/...` | Existing pattern |
| Public item (anonymous) | `https://cs.example.edu/museum/cspace-services/publicitems/{csid}/{tenantId}/content` | `PublicItemResource` precedent |
| **Proposed OAI base** | `https://cs.example.edu/museum/cspace-services/oai` | Registered in services WAR; anonymous when enabled |
| Gateway (if used) | `https://cs.example.edu/gateway/museum/cspace-services/oai` | Optional; add route in `cspace-public-gateway` |

---

## CollectionSpace repositories touched

| Repository | Role in OAI feature | Expected change level |
|------------|---------------------|------------------------|
| [collectionspace/services](https://github.com/collectionspace/services) | **Primary** - JAX-RS endpoint, mappers, batch jobs, listeners, tenant bindings | **Major** - new `oai` module |
| [collectionspace/application](https://github.com/collectionspace/application) | Tenant templates, default properties, Tomcat packaging | **Minor** - defaults in `*-tenant.xml`, profile deltas |
| [collectionspace/cspace-ui.js](https://github.com/collectionspace/cspace-ui.js) | Staff UI - settings page, Publish To, bulk job invoke | **Moderate** - new admin plugin + vocabulary display |
| [collectionspace/cspace-public-gateway](https://github.com/collectionspace/cspace-public-gateway) | Anonymous proxy to services/ES | **Optional minor** - route `/oai` if harvesters must use gateway hostname |
| Nuxeo platform extensions (under `services/`) | Document types, listeners | **Possible** - harvest record doctype or reuse ES-only index |

**Not required:** changes to `cspace-public-browser.js` (consumes ES for human search, not OAI).

---

## Existing components to reuse

CollectionSpace has **no OAI-PMH code today**. These patterns are the closest analogues:

### HTTP / JAX-RS registration

| Component | Location | Reuse for OAI |
|-----------|----------|---------------|
| `CollectionSpaceJaxRsApplication` | `services/JaxRsServiceProvider/.../CollectionSpaceJaxRsApplication.java` | Register new `OaiResource` singleton |
| `SecurityInterceptor` | `services/common/.../security/SecurityInterceptor.java` | Whitelist anonymous access on `/oai` when enabled (same pattern as `PublicItemResource.allowAnonymousAccess()`) |
| `*Resource` + `*Client` pair | Each service module | Follow `ExportClient.SERVICE_PATH` convention |

### Public / published content

| Component | Location | Reuse for OAI |
|-----------|----------|---------------|
| `PublicItemResource` | `services/common/.../publicitem/PublicItemResource.java` | Precedent for **anonymous** read endpoint backed by Nuxeo |
| `PublicItemDocumentModelHandler` | `services/publicitem/.../nuxeo/` | URL generation for public media links in DC `relation`/`identifier` |
| Publish To (`publishto` vocab) | `publishTo`/`publishToList` on collection object, media, exhibition (`cspace-ui.js` `recordTypes/*/fields.js`); public predicate `publishToList.shortid ∈ {all, cspacepub}` (`cspace-public-gateway`, `DefaultESDocumentWriter`) | **Reuse the existing public state** as the harvest gate - no new term |

### Query, export, and bulk update

| Component | Location | Reuse for OAI |
|-----------|----------|---------------|
| `ExportResource` | `services/export/.../ExportResource.java` | NXQL/query iteration over Nuxeo documents |
| `AbstractDocumentsByQueryIterator` | `services/export/.../` | Walk matching collection objects for harvest index build |
| `BatchResource` + `AbstractBatchJob` | `services/batch/.../` | Bulk enable Publish To; scheduled harvest index refresh |
| `ReindexFullTextBatchJob` (example) | `services/batch/.../nuxeo/` | Template for `OaiHarvestIndexBatchJob` |

### Search index

| Component | Location | Reuse for OAI |
|-----------|----------|---------------|
| `IndexResource` | `services/index/.../IndexResource.java` | `POST /index/{indexid}` reindex hook |
| `IndexDocumentModelHandler` | `services/index/.../` | Per-tenant NXQL for what gets indexed |
| Tenant index bindings | `services/common/.../tenants/tenant-bindings-proto-unified.xml` | Declare new index id (e.g. `oai-harvest`) |

### Authorization

| Component | Location | Reuse for OAI |
|-----------|----------|---------------|
| `CSpaceAction`, `AuthZ`, `RoleResource`, `PermissionResource` | `services/authorization*` | New permission e.g. `OAI-PMH Admin` with `ADMIN` on OAI config resource |
| Service authz suffix pattern | `{Module}Client.SERVICE_AUTHZ_SUFFIX` | e.g. `/*/oai/` for config mutations |

### Configuration

| Component | Location | Reuse for OAI |
|-----------|----------|---------------|
| `tenant-bindings-proto-unified.xml` + profile deltas | `services/common/.../tenants/` | Service binding for OAI module, batch jobs, listeners |
| `{profile}-tenant.xml` | `application/tomcat-main/src/main/resources/` | Instance-level defaults |
| `TenantBindingConfigReaderImpl` | `services/config/.../` | Runtime read of OAI settings |

---

## Proposed new components

### New Maven module: `services/oai/`

Mirror structure of `export` and `publicitem`:

```
services/oai/
  client/
    org/collectionspace/services/client/OaiClient.java
  jaxb/
    oai_config.xsd                    # admin config payload (optional REST CRUD)
    oai_harvest_record.xsd            # internal harvest document shape
  service/
    org/collectionspace/services/oai/
      OaiResource.java                # @Path("/oai") - verb dispatcher
      OaiRequestParser.java           # GET/POST param normalization
      OaiResponseWriter.java          # XML serialization, gzip
      OaiConfigService.java           # read merged tenant + admin config
      OaiHarvestRecordRepository.java # query harvest store (ES or Nuxeo)
      verb/
        IdentifyHandler.java
        ListMetadataFormatsHandler.java
        ListSetsHandler.java          # returns noSetHierarchy
        ListIdentifiersHandler.java
        ListRecordsHandler.java
        GetRecordHandler.java
      OaiResumptionTokenService.java  # token issue/validate/TTL
      mapper/
        OaiMetadataMapper.java        # interface
        OaiDcMapper.java              # oai_dc for collectionobject (per profile)
        ProfileMapperRegistry.java    # anthro, fcart, registration, etc.
      nuxeo/
        OaiHarvestDocumentModelHandler.java   # if harvest docs live in Nuxeo
      batch/
        OaiHarvestIndexBatchJob.java          # rebuild harvest index
        OaiPublishBatchJob.java               # bulk set Publish To from query
    resources/
      OaiHarvestIndexBatchJob.xml
      OaiPublishBatchJob.xml
```

### Class responsibilities (sketch)

**`OaiResource`** - single entry point; OAI uses query params, not RESTful subpaths:

```java
@Path(OaiClient.SERVICE_PATH)  // "/oai"
public class OaiResource extends AbstractResource {
    public boolean allowAnonymousAccess() { return configService.isEndpointEnabled(); }

    @GET @POST
    @Produces("application/xml")
    public Response handleOaiRequest(@Context UriInfo uri, MultivaluedMap formParams) {
        if (!configService.isEndpointEnabled()) return disabledResponse(); // see G-11
        OaiVerb verb = parser.parseVerb(uri, formParams);
        return verbRouter.dispatch(verb, parser.buildContext(uri, formParams));
    }
}
```

**`OaiHarvestIndexBatchJob`** - ETL from Nuxeo → harvest store:

```java
// Pseudocode: select PUBLIC collection objects, map to harvest records.
// Eligibility reuses the existing public state (the same set as the public browser):
// the record's Publish To list contains a public term whose refName shortId is
// "all" or "cspacepub". Configurable via oai.harvestPublishToValues (default: all,cspacepub).
for (DocumentModel doc : findPublicCollectionObjects(from, until)) {
    HarvestRecord rec = mapper.toHarvestRecord(doc);
    rec.setOaiIdentifier(pidFactory.for(doc));
    rec.setDatestamp(doc.getModifiedDate()); // UTC seconds
    rec.setDeleted(false);
    harvestRepository.upsert(rec);
}
tombstonePass(); // mark records whose public term was cleared, soft-deletes, hard-deletes

// findPublicCollectionObjects(...) should either:
//   (a) read from the existing public Elasticsearch index (recommended; see D-01), or
//   (b) run NXQL over collectionobjects_common:publishToList and filter in code with
//       RefNameUtils.getItemShortId(value) ∈ {all, cspacepub}. Publish To is stored as
//       refNames, so a pure-NXQL shortId predicate is awkward; reusing the public index
//       (a) keeps OAI eligibility identical to the public browser by construction.
```

**`ListRecordsHandler`** - read from harvest store, not live Nuxeo:

```java
Page<HarvestRecord> page = repository.findPublished(
    metadataPrefix, from, until, set, resumptionToken, maxRecords);
if (page.isEmpty()) return error("noRecordsMatch");
OaiXml records = page.items().stream()
    .map(r -> xml.record(r.identifier(), r.datestamp(), mapper.toMetadata(r)))
    .collect(OaiXml.listRecords());
if (page.hasMore()) records.setResumptionToken(tokenService.issue(page));
return Response.ok(records).build();
```

### Files to modify (existing)

| File | Change |
|------|--------|
| `services/pom.xml` | Add `<module>oai</module>` |
| `CollectionSpaceJaxRsApplication.java` | `singletons.add(new OaiResource());` or `addResourceToMapAndSingletons` |
| `tenant-bindings-proto-unified.xml` | OAI service binding, batch jobs, optional listener, index definition |
| Profile `*-tenant-bindings.delta.xml` | Register profile-specific `OaiDcMapper` |

> **No change to the `publishto` vocabulary.** Earlier drafts added an `OAI-PMH` term; that is removed. OAI eligibility reuses the existing public terms (`all`, `cspacepub`). See *How "publishing" works*.

---

## Configuration model

Two tiers align with the parent spec's roles:

### Tier 1 - System administrator (instance / tenant template)

Stored in **tenant bindings XML** and/or `{profile}-tenant.xml` in the **application** repo. Not editable in Staff UI.

| Key | Example | Purpose |
|-----|---------|---------|
| `oai.featureAvailable` | `true` | Master switch - without this, OAI code paths are inactive |
| `oai.baseUrl` | `https://cs.example.edu/museum/cspace-services/oai` | Canonical `baseURL` in Identify (may be computed from request if unset) |
| `oai.protocolVersion` | `2.0` | Identify response |
| `oai.deletedRecord` | `persistent` | Identify response; tombstone headers in List* |
| `oai.granularity` | `YYYY-MM-DDThh:mm:ssZ` | Identify response |
| `oai.maxRecordsPerRequest` | `100` | Resumption token threshold |
| `oai.resumptionTokenTtlSeconds` | `3600` | Token cache TTL |
| `oai.compressionSupported` | `true` | gzip response encoding |
| `oai.harvestIndexId` | `oai-harvest` | ES index name or Nuxeo doc type namespace |
| `oai.harvestPublishToValues` | `all,cspacepub` | Publish To shortIds that make a record harvestable; mirrors the gateway's `allowedPublishToValues`. Default = the public-browser set (i.e. OAI eligibility == public state) |
| `oai.harvestRefreshCron` | *(external)* | Document that ops scheduler invokes batch job - CS has no built-in cron |
| `oai.metadataFormats` | `oai_dc` | ListMetadataFormats source of truth |
| `oai.setSupportEnabled` | `false` | Sets deferred (Epic 5) |

**Storage mechanism:** extend tenant service binding for a new `OaiClient.SERVICE_NAME` in `tenant-bindings-proto-unified.xml`, properties read at runtime via existing `ServiceMain.getTenantBindingConfigReader()`.

### Tier 2 - OAI-PMH Administrator (Staff UI)

Stored in **Nuxeo configuration document** or **dedicated config record** exposed via authenticated REST (pattern used by other admin settings). Editable in Staff UI when user holds new permission.

| Key | Purpose |
|-----|---------|
| `oai.enabled` | Administrator toggle - endpoint returns 503/disabled when false |
| `oai.repositoryName` | Identify |
| `oai.repositoryDescription` | Identify `<description>` |
| `oai.adminEmail` | Identify (required) |
| `oai.earliestDatestamp` | Identify - computed from harvest index min datestamp unless overridden |
| `oai.includeMediaLinks` | Whether DC includes thumbnail/public URLs (`Supported Media` in parent spec) |
| `oai.publicBaseUrl` | Base for `relation` link to public browser record |

**REST shape (illustrative):**

```
GET  /cspace-services/oai/config        → 200 + OAI config JSON/XML (auth required)
PUT  /cspace-services/oai/config        → update admin-tier settings
POST /cspace-services/oai/config/test     → optional Identify dry-run for admins
```

### Record-level eligibility

| Field | Where | Rule |
|-------|-------|------|
| `publishTo` / `publishToList` | Collection object (and media, for media links) | Must include a **public** term (refName shortId `all` or `cspacepub`) - the same state that publishes to the public browser. No OAI-specific term |
| `ecm:modified` / record audit | Nuxeo | Becomes OAI **datestamp** (UTC, seconds) |

Bulk update: marking records public is the **existing publish-to-public workflow**. A bulk data update can set the public Publish To term from an advanced-search query URI (same invoke pattern as export/report batch jobs per meeting notes). Because eligibility reuses the public state, this does not need to be an OAI-specific job; `OaiPublishBatchJob` is optional sugar over the existing publish mechanism.

---

## Staff UI touchpoints (`cspace-ui.js`)

| Location | Change |
|----------|--------|
| **Administration → OAI-PMH Settings** (new) | New invocable plugin under admin/tools; mirrors ArchivesSpace "Manage OAI-PMH Settings" |
| **Publish To** field | **No change** - a record becomes harvestable when marked public (Publish To = *All* or *CollectionSpace Public Browser*), the same control already used for the public browser |
| **Bulk data update** | Reuse the existing publish-to-public bulk workflow (set the public Publish To term from a search query); no OAI-specific job required |
| **Record editor cue** | Optional help text clarifying that **public** records are also exposed via OAI-PMH (parent spec BS03) |

Proposed plugin path: `src/plugins/invocables/oaiSettings/` (or under existing admin plugin structure).

Permission gate: hide settings unless user has new **OAI-PMH Administrator** permission (parent spec).

---

## Data flow: harvest index (recommended)

Meeting notes and performance requirements point to **decoupling harvest reads from live Nuxeo queries**:

```mermaid
sequenceDiagram
  participant Staff
  participant UI as cspace-ui.js
  participant Svc as services
  participant Nuxeo
  participant ES as Elasticsearch
  participant Harv as Harvester

  Staff->>UI: Set Publish To = Public (All / CollectionSpace Public Browser)
  UI->>Svc: PUT collectionobject
  Svc->>Nuxeo: save document
  Note over Svc: Optional listener queues incremental update

  Note over Svc: Scheduled OaiHarvestIndexBatchJob
  Svc->>Nuxeo: NXQL published objects
  Svc->>ES: upsert oai-harvest documents

  Harv->>Svc: ListRecords?metadataPrefix=oai_dc&from=...
  Svc->>ES: paginated query + date filter
  Svc-->>Harv: OAI-PMH XML + resumptionToken
```

### Harvest record document (logical)

Internal shape stored in ES (or Nuxeo sidecar documents):

```json
{
  "csid": "abc-123",
  "oaiIdentifier": "oai:cs.example.edu:museum/abc-123",
  "datestamp": "2026-06-01T14:30:00Z",
  "deleted": false,
  "metadataPrefix": "oai_dc",
  "profile": "anthropology",
  "metadataXml": "<oai_dc:dc>...</oai_dc:dc>"
}
```

Pre-computing `metadataXml` at index time avoids mapping cost on every harvest request; remapping requires reindex job after code/config changes.

**Alternative (simpler, higher load):** query Nuxeo directly on each ListRecords - acceptable only for small repositories; not recommended as default.

---

## OAI protocol surface

Inherited from parent spec; implementation mapping:

| Verb | Behavior | Handler |
|------|------------------|---------|
| `Identify` | Repository metadata from config | `IdentifyHandler` |
| `ListMetadataFormats` | At minimum `oai_dc` | `ListMetadataFormatsHandler` |
| `ListSets` | Error `noSetHierarchy` | `ListSetsHandler` |
| `ListIdentifiers` | Headers from harvest index | `ListIdentifiersHandler` |
| `ListRecords` | Headers + metadata | `ListRecordsHandler` |
| `GetRecord` | Single record by OAI identifier | `GetRecordHandler` |

| Requirement | Implementation note |
|-------------|---------------------|
| GET and POST | Both hit `OaiResource.handleOaiRequest` |
| Persistent identifiers | Build from tenant + CSID: `oai:{host}:{tenant}/{csid}` (parent spec G - confirm with product) |
| Deleted records | `deletedRecord=persistent`; tombstone entries in harvest index when object soft-deleted or Publish To cleared |
| Resumption tokens | `OaiResumptionTokenService` - in-memory or Nuxeo/Redis cache; `badResumptionToken` if expired |
| Compression | `OaiResponseWriter` wraps XML with gzip when `Accept-Encoding` allows |

---

## Delete and unpublish semantics

CollectionSpace has multiple removal paths (meeting notes). This release must document behavior:

| Event | Proposed OAI behavior |
|-------|----------------------|
| Public Publish To term cleared (record no longer public) | Harvest index row updated; next List* shows `status="deleted"` tombstone |
| Soft delete | Tombstone with last known identifier |
| Hard delete | Tombstone retained in harvest index with `deleted=true` (persistent policy); identifier may be CSID-based |
| Incremental harvest | Harvester diffs ListIdentifiers; deleted headers signal removal in discovery layer |

Reference: ArchivesSpace `OAIDeletion` / tombstone pass in [AS OAI repository](https://github.com/archivesspace/archivesspace/blob/master/backend/app/lib/oai/aspace_oai_repository.rb).

---

## Dublin Core mapping

| Source | Direction |
|--------|-----------|
| [Internal DC mapping draft (Confluence)](https://collectionspace.atlassian.net/wiki/spaces/CPD/pages/4081451009/Open+for+Internal+Comment+Dublin+Core+Mapping) | **Authoritative** for field choices |
| [`C1-cs-oai-pmh.md` Anthro table](C1-cs-oai-pmh.md#default-dublin-core-field-mapping---anthro-profile) | Example for one profile |
| Meeting notes | **Not user-configurable** in this release; no arbitrary XSLT upload |

Implementation: one `OaiDcMapper` subclass or profile section per CollectionSpace profile; registered in `ProfileMapperRegistry` at startup from tenant profile id.

Media links: include public thumbnail URL in `dc:relation` when `oai.includeMediaLinks` is true (parent spec G-03).

---

## Reference: ArchivesSpace OAI (behavioral, not code reuse)

| AS component | CS analogue |
|--------------|-------------|
| `ArchivesSpaceOAIRepository` | `OaiResource` + verb handlers |
| `ArchivesSpaceOAIRecord` | `HarvestRecord` |
| `ArchivesSpaceResumptionToken` | `OaiResumptionTokenService` |
| `OAIDeletion` / tombstone pass | End of `OaiHarvestIndexBatchJob` |
| `oai/mappers/oai_dc.rb` | `OaiDcMapper.java` |
| System → Manage OAI-PMH Settings | Administration → OAI-PMH Settings |
| Separate OAI port (8082) | Shared services WAR path `/oai` (simpler ops) |

---

## Open decisions (for client / product feedback)

| ID | Question | Options | Default recommendation |
|----|----------|---------|------------------------|
| D-01 | Harvest store backend | Elasticsearch index vs Nuxeo harvest documents | **Elasticsearch** - aligns with public browser infra |
| D-02 | Endpoint hostname | Services direct vs public gateway | **Services direct** unless institution requires single gateway URL |
| D-03 | Endpoint authentication | Open vs IP allowlist vs token | **Open when enabled** (OAI convention); document risk |
| D-04 | User-configurable DC mapping | Fixed code vs admin UI vs XSLT | **Fixed per profile** per meeting notes |
| D-05 | Publish To scope | Reuse public state vs new OAI target | **Resolved (per feedback): reuse the public/not-public state**; no `OAI-PMH` term. Confirm the coupling (OAI set == public-browser set) is acceptable, and whether `oai.harvestPublishToValues` should ever be allowed to differ from the gateway's `allowedPublishToValues` |
| D-06 | Missing required DC fields | Block publish / exclude / empty elements | Recommend **warn in UI, exclude from harvest** until complete |
| D-07 | Disabled endpoint HTTP code | 503 vs 404 vs OAI error document | Recommend **503** with plain text or minimal OAI error (G-11) |
| D-08 | Metadata formats beyond `oai_dc` | Baseline vs later | **Defer (Epic 5)** unless C2 timeline requires MODS/LIDO |
| D-09 | Listener vs batch-only refresh | Real-time index update vs scheduled only | **Both**: listener for low latency; batch for full rebuild |
| D-10 | New permission name / role mapping | Greenfield vs extend Exports role | **New permission** per parent spec |

---

## Suggested epics

These are units of work, **not sequential phases** - the whole feature is a single delivery. The numbering is for reference only; several epics can proceed in parallel once Epic 1 establishes the harvest index (e.g. Admin UI and Staff workflow), and Epic 5 is the natural "later" work if the program team chooses to extend beyond the baseline.

| Epic | Deliverable | Repos |
|------|-------------|-------|
| **0 - Spike** | Identify + ListMetadataFormats on static config; anonymous routing | `services` |
| **1 - Core harvest** | Harvest index job, ListRecords/ListIdentifiers/GetRecord, `oai_dc` for one profile | `services`, `application` |
| **2 - Admin UI** | Settings page, permission, enable/disable toggle | `cspace-ui.js`, `services` |
| **3 - Staff workflow** | Reuse public Publish To state, bulk publish (existing workflow), delete/tombstone pass | `services`, `cspace-ui.js` |
| **4 - Hardening** | Compression, resumption token edge cases, logging, additional profiles | `services` |
| **5 - Sets & formats** | ListSets, optional metadata prefixes | `services` |

---

## Related documents

| Document | Relationship |
|----------|--------------|
| [`C1-cs-oai-pmh.md`](C1-cs-oai-pmh.md) | Requirements baseline - roles, verbs, config table, gaps G-01–G-12 |
| [`proposal/cs-meeting-notes.md`](../proposal/cs-meeting-notes.md) | Program-team constraints (Publish To, no sets, fixed mapping, batch index) |
| [`A2-dspace-bulk-linking.md`](A2-dspace-bulk-linking.md) | Example of consultant "dev spec" depth for comparison; C1 lower-level pass would add similar pseudocode per verb |

---

## Document history

| Version | Date | Notes |
|---------|------|-------|
| 0.1-draft | 2026-06-10 | Initial high-level feature design |
| 0.2-draft | 2026-06-23 | Reworked "publishing" model per program-team feedback: OAI eligibility reuses the existing public/not-public state (Publish To shortId `all`/`cspacepub`) instead of adding an `OAI-PMH` publish target. Added *How "publishing" works* section; updated A-04, NXQL, config (`oai.harvestPublishToValues`), eligibility, Staff UI, data flow, deletes, and D-05. |
| 0.3-draft | 2026-06-23 | Removed "phase" framing (feedback found it confusing): the work is a single delivery. Renamed "Suggested delivery phases" to "Suggested epics" (parallelizable units of work), renumbered the trailing "II - Sets & formats" to "5", and stripped "Phase I"/"Phase II" language throughout. |
