---
source: https://docs.google.com/document/d/1_ecWifpqfNN5PrmN3ZnqcjlgAqrYTbtNMWLDi5x6y1s
scenario: F1
issue: https://github.com/lyrasisorghome/InteroperabilityProject/issues/58
last_synced: 2026-05-27
---
# **Integration Scenario Registry**

## Technical Specification

*A read/write registry of Interoperability Implementations for ArchivesSpace, DSpace, CollectionSpace, VIVO, and Fedora*

Document Status: DRAFT  
Version: 0.1  
Date: May 2026  
Source Story: [F1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/58)  
Project: LYRASIS Interoperability Project  
Systems: Registry Web UI, Registry API, ArchivesSpace, DSpace, CollectionSpace, VIVO, Fedora

\[TOC\]

# **Purpose and Scope**

This specification defines requirements for an Integration Scenario Registry. The registry is a lightweight repository for storing, discovering, and retrieving records that describe real-world implementations of integrations with ArchivesSpace, DSpace, CollectionSpace, VIVO, and Fedora, or an external system and any of these applications.

The registry serves two primary use cases:

* Deposit (write): A practitioner who has implemented an integration submits a structured record describing what they built, how it works, and how others could replicate it.  
* Search and retrieval (read): Any person wanting to find a relevant integration looks up records by system, protocol, integration type, or keyword, and retrieves enough information to evaluate and apply the scenario to their own environment.

The registry is not a code repository, a ticketing system, or a specification authoring tool. It does not host or maintain documentation. It is a discovery and knowledge-sharing layer that links to external resources (code, documentation, specifications) rather than hosting them directly.

Out of scope: hosting integration code or binaries, enforcing technical standards compliance, providing support for specific integrations.

# **Background**

Libraries, archives, and museums using ArchivesSpace, DSpace, CollectionSpace, VIVO, and Fedora sometimes face similar interoperability challenges. Institutions independently solve problems that others have already solved by building custom scripts, using middleware, or implementing plugins. Sometimes this work is documented publicly, but even if so, there is no shared place to go to find out what has already been implemented and how.

A registry of implemented integration scenarios would reduce duplicated effort, lower the barrier to adopting best-practice integrations, and enable the community to identify patterns and gaps across the ecosystem. It would also complement the technical specifications produced by the LYRASIS Interoperability Project by grounding them in real-world evidence of what has been built.

The registry is designed to be useful to human researchers (browsing via a web interface) in Phase I and automated clients (querying via an API) in Phase II, reflecting the reality that integrations themselves are often machine-to-machine workflows.

# **Stakeholders and Roles**

| Role | Responsibility | Notes |
| :---- | :---- | :---- |
| Community member developer or product owner | Submits new integration scenario records and updates records they own. | Must have a valid account in the registry. Account creation policy TBD (see Gap G-01). |
| Global Registry Administrator | Manages user accounts, reviews flagged records, maintains controlled vocabularies, and monitors system health. |  |
| Community member and potential member staff | Searches and browses the registry via the web UI to find relevant integrations. | No account required for read access. |
| Approver | Approves user submissions | Not required. Can turn approval step on or off. Only people logged in can submit records. |
| Reviewer | Provides peer feedback on submitted records (e.g., a 'helpful' rating, a comment, or a correction). | \[PLACEHOLDER — community review model TBD, see Gap G-03.\] |

# **Integration Scenario Record Data Model** {#integration-scenario-record-data-model}

## Data Formats and Metadata Standards

* Registry data model: determined based on registry platform selection; required fields below.  
* REST API: Implementation Round II, Optional

## Required Fields

| Field | Type | Description |
| :---- | :---- | :---- |
| id | UUID | System-generated unique identifier. Stable and permanent once assigned. |
| title | Text | Short, descriptive name for the integration (e.g., 'ArchivesSpace Digital Object linking to DSpace via REST API'). |
| source\_system | Controlled list (multi-select) | One or more of: ArchivesSpace, DSpace, CollectionSpace, VIVO, Fedora, Other. The system(s) where the integration originates or is initiated. |
| target\_system | Controlled list (multi-select) | One or more of the same list. The system(s) that receive data or expose endpoints consumed by the integration. |
| integration\_type | Controlled list | One of: Linking, Deposit, Metadata Harvesting (OAI-PMH), Search/Discovery, Bidirectional Sync, Other. |
| protocol | Controlled list (multi-select) | One or more of: SWORD v2, SWORD v3, OAI-PMH v2, REST API, SPARQL, Custom/Bespoke, Other. |
| status | Controlled list | One of: Active (currently in use at the submitting institution), Experimental (proof of concept), Deprecated (was active, no longer maintained), Retired, Recalled. |
| description | Long text | Free-text description of what the integration does, the problem it solves, and any key implementation decisions. Markdown supported. |
| submitted\_by | Text / User ref | Institution name (and optionally a contact name) of the submitter. |
| submitted\_date | Date | System-generated submission timestamp (ISO 8601). |

## Optional Fields

| Field | Type | Description |
| :---- | :---- | :---- |
| prerequisites | Long text | Software versions, permissions, configurations, or third-party tools required before the integration can be replicated. |
| configuration\_notes | Long text | Practical notes for replication: key configuration parameters, known gotchas, institution-specific decisions. Markdown supported. |
| code\_repository\_url | URL | Link to a public code repository (GitHub, GitLab, etc.) containing implementation code, scripts, or plugins. |
| documentation\_url | URL | Link to external documentation, wiki page, or technical write-up. |
| related\_spec\_url | URL | Link to a formal technical specification (e.g., a LYRASIS Interoperability Project spec) that this implementation corresponds to. |
| related\_scenario\_ids | UUID list | IDs of other registry records that this scenario builds on, extends, or is related to. |
| min\_system\_version | Controlled List (multi-Select) | Minimum version of source/target systems tested (e.g., 'ArchivesSpace 3.4, DSpace 7.3'). |
| def\_system\_version | Controlled List (multi-select) | Main version of source/target systems tested |
| last\_verified\_date | Date | Date the implementer last confirmed the integration was still operational. |
| contact\_email | Email | Optional contact for follow-up questions. Not displayed publicly by default (see Gap G-04). |
| license | SPDX identifier | License under which the configuration notes and linked code are shared (e.g., CC-BY-4.0, MIT, Apache-2.0). |
| tags | Text list (free) | Free-text keywords for discovery (e.g., 'digitization workflow', 'born digital', 'finding aid', 'researcher profile'). |
| updated\_date | Date | System-generated timestamp of the most recent edit to the record. |

## System-Controlled Fields (not editable by depositor)

| Field | Type | Description |
| :---- | :---- | :---- |
| record\_url | URL | Canonical URL for this record in the registry (constructed from base URL \+ id). |
| version\_history | Audit log | Immutable log of all edits, with timestamp and editor, retained for provenance. \[PLACEHOLDER — versioning model TBD, see Gap G-05.\] |
| flagged | Boolean | Set by registry administrator if a record is under review for accuracy or policy issues. |

# **System Overview**

## Integration Architecture

| Component | Role | Notes |
| :---- | :---- | :---- |
| Registry form | Public-facing interface; hosts searchable registry data. | TBD after a landscape review |
| Data store | Stores data according to defined [data model](#integration-scenario-record-data-model) | No interface |
| Configuration UI |  |  |
| Optional approval process |  |  |
| User interaction with registry records |  |  |
| Submission workflow |  |  |
| Index |  | User does not expect immediate availability of document after submission |

# **Configuration Requirements**

## Email Notifications

The registry should send email directly. If the chosen registry software does not include the ability to configure the following notifications, then an external notification service must be selected and integrated into the registry. Ideally the notifications can be tied to roles.

* Account access request  
* Record submitted  
* Record updated  
* Record status change

## Account and Access Configuration

The registry must require authentication for users who wish to deposit integration scenarios. Ideally users will access accounts through GitHub SSO. The submitted\_by field value will be the user account name.

The global administrator will approve users who request access to the registry. 

## User-Submitted Record Approval

Users may submit records to the registry after logging in, ideally through GitHub OAuth, and after having their access approved by the global administrator. Individual records do not require approval to be submitted.

The registry should include five optional \[Community\] Approver or Reviewer roles that communities can choose to implement. Anyone with an authenticated account could be assigned this role. Users assigned with this role get email notifications from the registry when new records are submitted, with a link to review the record. The Approver can then update status to Recalled if the record needs to be reviewed for potential spam or other harmful material. 

## Version Control

The registry should include a mechanism for version control. Version control settings should be flexible and configurable by the global administrator.

Versioning should be able to evolve as the registry expands or system needs evolve.

### Deletions

Records that are marked inactive in the registry are removed from default public views of the registry. No records are deleted from the registry.

## Customizable Options

### Global Options

#### **Controlled Vocabulary Management**

The controlled list values may need to be updated as the programs expand or change:

* Source\_system  
* target\_System  
* Integration\_type  
* Protocol  
* Status

These fields and configurations must be maintainable by a registry administrator without code changes. The design must allow new systems beyond the five Lyrasis CSTs to be added to the controlled list as the project scope expands.

#### **Global Configuration**

* User roles  
* Version control options  
* Email notifications

#### **User Configuration**

* 

# **Phase II: API**

### Stakeholders and Roles

| Role | Responsibility | Notes |
| :---- | :---- | :---- |
| Machine Client | Queries the registry API programmatically to retrieve integration scenario records. | No authentication required for read access. See Gap G-02 for rate limiting. |

### Configuration Notes

API specifications shall include:

* URL  
* Rate limits and associated error scenario for too many requests or other behavior for responses to exceeding the limit  
* Token  
* Response formats (if XML, define schema)

### Proposed/Sample Specification

The registry exposes a RESTful JSON API. Full OpenAPI/Swagger documentation should be generated from the implementation. The following table summarizes the required endpoints.

| Method | Endpoint | Auth Required | Description |
| :---- | :---- | :---- | :---- |
| GET | /api/v1/scenarios | No | List/search records. Supports query params: source\_system, target\_system, integration\_type, protocol, status, keyword, tags, updated\_since, page, per\_page. |
| POST | /api/v1/scenarios | Yes (token) | Create a new integration scenario record. Body: JSON conforming to Section 4 schema. |
| GET | /api/v1/scenarios/{id} | No | Retrieve a single record by UUID. Supports content negotiation (JSON, XML). |
| PATCH | /api/v1/scenarios/{id} | Yes (owner token) | Update one or more fields of an existing record. Partial update (JSON Merge Patch). |
| GET | /api/v1/vocabularies | No | Retrieve current controlled vocabulary lists (systems, integration types, protocols, statuses). |
| GET | /api/v1/schema | No | Retrieve the current JSON schema for integration scenario records. |

*Note: DELETE is intentionally omitted. Records should be marked Retired rather than deleted, preserving the audit trail and inbound links.*

# **Behavior Scenarios**

Draft: [See F1](https://github.com/orgs/lyrasisorghome/projects/1/views/1?pane=issue&itemId=178176362&issue=lyrasisorghome%7CInteroperabilityProject%7C58)  
Gap G-11: Compile edited behavior scenarios from first drafts and AI-generated summaries.

## Deposit (Write)

## Update (Write)

## Search and Retrieve (Read)

## Export (Harvest)

# **Error Scenarios**

Gap G-03

## Deposit with missing or invalid required fields

## Duplicate record detection

## Search returns no results

## Unauthorized edit attempt

## Record flagged for review

# **Open Questions and Specification Gaps**

## Implementation Gaps

| \# | Gap | Description | Owner |
| :---- | :---- | :---- | :---- |
| **G-01** | Duplicate detection algorithm | Define the logic for identifying potential duplicates (ES02). A simple approach: flag if submitted\_by \+ source\_system \+ target\_system \+ integration\_type exactly match an existing record. A more sophisticated approach uses fuzzy title matching. Define the threshold and whether it is a hard block or advisory warning. | Developer / Product Owner |
| **G-02** | Maintenance plan | Define functionality for how records will be deprecated for integrations that are no longer supported or possible. |  |

## RFP Deliverable Gaps

| \# | Gap | Description | Owner |
| :---- | :---- | :---- | :---- |
| **G-03** | Error handling, logging, and monitoring |  | Repository Administrators |
| **G-04** | Security and data privacy |  | Developer / Product Owner |
| **G-05** | Performance and scalability  |  |  |
| **G-06** | Documentation |  | Users |
| **G-07** | Change management | Recommendations for handling change management across applications, considering the governance structure and development practices of the participant technologies. (Should include identifying any known blockers or other issues). |  |
| **G-08** | Frequency | Real-time, batch, scheduled, etc. |  |
| **G-09** | Volume | Data load and message frequency |  |
| **G-10** | Diagrams | Diagrams of system interactions (ideally provided in graphviz or other open diagram format) |  |
| **G-11** | Behavior scenarios: Final | Compile edited behavior scenarios from first drafts and AI-generated summaries. |  |

# 

# **Development Areas**

TBD \- This will be a list to satisfy RFP deliverable: Identification of gaps between the requirements and existing functionality with recommendations for paths to implementation.