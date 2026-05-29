---
source: https://docs.google.com/document/d/1TuCEufv8ekB6XgZT3aEr8g7ciW4d-xPvLh7T8tLswO4
scenario: C1
issue: https://github.com/lyrasisorghome/InteroperabilityProject/issues/46
last_synced: 2026-05-27
---
# **OAI-PMH for CollectionSpace**

## Technical Specification

*Enabling discovery of a CollectionSpace object in an OAI-PMH enabled discovery repository*

Document Status: DRAFT  
Version: 0.2  
Date: April 2026  
Source Story: [C1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/46)  
Project: LYRASIS Interoperability Project  
Systems: CollectionSpace / OAI-PMH 2.0 / Enabled repositories or discovery layers

# **Table of Contents** {#table-of-contents}

[Table of Contents	1](#table-of-contents)

[Purpose and Scope	2](#purpose-and-scope)

[Background	2](#background)

[Stakeholders and Roles	3](#stakeholders-and-roles)

[System Overview	3](#system-overview)

[Integration Architecture	3](#integration-architecture)

[Data Formats and Metadata Standards	4](#data-formats-and-metadata-standards)

[OAI-PMH Protocol Support	4](#oai-pmh-protocol-support)

[Configuration Requirements	6](#configuration-requirements)

[Default Dublin Core Field Mapping \- Anthro Profile	8](#default-dublin-core-field-mapping---anthro-profile)

[Behavior Scenarios	9](#behavior-scenarios)

[BS01: Administrator enables and configures OAI-PMH in CollectionSpace	10](#bs01:-administrator-enables-and-configures-oai-pmh-in-collectionspace)

[BS02:  Discovery system harvests records from CollectionSpace via OAI-PMH	10](#bs02:-discovery-system-harvests-records-from-collectionspace-via-oai-pmh)

[BS04: Discovery system administrator configures the harvester (CollectionSpace requirements)	10](#bs04:-discovery-system-administrator-configures-the-harvester-\(collectionspace-requirements\))

[Error Scenarios	10](#error-scenarios)

[ES01: OAI-PMH endpoint is not enabled	10](#es01:-oai-pmh-endpoint-is-not-enabled)

[ES02: Harvest returns no records (empty repository)	10](#es02:-harvest-returns-no-records-\(empty-repository\))

[ES03: Harvest fails due to server error	10](#es03:-harvest-fails-due-to-server-error)

[ES04: Record missing required Dublin Core fields	10](#es04:-record-missing-required-dublin-core-fields)

[ES05: Harvest requests a set	10](#es05:-harvest-requests-a-set)

[ListIdentifiers Error Scenarios	10](#heading=)

[● badArgument \- The request includes illegal arguments or is missing required arguments.	10](#heading=)

[● badResumptionToken \- The value of the resumptionToken argument is invalid or expired.	10](#heading=)

[● cannotDisseminateFormat \- The value of the metadataPrefix argument is not supported by the repository.	10](#heading=)

[● noRecordsMatch- The combination of the values of the from, until, and set arguments results in an empty list.	10](#heading=)

[● noSetHierarchy \- The repository does not support sets.	10](#nosethierarchy---the-repository-does-not-support-sets.)

[Configuration GUI	11](#configuration-gui)

[Open Questions and Specification Gaps	12](#open-questions-and-specification-gaps)

# **Purpose and Scope** {#purpose-and-scope}

This specification defines requirements for adding OAI-PMH (Open Archives Initiative Protocol for Metadata Harvesting) provider functionality to CollectionSpace. Adding OAI-PMH enables external discovery systems to harvest CollectionSpace object records and their associated digital content on a configurable schedule.

OAI-PMH 2.0 is the target protocol version. The feature has two components: (1) an OAI-PMH compliant API endpoint exposed by CollectionSpace, and (2) a graphical configuration interface within CollectionSpace allowing administrators and staff users to control which records are harvested and how.

Out of scope: changes to the discovery system(s) harvesting records, non-OAI-PMH sharing protocols (e.g., ResourceSync, IIIF), support for OAI-PMH retrieval of procedure or authority records, and any CollectionSpace records not explicitly flagged for public sharing.

# **Background** {#background}

OAI-PMH is a standard and best practice for sharing metadata records, particularly in libraries and archives. Many discovery systems are OAI-PMH compliant. Many institutions that use CollectionSpace also operate an OAI-PMH compliant discovery layer (such as a digital library, institutional repository, library catalog, or union catalog).

Without native OAI-PMH support in CollectionSpace, institutions must either build custom export pipelines (e.g., exporting to Solr and exposing via the Solr API) or forgo discovery layer integration entirely.

Adding OAI-PMH provider support to CollectionSpace would:

* Remove the need for institution-specific middleware to push CollectionSpace data to discovery systems.  
* Make CollectionSpace collections more discoverable alongside library and archival content in shared discovery interfaces.

# **Stakeholders and Roles** {#stakeholders-and-roles}

Roles and permissions in CollectionSpace are defined at the local level. The user role that each local repository chooses should have the following permissions.

| Stakeholder Role | Description | Responsibility | Other Requirements |
| :---- | :---- | :---- | :---- |
| CollectionSpace System Administrator | User or system with the ability to install and configure the CollectionSpace instance | Enables or disables access to the feature at the instance level and sets the default configuration  | Configurations available only to this role do not need to be exposed in the Staff UI. |
| CollectionSpace OAI-PMH Administrator | User with a CollectionSpace user account assigned the permission to administer the OAI-PMH details. | Can disable the feature and customize some aspects of it. | Necessitates that a new permission be added to CollectionSpace to designate this level of access. Any configuration available to this role must be editable from the Staff UI. |
| CollectionSpace Staff User | User with a CollectionSpace user account with the ability to write to objects. | Creates and edits collection objects.  May be able to make objects public thereby exposing them through the OAI-PMH interface. | Staff user should be able to understand what enables OAI-PMH either from documentation or cues in the CSpace GUI |
| Discovery system administrator | User or system with the ability to configure a discovery system that harvests data from CollectionSpace. | Configures the harvesting schedule and filter in the external discovery system; consumes the CollectionSpace OAI-PMH endpoint. | This role is outside CollectionSpace but the spec must define what CollectionSpace provides to support it (see BS03). |
| End User (public) | User who accesses data harvested from CollectionSpace in some other system. | Access successfully harvested collections |  |

# **System Overview** {#system-overview}

## Integration Architecture {#integration-architecture}

| Component | Role | Interface |
| :---- | :---- | :---- |
| CollectionSpace Application | Source of truth for object metadata and digital object references. | Internal CSpace data model |
| CollectionSpace Gateway |  |  |
| CollectionSpace OAI-PMH Provider | New API endpoint for CollectionSpace that adheres to the OAI-PMH 2.0 spec | OAI-PMH specification; must be accessible at distinct path (e.g. /api/oai) |
| Collection Space Staff UI | Collection Space User Interface |  |
| OAI-PMH Configuration UI | Admin GUI within CollectionSpace for managing endpoint settings. | CollectionSpace admin interface |
| 'Publish To' Field | Staff-facing record-level toggle that marks an object as publishable. | Existing CSpace field |
| Discovery System / Harvester | External system that periodically sends OAI-PMH requests to the CollectionSpace endpoint and ingests responses. | Standard OAI-PMH 2.0 client (not in scope to build) |

## Data Formats and Metadata Standards {#data-formats-and-metadata-standards}

* CollectionSpace data model  
* Dublin Core  
* OAI-PMH XML Schema (https://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm\#OAIPMHschema)

## OAI-PMH Protocol Support {#oai-pmh-protocol-support}

The OAI-PMH standard uses the Hypertext Transport Protocol (HTTP) as a transport layer and specifies six query methods (called verbs) that must be supported by an OAI-PMH compliant data provider (also referred to as a repository). These methods are:

1. GetRecord \- retrieves a complete metadata record from a repository by identifier;  
2. Identify \- retrieves information about a repository, including, at a minimum, repositoryName, baseURL, protocolVersion, earliestDatestamp, deletedRecord policy, and granularity (for timestamp format).  
3. ListIdentifiers \- retrieves a metadata record header which may include URL identifier, timestamp. The records may be filtered by set or date range. Supports resumptionToken for large result sets.  
4. ListMetadataFormats \- retrieves a list of available metadata record formats supported by a repository.  
5. ListRecords \- retrieves complete metadata records from a repository  
6. ListSets \- retrieves the set structure from a repository.

The OAI-PMH compliant data provider must accept requests from both HTTP GET and HTTP POST request methods. Responses from the data provider must be returned as an XML-encoded stream. Error handling must be supported by the data provider and return the correct error response code back to the harvester. Detailed specifications and examples of all six verbs may be viewed in Section 4 of the [OAI-PMH standards document](http://www.openarchives.org/OAI/openarchivesprotocol.html).

### Required Scope

The implementation must adhere to  [OAI-PMH Guidelines for Repository Submitters](https://www.openarchives.org/OAI/2.0/guidelines-repository.htm).

In addition, the following scope is required:

| Feature | Required | Scope | Notes |
| :---- | :---- | :---- | :---- |
| GET HTTP Protocol | Required | All verbs |  |
| POST HTTP Protocol | Required | All verbs |  |
| Identify | Required | Per the spec |  |
| GetRecord | Required | Returns metadata for Object Records flagged as Public |  |
| ListIdentifiers | Required | Returns PIDs for Object Records flagged as Public |  |
| ListMetadataFormats | Required | At a minimum must return Dublin Core | Implementation should be extensible to allow for other metadata formats in the future |
| ListRecords | Required | Returns metadata Object Records flagged as Public |  |
| ListSets | Required | Returns noSetHierarchy Error | Implementation should be extensible to allow for sets to be implemented in a future phase |
| Persistent Identifiers  | Required | Must adhere to [URI](http://www.ietf.org/rfc/rfc2396.txt?number=2396) syntax | These need to be globally unique across CSpace instances. It is separate from what gets exposed in the metadata record.  Probably we should build them from the CSID  |
| Datestamps | Required | Must be expressed in UTC with seconds granularity | Reflects the datestamp of last modification date of any object record metadata. |
| Deleted Records | Required | persistent | CSpace supports persistent deleted records. See the spec for details. |
| Resumption Tokens | Required | Must support at least cases when there are no changes in the repository between requests.  | May defer support for cases where repository changes occur in between requests  can return badResumptionToken error in this case. |
| Compression | Required | Should support compression option per the OAI-PMH spec |  |

# **Configuration Requirements** {#configuration-requirements}

All of the following must be configurable by the Collection Space System Administrator. Some elements may be overridden by a Collection Space Administrator as indicated.  Anything that is available to the Collection Space Administrator role must be configurable through the UI.

| Function | Role Access | Notes |
| :---- | :---- | :---- |
| Feature Available | System Admin | Feature flag to enable the feature itself; The availability of feature must be able to be turned on or off at the system admin level.  |
| Protocol Version | System Admin | OAI protocol version supported. Only 2.0 for now. Include for future proofing |
| PID Source | System Admin | For future proofing, we probably want to make it possible to define different approaches to PIDs.  For the initial version at a minimum we need to specify where the PID URI is coming from (e.g. is it the refName of the object? ) |
| ResumptionTokenExpiration Seconds | System Admin | Defines the cache TTL |
| Max Records Per Request | System Admin | Limit on number of records that can be returned in one response (more than this will trigger use of a resumption token) |
| DateStamp Granularity | System Admin | Should be second, but configurable just in case |
| Earliest DateStamp | System Admin | This should be the earliest possible datestamp in the system \- not sure if it should really be configurable or if it should come from the records themselves |
| Compression Support | System Admin | Whether or not the system supports compression (gzipping) of results \- should be yes by default. |
| Set Support | System Admin, maybe Admin | For future proofing, initially not supported |
| Supported Metadata Formats | System Admin, maybe Admin | Will require related mapping configuration for each format |
| Disabled | Admin | Ability for Administrator to disable the feature even if it’s available at the system level. |
| Repository Name | System Admin, Admin | Human-readable name returned in the Identify response (e.g., 'Example Institution CollectionSpace'). |
| Repository Description | System Admin, Admin | Human-readable description of the repository contents (for inclusion in Identify Response) |
| Admin Email | System Admin, Admin | Returned in the Identify response as required by OAI-PMH spec. |
| Supported Media | System Admin, Admin | Should be possible to use this to eliminate media links entirely, or to specify which derivatives to include links to (thumbnails, etc.) |

### Metadata Mapping Configuration

For each supported Metadata Format, it must be possible to configure the following details at the System Administration Level.  It may be desirable to expose this in the UI for the Administrator as well.

| Detail | Description | Notes |
| :---- | :---- | :---- |
| Metadata Prefix | Namespace prefix for responses | The prefix string should not be hard-coded |
| Metadata Schema Location | Schema Url to include in responses |  |
| Metadata Field Transformation Rules | Details of how collectionspace object metadata is mapped/transformed for response | Ideally, this mapping logic should not be hardcoded and is something that can be modified through configuration settings which could include reference to xslt stylesheets. This must be done securely and avoid script injection security holes. Implementation must include the default dublin core mapping for each CollectionSpace profile, including handling of media  |

#### Default Dublin Core Field Mapping \- Anthro Profile {#default-dublin-core-field-mapping---anthro-profile}

| CollectionSpace Element | DC Element | Notes |
| :---- | :---- | :---- |
| Title | title |  |
| objectProductionPerson objectProductionOrganization objectProductionPeople | creator | Default value: objectProductionPerson If Person is blank, then Org If Org is blank, then People |
| objectProductionDate | date |  |
| contentConcept | subject |  |
| briefDescription | description |  |
| fieldCollector | contributor |  |
| descriptionLevel:Item descriptionLevel:Group of Items | type | Value: Physical Object |
| dimensionSummary | format |  |
| objectNumber | identifier  |  |
| objectProductionPlace | coverage |  |
| rightStatement | rights |  |
|  | relation | CollectionSpace Public Browser link |
|  | publisher | Repository name |
| titleLanguage | language |  |
| objectHistoryNote | provenance |  |
| For each included media type | relation | Precede with derivative? Eg. thumbnail: |

# **Behavior Scenarios** {#behavior-scenarios}

Draft: [See C1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/46)

| Step | Description |
| :---- | :---- |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |

## BS01: Administrator enables and configures OAI-PMH in CollectionSpace {#bs01:-administrator-enables-and-configures-oai-pmh-in-collectionspace}

| Step | Description |
| :---- | :---- |
| Given | The CollectionSpace instance has been configured with the OAI-PMH feature set to available. |
|  | The administrator is logged into CollectionSpace with OAI-PMH Administrator access.  |
| When | The administrator navigates to the OAI-PMH Settings page. \[PLACEHOLDER — navigation path TBD, see Gap G-05.\] |
|  | The administrator enables the OAI-PMH endpoint and edits required configuration fields and field mapping details. |
|  | The administrator saves the configuration. |
| Then | The CollectionSpace OAI-PMH endpoint becomes active and responds to OAI-PMH verb requests. |
|  | The Identify verb returns the configured repository name, admin email, and policy settings. |

## BS02: OAI-PMH Identify Request is Fulfilled

## BS02: OAI-PMH ListMetadataFormats Request is Fulfilled

## BS02: OAI-PMH ListSets Request is Fulfilled

## BS02: OAI-PMH ListIdentifiers Request is Fulfilled

## BS02: OAI-PMH ListRecords Request is Fulfilled

## BS02: OAI-PMH GetRecord Request is Fulfilled

## 

## BS03: Staff user marks a record as eligible for OAI-PMH harvesting

| Step | Description |
| :---- | :---- |
| Given | An object record exists in CollectionSpace. |
|  | The staff user has write access to the record. |
| When | The staff user opens the record in CollectionSpace. |
|  | The user toggles the ‘Publish’ field to the on state |
|  | The user saves the record. |
| Then | The record is flagged as harvestable. |
|  | The record's datestamp is updated to the save timestamp, enabling incremental harvesting via from/until parameters. |

## BS04: Staff user deletes a record 

| Step | Description |
| :---- | :---- |
| Given | An object record exists in CollectionSpace. |
|  | The staff user has write access to the record. |
| When | The staff user opens the record in CollectionSpace. |
|  | The user toggles the ‘Publish’ field to the on state |
|  | The user saves the record. |
| Then | The record is flagged as harvestable and will appear in the next OAI-PMH ListRecords/ListIdentifiers response. |
|  | The record's datestamp is updated to the save timestamp, enabling incremental harvesting via from/until parameters. |

## BS03: OAI-PMH List Records Request is Fulfilled

| Step | Description |
| :---- | :---- |
| Given | An object record exists in CollectionSpace. |
|  | The staff user has write access to the record. |
| When | The staff user opens the record in CollectionSpace. |
|  | The user toggles the ‘Publish’ field to the on state |
|  | The user saves the record. |
| Then | The record is flagged as harvestable and will appear in the next OAI-PMH ListRecords/ListIdentifiers response. |
|  | The record's datestamp is updated to the save timestamp, enabling incremental harvesting via from/until parameters. |

## BS03: OAI-PMH List Records Request is Fulfilled

| Step | Description |
| :---- | :---- |
| Given | An object record exists in CollectionSpace. |
|  | The staff user has write access to the record. |
| When | The staff user opens the record in CollectionSpace. |
|  | The user toggles the ‘Publish’ field to the on state |
|  | The user saves the record. |
| Then | The record is flagged as harvestable and will appear in the next OAI-PMH ListRecords/ListIdentifiers response. |
|  | The record's datestamp is updated to the save timestamp, enabling incremental harvesting via from/until parameters. |

## BS02:  Discovery system harvests records from CollectionSpace via OAI-PMH {#bs02:-discovery-system-harvests-records-from-collectionspace-via-oai-pmh}

| Step | Description |
| :---- | :---- |
| Given | One or more object records are published and marked for OAI-PMH harvesting. |
|  | The CollectionSpace OAI-PMH endpoint is active. |
|  | The discovery system harvester is configured with the CollectionSpace OAI-PMH endpoint URL. |
| When | The discovery system sends a ListRecords (or ListIdentifiers) request with metadataPrefix=oai\_dc. |
|  | Optional: the request includes from/until parameters for incremental harvest. |
| Then | CollectionSpace returns an OAI-PMH XML response containing oai\_dc records for all published objects (filtered by date if from/until provided). |
|  | Each record includes a unique OAI identifier, datestamp, and mapped Dublin Core metadata. |
|  | If more records exist than fit in one response, a resumptionToken is included and subsequent requests with that token return the next page. |
|  | If digital objects are configured for exposure (Gap G-08), the dc:identifier or dc:relation field includes the digital object URL. |
|  | Harvested metadata and digital objects are displayed in the discovery system within the latency defined by the harvester's schedule (typically ≤ 24 hours after next scheduled harvest). |

## BS04: Discovery system administrator configures the harvester (CollectionSpace requirements) {#bs04:-discovery-system-administrator-configures-the-harvester-(collectionspace-requirements)}

This scenario describes what CollectionSpace must provide to enable configuration in a generic OAI-PMH harvesting tool. The discovery system UI varies and is not in scope to specify.

| Step | Description |
| :---- | :---- |
| Provided by CSpace | A publicly accessible OAI-PMH endpoint URL (e.g., https://cs.example.edu/oai). |
| Provided by CSpace | A valid Identify response including repository name, admin email, and granularity. |
| Provided by CSpace | A valid ListMetadataFormats response listing supported prefixes (minimum: oai\_dc). |
| Provided by CSpace | A valid ListSets response if set-based filtering is required. |
| Provided by CSpace | Resumption tokens for ListRecords/ListIdentifiers responses exceeding the configured page size. |
| \[PLACEHOLDER\] | Authentication requirements for the OAI-PMH endpoint (open/public vs. IP-restricted vs. token-based) are not yet defined. See Gap G-10. |

# 

# **Error Scenarios** {#error-scenarios}

## ES01: OAI-PMH endpoint is not enabled {#es01:-oai-pmh-endpoint-is-not-enabled}

## ES02: Harvest returns no records (empty repository) {#es02:-harvest-returns-no-records-(empty-repository)}

## ES03: Harvest fails due to server error {#es03:-harvest-fails-due-to-server-error}

## ES04: Record missing required Dublin Core fields {#es04:-record-missing-required-dublin-core-fields}

## ES05: Harvest requests a set {#es05:-harvest-requests-a-set}

## **7.1 ES01: OAI-PMH endpoint is not enabled**

| Step | Description |
| :---- | :---- |
| Given | The OAI-PMH integration is configured but the OAI-PMH Enabled toggle is off. |
| When | A harvester sends a request to the CollectionSpace OAI-PMH endpoint URL. |
| Then | CollectionSpace returns HTTP 503 or an OAI-PMH error response with code 'badVerb' or a custom message indicating the service is inactive. \[PLACEHOLDER — exact error response format TBD, see Gap G-11.\] |

## **7.2 ES02: Harvest returns no records (empty repository)**

| Step | Description |
| :---- | :---- |
| Given | The OAI-PMH endpoint is active but no records are currently published. |
| When | A harvester sends a ListRecords request. |
| Then | CollectionSpace returns a valid OAI-PMH response with error code 'noRecordsMatch' as specified by the OAI-PMH 2.0 protocol. |

## **7.3 ES03: Harvest fails due to server error**

| Step | Description |
| :---- | :---- |
| Given | The OAI-PMH endpoint is active. |
| When | A server-side error occurs while processing a harvest request (e.g., database timeout, configuration error). |
| Then | CollectionSpace returns an appropriate HTTP 5xx response or OAI-PMH error document. |
|  | The error is written to CollectionSpace server logs. \[PLACEHOLDER — log location for LYRASIS-hosted and self-hosted instances must be documented. See Gap G-12.\] |
|  | \[PLACEHOLDER — admin notification mechanism (email alert, dashboard warning) is not yet defined. See Gap G-12.\] |

## **7.4 ES04: Record missing required Dublin Core fields**

| Step | Description |
| :---- | :---- |
| Given | A staff user sets a record's 'Publish To' status to include OAI-PMH. |
| And | The record is missing one or more fields required by the configured Dublin Core mapping (e.g., no title, no date). |
| Then | \[PLACEHOLDER — behavior is undefined. Options: (a) warn the user and block publishing until required fields are filled, or (b) allow publishing but exclude the record from harvest until fields are present, or (c) include the record with empty DC elements. See Gap G-07.\] |

# **ListIdentifiers Error Scenarios**

* # **badArgument** \- The request includes illegal arguments or is missing required arguments.

* # **badResumptionToken** \- The value of the resumptionToken argument is invalid or expired.

* # **cannotDisseminateFormat** \- The value of the metadataPrefix argument is not supported by the repository.

* # **noRecordsMatch**\- The combination of the values of the from, until, and set arguments results in an empty list.

* # **noSetHierarchy** \- The repository does not support sets. {#nosethierarchy---the-repository-does-not-support-sets.}

ListMetadata Error Scenarios

* **badArgument** \- The request includes illegal arguments or is missing required arguments.  
* **idDoesNotExist** \- The value of the identifier argument is unknown or illegal in this repository.  
* **noMetadataFormats** \- There are no metadata formats available for the specified item.

ListRecords Error Scenarios

* **badArgument** \- The request includes illegal arguments or is missing required arguments.  
* **badResumptionToken** \- The value of the resumptionToken argument is invalid or expired.  
* **cannotDisseminateFormat** \- The value of the metadataPrefix argument is not supported by the repository.  
* **noRecordsMatch** \- The combination of the values of the from, until, set and metadataPrefix arguments results in an empty list.  
* **noSetHierarchy** \- The repository does not support sets.

ListSets Error Scenarios

* **badArgument** \- The request includes illegal arguments or is missing required arguments.  
* **badResumptionToken** \- The value of the resumptionToken argument is invalid or expired.  
* **noSetHierarchy** \- The repository does not support sets.

GetRecord Error Scenarios

* **badArgument** \- The request includes illegal arguments or is missing required arguments.  
* **cannotDisseminateFormat** \- The value of the metadataPrefix argument is not supported by the item identified by the value of the identifier argument.  
* **idDoesNotExist** \- The value of the identifier argument is unknown or illegal in this repository.

Identify Error Scenarios

* **badArgument** \- The request includes illegal arguments.

## Configuration GUI {#configuration-gui}

Administration \> OAI-PMH Settings  
![][image1]

# **Open Questions and Specification Gaps** {#open-questions-and-specification-gaps}

| \# | Gap | Description | Owner |
| :---- | :---- | :---- | :---- |
| **G-01** | Metadata format support beyond oai\_dc | oai\_dc (Dublin Core) is mandatory. Additional formats such as oai\_qdc (Qualified DC), LIDO (museum-specific), or schema.org are optional. Confirm which are feasible/desirable for the CollectionSpace user community. | Product Owner / Metadata Specialist |
| **G-02** | OAI set structure | OAI sets allow harvesters to retrieve subsets of records. How should CollectionSpace records be organized into sets? Options: by CollectionSpace Collection, by record type (object, group, etc.), by cataloging procedure, or by custom tag. Define default set structure and whether it is configurable. | Product Owner / Metadata Specialist |
| **G-03** | Digital object (image/file) exposure via OAI-PMH | OAI-PMH natively carries metadata, not binaries. Define how digital objects associated with CollectionSpace records are referenced in OAI-PMH responses: (a) dc:identifier or dc:relation pointing to the public CollectionSpace object URL, (b) a URL to the image/file directly, or (c) not exposed at all. If files are exposed, access control implications must be addressed. | Product Owner / Developer |
| **G-05** | OAI-PMH error response format for service-inactive state | The OAI-PMH spec does not define a 'service inactive' error code. Define the HTTP response (503? 404?) or OAI-PMH error document returned when the endpoint is disabled, so that harvesters can handle it gracefully. | Developer |
| **G-06** | Error logging and admin notification | Where are CSpace OAI-PMH server errors logged? For LYRASIS-hosted instances, how do administrators access logs? Is there an in-app notification (dashboard warning, email) when harvesting fails? This affects both troubleshooting and the ES03 scenario. | Developer / Product Owner |
|  | Publish To | Do we want to refactor the Publish To field in CollectionSpace, to change it to something more general \- e.g. just a publish toggle? |  |
|  |  |  |  |

# 

[image1]: <data:image/png;base64,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>