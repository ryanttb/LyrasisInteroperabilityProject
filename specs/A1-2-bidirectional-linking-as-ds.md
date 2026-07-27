---
source: https://docs.google.com/document/d/1GVP7IgAcK4kcJyl27Fobm_EuDJZTnh_IbUl5C61jNYw
scenarios:
  - A1
  - A2
issues:
  - https://github.com/lyrasisorghome/InteroperabilityProject/issues/7
  - https://github.com/lyrasisorghome/InteroperabilityProject/issues/44
last_synced: 2026-07-27
---
# **Bidirectional Linking Between ArchivesSpace and Dspace**

## Technical Specification

*Linking DSpace Digital Object records to ArchivesSpace finding aid components*

Document Status: DRAFT  
Version: 0.3  
Date: May 2026  
Source Stories: [A1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/7) and [A2](https://github.com/lyrasisorghome/InteroperabilityProject/issues/44)  
Project: LYRASIS Interoperability Project  
Systems: ArchivesSpace SUI, ArchivesSpace PUI, DSpace REST API (7.x / DSpace 9.x contract), ArchivesSpace REST API

# **Table of Contents** {#table-of-contents}

[Table of Contents	1](#table-of-contents)

[Purpose and Scope	2](#purpose-and-scope)

[Background	2](#background)

[Normative references	3](#normative-references)

[Stakeholders and Roles	3](#stakeholders-and-roles)

[User Narratives	3](#user-narratives)

[System Overview	4](#system-overview)

[Metadata Mappings	4](#metadata-mappings)

[Feature Modes	5](#feature-modes)

[DSpace API Operations	5](#dspace-api-operations)

[Bulk Linking Specifications	6](#bulk-linking-specifications)

[Actors	6](#actors)

[End-to-end flows	16](#end-to-end-flows)

[Algorithms	19](#algorithms)

[Example Walkthrough	20](#example-walkthrough)

[Result report (LinkBatch output)	20](#result-report-\(linkbatch-output\))

[Behavior Scenarios	21](#behavior-scenarios)

[Configuration	21](#configuration)

[Single Item Linking	22](#single-item-linking)

[Bulk/Collection Linking	26](#bulk/collection-linking)

[Error Scenarios	29](#error-scenarios)

[Error scenarios (API-level): Based on A2 Bulk Linking	29](#error-scenarios-\(api-level\):-based-on-a2-bulk-linking)

[User Configuration Requirements	29](#user-configuration-requirements)

[User Configuration Fields	29](#user-configuration-fields)

[New SUI Screen: DSpace Integration Configuration	30](#new-sui-screen:-dspace-integration-configuration)

[User Interface Requirements	31](#user-interface-requirements)

[New SUI Screen: Digital Object Search Screen	31](#new-sui-screen:-digital-object-search-screen)

[Existing SUI Screens:	32](#existing-sui-screens:)

[Open Questions and Specification Gaps	33](#heading=)

# **Purpose and Scope** {#purpose-and-scope}

This specification defines the functional and behavioral requirements for an ArchivesSpace feature that enables staff users to search for one or more DSpace items and collection records and link them bidirectionally to one or more ArchivesSpace digital object records. 

Out of scope for this specification: changes to the DSpace data model, discovery layer integrations, batch import via spreadsheet, use of legacy/EOL APIs, or any administrative workflow not triggered from within the ArchivesSpace SUI.

# **Background** {#background}

Staff who manage digitized and born-digital archival collections in DSpace need to reflect those digital objects in ArchivesSpace finding aids so that end users can see what is available online and access it directly. The reverse is also true: DSpace records benefit from links back to ArchivesSpace, which carries richer, more accurate archival description (context, relationships, provenance) than DSpace's bibliographic model can accommodate.

Current workarounds are manual and error-prone:

* Copying and pasting URIs one by one between systems.  
* Exporting links from DSpace, reformatting them to the ArchivesSpace Digital Object specification, and batch-importing via a spreadsheet importer.  
* The reverse path – getting the ArchivesSpace URI into DSpace – has no defined current workflow.

This feature replaces those workarounds with a search-and-select interface inside the ArchivesSpace SUI that calls the DSpace Search API and links the records, updating each with the corresponding link.  Organizations without a shared discovery layer are the primary beneficiaries, though the feature is useful for any institution maintaining both systems.

# **Normative references** {#normative-references}

* [DSpace REST API intro](https://wiki.lyrasis.org/spaces/DSDOC9x/pages/379126848/REST+API)  
* [DSpace RestContract](https://github.com/DSpace/RestContract/blob/main/README.md)  
* [DSpace search endpoint](https://github.com/DSpace/RestContract/blob/main/search-endpoint.md)  
* [DSpace metadata PATCH](https://github.com/DSpace/RestContract/blob/main/metadata-patch.md)  
* [ArchivesSpace API](https://archivesspace.github.io/archivesspace/api/)

# **Stakeholders and Roles** {#stakeholders-and-roles}

## User Narratives {#user-narratives}

1. I created a finding aid in ArchivesSpace for a collection that has a small number of digital objects associated with it. I created 1-10 digital object placeholders where I knew we would want to insert links later. I deposited the digital content to DSpace already. Now I need to put the DSpace URI in ArchivesSpace, and add the ArchivesSpace URI to DSpace.  
2. A patron requested digitization of one folder of a collection, and our digitization unit has completed digitization and deposited the content to DSpace. I need to create an ArchivesSpace digital object and link to it from DSpace.  
3. I need to configure my ArchivesSpace repository to connect with a DSpace repository. My institution may host several DSpace and ArchivesSpace repositories.

| Role | Responsibility in This Feature | Notes |
| :---- | :---- | :---- |
| ArchivesSpace Administrator | Configures the DSpace integration settings per repository. | Must also hold Collection Administrator level access in DSpace. |
| ArchivesSpace Staff User | Searches for DSpace records and creates links from the SUI. | Uses both single-item and bulk linking modes. |
| ArchivesSpace End User (PUI) | Views finding aid records with links to digital content. | Does not interact with the integration directly. |
| DSpace Collection Administrator | Provides configuration details; owns records that receive ArchivesSpace URI links. |  |
| DSpace service account | Makes authenticated DSpace API calls on behalf of any user. | See Gap G-02 |

# **System Overview** {#system-overview}

The integration operates as a plugin or extension within the ArchivesSpace Staff User Interface (SUI). It communicates outbound with a configured DSpace instance via the DSpace REST/Search API v7. Earlier versions of the DSpace REST API will not be supported via the plugin. No middleware or separate service is required; all orchestration occurs within the ArchivesSpace application layer. 

| Component | Role | Development Interface |
| :---- | :---- | :---- |
| ArchivesSpace SUI | Staff-facing interface; hosts search widget, file version instances, and configuration UI. | Browser / ArchivesSpace plugin framework |
| ArchivesSpace PUI | Public-facing finding aid interface; displays links created by this feature. | ArchivesSpace indexing pipeline |
| DSpace REST API | Used to execute queries in DSpace and update the DSpace record with link to the ArchivesSpace record | HTTPS / JSON (DSpace REST API) |

## Metadata Mappings {#metadata-mappings}

| ASpace Digital Object Field | DSpace Field | Repeatable? | Notes |
| :---- | :---- | :---- | :---- |
| Title | dc.title | No |  |
| Identifier | DSpace PID per Configuration | No |  |
| File URI | Per configuration | No |  |
| VRA Core Level |  | No | See G-16 |
| Digital Object Type |  | No | See G-16 |
| Restrictions |  | No | See G-16 |
| Languages | dc.language | Yes | See G-27 |
| Per configuration | dc.identifier.uri | Yes |  |

## Feature Modes {#feature-modes}

The integration has two operational modes, both sharing the same configuration and API authentication layer:

| Mode | Trigger | Outcome |
| :---- | :---- | :---- |
| Single-Item Linking | User opens a Digital Object, Resource, or Archival Object record and uses the DSpace URI field or the Add Digital Object linker. | One DSpace item URI added to one ArchivesSpace Digital Object record. One ArchivesSpace URI written to DSpace. |
| Bulk/Collection Linking | User opens a series or sub-series Archival Object record and selects Add Digital Collection under Instances. | A DSpace collection is matched to an ArchivesSpace component; multiple Digital Object records are created or updated. ArchivesSpace URIs written to DSpace. |

## DSpace API Operations {#dspace-api-operations}

See also:

[https://wiki.lyrasis.org/spaces/DSDOC9x/pages/379126848/REST+API](https://wiki.lyrasis.org/spaces/DSDOC9x/pages/379126848/REST+API) 

[https://github.com/DSpace/RestContract/blob/main/README.md](https://github.com/DSpace/RestContract/blob/main/README.md) 

| Operation | DSpace Endpoint | Outcome |
| :---- | :---- | :---- |
| CSRF token GET | /api/security/csrf  | Gets an initial CSRF Token for API usage for a specific session |
| Log in POST | /api/authn/login | Login via a DSpace service user with JSON Web Token & refresh the CSRF token |
| Log out POST | /api/authn/logout | Log out with DSpace service user |
| Search POST | /api/discover/search | Search and retrieve items, collections, and communities. Filter search to specific collections or communities. |
| Items PATCH | items/\<uuid\> (op: add, path:/metadata/dc.identifier/-/uri/-) | Use add operation to add DSpace links. See also G-09 |

## Bulk Linking Specifications {#bulk-linking-specifications}

## Actors {#actors}

![][image1]

| Actor | Role |
| :---- | :---- |
| **Link orchestrator** | Integration code (AS plugin or external service) that sequences API calls. |
| **AS REST API** | Source of truth for digital object records. |
| **DSpace REST API** | Search target; receives AS URI via metadata PATCH. |

### Configuration (minimum)

Stored per AS repository (same model as A1):

| Key | Example | Used for |
| :---- | :---- | :---- |
| `dspace.base_url` | `https://dspace.example.edu/server` | DSpace API root |
| `dspace.service_user` / `password` | — | DSpace auth |
| `dspace.as_uri_field` | `dc.identifier.uri` | DSpace metadata field for AS link |
| `dspace.as_uri_source` | `digital_object` | `archival_object` | Which AS URI to write |
| `dspace.default_scope` | collection UUID (optional) | Default Discovery `scope` param |
| `as.public_base_url` | `https://as.example.edu` | PUI base for public URIs |

### Data contracts

#### **LinkMap (input to link phase)**

The LinkMap is the handoff between **search/selection** (future UI) and **link execution**. A single entry covers A1; an array covers A2.

```json
{
  "repository_id": 1,
  "links": [
    {
      "as_ref": "/repositories/1/digital_objects/1",
      "dspace_item_href": "/api/core/items/9f3288b2-f2ad-454f-9f4c-70325646dcee",
      "mode": "append_file_version",
      "publish": false
    }
  ]
}
```

| Field | Required | Description |
| :---- | :---- | :---- |
| `repository_id` | yes | AS repository numeric ID |
| `links[].as_ref` | yes | AS URI of target record (`digital_objects`, `archival_objects`, or `resources`) |
| `links[].dspace_item_href` | yes | DSpace item self link from search (or full item GET) |
| `links[].mode` | yes | `append_file_version` | `create_digital_object` |
| `links[].publish` | no | If true, call AS publish after successful link |

**1:1 rule:** Each `as_ref` and each `dspace_item_href` MUST appear at most once per LinkMap.

#### **SearchResultItem (extracted from DSpace search)**

From `GET /api/discover/search/objects`:

```json
{
  "dspace_item_uuid": "9f3288b2-f2ad-454f-9f4c-70325646dcee",
  "dspace_item_href": "/api/core/items/9f3288b2-f2ad-454f-9f4c-70325646dcee",
  "name": "test result",
  "handle": "10673/4",
  "dso_type": "item"
}
```

Extraction rule:

```
uuid  ← _embedded.indexableObject.uuid
href  ← _links.indexableObject.href
name  ← _embedded.indexableObject.name
handle← _embedded.indexableObject.handle (if present)
```

#### **Field mapping (DSpace item → AS digital object)**

Applied when `mode = create_digital_object` or when refreshing metadata on update:

| AS field | DSpace source | Notes |
| :---- | :---- | :---- |
| `title` | `metadata.dc.title[0].value` | Required |
| `digital_object_id` | `metadata.{configured_pid_field}[0].value` or `handle` | Institution-specific |
| `file_versions[].file_uri` | `{baseUrl}/handle/{handle}` | Primary link |
| `lang_materials[].language_and_script.language` | `metadata.dc.language[*].value` | Optional; map ISO codes |

### DSpace API operations

#### **Session bootstrap**

![][image2]

| Step | Method | Endpoint | Notes |
| :---- | :---- | :---- | :---- |
| 1 | GET | `/api/security/csrf` | Capture `X-CSRF-TOKEN` |
| 2 | POST | `/api/authn/login` | Basic auth; capture JWT |
| 3 | POST | `/api/authn/logout` | End session (optional) |

#### **Search objects**

**Endpoint:** `GET /api/discover/search/objects`

| Parameter | Example | Purpose |
| :---- | :---- | :---- |
| `query` | `test` | Solr query string |
| `dsoType` | `item` | `collection` | `all` | Limit result types |
| `scope` | `{collectionUuid}` | Limit to community/collection |
| `page`, `size` | `0`, `20` | Pagination |

#### **Example request:**

```
GET /api/discover/search/objects?query=test&dsoType=item&page=0&size=20
Authorization: Bearer {jwt}
```

#### **Example response** (abbreviated; matches RestContract)**:**

```
{
  "query": "test",
  "_embedded": {
    "searchResults": {
      "_embedded": {
        "objects": [
          {
            "hitHighlights": {
              "dc.description.abstract": "test result"
            },
            "_links": {
              "indexableObject": {
                "href": "/api/core/items/9f3288b2-f2ad-454f-9f4c-70325646dcee"
              }
            },
            "_embedded": {
              "indexableObject": {
                "uuid": "9f3288b2-f2ad-454f-9f4c-70325646dcee",
                "name": "test result",
                "handle": "10673/4"
              }
            }
          }
        ]
      },
      "page": { "size": 20, "totalElements": 1, "totalPages": 1, "number": 0 }
    }
  }
}

```

#### **Resolve item metadata**

```
GET /api/core/items/{uuid}
Authorization: Bearer {jwt}
```

Use full `metadata` map for field mapping and to build public item URI.

#### **Write AS URI to DSpace**

```
PATCH /api/core/items/{uuid}
Authorization: Bearer {jwt}
X-CSRF-TOKEN: {token}
Content-Type: application/json
If-Match: {etag from GET item}

[
  {
    "op": "add",
    "path": "/metadata/dc.identifier.uri/-",
    "value": {
      "value": "https://as.example.edu/repositories/1/digital_objects/1"
    }
  }
]
```

### ArchivesSpace API operations

**Important:** AS has **no PATCH**. Updates use `POST/repositories/:repo_id/digital_objects/:id` with a **full** JSONModel body. Always `GET` → merge → `POST`.

#### **Session**

```
POST /session
Content-Type: application/json

{"user": "...", "password": "..."}
```

Response header: `X-ArchivesSpace-Session` — send on all subsequent requests.

#### **Link mode: `append_file_version` (existing digital object)**

Your example targets `/repositories/1/digital_objects/1`.

![][image3]

#### **GET digital object:**

```
GET /repositories/1/digital_objects/1
X-ArchivesSpace-Session: {session}
```

#### **POST update** (minimal delta shown; payload must include full record):

```
{
  "jsonmodel_type": "digital_object",
  "title": "Existing title",
  "digital_object_id": "DO-001",
  "file_versions": [
    {
      "jsonmodel_type": "file_version",
      "file_uri": "https://dspace.example.edu/handle/10673/4",
      "publish": true,
      "xlink_actuate_attribute": "onRequest",
      "xlink_show_attribute": "new"
    }
  ]
}
```

```
POST /repositories/1/digital_objects/1
X-ArchivesSpace-Session: {session}
Content-Type: application/json
```

### **Link mode: `create_digital_object` (A2 bulk path)**

Used when AS has archival structure but no digital objects yet.  
![][image4]

#### **Create:**

```
POST /repositories/1/digital_objects
X-ArchivesSpace-Session: {session}
```

Body includes mapped `title`, `digital_object_id`, and initial `file_versions[0].file_uri` from DSpace.

## End-to-end flows {#end-to-end-flows}

### Flow 1 — Single link (A1-compatible subset)

| Step | Action |
| :---- | :---- |
| 0 | Config present (A-01) |
| 1 | Bootstrap DSpace session |
| 2 | `GET /api/discover/search/objects?query=test&dsoType=item` |
| 3 | Build LinkMap with one entry (user selection assumed) |
| 4 | Execute **LinkEntry** algorithm (below) |
| 5 | Return per-link result report |

### Flow 2 — Bulk link from DSpace collection (A2)

| Step | Action |
| :---- | :---- |
| 1 | Search collection: `GET …/search/objects?query={title}&dsoType=collection` |
| 2 | User selects collection → extract `collectionUuid` |
| 3 | List member items: `GET …/search/objects?scope={collectionUuid}&dsoType=item&query=*&size=100` (paginate) |
| 4 | User maps each item to an AS target → LinkMap with N entries |
| 5 | Execute **LinkBatch** (sequential or parallel with rate limit) |

![][image5]

## Algorithms {#algorithms}

### LinkEntry(link)

```

INPUT:  link ∈ LinkMap.links
OUTPUT: LinkResult { as_ref, dspace_item_uuid, status, errors[] }

1. AS_RECORD ← GET(link.as_ref)
2. DS_ITEM    ← GET(link.dspace_item_href)   // includes ETag
3. DS_URI     ← buildItemPublicUri(DS_ITEM)
4. AS_URI     ← buildAsPublicUri(AS_RECORD, config.as_uri_source)

5. IF link.mode == "append_file_version":
     AS_RECORD.file_versions.append(newFileVersion(DS_URI))
     POST(link.as_ref, AS_RECORD)             // full body
   ELSE IF link.mode == "create_digital_object":
     NEW_DO ← mapDspaceToDigitalObject(DS_ITEM)
     CREATED ← POST(/repositories/{repo}/digital_objects, NEW_DO)
     optionally attach CREATED to archival_object.instances
     AS_URI ← buildAsPublicUri(CREATED, …)

6. PATCH(DS_ITEM, add dc.identifier.uri = AS_URI)
   IF PATCH fails:
     record error; optionally rollback AS change (policy TBD)

7. IF link.publish:
     POST({as_ref}/publish)

8. RETURN LinkResult

```

### LinkBatch(linkMap)

```

results ← []
FOR EACH link IN linkMap.links:
  results.append(LinkEntry(link))
RETURN { total, succeeded, failed, results }
```

**Bulk semantics:** No special bulk endpoint required. `LinkBatch` with `len(links) == 1` is the single-link case.

## Example Walkthrough {#example-walkthrough}

**Given:** AS repository `1`, existing digital object `/repositories/1/digital_objects/1`, DSpace configured.

**Search:**

```
GET {dspace}/api/discover/search/objects?query=test&dsoType=item
```

**LinkMap** (after user selection):

```
{
  "repository_id": 1,
  "links": [
    {
      "as_ref": "/repositories/1/digital_objects/1",
      "dspace_item_href": "/api/core/items/9f3288b2-f2ad-454f-9f4c-70325646dcee",
      "mode": "append_file_version",
      "publish": false
    }
  ]
}
```

**AS update:** `GET` DO 1 → append `file_uri` → `POST /repositories/1/digital_objects/1`

**DSpace update:** `PATCH /api/core/items/9f3288b2-f2ad-454f-9f4c-70325646dcee` with AS public URI.

## Result report (LinkBatch output) {#result-report-(linkbatch-output)}

```
{
  "total": 2,
  "succeeded": 1,
  "failed": 1,
  "results": [
    {
      "as_ref": "/repositories/1/digital_objects/1",
      "dspace_item_uuid": "9f3288b2-f2ad-454f-9f4c-70325646dcee",
      "status": "linked",
      "as_uri_written": "https://as.example.edu/repositories/1/digital_objects/1",
      "dspace_uri_written": "https://dspace.example.edu/handle/10673/4"
    },
    {
      "as_ref": "/repositories/1/digital_objects/2",
      "dspace_item_uuid": "ff7ec3a4-0aab-418b-94fc-d0e8189084db",
      "status": "failed",
      "errors": ["DSpace PATCH 403: insufficient permissions"]
    }
  ]
}
```

# **Behavior Scenarios** {#behavior-scenarios}

## Configuration {#configuration}

### BS-01: Administrator configures the DSpace integration

| Step | Description |
| :---- | :---- |
| Given | The user has Administrator-level access to ArchivesSpace. |
|  | The user has Collection Administrator-level access to DSpace. |
| When | The administrator navigates to System \> Manage Repositories in the ArchivesSpace SUI. |
|  | The administrator selects the repository to configure. |
|  | The administrator opens the DSpace Integration Settings field group. |
|  | The administrator enters the required configuration fields (see Section 5.2) and saves. |
| Then | The DSpace integration is active for the repository. |
|  | DSpace URI fields and the Add Digital Collection button become active in the SUI for users of that repository. |

## Single Item Linking {#single-item-linking}

### BS-02: User can search DSpace to add a Digital Object to an Archival Object; AND

### BS-03: User can search DSpace to add a Digital Object to a Resource Record

| Step | Description |
| :---- | :---- |
| Given | An Archival Object exists in ArchivesSpace (no linked Digital Object). |
|  | DSpace integration is configured and enabled. |
| When | The user opens the Resource or Archival Object record in the SUI. |
|  | The user navigates to Instances and selects Add DSpace Digital Object. |
| Then | The DSpace Digital Object Search popup appears |
|  | The Title field is pre-populated with the Resource or Archival Object Record Title |
|  | The URI field is pre-populated with the Resource or Archival Object Record URI |
|  | The keywords field is empty |
|  | All search fields are editable |

### BS-04: User can search Dspace to add a new File Version for an existing Digital Object

| Step | Description |
| :---- | :---- |
| Given | A Resource or Archival Object record exists in ArchivesSpace with a linked Digital Object |
|  | DSpace integration is configured and enabled. |
| When | The user opens the Digital Object record in the SUI. |
|  | The user expands the File Versions field group and selects Add DSpace Digital Object |
| Then | The Browse Digital Objects Search popup appears |
| When | The user filters results to DSpace Digital Object |
|  | The user filters the text search to keywords in the title |
|  | The user searches title keywords |
| Then | The user finds and selects the corresponding DSpace record |

### BS-05: User executes first search of DSpace in an ArchivesSpace session

| Step | Description |
| :---- | :---- |
| Given | An item record exists in DSpace. |
|  | DSpace integration is configured and enabled. |
|  | The user has arrived at the DSpace Digital Object search screen |
|  | The search form is populated with all fields populated |
|  | The user has not yet performed a DSpace search in this session |
| When | The user clicks Search |
| Then | The DSpace CSRF api endpoint is called to create a CSRF token |
|  | The DSpace login api is called to login the session |
|  | A recurring Refresh job is initiated to refresh the CSRF token at an interval less than the expires claim returned in the login response  |

### BS-06: User searches for an existing digital object in DSpace using all Fields

| Step | Description |
| :---- | :---- |
| Given | An item record exists in DSpace. |
|  | DSpace integration is configured and enabled. |
|  | The DSpace CSRF token is created and the session is active |
|  | The user has arrived at the DSpace Digital Object search screen |
|  | The search form is populated with all fields populated |
| When | The user clicks Search |
| Then | The DSpace Search API is called with the appropriate parameters |

### BS-07: User searches for an existing digital object in DSpace using a subset of fields

| Step | Description |
| :---- | :---- |
| Given | An item record exists in DSpace. |
|  | DSpace integration is configured and enabled. |
|  | The DSpace CSRF token is created and the session is active |
|  | The user has arrived at the DSpace Digital Object search screen |
|  | The search form is populated with at least one field populated and one field blank |
| When | The user clicks Search |
| Then | The DSpace Search API is called with the appropriate parameters |

### BS-08: User searches for an existing digital object in DSpace and receives a single result

| Step | Description |
| :---- | :---- |
| Given | An item record exists in DSpace. |
|  | DSpace integration is configured and enabled. |
|  | The DSpace CSRF token is created and the session is active |
|  | The user has arrived at the DSpace Digital Object search screen |
|  | The search form is populated with field values that will product a single result |
| When | The user clicks Search |
| Then | The DSpace Search API is called  with the appropriate parameters |
|  | A single result is displayed with the fields defined in the configuration |
|  | A Save Button is displayed |
|  | A Publish Button is displayed |

### BS-09: User searches for an existing digital object in DSpace and receives multiple possible results of DSpace objects and/or collections

| Step | Description |
| :---- | :---- |
| Given | An item record exists in DSpace. |
|  | DSpace integration is configured and enabled. |
|  | The DSpace CSRF token is created and the session is active |
|  | The search form is populated with field values that will product multiple results |
| When | The user clicks Search |
| Then | The DSpace Search API is called with the appropriate parameters |
|  | A list of results is displayed with the fields defined in the configuration |
|  | A Save button appears next to each result |
|  | A Publish button appears next to each result |

### BS-10: User Saves a single Digital Object link as a new File Version

| Step | Description |
| :---- | :---- |
| Given | The user has executed a successful search for a Digital Object in DSpace from Digital Object \> File Version |
| When | The user clicks Link on the search interface |
| Then | A file version is added to the Digital Object |
|  | The DSpace URI for the selected item is added to File Versions \> File URI in the pre-existing digital object record in ArchivesSpace |
|  | The DSpace API PATCH method is called to append the ArchivesSpace Archival Object URI to the record in DSpace |

### BS-11: User Saves a single Digital Object link as a new Digital Object using DSpace Metadata source

| Step | Description |
| :---- | :---- |
| Given | The user has executed a successful search for a Digital Object in DSpace from Instances \> Create Digital Object |
|  | DSpace is configured as the Metadata source for new Digital Objects |
| When | The user clicks Link from the search interface |
| Then | An ArchivesSpace digital object is created using metadata from the DSpace object |
|  | The DSpace URI for the selected item is added to the newly created digital object record in ArchivesSpace |
|  | The DSpace API PATCH method is called to append the ArchivesSpace Digital Object URI to the DSpace Item |
|  | The ArchivesSpace Digital Object record is indexed in the ArchivesSpace PUI |

## Bulk/Collection Linking {#bulk/collection-linking}

### BS-12: User can search DSpace to match a Collection to a Resource

| Step | Description |
| :---- | :---- |
| Given | A Resource with Archival Objects exists in ArchivesSpace. |
|  | A corresponding Collection with Items exists in DSpace. |
|  | DSpace integration is configured and enabled. |
| When | The user opens the Resource record in the SUI. |
|  | The user navigates to Instances and selects Browse. |
| Then | The Browse Digital Objects Search popup appears |
| When | The user filters results to **DSpace Collection** |
|  | The user filters the text search to keywords in the title |
|  | The user searches title keywords or UUID |
| Then | The user finds and selects the corresponding DSpace record |

### BS-13: User creates new Digital Objects using DSpace Metadata source

| Step | Description |
| :---- | :---- |
| Given | The user has executed a successful search for a Collection in DSpace via ArchivesSpace Digital Object search, and selected the desired collection |
|  | DSpace is configured as the Metadata source for new Digital Objects in ArchivesSpace |
| When | The user clicks Link |
| Then | An ArchivesSpace digital object is created for each item in the DSpace collection using the metadata from the DSpace object |
| And | The process is documented in a background job. |
| And | The user receives a pop up when the job is complete. |
| And | The Digital Objects are indexed by the ArchivesSpace PUI |

### BS-14: User links new Digital Objects to corresponding Archival Objects

| Step | Description |
| :---- | :---- |
| Given | The user has matched a DSpace collection to an ArchivesSpace resource and generated Digital Objects |
| When | The user navigates to Create \> Digital Object Links (New Option) |
| Then | The user navigates to the field group for linking AOs to DOs 1:1 |
|  | The user selects the parent AO |
|  | The user selects the background job for creating DOs from DSpace records to reference for DOs |
|  | The user selects a field to match: Title |
| When | The user selects a button to Review and Link |
| Then | The user receives a pop up (or loaded into the same interface) with the AOs and their corresponding DOs based on the matched field.  |
|  | The user deletes any entries with incorrect links |
| When | The user selects Link |
| Then | The process is documented in a background job, including a section on links that were removed from the bulk process |
| And | The objects are re-indexed in the ArchivesSpace PUI |

### BS-15: User links new Digital Objects to one corresponding Archival Object or Resource

| Step | Description |
| :---- | :---- |
| Given | The user has matched a DSpace collection to an ArchivesSpace resource and generated Digital Objects |
| When | The user navigates to Create \> Digital Object Links (New Option) |
| Then | The user navigates to the field group for linking a set of DOs to an AO |
|  | The user selects the AO to link |
|  | The user selects the background job for creating DOs from DSpace records to reference for DOs |
| When | The user selects Link |
| Then | The Digital Objects are linked as Instances of the Archival Object or Resource |
| And | The objects are re-indexed in the ArchivesSpace PUI |

### BS-16: User links Digital Objects or Archival Objects back to DSpace items

| Step | Description |
| :---- | :---- |
| Given | A set of Digital Objects exists in ArchivesSpace that include URIs to DSpace |
| And | A corresponding set of Items exists in DSpace |
| When | The user navigates to Create \> Digital Object Links (New Option) |
| Then | The user navigates to the field group for linking a set of DOs to an external repository’s items |
|  | The user selects the parent AO or Resource  |
|  | The user selects the link source for DSpace: AO or DO |
| When | The user selects Link |
| Then | The AO or DO link is added to the corresponding DSpace item |
| And | The objects are re-indexed in DSpace |

# 

# **Error Scenarios** {#error-scenarios}

## Error scenarios (API-level): Based on A2 Bulk Linking {#error-scenarios-(api-level):-based-on-a2-bulk-linking}

| ID | Condition | Expected behavior |
| :---- | :---- | :---- |
| ES-01 | DSpace auth failure (401) | Abort batch; no AS mutations |
| ES-02 | Search returns 0 results | Return empty result set; no mutations |
| ES-03 | AS GET fails (404) | Skip link; record error for that entry |
| ES-04 | AS POST fails (400) | Skip DSpace PATCH; record validation errors |
| ES-05 | DSpace PATCH fails after AS success | Record partial state; surface rollback need |
| ES-06 | Duplicate `as_ref` or `dspace_item_href` in LinkMap | Reject batch at validation (1:1 rule) |
| ES-07 | DSpace item missing `dc.date.issued` when creating in DSpace | N/A for A2 spec (BS02 out of scope) |

# **User Configuration Requirements** {#user-configuration-requirements}

## User Configuration Fields {#user-configuration-fields}

The following fields are proposed for the DSpace Integration Settings field group. Exact field names and validation rules are subject to developer review (see Section 9, Open Questions). 

| Field | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| Integration Enabled | Boolean (toggle) | Yes | Master switch; controls whether the DSpace search UI elements are active for this repository. |
| DSpace Base URL | URL | Yes | Root URL of the target DSpace instance (e.g., https://dspace.example.edu). |
| DSpace Display Name | Text | No | Human-readable label for the DSpace connection (useful when multiple DSpace repos are configured). See also G-28 |
| DSpace Service User | Text | Yes | Username for DSpace service account |
| DSpace Service Password | Text | Yes | Password for DSpace service account |
| Default Search Set | URI | No | Optional scoping filter to limit DSpace search results to a specific community or collection by Collection or Item URI. See also G-21 |
| DSpace PID Field | URI | Yes | DSpace source field for PID |
| DSpace Link Field | Text | Yes | DSpace source field for Digital Object link |
| ASpace Link Field | Select (Digital ObjectURI or  Parent Object URI) | Yes | ArchivesSpace source field to use for link added to DSpace |
| DSpace Display Fields | Text | Yes | See G-15 |
| DSpace Max Results | Number | Yes | See G-20 |

## New SUI Screen: DSpace Integration Configuration {#new-sui-screen:-dspace-integration-configuration}

Configuration is per ArchivesSpace repository, is managed by an Administrator, and is one-to-one. Each ArchivesSpace repository can connect to one DSpace collection or community. An institution may configure connections to different DSpace repositories by operating more than one ArchivesSpace repository, each with its own settings. 

The DSpace repository is a required field in the ArchivesSpace integration interface. ArchivesSpace administrators can optionally scope the digital object search to a specific community or collection within the DSpace repository.

### Configuration Location

Configuration is accessible via: System \> Manage Repositories \> \[Select Repository\] \> DSpace Integration Settings.

The field group should be collapsible. Saving the configuration should trigger a validation check (connectivity test to the DSpace base URL).

**Fields** \- See Configuration  
**Buttons**

| Button | Action | Notes |
| :---- | :---- | :---- |
| Save | Saves Changes |  |
| Cancel | Reverts Changes |  |

![][image6]

# **User Interface Requirements** {#user-interface-requirements}

## New SUI Screen: Digital Object Search Screen {#new-sui-screen:-digital-object-search-screen}

### Search Section

**Search Fields**

| Field Name | Field Type | Validation Rules | Business Logic |
| :---- | :---- | :---- | :---- |
| Title | Text |  |  |
| URI | Text |  |  |
| Keywords | Text |  | Split on spaces? |

**Buttons**

| Button | Action | Notes |
| :---- | :---- | :---- |
| Search | Posts search to DSpace API |  |
| Cancel | Closes screen returns user to prior screen |  |
|  |  |  |

### Results Section

**Display Fields**  
Per configuration

**Buttons**

| Button | Action | Notes |
| :---- | :---- | :---- |
| Publish | Executes publish steps | Next to each result |
| Pagination? |  |  |

## Existing SUI Screens: {#existing-sui-screens:}

| UI Section | UI Element | Specification |
| :---- | :---- | :---- |
| System \> Manage Repositories \> \[Select Repository\] \>  | Configure DSpace | A new Configure DSpace option that procure the DSpace Configuration screen |
| Resources \> Instances | Add DSpace Digital Object | A new Add DSpace Digital Object Button that produces the DSpace Digital Object Search Screen, visible only when DSpace linking integration is enabled  |
| Resources \> Archival Object \> Instances | Add DSpace Digital Object | A new Add DSpace Digital Object Button that produces the DSpace Digital Object Search Screen, visible only when DSpace linking integration is enabled  |
| Digital Object \> File Versions | Add Dspace Digital Object | A new Add DSpace Digital Object Button that produces the DSpace Digital Object Search Screen, visible only when DSpace linking integration is enabled |

# **Open Questions and Specification Gaps**

| \# | Functional Areas | Description | Who |
| :---- | :---- | :---- | :---- |
| **G-01** | Configuration | Is DSpace configuration per ArchivesSpace repository or per ArchivesSpace instance? | ASpace Program Manager |
| **G-02** | Configuration | Do we need to support the possibility of configuring multiple DSpace repositories for end-user selection? | ASpace Program Manager |
| **G-03** | Authentication | Is the DSpace service user feasible for handling authentication? Does the submission need to be tied to an individual end-user? Possible through OnBehalfOf header but would increase scope to handle matching ASpace user to DSpace user. Can we exclude it from scope? | ASpace Program Manager |
| **G-04** | Linking | Is there any duplicate detection required for DSpace links added to ArchivesSpace (within or across ArchivesSpace records? | ASpace Program Manager, ASpace Devs |
| **G-05** | Configuration, Linking | Is the proposed solution for identifying the ArchivesSpace URI to add to DSpace sufficient? (e.g. configuration option to choose Digital Object or Parent record as the source) | ASpace Program Manager, ASpace Devs |
| **G-06** | Linking, Search | We need more work on the way bulk linking will work.  So far we have only defined the scenario where all items in a DSpace collection are added to an ArchivesSpace record.  What are the actual scenarios we need to cover? How will many-to-many matching work when the number of items differs? Need to step through the possibilities here. | Jess, ASpace Program Manager, ASpace Devs |
| **G-07** | Configuration | Should the content-types supported for linking be configurable?  | ASpace Program Manager |
| **G-08** | Linking | Add Behavior Scenario for handing of multi-valued language when populating Digital Object metadata (But see also G-27) | Jess |
| **G-09** | Linking | Review behavior for when DSpace object already has linked identifiers and whether we need to support different PATCH operators | Maybe can wait for implementation? |
| **G-10** | Linking, Search | DSpace search field behavior needs further investigation \- can we search multiple fields at a time? What operators are available? Do we need to let the users choose? | Jess |
| **G-11** | Authentication | Confirm feasibility of token refresh behavior | ASpace Devs |
| **G-12** | Linking | Confirm that options for both publish and save should be supported distinctly and if so add behavior scenarios for when user chooses Publish vs Save from DSpace search results (i.e. Save & Publish in one step).  | ASpace Program Manager, ASpace Devs |
| **G-13** | Linking | What transaction support is required (e.g. if publishing a link to DSpace fails, does the link in ArchivesSpace also fail?) | ASpace Program Manager, ASpace Devs |
| **G-14** | Configuration | Do search fields need to be configurable? | ASpace Program Manager |
| **G-15** | Configuration | Do search result display fields need to be configurable?   Items returns dc.title, UUID, handle, owningCollection, mappedCollections (plus more). Browses returns dc.title, dc.dateissued, dc.dateaccessioned (only). | ASpace Program Manager |
| **G-16** | Configuration | Should any other fields in the ASpace Digital Object record besides title, identifier, URI and language be populatable from the DSpace metadata? | ASpace Program Manager, ASpace Devs |
| **G-17** | Linking | Is there ever a scenario where anything other than the DSpace metadata is used to create a new Digital Object from a DSpace object? | ASpace Program Manager |
| **G-18** | Linking | When creating a new Digital Object from a DSpace object, does it get created as a new File Version? Does this need to be explicitly stated in the behavior scenario? | ASpace Devs |
| **G-19** | Linking | Is confirmation required before creating multiple ArchivesSpace Digital Objects? | ASpace Program Manager, ASpace Devs |
| **G-20** | Linking, Configuration | Should pagination of search results be supported? Max number of results enforced? | ASpace Program Manager, ASpace Devs |
| **G-21** | Configuration | Is the option to scope search to a single parent collection in DSpace useful? | ASpace Program Manager |
| **G-22** | UI | Does anything need to be changed about the System \> System Information page?  | ASpace Devs |
| **G-23** | Error handling & Logging | Do we need to capture errors in the ArchivesSpace logs? | ASpace Program Manager, ASpace Devs |
| **G-24** | Error handling & Logging | What details about link actions need to be recorded in the ArchivesSpace logs?  | ASpace Program Manager, ASpace Devs |
| **~~G-26~~** | ~~User Stories~~ | ~~Copy the nice user story narratives from the GitHub issues into the overview~~ | ~~Jess~~ |
| **G-27** | Linking, Configuration | Do DSpace and Archive use different language codes? How do we handle this mapping? | ASpace Program Manager, ASpace Devs |
| **G-28** | Configuration, UI | Do we want to allow for use of DSpace Display Name from configuration in the UI Widgets for accessing the functionality (e.g. buttons, etc.) | ASpace Program Manager, ASpace Devs |
| **G-29** | Bulk Linking | Rollback AS when DSpace PATCH fails? Default for v0.1 \= Fail-forward; report partial state | ASpace Program Manager, Devs |
| **G-30** | Bulk Linking | Attach new DO to archival\_object.instances in same transaction? Default v0.1 \= Required for `create_digital_object` mode |  |
| **G-31** | Bulk Linking | Proposed plugin endpoint wrapping LinkBatch? Default for v0.1 \= Required for `create_digital_object` mode |  |
| **G-32** | Bulk Linking | Proposed plugin endpoint wrapping LinkBatch? Default for v0.1 \= Optional `POST /repositories/:id/integrations/dspace/links` — not required if orchestrator is external |  |
| **G-33** | Linking | Exact DSpace metadata field for AS URI? Default for v0.1 \= `dc.identifier.uri` Is this Handle on the front end? What if there are multiple URIs? |  |
