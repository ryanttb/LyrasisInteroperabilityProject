---
source: https://docs.google.com/document/d/1s9IQHVJMjTGMrK_rt38mDC1PvkAVCWv117MsJN6vF-w
scenarios:
  - A3
  - A4
issues:
  - https://github.com/lyrasisorghome/InteroperabilityProject/issues/45
  - https://github.com/lyrasisorghome/InteroperabilityProject/issues/52
last_synced: 2026-07-14
---
# **ArchivesSpace SWORD Deposits**

## Technical Specification

*SWORD-based deposit of Archival Files from ArchivesSpace*

Document Status: DRAFT  
Version: 0.3  
Date: May 2026  
Source Stories: [A3](https://github.com/lyrasisorghome/InteroperabilityProject/issues/45) and [A4](https://github.com/lyrasisorghome/InteroperabilityProject/issues/52)  
Project: LYRASIS Interoperability Project  
Systems: ArchivesSpace SUI, ArchivesSpace PUI, DSpace REST API (7.x / DSpace 9.x contract), ArchivesSpace REST API

[Purpose and Scope](#purpose-and-scope)

[Background](#background)

[Actors and Roles](#actors-and-roles)

[System Overview](#system-overview)

[Configuration Requirements](#configuration-requirements)

[Deposit Wizard](#deposit-wizard)

[Behavior Scenarios](#behavior-scenarios)

[Error Scenarios](#error-scenarios)

[Open Questions and Specification Gaps](#open-questions-and-specification-gaps)

[Development Areas](#development-areas)

# **Purpose and Scope** {#purpose-and-scope}

This specification defines requirements for a feature enabling ArchivesSpace staff users to deposit digital files from within an ArchivesSpace component record into a compliant repository via the SWORD (Simple Web-service Offering Repository Deposit) protocol, and then create ArchivesSpace digital object records linked to ArchivesSpace archival object records referencing the deposited content.

DSpace supports SWORD server v2. The design must incorporate a SWORD app. The design must also accommodate future support for other target repositories and other SWORD protocol versions (including SWORD v3) through an abstraction layer, without requiring re-architecture.

Out of scope: manual file upload workflows, discovery layer integrations, bulk re-ingest of previously deposited content, and changes to the deposit approval/workflow configuration of the repository receiving the deposit.

# **Background** {#background}

Staff managing digitized and born-digital archival collections in ArchivesSpace often need to deposit associated files into a SWORD-compliant repository for long-term access and discovery. The current workflow is entirely manual: files are uploaded to the repository, then URIs are copied back into ArchivesSpace digital object records one by one.

SWORD is a standard deposit protocol supported by DSpace (v2) and a growing number of other repositories. Integrating SWORD into ArchivesSpace would allow staff to initiate deposits without leaving the system they use to describe archival content, reducing errors and the time cost of maintaining links between the two systems.

Key distinctions from the companion ArchivesSpace-DSpace linking specification ([A1-2](https://docs.google.com/document/d/1GVP7IgAcK4kcJyl27Fobm_EuDJZTnh_IbUl5C61jNYw/edit?tab=t.0)): 

1. A1-2 handles linking to pre-existing DSpace records; this spec handles the deposit of new content into DSpace where no DSpace record yet exists for the files being processed.
2. This spec covers pushing descriptive metadata from ArchivesSpace to DSpace with or without a deposit; A1-2 does not account for descriptive metadata, just bidirectional linking.



# **Actors and Roles** {#actors-and-roles}


| Actor                        | Role                                                                                                         | Notes                                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| ArchivesSpace Administrator  | Configures SWORD endpoint(s) and deposit settings per repository.                                            | May configure more than one endpoint (e.g., multiple DSpace instances or future non-DSpace repositories). |
| ArchivesSpace Staff User     | Selects files attached to an AS component, triggers deposit, and confirms the resulting digital object link. | Requires write access to the ArchivesSpace repository.                                                    |
| DSpace Collection Manager    | Owns the target DSpace collection; configures deposit permissions for the SWORD client.                      | May need to approve deposits depending on DSpace workflow settings.                                       |
| ArchivesSpace End User (PUI) | Views finding aid records with links to deposited content in DSpace.                                         | No direct interaction with the deposit feature.                                                           |




# **System Overview** {#system-overview}



## Integration Architecture

The integration operates as a plugin within the ArchivesSpace SUI. It requires a SWORD application. The SWORD application communicates with a configured SWORD endpoint using the SWORD v2 protocol (AtomPub-based). The design must abstract the SWORD version and endpoint type so that v3 (Signposting/Linked Data Notifications based) can be added in the future without replacing the core deposit logic.


| Component                           | Role                                                                           | Interface                                       |
| ----------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------- |
| ArchivesSpace SUI                   | Hosts deposit wizard and configuration UI.                                     | Browser / ArchivesSpace plugin framework        |
| SWORD Client (AS Plugin)            | Constructs deposit packages, submits to SWORD endpoint, handles responses.     | SWORD v2 (HTTP/AtomPub); extensible to v3       |
| SWORD v2 Endpoint                   | Receives deposit package, creates item in target collection, returns item URI. | SWORD v2 (HTTP POST, Atom entry or zip package) |
| ArchivesSpace Digital Object Record | Created or updated post-deposit with the SWORD repository item URI.            | Internal AS data model                          |
| ArchivesSpace PUI                   | Displays links to deposited content.                                           | AS indexing pipeline                            |




## SWORD Protocol Scope

SWORD v2 is the required protocol for initial implementation. The following v2 operations are in scope:

- Service Document retrieval: discover available collections and accepted package formats.  
- Binary file deposit (HTTP POST with Content-Type and Packaging headers).  
- Packaged deposit (e.g., Simple Zip, METS/SWAP): PLACEHOLDER — package format TBD, see Gap G-04.  
- Deposit Receipt processing: extract the deposited item URI from the SWORD response.  
- Error response handling: parse SWORD error documents and surface meaningful messages to the user.

SWORD v3 compatibility requirements: PLACEHOLDER — to be defined once the v3 specification is finalised and stakeholder demand is confirmed. The abstraction layer should make v3 support additive, not a breaking change.

# **Configuration Requirements** {#configuration-requirements}



## Configuration Location

System  Manage Repositories  Select Repository  SWORD Deposit Settings.

## Configuration Fields (Proposed) {#configuration-fields-(proposed)}


| Field                  | Type             | Required | Description                                                                                                                                                   |
| ---------------------- | ---------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SWORD Endpoint URL     | URL              | Yes      | Service Document URL for the SWORD endpoint (e.g., [https://dspace.example.edu/swordv2/servicedocument](https://dspace.example.edu/swordv2/servicedocument)). |
| SWORD Protocol Version | Select (v2 / v3) | Yes      | Determines which protocol adapter is used. v3 support is future scope.                                                                                        |
| Authentication Type    | Select           | Yes      | PLACEHOLDER — Basic Auth (username/password) is the DSpace SWORD v2 default; OAuth or API key may be needed for future repos. See Gap G-01.                   |
| Username / Credential  | Secure text      | Yes      | Credential for the SWORD deposit account.                                                                                                                     |
| Default Package Format | Select           | Yes      | PLACEHOLDER — e.g., Simple Zip, METS/SWAP. See Gap G-04.                                                                                                      |
| Integration Enabled    | Boolean          | Yes      | Master switch for this repository.                                                                                                                            |
| Display Name           | Text             | No       | Human-readable label for this endpoint (useful when multiple endpoints are configured).                                                                       |




# **Deposit Wizard** {#deposit-wizard}



## Deposit Wizard Fields (Proposed)


| Field             | Type    | Required | Description                                                                                                                                                   |
| ----------------- | ------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Target Collection | URL     | No       | Service Document URL for the SWORD endpoint (e.g., [https://dspace.example.edu/swordv2/servicedocument](https://dspace.example.edu/swordv2/servicedocument)). |
| Source location   | Address | Yes      |                                                                                                                                                               |




## Default Dublin Core Mapping

[`as-dc-mapping.html`](../references/as-dc-mapping.html)

# **Behavior Scenarios** {#behavior-scenarios}



### BS-01: Administrator configures a SWORD deposit endpoint


| Step  | Description                                                                                                          |
| ----- | -------------------------------------------------------------------------------------------------------------------- |
| Given | The user has Administrator-level access to ArchivesSpace.                                                            |
|       | The administrator has a deposit account for a SWORD v2 enabled repository.                                           |
| When  | The administrator navigates to System Manage Repositories, selects the repository, and opens SWORD Deposit Settings. |
|       | The administrator enters the required fields ([Configuration Fields (Proposed)](#configuration-fields-(proposed))    |
| Then  | The system retrieves and validates the SWORD Service Document from the configured endpoint URL.                      |
|       | The system notifies the administrator that the SWORD endpoint is enabled.                                            |
|       | The SWORD Deposit button becomes active in the SUI for staff users of that repository.                               |




### BS02: Staff user deposits one or more files from an Archival Object component into a SWORD-compliant repository

REMOVED: 

There are no actual digital files in ArchivesSpace. ASpace is a CMS and not a DAMS.
So AFAICT this is not a use case.
We need to be able to send data to DSpace without a deposit.

### BS02: Staff user sets up a deposit for a file or a batch of files that relate to many Archival objects


| Step  | Description                                                                                                                                                                                                                                                                                                                             |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Given | A Resource with Archival Objects or an Archival Object with child archival objects exists in ArchivesSpace.                                                                                                                                                                                                                             |
|       | Multiple files are associated with multiple archival objects.                                                                                                                                                                                                                                                                           |
|       | SWORD deposit is configured and enabled.                                                                                                                                                                                                                                                                                                |
| When  | The staff user initiates a batch deposit from the parent component by selecting a button. (For example: A new “Create” button beside the existing “Make Representative” button, which is inside the “Add Digital Object” feature that is accessed from the “Instances” field group).                                                    |
| Then  | A SWORD Deposit pop up wizard appears.                                                                                                                                                                                                                                                                                                  |
| When  | The staff user fills out Page 1 of the wizard, which requires them to choose a Target Collection and a Source location for the files. The staff user is not depositing to a specific collection, or their repository has no collections, so they choose “None” for Target Collection. The staff user completes the action via a button. |
| Then  | Page 2 of the SWORD pop up wizard appears.                                                                                                                                                                                                                                                                                              |
| When  | Page 2 of the wizard shows a file tree of the Source Location with checkboxes for choosing files to upload, including options to select or de-select all. The staff user selects the files they want to upload and completes the action via a button.                                                                                   |
| Then  | Page 3 of the SWORD pop up wizard appears.                                                                                                                                                                                                                                                                                              |
|       | Page 3 of the wizard shows two file trees: one with only the files that will be deposited; and one with the archival objects that the user can relate the files to.                                                                                                                                                                     |
|       | The staff user drags and drops files to the archival objects they relate to. Some archival objects have many files related to one archival object. Some only have one file related to the archival object.                                                                                                                              |
|       | The staff user initiates the deposit by selecting a button.                                                                                                                                                                                                                                                                             |




### BS03: ArchivesSpace deposits the files, retrieves URIs, and generates digital objects


| Step  | Description                                                                                                                                           |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Given | A staff user has configured a SWORD deposit using the ArchivesSpace deposit wizard.                                                                   |
|       | Multiple files are associated with multiple archival objects.                                                                                         |
|       | SWORD deposit is configured and enabled.                                                                                                              |
| When  | The staff user completes the action via a button.                                                                                                     |
| Then  | A SWORD deposit is made for each archival object’s file grouping (sometimes a single file, sometimes a group of files). A SWORD receipt is generated. |
| When  | ArchivesSpace receives the SWORD receipt with new URIs for digital objects in the SWORD-enabled system.                                               |
| Then  | Digital Object records are created in ArchivesSpace for each deposited item or group of items, linked to their respective sub-components.             |
|       | A batch deposit summary is displayed showing success/failure per file.                                                                                |
|       | Successful deposits are logged; failed deposits are flagged for retry (see ES02).                                                                     |




# **Error Scenarios** {#error-scenarios}



## ES01: SWORD endpoint not configured or not active


| Step  | Description                                                                                                                                                                      |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Given | SWORD Deposit Settings are absent or the Integration Enabled toggle is off.                                                                                                      |
| When  | A staff user navigates to an Archival Object or Resource record.                                                                                                                 |
| Then  | The Deposit to Repository option is not visible (or is visible but inactive with a tooltip: 'SWORD deposit is not configured for this repository. Contact your administrator.'). |




## ES02: Deposit fails at the SWORD endpoint


| Step        | Description                                                                                                     |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| Given       | SWORD deposit is configured and a deposit is attempted.                                                         |
| When        | The DSpace SWORD endpoint returns an error response (HTTP 4xx or 5xx, or a SWORD Error Document).               |
| Then        | The error type and message from the SWORD Error Document are displayed to the user in plain language.           |
|             | No ArchivesSpace Digital Object record is created for the failed deposit.                                       |
|             | The error is written to the deposit log with the full SWORD error body, timestamp, and user.                    |
|             | The user is offered the option to retry the deposit or cancel.                                                  |
| PLACEHOLDER | Behavior when a batch deposit partially fails (some files succeed, some fail) is not yet defined. See Gap G-07. |




## ES03: Authentication failure


| Step  | Description                                                                                                                 |
| ----- | --------------------------------------------------------------------------------------------------------------------------- |
| Given | SWORD deposit is configured with a credential.                                                                              |
| When  | The SWORD endpoint returns HTTP 401 or 403                                                                                  |
| Then  | The user is shown: 'Authentication failed. Your SWORD credentials may be expired or incorrect. Contact your administrator.' |
|       | No deposit is attempted. The error is logged.                                                                               |




## ES04: Missing required metadata


| Step  | Description                                                                                                                                                                                                                     |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Given | A deposit is initiated for an Archival Object that is missing fields required by the SWORD package format (e.g., no date).                                                                                                      |
| When  | The user reaches the metadata review step in the deposit wizard.                                                                                                                                                                |
| Then  | Required-but-missing fields are highlighted. The user cannot proceed until they are filled in or acknowledged. PLACEHOLDER — which fields are required is determined by the package format and target repository. See Gap G-05. |




# **Open Questions and Specification Gaps** {#open-questions-and-specification-gaps}


|      | Gap                                                    | Description                                                                                                                                                                                                                                                                                                            | Owner                               |
| ---- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| G-01 | SWORD authentication type                              | DSpace SWORD v2 uses HTTP Basic Auth by default. Future repositories may require OAuth 2.0 or API keys. The configuration field and credential storage must be designed to support multiple auth types without storing plaintext passwords. Confirm acceptable credential storage approach for AS plugin architecture. | Developer / Security                |
| G-02 | File attachment mechanism in AS                        | How are files associated with an Archival Object prior to deposit? Does ArchivesSpace natively store binary files, or are files referenced by URI/path? If the latter, can the deposit plugin access the binary content? This is a prerequisite for understanding what can actually be deposited.                      | Developer / Product Owner           |
| G-03 | UI trigger and placement                               | Where exactly in the SUI is the deposit action initiated? Options include: a new Instances sub-menu item, a toolbar button, a right-click context action. Must be consistent with existing AS UI patterns.                                                                                                             | UX / Developer                      |
| G-04 | SWORD package format                                   | SWORD v2 supports multiple packaging formats (Simple Zip, METS/SWAP, BagIt, etc.). Which format(s) will be supported? The choice affects what metadata fields can be included and how DSpace processes the deposit. DSpace SWORD v2 most commonly accepts Simple Zip with a mets.xml descriptor.                       | Developer / DSpace Admin            |
| G-05 | Metadata mapping AS → SWORD package                    | Which ArchivesSpace fields are mapped to which SWORD/DSpace metadata fields? Minimum required fields and optional fields must be specified. Special cases: date handling (AS date ranges vs. DSpace single-year requirement), rights/access, creator, subject. Full mapping table needed.                              | Product Owner / Metadata Specialist |
| G-06 | Granularity: one DSpace item per file or per component | When a component has multiple files, does each file become a separate DSpace item, or do all files for a component become bitstreams within one DSpace item? This affects the Digital Object record structure in AS and the DSpace collection organisation.                                                            | Product Owner / DSpace Admin        |
| G-07 | Partial batch failure handling                         | If a batch deposit of N files fails for M N of them, what is the correct behavior? Options: roll back all, keep successes and surface failures, or queue failures for retry. Must define retry UX and how partial states are represented in AS.                                                                        | Product Owner / Developer           |
| G-08 | SWORD v3 abstraction requirements                      | SWORD v3 uses a completely different protocol (HTTP PATCH, JSON-LD, Signposting). Define the minimum abstraction interface the SWORD client module must expose so that a v3 adapter can be added without re-architecting deposit logic. Timing: document interface contract before v2 implementation is finalised.     | Developer                           |
| G-09 | DSpace workflow / approval                             | DSpace collections may have submission workflows requiring approval before an item is published. Does the SWORD deposit bypass workflow (via DSpace 'in progress' flag)? Or does the deposit appear in draft until approved? How is the AS digital object status affected if the DSpace item is pending approval?      | Developer / DSpace Admin            |
| G-10 | Re-deposit / update behaviour                          | If the same file is deposited a second time (e.g., to update content), should the plugin create a new DSpace item or update the existing one via SWORD replace/update? DSpace SWORD v2 supports item update via HTTP PUT. Policy must be defined.                                                                      | Product Owner                       |




# **Development Areas** {#development-areas}


|             | Work Item                                                                                               | Notes                                                                             |
| ----------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| D-01        | Build SWORD Deposit Settings field group in System Manage Repositories                                  | Shared config layer; must support multiple endpoint profiles.                     |
| D-02        | Build SWORD client module: Service Document retrieval, package construction, HTTP POST, receipt parsing | Must be version-abstracted (v2 now, v3 future). See G-08.                         |
| D-03        | Build deposit wizard UI in SUI (single-file and batch modes)                                            | Metadata pre-population from AS record; target collection picker; file selection. |
| D-04        | Implement post-deposit Digital Object record creation in ArchivesSpace                                  | Set DSpace URI; link to Archival Object; trigger PUI indexing.                    |
| D-05        | Implement deposit logging                                                                               | Timestamp, user, target, package, SWORD response, status.                         |
| D-06        | Implement SWORD error document parsing and user-facing error display                                    | ES02, ES03, ES04.                                                                 |
| D-07        | Batch deposit orchestration and partial-failure handling                                                | Resolution of G-07 required first.                                                |
| D-08 Future | SWORD v3 adapter implementation                                                                         | After G-08 abstraction contract is defined.                                       |






