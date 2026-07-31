---
source: https://docs.google.com/document/d/1_yfEmANTI4Ig9CrJOEpnqZcirJriTFNH5MvacOgA-C0
scenario: C3
issue: https://github.com/lyrasisorghome/InteroperabilityProject/issues/51
last_synced: 2026-07-31
---
# **Shared Discovery for CollectionSpace and ArchivesSpace**

## Technical Specification

*Unified Search and Display Interface for archives and material culture*

Document Status: DRAFT  
Version: 0.3  
Date: June 2026  
Source Story: [C3](https://github.com/lyrasisorghome/InteroperabilityProject/issues/51)  
Project: LYRASIS Interoperability Project  
Systems: Discovery Layer (OAI-PMH) – ArchivesSpace PUI – CollectionSpace Public Browser

[Purpose and Scope](#heading=)

[Background](#heading=)

[System Overview](#heading=)

[Actors and Deployment Context](#actors-and-deployment-context)

[Configuration Requirements](#configuration-requirements)

[New components](#new-components)

[Search](#search-backends)

[Intermediate Result Card Schema](#intermediate-result-card-schema)

[Display Implementation Options](#display-implementation-options)

[BFF search contract (sketch)](#bff-search-contract-\(sketch\))

[High-Level Sequence](#high-level-sequence)

[Behavior Scenarios](#behavior-scenarios)

[Error Scenarios](#error-scenarios)

[Open Questions and Specification Gaps](#open-questions-and-specification-gaps)

[Review Questions](#review-questions)

# **Purpose and Scope**

This specification defines requirements for a unified search and display interface that surfaces records from both ArchivesSpace and CollectionSpace in a single search experience. 

## Assumptions

| ID | Assumption |
| :---- | :---- |
| A-01 | **Path A** is the implementation target for this deliverable unless product explicitly selects Path B. |
| A-02 | Scope is **one configured pair**: one ArchivesSpace instance (one or more repositories, configurable) \+ one CollectionSpace tenant. |
| A-03 | Deliverable is a **new** shared-discovery application (public UI \+ BFF), not a plugin inside AS PUI or CS Public Browser. |
| A-04 | **Click-through only:** result titles / “View full record” open the AS PUI or CS Public Browser in a **new tab**. No intermediate detail page in the shared UI. |
| A-05 | AS record types in v1: **`archival_object`** and **`digital_object`**. Resources, agents, accessions, etc. deferred. |
| A-06 | CS record types in v1: **collection objects** already exposed to the public browser / gateway (same publish gate as C1: Publish To `all` / `cspacepub`). |
| A-07 | CS queries go through the **public gateway → Elasticsearch** path (anonymous), not authenticated Common Services staff search. |
| A-08 | AS queries use the **backend Search API** (`/repositories/:id/search` or `/search`). Prefer a **read-only API user \+ session token** held only in the BFF; investigate anonymous/public search if a given deploy allows it. Backend port **8089 must not be exposed to browsers** — only to the BFF (allowlist). |
| A-09 | Results are presented **grouped by source** (see Display options). No global merged relevance ranking in v1. |
| A-10 | Facets in v1 are **coarse**: source system; optional “has media/thumbnail”; optional simple date bounds if both adapters can supply them cheaply. |
| A-11 | “Is it digitized / can I view the item?” is a **nice-to-have** signal on the card when detectable — not a v1 blocker. |
| A-12 | Duplicate / related-record merging across AS and CS is **out of scope**. |
| A-13 | **C1 is not required** for Path A. OAI remains the path for *external* harvesters and for Path B. |

## Records in Scope

| System | Records Searched and Displayed |
| :---- | :---- |
| ArchivesSpace | Archival Object records, Digital Object records |
| CollectionSpace | Object records, associated media |

Out of scope: the underlying discovery platform implementation (Blacklight, VuFind, Primo, etc.), OAI-PMH harvesting infrastructure, authentication/authorization for end users, and any changes to ArchivesSpace or CollectionSpace data models.

# **Background**

ArchivesSpace is an archives content management system with resource records (collections), archival object components (series, folders, items), and related digital objects and agents. CollectionSpace manages material culture records: individual objects, groups of objects (exhibitions), and associated media. Following C1 implementation, both systems will be able to publish their records to an OAI-PMH discovery layer, but users searching that layer would see records from both systems intermingled without context about their origin or type, making it difficult to understand what they are looking at or how to navigate to the source system for more detail.

Institutions with both ArchivesSpace and CollectionSpace sometimes hold historically related material across both systems. A researcher looking for records about a person, event, or topic may find relevant archival finding aids in ArchivesSpace and related museum objects in CollectionSpace. A unified search interface that presents both — while clearly distinguishing them — significantly improves research usability.

# **System Overview**

## Architecture Paths

### Search Path A \- Federated Live Search

![][image1]  
  On each search request the BFF (backend for frontend):

1. Issues **parallel** queries to AS and CS (subject to source filter).  
2. Maps each hit into a shared **result card** schema.  
3. Returns **grouped** result sets (one group per source) plus coarse filter metadata.  
4. Never stores a full metadata mirror; optional short-lived response cache only.

**Pros:** No harvest lag; reuses published search indexes; no dependency on C1; smallest honest v1.

**Cons:** Relevance scores are **not comparable** across systems; facet vocabularies differ; one source down ⇒ partial results (not “stale harvest”).

Only select fields are displayed to the user (see [Display Implementation Options](#display-implementation-options)). The user will have a single search bar where they can key an initial search by keyword. Additional search refinement happens after the search is complete using filters and facets. 

The keyword search searches all of the Dublin Core fields available, whether or not the fields are shown in the user’s unified search preview display. 

The user can follow links to the records in the source system (ArchivesSpace Public User Interface or CollectionSpace Public Browser), which includes additional metadata beyond Dublin Core.

### Search Path B: Harvest → institutional discovery index

![][image2]

This is what the drafted behavior scenarios describe. It remains valid for institutions that **already** run (or will run) a discovery platform. C1 then becomes a real dependency for CS participation. This draft does **not** design Path B beyond noting where previously identified gaps (G-04 source detection, G-08 harvest staleness, D-01–D-05) belong.

| Concern | Path A | Path B |
| :---- | :---- | :---- |
| Search mechanism | Live IR APIs | Local index over harvested DC (+ extras) |
| C1 required? | **No** | **Yes** (for CS) |
| Freshness | Near real-time with IR indexes | Harvest schedule; ES01 stale-data UX |
| New software in this project | **Yes** — shared discovery app | Mostly config of existing platform |
| Cross-system relevance ranking | Not claimed | Possible inside one index |
| Deduping AS↔CS | Out of scope (both) | Out of scope (both) |

# **Actors and Deployment Context** {#actors-and-deployment-context}

![][image3]

| Actor | Role |
| :---- | :---- |
| **End user** | Keywords search; filters by source / coarse facets; opens source records |
| **Shared Discovery Administrator** | Configures the AS↔CS pair, base URLs, repository IDs, display labels, timeouts |
| **ArchivesSpace Administrator** | Ensures PUI URLs resolve; provides read-only API credentials (or confirms anonymous search policy) |
| **CollectionSpace Administrator** | Ensures public gateway \+ ES indexing for published collection objects; provides public browser base URL |

# **Configuration Requirements** {#configuration-requirements}

| Item | Description |
| :---- | :---- |
| `as.baseApiUrl` | ArchivesSpace backend base (BFF-only network path) |
| `as.username` / `as.password` | Read-only API user (or equiv.) |
| `as.repositoryIds` | One or more repo IDs to search |
| `as.puiBaseUrl` | For link-out: `AppConfig[:public_proxy_url]` equivalent |
| `as.types` | Default `archival_object,digital_object` |
| `cs.gatewayUrl` | e.g. `https://cs.example.edu/gateway/museum` |
| `cs.publicBrowserBaseUrl` | Link-out base for object pages |
| `cs.esIndex` / query template | Match public browser expectations for the tenant/profile |
| `ui.defaultLayout` | `grouped` (A) or `unified` (B) |
| `ui.labels` | “Archival Records” / “Museum Objects” (parent G-05) |
| Timeouts / page size defaults | Fail a group fast rather than block the whole response |

# **New components** {#new-components}

## Repositories / packages (proposed)

| Component | Responsibility |
| :---- | :---- |
| `shared-discovery-ui` | Public SPA: search box, Option A/B layouts, coarse filters, pagination per group, link-out |
| `shared-discovery-bff` | Authenticated-to-IR adapter layer; parallel search; normalize to result cards; never expose AS session tokens to the browser |
| `as-search-adapter` | Maps unified query → AS Solr search params; maps hits → card schema; builds PUI URLs |
| `cs-search-adapter` | Maps unified query → gateway ES query; maps hits → card schema; builds Public Browser URLs |
| Config store | Environment / file / simple admin JSON for the single pair (URLs, credentials, labels, page size) |

Technology choice (React/Vue/Svelte, Node/Java/Go) is **not** locked in v0.1; the contracts below are.

## BFF HTTP surface (logical)

| Method | Path | Purpose |
| :---- | :---- | :---- |
| `GET` | `/api/v1/health` | Liveness; optional upstream ping summary |
| `GET` | `/api/v1/search` | Federated search (see request/response) |
| `GET` | `/api/v1/config/public` | Non-secret UI config (labels, enabled sources, default page size) |

No public write APIs. No proxy of raw AS/CS admin endpoints to the browser.

# **Search backends** {#search-backends}

## ArchivesSpace

* Search is **Solr** behind routes documented under [Search requests](https://docs.archivesspace.org/api/#search-requests).  
* Typical call (auth via `X-ArchivesSpace-Session` after `/users/:user/login`):

```
GET /repositories/{repo_id}/search?q={lucene}&type[]=archival_object&type[]=digital_object&page=1&page_size=20
```

* Hits are **Solr documents**, not full JSONModels. Useful fields commonly include `title`, `primary_type` / `types`, `uri`, `identifier`, dates, and a string `json` blob for deeper mapping when needed.  
* **Auth model for v1:** BFF holds a read-only username/password (or long-lived session refresh). Browser never sees the session header. Confirm with each deploy whether firewall policy allows only the BFF IP to reach `:8089`.  
* **Publish/public visibility:** Prefer filters that match what the **PUI** would show (unpublished suppression). Exact filter\_query flags are an open decision (D-03) — do not return staff-only hits in a public UI.

## CollectionSpace

* Public Browser talks to **Elasticsearch through `cspace-public-gateway`** (e.g. `https://{host}/gateway/{tenant}/es/...`), not directly to Nuxeo.  
* The gateway already restricts to publicly published records (Publish To shortIds such as `all`, `cspacepub` — same set C1 reuses).  
* BFF issues ES `_search` (or the same query shape the public browser uses) limited to **CollectionObject** (and media fields needed for thumbnails).  
* **Auth model:** anonymous via gateway, same as the public browser.

## What we deliberately do *not* query

* OAI-PMH endpoints (no `q=` search)  
* CS staff Common Services search (auth \+ over-broad visibility)  
* Direct browser calls to AS `:8089`

# **Intermediate Result Card Schema** {#intermediate-result-card-schema}

Normalize **after** search, at the BFF Align display labels with the parent Intermediate Metadata Schema where practical.

| Field | Type | Required | Notes |
| :---- | :---- | :---- | :---- |
| `id` | string | yes | Stable within source: AS `uri` or CS CSID / ES `_id` |
| `source` | `"archivesspace"` | `"collectionspace"` | yes | Drives labels / filters |
| `recordType` | string | yes | e.g. `archival_object`, `digital_object`, `CollectionObject` |
| `title` | string | yes | Display \+ link text |
| `identifier` | string | no | AS component id / CS objectNumber |
| `dateDisplay` | string | no | Pre-formatted; do not pretend full calendar normalization in v1 |
| `description` | string | no | Truncate \~250 chars in UI |
| `creator` | string | no |  |
| `subjects` | string\[\] | no | Nice-to-have; coarse filter later |
| `thumbnailUrl` | string | null | no | Nice-to-have (Gap G-11) |
| `hasMedia` | boolean | no | Nice-to-have digitized signal |
| `sourceUrl` | string | yes | Absolute link-out to AS PUI or CS Public Browser |
| `foundIn` | string | null | no | AS hierarchy breadcrumb text; CS usually null (Gap G-10) |

**Display field matching:** When rendering a card, use this schema’s keys so the UI does not show both `Title` and `title` as separate rows. Source-specific labels (e.g. “Scope and Contents” vs “Brief Description”) may still differ by `source` in Option A templates; Option B uses the unified labels above.

## Intermediate Metadata Schema Maps

### Search Path A and B

| Dublin Core Field | System label (Proposed) | Display Label (Proposed) | ArchivesSpace Field | CollectionSpace Field |
| :---- | :---- | :---- | :---- | :---- |
| title | `title` | Title | Object:archival\_object Property: Title | Title |
| identifier | `identifier` | Identifier | Object:archival\_object Properties: component\_id | objectNumber |
| subject | `subjects` | Category or Subject | Object:linked\_agents Properties: IF role \== subject | contentConcept |
| date | `dateDisplay` | Date Created | Object:dates Properties: IF ‘expression’, ELSE ‘begin \+ “...” \+ end’ | Pull earliest/latest scalar values from the date details and concatenate them with '/'. |
| description | `description` | Description | Object:notes Properties: type \= scopecontent | briefDescription |
| creator | `creator` | Creator | Object:linked\_agents Properties: role \== creator & NOT relator \== ctb OR pbl | IF ‘objectProductionPerson’ ELSE ‘objectProductionOrganization’ELSE ‘objectProductionPeople’ |
| Identifier (repeated) | `id` | \[Title\] | Object:resource Property:uri "AppConfig\[:public\_proxy\_url\] \+ " uri | [C1 Gap G-13](https://docs.google.com/document/d/1TuCEufv8ekB6XgZT3aEr8g7ciW4d-xPvLh7T8tLswO4/edit?tab=t.0#heading=h.7qjoulj8v5dv) |
| source | `source` | Source | Object Type subset (archival\_object, digital\_object) | Record Type: Object |
| Gap G- : Is there a DC mapping for this? | `foundIn` | Found in | Hyperlinked breadcrumb of item’s location in hierarchy out of scope, see Gap G-10 | None |
| Gap G-11 \- thumbnail / media preview | `thumbnailURL` | N/A | Gap G-11 \- Digital object preview | Gap G-11 \- media thumbnail |

### Search Path B: Additional Fields

| Dublin Core Field | Proposed Display Label (Unified) | ArchivesSpace Field | CollectionSpace Field |
| :---- | :---- | :---- | :---- |
| Gap G-08 | Last successful harvest | Gap G-08 | Gap G-08 |
|  |  |  |  |

# **Display Implementation Options** {#display-implementation-options}

## Display Option A – Grouped / Side-by-side

* Two result groups: **Archival records** (AS) and **Museum objects** (CS).  
* Each group has its **own** total count, page controls, and empty state.  
* Source filter can hide a group entirely.  
* Natural fit for federated search: no fake global ranking.

### Search Results Display

Each feature is repeated for each data source in Display Option A.

| Proposed Display Label | Proposed Field Behavior |
| :---- | :---- |
| View and Filter All \[platform\] results | Links to all results in ASpace PUI or CSpace PB |
| Previous | Showing results **\# \- \#** | Next | Search navigation: Previous and next buttons link to sequential pages of search results |
| Page navigation | Current page of results highlighted with ‘previous’ and ‘next’ buttons to navigate through each platform’s search results |

### Record Metadata Display

| dc\_oai field | Proposed Display Label | AS Record Display | CS Record Display | Proposed Field Behavior |
| :---- | :---- | :---- | :---- | :---- |
| title | Title | x | x | Links to ASpace PUI or CSpace PB record |
| type | Type | x | x | Not linked |
| identifier | Object Number |  | x | Not linked |
| identifier | Identifier | x |  | Not linked |
| created | Date Made |  | x | Not linked |
| description | Brief Description |  | x | Display limited to 250 characters with link to read more |
| description | Scope and Contents | x |  | Display limited to 250 characters with link to read more |
| Gap G-10 | Found in | x |  | Breadcrumbs link to the record in AS PUI |
| Gap G-11 | none | x | x | Thumbnail / media preview |

## Display Option B – Unified List

* Single vertical list of cards, each stamped with source \+ record type.  
* **v1 ranking rule:** do **not** interleave by foreign relevance scores. Prefer deterministic ordering, e.g. round-robin merge of the two current pages, or “AS block then CS block” within the viewport, with clear group headers still available.  
* Source facet filters the list to one source (degrades to Option A with one group).

### Search Results Display and Faceting

| Proposed Display Label | Element type | Source field | Purpose |
| :---- | :---- | :---- | :---- |
| Previous | Showing results **\# \- \#** | Next | Search navigation | N/A | Search navigation |
| Platform or Type | Filter | Source system field (see [Configuration Requirements](#configuration-requirements)) | Filter results by CollectionSpace or ArchivesSpace |
| Creator | Free text box | oai:dc:creator |  |
| Date \- Earliest | Validated Text box (YYYY or YYYY-MM-DD) | oai:dc:date | Filter results by date |
| Date \- Latest | Validated Text box (YYYY or YYYY-MM-DD) | oai:dc:date | Filter results by date |
| Results Display | Controlled field | Thumbnail display | Filter results by ‘Records with Media’ or ‘All Records’ |

### Record Metadata Display: OAI Fields

See [Intermediate Metadata Schema](#intermediate-result-card-schema) for detailed information on how to render ArchivesSpace and CollectionSpace fields.

| dc\_oai Field | Proposed Display Label | ArchivesSpace Field | CollectionSpace Field | Proposed Field Behavior |
| :---- | :---- | :---- | :---- | :---- |
| title | Title | Title | Title | Links to ASpace PUI or CSpace PB record |
| identifier | Identifier | component\_id | objectNumber | Not linked |
| subject | Category or Subject | linked\_agents | contentConcept | Not linked |
| date | Date Created | date | date | Not linked |
| description | Description | notes | briefDescription | Display limited to 250 characters with link to read more |
| Gap G-11 | none | x | x | Thumbnail / media preview |

### Record Metadata Display: Non-OAI Fields

| Dublin Core Field | Proposed Display Label | ArchivesSpace Field | CollectionSpace Field | Proposed Field Behavior |
| :---- | :---- | :---- | :---- | :---- |
| type | Type | Type subset (archival\_object, resource, accession, digital\_object, classification) | Gap G-  Record Type: Object, Relationship:Record Group?  | Does not come from OAI-PMH Not linked |
| Gap G-10 | Found in | Hyperlinked breadcrumb of item’s location in hierarchy | None | Breadcrumbs link to the record in AS PUI |

## Recommendation: Display Options

**Recommendation:** Ship **Option A as default**; implement Option B as an alternate layout flag once cards exist. Both share the same BFF response (`groups[]`).

# **BFF search contract (sketch)** {#bff-search-contract-(sketch)}

## Request

```
GET /api/v1/search?q=pottery&sources=archivesspace,collectionspace&pageAs=1&pageCs=1&pageSize=20&hasMedia=any
```

| Param | Notes |
| :---- | :---- |
| `q` | Keyword; BFF maps to Lucene `q` (AS) and ES `query_string` / `multi_match` (CS) |
| `sources` | Subset of configured sources |
| `pageAs` / `pageCs` | Independent pagination (Option A). Option B UI may advance both or the active source |
| `pageSize` | Per source |
| `hasMedia` | `any` | `true` — best-effort; ignored if adapter cannot filter |
| `dateFrom` / `dateTo` | Optional coarse strings; adapter no-ops if unsupported |

```json
{
  "query": "pottery",
  "groups": [
    {
      "source": "archivesspace",
      "label": "Archival Records",
      "total": 42,
      "page": 1,
      "pageSize": 20,
      "status": "ok",
      "results": [ { "id": "/repositories/2/archival_objects/99", "title": "…", "sourceUrl": "https://…" } ]
    },
    {
      "source": "collectionspace",
      "label": "Museum Objects",
      "total": 17,
      "page": 1,
      "pageSize": 20,
      "status": "ok",
      "results": [ { "id": "…", "title": "…", "sourceUrl": "https://…" } ]
    }
  ],
  "filters": {
    "sources": [
      { "value": "archivesspace", "count": 42 },
      { "value": "collectionspace", "count": 17 }
    ]
  }
}
```

If one upstream fails: that group returns `"status": "error"` (or `"degraded"`) with `results: []` and an opaque message; the other group still renders. This replaces parent ES01’s harvest-staleness story for the previous spec.

# **High-Level Sequence** {#high-level-sequence}

![][image4]

# **Behavior Scenarios** {#behavior-scenarios}

Note: Behavior Scenarios may be updated to align with Display Implementation Option, once a pathway is chosen.

## BS01: End user searches and receives results from both ArchivesSpace and CollectionSpace

| Step | Description |
| :---- | :---- |
| Given | The discovery layer has harvested records from both ArchivesSpace and CollectionSpace. |
|  | Both source systems are labeled and record types are indexed. |
|  | Both source systems have defined search APIs |
| When | An end user enters a keyword search in the unified discovery interface. |
| Then | \[*Result depends on Implementation Path; this example is for unified display\]* Search results include records from both ArchivesSpace and CollectionSpace, ranked by relevance. |
|  | Each result card displays: title, source system label (e.g., 'Archival Records' / 'Museum Objects'), record type, date, brief description, and thumbnail (if available). |
|  | The result count shows totals from both systems combined. |

## BS02: End user filters results by source system

| Step | Description |
| :---- | :---- |
| Given | Search results contain records from both ArchivesSpace and CollectionSpace. |
| When | The user selects 'Archival Records' in the source system facet. |
| Then | Only ArchivesSpace records are displayed. |
|  | The record type facet updates to show only ArchivesSpace record types. |
|  | Selecting 'Museum Objects' shows only CollectionSpace records, with CollectionSpace-specific facet values. |

## BS03: End user views a search result and navigates to the source system

| Step | Description |
| :---- | :---- |
| Given | A search result record is displayed in the unified interface. |
| When | The user clicks the record title or a 'View full record' link. |
| Then | For an ArchivesSpace record: the user is taken to the corresponding record in the ArchivesSpace PUI. |
|  | For a CollectionSpace record: the user is taken to the corresponding record in the CollectionSpace public browser. |
|  | The link opens in a new tab. |
|  | The user views a full metadata record, which includes additional metadata beyond the Dublin Core OAI-PMH harvest |

## BS05: End user finds related records across both systems

| Step | Description |
| :---- | :---- |
| Given | A search result from ArchivesSpace has a subject heading that also appears in CollectionSpace records. |
| When | The user views the result. |
| Then | A 'Related records' panel or subject heading link allows the user to see other records (from either system) sharing the same subject. \[PLACEHOLDER — related record display mechanism TBD, see Gap G-07.\] |

## BS05: End user searches or facets by subject (unified interface only)

| Step | Description |
| :---- | :---- |
| Given | A user has performed a successful search in a unified interface. *(OR a user is performing an advanced search. See Gap G- )* |
| When | The user views the result. |
| And | The user chooses from available subjects/categories to limit the results. |
| Then | The interface displays both ArchivesSpace and CollectionSpace records with records that contain the subject or category. |

# **Error Scenarios** {#error-scenarios}

## ES01: System cannot provide data (Search Path A)

| Step | Description |
| :---- | :---- |
| Given | The shared discovery layer is configured. |
| When | The user performs a search.  |
| And | At least one request fails because at least one system is unable to provide data at this time. |
| Then | The group returns `"status": "error"` (or `"degraded"`) with `results: []` and an opaque message; the other group still renders. |

## ES02: One source system is temporarily unavailable for harvest (Search Path B)

### Search Path B

| Step | Description |
| :---- | :---- |
| Given | The discovery layer harvests from both AS and CS on a schedule. |
| When | One system's OAI-PMH endpoint is unavailable during a scheduled harvest. |
| Then | The discovery layer continues to display previously harvested records from the unavailable system (stale data). |
|  | A staleness indicator or 'last updated' timestamp is displayed on search results from that source.  |
|  | The discovery layer administrator is notified of the harvest failure (mechanism TBD, see Gap G-08). |

This error does not apply to search path A. In search path A, we will query individual systems live and take advantage of their caching.

# **Open Questions and Specification Gaps** {#open-questions-and-specification-gaps}

## Open Questions and Specification Gaps

| \# | Gap | Description | Owner |
| :---- | :---- | :---- | :---- |
| **G-01** | Search scope | The search is designed as a single search bar with a keyword search option. Should advanced search options be added? | Product Owner  |
| **G-02** | [Result Card Schema Review](#intermediate-result-card-schema) | How does the data model look to you? Is there anything you would add or remove? (material type?) | Product Owner |
| **G-04** | OAI-PMH identifier namespace and source system detection | How does the discovery layer know which records came from ArchivesSpace vs. CollectionSpace? Options: (a) distinct OAI set per source system, (b) OAI identifier prefix convention, or (c) a custom metadata field injected during harvest. A consistent convention must be agreed across both system configurations. | Developer |
| **G-05** | Display labels and facet vocabulary review | The proposed record type display labels and facet values (see [Display Implementation Options](#display-implementation-options)) must be reviewed and approved by stakeholders, including end user representatives.  | Product Owner / UX / End Users |
| **G-06** | ArchivesSpace record type scope | Please review the recommendation: Archival objects \+ digital objects | **ArchivesSpace** Product Owner, Developers  |
| **G-07** | Related records display mechanism | How will subject-based or identifier-based relationships between AS and CS records surfaced to users?  Options: subject heading hyperlinks to a filtered search, a dedicated 'Related records' panel, or no explicit relationship display. Define the mechanism and its data requirements. | Product Owner / UX |
| **G-08** | Harvest failure notification | How is the discovery layer administrator notified when harvesting from one source fails? This may be a feature of the discovery platform rather than AS/CS, but minimum error information (last successful harvest timestamp per source) should be surfaceable in the unified interface. | Discovery Admin / Developer |
| **G-10** | Archival hierarchy display in search results | How is the breadcrumb rendered? Is this nice to have or required? | **ArchivesSpace** Developer, Product Owner |
| **G-11** | Thumbnail | How will the system identify and render thumbnails or digital object previews?Is this nice to have or required? | Consultants, Developers, Product Owners |

## Development Areas

| \# | Work item | Notes |
| :---- | :---- | :---- |
| D-A01 | Scaffold shared-discovery UI \+ BFF | Public read-only |
| D-A02 | AS search adapter (AO \+ DO) | Session handling, PUI link builder, publish filters |
| D-A03 | CS gateway ES adapter (CO) | Mirror public-browser eligibility |
| D-A04 | Result card mapper \+ truncation | Unified keys; per-source label overlays for Option A |
| D-A05 | Option A grouped UI \+ independent pagination | Default |
| D-A06 | Option B unified layout flag | Same `groups[]` payload |
| D-A07 | Coarse source filter \+ optional hasMedia |  |
| D-A08 | Partial-failure UX | One source down |
| D-A09 | Deploy docs | Network allowlist for AS API; gateway URL; secrets |
| D-B01+ | Path B harvest platform work | Only if product selects Path B; depends on C1 for CS |

# **Review Questions** {#review-questions}

1. Confirm **Path A** as the funded deliverable (vs configuring an existing Blacklight/etc.).  
2. Confirm v1 types: **AS AO+DO**, **CS collection objects only**.  
3. Approve **link-out only** (no unified detail page).  
4. Provide a reference deploy (hostnames for AS API, PUI, CS gateway, public browser) for adapter spikes.  
5. Choose the default layout Option: **grouped (A)** vs **unified (B)**.
