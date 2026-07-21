---
source: https://docs.google.com/document/d/1YWPMBOrjoQC3e_cQUTZu3BKsgVw0TH0cqh7-o_UNV8U
scenario: V1
issue: https://github.com/lyrasisorghome/InteroperabilityProject/issues/54
last_synced: 2026-07-21
---
# **VIVO SWORD Deposit**

## Technical Specification

*SWORD-Based Deposit of Publications from VIVO to an Institutional Repository*

Document Status: DRAFT  
Version: 0.2  
Date: June 2026  
Source Story: [V1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/54)  
Project: LYRASIS Interoperability Project  
Systems: VIVO / any SWORD-enabled IR

[Purpose and Scope](#purpose-and-scope)

[Background](#background)

[Actors and Roles](#actors-and-roles)

[System Overview](#system-overview)

[Integration Architecture](#integration-architecture)

[Configuration Requirements](#heading=h.o7inc7tl1zc3)

[Metadata Extraction and Storage Requirements](#heading=h.sz76smzg4p1m)

[API Interactions](#heading=h.xkvgi3r9dumb)

[Behavior Scenarios](#behavior-scenarios)

[Error Scenarios](#error-scenarios)

[Open Questions and Specification Gaps](#open-questions-and-specification-gaps)

# **Purpose and Scope** {#purpose-and-scope}

This specification defines **how VIVO would implement** a workflow in which a signed-in researcher uploads a publication file — either a single **PDF** (no accompanying metadata) or a **METS-compliant ZIP** (for example, a PDF plus a METS-formatted XML file) — from their profile, VIVO deposits the package to a configured IR via **SWORD v2**, and then creates or updates a **publication record on the profile** linked to the IR item URI returned by the deposit. SWORD v2 is the primary protocol in scope. There are currently no known implementations of SWORD v3, but the spec notes where SWORD v3 configuration would differ from v2, should any v3 servers be built in the future.

With this feature, users will achieve two steps of their RDM/RIM workflow at once: deposit publications and display linked references to them on their VIVO profile. While the feature should be designed to integrate with any SWORD repository, we will use DSpace as a proof of concept integration and basis for defining required functionality.

This draft covers:

1. **Deployment context** — VIVO/Vitro Web application ARchive (WAR) layout and where HTTP requests land  
2. **Existing components** to extend or reuse (Create-and-Link, Site Admin registration, permissions, file upload limits)  
3. **New components** (proposed packages, class names, responsibilities)  
4. **Configuration and persistence** — admin UI, endpoint records, credentials, protocol version selection  
5. **Reference UI touchpoints** — Wilma theme profile page and admin screens only (custom themes out of scope for this deliverable)  
6. **SWORD packaging for PDF and METS ZIP uploads** — concrete v2 behavior   
7. **High-level request/data flows** with pseudocode sketches  
8. **SWORD v3 forward compatibility** — adapter hook only; no v3 client in v0.1  
9. **Open decisions** 

Out of scope for v0.1 (defer to a lower-level design pass or client feedback):

1. Authoring the METS package itself — the spec accepts a METS-compliant ZIP as an upload format but does not define how the METS document is produced (see the [DSpace METS SIP Profile](https://wiki.lyrasis.org/spaces/DSDOC10x/pages/446399329/DSpaceMETSSIPProfile) for the reference profile)  
2. Line-by-line BIBO ↔ IR metadata field mapping for every deployment ontology profile  
3. IR-side ingest workflow configuration (embargo, review queues, collection policies)  
4. Retrospective migration of existing IR items into VIVO  
5. Automated extraction of metadata from uploaded files (PDF text/OCR parsing or reading the METS document)  
6. SWORD v3 implementation (no production v3 servers identified yet)  
7. Changes to non-reference themes (`nemo`, `tenderfoot`, etc.)  
8. Retrieving URL and metadata from a SWORD repository then updating VIVO profile without depositing (will be addressed in revision phase)  
9. Using SWORD to deposit an SAF to DSpace (open question: Is this a significant user need?)  
10. Validating that the selected content license matches allowed licenses for each individual IR

This spec describes integration with **any SWORD-compliant IR** via standard protocol endpoints. It does not name or assume a particular repository product unless required by the protocol itself.

# **Background** {#background}

VIVO is an open-source semantic web platform for researcher profiling. Researchers and their support staff use VIVO to record and publish information about publications, grants, and professional activities. Because different research activities are represented in different repositories, a primary goal of the VIVO software is to be interoperable.

Many institutions also operate an institutional repository (IR) for long-term open-access deposit of research outputs.

Currently, researchers must deposit content in the IR separately from describing it in VIVO, then manually add the IR link to their VIVO profile. This creates duplicated effort and inconsistency. It is difficult to incentivize scholars to maintain their data in both places. If scholars could deposit their publication to their IR at the same time as linking the publication to their VIVO profile, it would be easier to ensure this data makes it to VIVO. VIVO has metadata retrieval functionality, but no external deposit integrations have been identified to date.

SWORD (Simple Web-service Offering Repository Deposit) is a standard protocol supported by several open repositories. The SWORD protocol provides a programmatic path for VIVO to initiate deposits on a researcher's behalf to a SWORD-compliant repository, such as DSpace, ArXiv, or Alma. 

# **Actors and Roles** {#actors-and-roles}

![][image1]

| Actor | Role |
| :---- | :---- |
| VIVO Administrator | Registers one or more IR SWORD endpoints, credentials, default collection, protocol version (v2), and master enable flag via Site Admin. |
| Researcher / Faculty (VIVO User) | On their own profile (self-editing), uploads a PDF or METS-compliant ZIP, confirms the publication metadata for the VIVO profile record, selects target collection, submits deposit. |
| SWORD-enabled Repository Manager | Configures SWORD permissions and collections on the IR (outside VIVO). |
| Profile visitor (end user) | Follows the publication's **web link** on the public profile to the IR item (no deposit UI). |
| SWORD deposit module (system agent) | Validates upload, extracts metadata, calls SWORD client, writes RDF, logs outcome. |

# **System Overview** {#system-overview}

**Recommendation:** Implement as a **VIVO `api` module feature** (same tier as the existing Create-and-Link publication workflow), use [**JavaClient2.0**](https://github.com/swordapp/JavaClient2.0) for SWORD v2, mirror the **`CreateAndLinkResourceController`** servlet \+ Freemarker wizard pattern, and register admin screens through **`BaseSiteAdminController.registerSiteConfigData`**. Limit **reference UI** changes to the **Wilma** theme templates under `webapp/themes/wilma/`.

## Typical URL Shapes

Assume host `https://vivo.example.edu` and profile `https://vivo.example.edu/display/cwid-ana4036`:

| Surface | Example URL | Notes |
| :---- | :---- | :---- |
| Individual profile (public) | `/display/{localName}` | Existing Vitro routing |
| Create-and-Link (precedent) | `/createAndLink/doi?profileUri=…` | Existing publication claim flow |
| **Proposed deposit entry** | `/swordDeposit/upload?profileUri=…` | GET → upload form; POST → process |
| **Proposed admin** | `/admin/sword` | CRUD for endpoint configuration |
| Site Admin hub | `/siteAdmin` | Existing; new link under Site Configuration |

## VIVO / Vitro repositories touched

| Repository | Role in SWORD feature | Expected change level |
| :---- | :---- | :---- |
| [vivo-project/VIVO `api`](https://github.com/vivo-project/VIVO/tree/main/api) | **Primary** — deposit servlet, services, metadata extraction, SWORD adapter, RDF writes | **Major** — new `sword` package |
| [vivo-project/VIVO `webapp`](https://github.com/vivo-project/VIVO/tree/main/webapp) | Freemarker wizard templates; **Wilma** profile button | **Moderate** |
| [vivo-project/VIVO `home`](https://github.com/vivo-project/VIVO/tree/main/home) | Default `runtime.properties` keys; optional first-time RDF for permissions | **Minor** |
| [vivo-project/Vitro `api`](https://github.com/vivo-project/Vitro/tree/main/api) | Site Admin registration hook; optional new `SimplePermission` | **Minor** |
| [vivo-project/Vitro `webapp`](https://github.com/vivo-project/Vitro/tree/main/webapp) | Shared `siteAdmin-siteConfiguration.ftl` only if link is registered from Vitro side | **Optional minor** |
| [swordapp/JavaClient2.0](https://github.com/swordapp/JavaClient2.0) | SWORD v2 HTTP client library | **Dependency** (Maven) |

**Not required:** Vitro core changes beyond permission registration unless admin UI is implemented entirely in Vitro (recommended: VIVO `api` registers its own Site Admin link at startup, same pattern as other extensions).

# **Integration Architecture** {#integration-architecture}

## Existing components to reuse

VIVO has **no SWORD code today**. These are the closest analogues:

### Publication claim workflow (Create-and-Link)

| Component | Location | Reuse for SWORD deposit |
| :---- | :---- | :---- |
| `CreateAndLinkResourceController` | `VIVO/api/.../CreateAndLinkResourceController.java` | **Template** for multi-step Freemarker wizard, profile URI parameter, RDF publication creation, authorship linking |
| `CreateAndLinkResourceProvider` | `VIVO/api/.../createandlink/` | Pattern for pluggable external systems (here: SWORD replaces Crossref/PubMed lookup) |
| Profile UI claim buttons | `webapp/themes/wilma/templates/individual--foaf-person.ftl` | Add **Upload Publication** alongside DOI/PMID claim forms |
| `createAndLink.providers` | `runtime.properties` | Precedent for feature toggles; add `swordDeposit.enabled` |

Create-and-Link already:

- Requires **`SimplePermission.EDIT_OWN_ACCOUNT`** for the claiming user  
- Creates `bibo:` individuals and links them with **`vivo:relatedBy`** / author nodes  
- Adds external URLs via **`vcard:hasURL`** when a resource URL is known

SWORD deposit extends this: the **IR item URI** from the deposit receipt becomes that external URL.

### Site Admin and permissions

| Component | Location | Reuse for SWORD deposit |
| :---- | :---- | :---- |
| `BaseSiteAdminController.registerSiteConfigData` | `Vitro/api/.../BaseSiteAdminController.java` | Register **`manageSwordEndpoints`** → `/admin/sword` under Site Configuration |
| `SimplePermission` | `Vitro/api/.../SimplePermission.java` | Add **`ManageSwordEndpoints`** (admin) |
| `simple_permissions_admin.n3` | `Vitro/home/.../accessControl/firsttime/` | Grant new permission to Admin role set |
| `siteAdmin-siteConfiguration.ftl` | `Vitro/webapp/.../siteAdmin-siteConfiguration.ftl` | Renders registered config links automatically |

### Configuration and file handling

| Component | Location | Reuse for SWORD deposit |
| :---- | :---- | :---- |
| `ConfigurationProperties` / `runtime.properties` | `Vitro/home/.../example.runtime.properties` | Global limits: `fileUpload.maxFileSize`, `fileUpload.allowedMIMETypes` (already documents `application/pdf`) |
| Multipart request handling | `EditConfigurationVTwo`, Vitro filters | Existing Commons FileUpload pipeline for form posts |
| `RDFService` / `ChangeSet` | Vitro API | Atomic write of new publication triples |

### Theming

| Component | Location | Reuse for SWORD deposit |
| :---- | :---- | :---- |
| `ThemeInfoSetup` | `Vitro/api/.../ThemeInfoSetup.java` | Themes live under `/themes/{name}/`; Site Information selects active theme |
| Wilma person template | `VIVO/webapp/themes/wilma/templates/individual--foaf-person.ftl` | **Only theme modified** in v0.1 |

## Proposed new components

### New Java package: `org.vivoweb.webapp.sword`

Mirror the Create-and-Link layout under `VIVO/api/src/main/java/org/vivoweb/webapp/`:

```java
VIVO/api/src/main/java/org/vivoweb/webapp/sword/
  controller/
    SwordDepositController.java          # @WebServlet /swordDeposit/*
    SwordAdminController.java            # @WebServlet /admin/sword/*
  service/
    SwordDepositService.java             # orchestration: extract → deposit → rdf
    SwordEndpointConfigService.java      # load/save/test endpoint configs
    PublicationRdfWriter.java            # create bibo individual + authorship + webpage
    SwordDepositAuditLog.java            # timestamp, user, collection, IR URI
  metadata/
    UploadPackage.java                   # PDF or METS ZIP wrapper (stream, filename, md5)
    UploadPackageParser.java             # validate MIME, classify PDF vs ZIP (no content parsing)
    PublicationMetadata.java             # researcher-entered metadata for the VIVO profile record
  sword/
    SwordProtocolAdapter.java            # interface: service doc, deposit, status
    SwordV2ClientAdapter.java            # wraps org.swordapp.client.SWORDClient
    SwordV3ClientAdapter.java            # stub / NotImplemented in v0.1
    SwordAdapterFactory.java             # select by configured version (+ future auto-detect)
    SwordPackageBuilder.java             # build org.swordapp.client.Deposit; PDF → binary (no packaging), ZIP → setPackaging(METS)
    SwordDepositResult.java              # IR item URI, status IRI, in-progress flag
  model/
    SwordEndpointConfig.java             # endpoint DTO
    SwordEndpointConfigStore.java        # persistence interface
    FileSwordEndpointConfigStore.java    # JSON in VIVO home (v0.1 default)
  setup/
    SwordSiteAdminSetup.java             # ServletContextListener → registerSiteConfigData
    SwordPermissionSetup.java            # register SimplePermission + n3 snippet
```

### Class responsibilities (sketch)

**`SwordDepositController`** — HTTP entry for researchers:

```java
@WebServlet(name = "SwordDeposit", urlPatterns = {"/swordDeposit/*"})
public class SwordDepositController extends FreemarkerHttpServlet {
    public static final AuthorizationRequest REQUIRED_ACTIONS =
        SimplePermission.EDIT_OWN_ACCOUNT.ACTION;

    // GET  /swordDeposit/upload?profileUri=…        → upload form
    // POST /swordDeposit/upload                     → parse multipart, classify PDF vs METS ZIP
    // GET  /swordDeposit/confirm?…                  → review metadata + pick collection
    // POST /swordDeposit/deposit                    → run SwordDepositService.deposit(...)
}
```

**`SwordV2ClientAdapter`** — thin wrapper over JavaClient2.0:

```java
public class SwordV2ClientAdapter implements SwordProtocolAdapter {
    private final SWORDClient client;

    public ServiceDocument fetchServiceDocument(SwordEndpointConfig cfg) {
        AuthCredentials auth = new AuthCredentials(cfg.getUsername(), cfg.getPassword());
        return client.getServiceDocument(cfg.getServiceDocumentUrl(), auth);
    }

    public SwordDepositResult deposit(SWORDCollection collection, Deposit deposit,
                                      SwordEndpointConfig cfg) {
        DepositReceipt receipt = client.deposit(collection, deposit, authFor(cfg));
        return SwordDepositResult.fromReceipt(receipt);
    }
}
```

**`SwordDepositService`** — core orchestration:

```java
public SwordDepositResult deposit(VitroRequest vreq, UploadPackage pkg,
                                  PublicationMetadata md,   // researcher-entered, for the VIVO record
                                  String collectionHref, String profileUri) {
    UploadPackage parsed = uploadPackageParser.parse(pkg);          // validate MIME, classify PDF vs ZIP

    SwordEndpointConfig endpoint = configService.getEnabledEndpoint(...);
    SWORDCollection collection = adapter.resolveCollection(endpoint, collectionHref);

    // Fork on upload type: PDF deposits without metadata; ZIP is sent as a METS package.
    Deposit swordDeposit = packageBuilder.build(parsed, endpoint);

    SwordDepositResult result = adapter.deposit(collection, swordDeposit, endpoint);

    publicationRdfWriter.createOrUpdatePublication(profileUri, md, result.getItemUri());
    auditLog.record(vreq, endpoint, collectionHref, result);
    parsed.dispose();  // delete temp files
    return result;
}
```

**`SwordSiteAdminSetup`** — register admin nav (runs at startup):

```java
BaseSiteAdminController.registerSiteConfigData(
    "manageSwordEndpoints",
    "/admin/sword",
    null,
    SimplePermission.MANAGE_SWORD_ENDPOINTS.ACTION);
```

### Files to modify (existing)

| File | Change |
| :---- | :---- |
| `VIVO/api/pom.xml` | Add dependency on `org.swordapp:sword-client` (JavaClient2.0 coordinates TBD — may require vendoring or JitPack) |
| `VIVO/webapp/themes/wilma/templates/individual--foaf-person.ftl` | Add Upload Publication control when `swordDeposit.enabled=true` |
| `VIVO/home/.../example.runtime.properties` | Document new keys (see Configuration) |
| `Vitro/.../SimplePermission.java` | Add `MANAGE_SWORD_ENDPOINTS` |
| `Vitro/.../simple_permissions_admin.n3` | Include new permission for Admin role |

## Configuration model

Two tiers align with the behavior scenarios and VIVO conventions:

### Tier 1 — System administrator (`runtime.properties`)

Global feature flags and limits. Not editable in the Site Admin UI.

| Key | Example | Purpose |
| :---- | :---- | :---- |
| `swordDeposit.enabled` | `true` | Master switch; hides UI and rejects `/swordDeposit/*` when false |
| `swordDeposit.configStore` | `file` | `file` (default) or future `rdf` |
| `swordDeposit.configPath` | `{vivoHome}/config/sword-endpoints.json` | Endpoint registry file location |
| `swordDeposit.maxUploadBytes` | `52428800` | Override; default falls back to `fileUpload.maxFileSize` |
| `swordDeposit.allowedMimeTypes` | `application/pdf,application/zip` | Upload validation |
| `swordDeposit.defaultProtocolVersion` | `v2` | Used when admin leaves version as `auto` |
| `swordDeposit.tempDir` | `{java.io.tmpdir}/vivo-sword` | Short-lived upload staging |

### Tier 2 — VIVO administrator (Site Admin UI)

Stored in **`sword-endpoints.json`** (v0.1) as an array of endpoint records. Editable at **Site Admin → Site Configuration → SWORD Configuration** (`/admin/sword`).

| Field | Type | Required | Description |
| :---- | :---- | :---- | :---- |
| `id` | UUID | Yes | Stable key |
| `displayName` | string | Yes | Label shown in deposit wizard |
| `enabled` | boolean | Yes | Per-endpoint enable |
| `serviceDocumentUrl` | URL | Yes | SWORD v2 Service Document URL |
| `protocolVersion` | enum | Yes | `v2` (default), `v3` (disabled until implemented), `auto` (future: probe endpoint) |
| `authType` | enum | Yes | `basic` (v0.1 only) |
| `username` | string | Cond. | Basic auth user |
| `password` | secret | Cond. | Encrypted at rest (see D-02) |
| `defaultCollectionHref` | URL | No | Pre-selected collection IRI/href from service document |
| `defaultLicenseUri` | URI | No | Passed in Atom metadata if IR requires (out of scope: validating that the license is accepted in the IR) |
| `slugPrefix` | string | No | Optional SWORD Slug prefix |
| `inProgressByDefault` | boolean | No | SWORD `In-Progress` header default |

**Save / test actions:**

- **Test connection** — GET Service Document, populate collection dropdown, surface HTTP/auth errors to admin (implements BS01 validation steps).  
- **Version auto-detect (future)** — `auto` attempts v2 Service Document first; if v3 signposting is detected, set adapter to v3 when implemented.

### Researcher permissions

| Permission | Who | Purpose |
| :---- | :---- | :---- |
| `EditOwnAccount` | Researcher (existing) | Gate deposit wizard — same as Create-and-Link |
| Self-editing policy | Researcher (existing) | User may only deposit on profiles they are allowed to edit |
| `ManageSwordEndpoints` | VIVO admin (new) | Configure endpoints |

**No new researcher role**; reuse **`EditOwnAccount`** plus existing self-editing configuration. Add **`ManageSwordEndpoints`** for administrators only.

## Reference UI touchpoints (Wilma theme)

| Location | Change |
| :---- | :---- |
| **`individual--foaf-person.ftl`** | When signed in and self-editing, show **Upload Publication** button/link next to existing “Claim publications by DOI/PMID” forms. Links to `/swordDeposit/upload?profileUri={uri}`. |
| **`swordDepositUpload.ftl`** (new) | File input (`accept=".pdf,.zip"`), short help text describing the two accepted formats: a single PDF (no metadata) or a METS-compliant ZIP |
| **`swordDepositConfirm.ftl`** (new) | Enter/confirm title, authors, date, abstract, DOI for the VIVO profile record; select IR endpoint (if multiple enabled) and collection; optional license; submit |
| **`swordDepositResult.ftl`** (new) | Success → link to new publication on profile \+ link to IR item; failure → actionable error (Error workflow is gap G-06) |
| **`admin/swordEndpointList.ftl`** (new) | List/add/edit/delete endpoints |
| **`admin/swordEndpointEdit.ftl`** (new) | Form for Tier 2 fields \+ **Test connection** |

Shared templates under `webapp/templates/freemarker/` may be included from Wilma if other themes later opt in; v0.1 only ships Wilma overrides.

**i18n:** Add keys to `themes/wilma/i18n/` (and optionally `webapp/i18n/`) following existing VIVO property file conventions.

## Uploads, metadata, and packaging

VIVO accepts two upload formats and does not assume a vendor-specific archive layout. Producing a METS package is out of scope; VIVO only accepts it as an upload format.

### Accepted uploads

| Input | Validation | Deposited to IR as |
| :---- | :---- | :---- |
| **`application/pdf`** | Single PDF within size limit | Binary deposit — **no metadata, no packaging** |
| **`application/zip`** | Valid ZIP within size limit; treated as a **METS package** and passed through unmodified (VIVO does not parse, validate, or repackage its contents) | Package deposit with **`Packaging`** set to the METS SIP profile URI (see **SWORD v2 package construction** below) |

**Rejected:** disallowed MIME types; uploads exceeding size limits.

### METS package (ZIP uploads)

A ZIP upload is treated as a **METS-compliant Submission Information Package (SIP)** and deposited to the IR **as-is**. VIVO does **not** parse, validate, or repackage the archive, and this spec does **not** define how the METS document is authored — it only defines that a METS ZIP is an accepted upload format.

- On deposit, the SWORD client sets the **`Packaging`** value to the METS SIP profile URI (see **SWORD v2 package construction** below).  
- Reference profile: [DSpace METS SIP Profile](https://wiki.lyrasis.org/spaces/DSDOC10x/pages/446399329/DSpaceMETSSIPProfile). The feature is designed to be IR-agnostic, but DSpace is the reference/target IR in practice.  
- Producing a valid METS package is the responsibility of the depositor or an upstream tool and is out of scope here.

### Mapping to VIVO RDF (high level)

In v0.1 the researcher enters/confirms this metadata in the deposit wizard for the VIVO profile record; VIVO does not extract metadata from the uploaded PDF or METS ZIP. Reuse Create-and-Link predicate constants where possible:

| Field | VIVO / BIBO target |
| :---- | :---- |
| Title | `rdfs:label`, `bibo:title` |
| Authors | `bibo:authorList` → `foaf:Person` / `vivo:Authorship` nodes |
| Date | `bibo:date` (with Vitro date precision) |
| DOI | `bibo:doi` |
| Abstract | `bibo:abstract` |
| Type | `rdf:type` (`bibo:Article`, `bibo:Book`, …) |
| IR item URL (post-deposit) | `vcard:hasURL` on the publication individual (same as Create-and-Link external URL) |

The full mapping table remains **G-01** for metadata specialists; v0.1 implements a **minimal DC-like subset** sufficient for PoC.

## SWORD v2 package construction

The deposit package is determined by the **upload type** (not by configuration):

| Upload | JavaClient2.0 usage |
| :---- | :---- |
| **PDF** | `Deposit` with the PDF `InputStream`, `mimeType = application/pdf`, optional `slug` and `md5` digest. **No metadata and no packaging** are sent. |
| **METS ZIP** | `Deposit` with the ZIP `InputStream`, `mimeType = application/zip`, and **`setPackaging(...)`** set to the METS SIP profile URI. The archive is sent unmodified. |

Sample fork (mirrors the JavaClient2.0 [METS deposit test](https://github.com/swordapp/JavaClient2.0/blob/0ecebabe136b19948b2108bb1ee8b05e99bff075/src/test/java/org/swordapp/client/test/METSDepositTests.java#L24)):

```java
// DSpace METS SIP packaging identifier, as used by the JavaClient2.0 METS test
private static final String METS = "http://purl.org/net/sword/package/METSDSpaceSIP";

Deposit deposit = new Deposit();
deposit.setFile(parsed.getInputStream());
deposit.setFilename(parsed.getFilename());
deposit.setMd5(parsed.getMd5());               // optional Content-MD5

if (parsed.isPdf()) {
    deposit.setMimeType("application/pdf");
    // PDF path: no metadata, no packaging
} else { // METS ZIP
    deposit.setMimeType("application/zip");
    deposit.setPackaging(METS);
}
```

The `Packaging` URI signals to the IR that the ZIP is a METS SIP. The feature targets any SWORD-compliant IR, but DSpace is the reference implementation, so the DSpace METS SIP identifier (`http://purl.org/net/sword/package/METSDSpaceSIP`, per the [DSpace METS SIP Profile](https://wiki.lyrasis.org/spaces/DSDOC10x/pages/446399329/DSpaceMETSSIPProfile)) is used by default.

Collection **`accept`** and **`acceptPackaging`** from the Service Document drive validation before POST (JavaClient2.0 already warns on mismatch).

**Storage:** Streams only; if spooled to disk, use `swordDeposit.tempDir` and delete in `finally`.

## SWORD v2 protocol surface (implementation mapping)

| Operation | SWORD v2 | Adapter method |
| :---- | :---- | :---- |
| Service Document | `GET` Service-Document IRI | `fetchServiceDocument` |
| List collections | Parse workspaces from Service Document | `listCollections` |
| Deposit | `POST` to Collection IRI | `deposit` → `DepositReceipt` |
| In-progress / complete | `In-Progress` header; Status-IRI in receipt | `pollStatus` (optional v0.1) |
| Auth | HTTP Basic | `AuthCredentials` |

Headers mapped by JavaClient2.0 (parent BS02): **Authorization**, **Content-Type**, **Content-Length**, **Slug**, **In-Progress**, **Digest** (when MD5 supplied).

### In-progress deposits

If the IR returns **`In-Progress: true`**:

- v0.1: Show researcher a **“deposit submitted, pending IR review”** message; still create the VIVO publication stub with Status-IRI stored as a **`vivo:DepositStatus`** annotation (new optional predicate) or admin-visible log only (see D-04).  
- Later: background poller on Status-IRI until `true` → update webpage link when item URI available.

### SWORD v3 forward compatibility

| Concern | v0.1 approach |
| :---- | :---- |
| Adapter selection | `SwordAdapterFactory.forVersion(config.getProtocolVersion())` |
| v3 implementation | `SwordV3ClientAdapter` throws `UnsupportedOperationException` |
| Admin `auto` mode | Attempt v2 Service Document; if failure and v3 client present, try v3 (disabled until client exists) |
| Auth | Document OAuth bearer for v3 in config schema; unused in v0.1 |

## Data flow: happy path

# **![][image2]**

[Link to higher resolution image](https://drive.google.com/file/d/1XPi4vUQTZiOE5YXHcxLp2eyhbZ6YjG8H/view?usp=sharing)

# **Behavior Scenarios** {#behavior-scenarios}

### BS01: Administrator configures a SWORD endpoint in VIVO

| Step | Description |
| :---- | :---- |
| Given | The user has VIVO Administrator access. |
|  | A target IR with SWORD (v2 or v3) enabled exists and credentials are available. |
| When | The administrator navigates to the SWORD configuration screen in the VIVO admin interface. |
|  | The administrator enters the required configuration fields and saves. |
| Then | The VIVO SWORD client retrieves and validates the Service Document from the endpoint URL. |
|  | Available collections in the IR are retrieved and listed for selection as the default. |
|  | The Deposit to Repository option becomes available in the VIVO publication editing interface for users of that VIVO instance. |

### BS02: Researcher selects a publication to deposit

| Step | Description |
| :---- | :---- |
| Given | A researcher is logged into VIVO. |
|  | SWORD deposit is configured and enabled for the VIVO instance. |
|  | No IR record exists yet for the publication being added. |
|  | The IR supports RDF data retrieval. |
|  | The IR supports SWORD v2 Server. |
| When | The researcher navigates to their Individual page and selects “Edit Individual” |
| And | The researcher selects the (new) button “Claim publications by: **SWORD Deposit**” |
| Then | A pop up appears to upload a file. |
| When | The researcher selects a PDF or a METS-compliant ZIP from their computer and clicks upload. |
| Then | A deposit wizard appears for the researcher to enter or confirm the metadata for the VIVO record. |

### BS03: Researcher deposits to a SWORD v2 server

| Step | Description |
| :---- | :---- |
| Given | A researcher is logged into VIVO and has selected a valid PDF or METS-compliant ZIP to deposit. |
|  | SWORD deposit is configured and enabled for the VIVO instance. |
|  | No IR record exists yet for the publication being added. |
|  | The IR supports RDF data retrieval. |
|  | The IR supports SWORD v2 Server. |
| When | The researcher selects the target repository’s collection. |
|  | The researcher reviews metadata, confirms license, and submits. |
| Then | The SWORD client constructs a deposit package in the configured format. |
|  | The package is submitted to the IR SWORD endpoint. |
|  | The IR returns a deposit receipt / status document containing the URI of the new IR item. |
|  | The user is notified of a successful deposit in the GUI. |
|  | The VIVO publication record is updated with the IR item URI as a related/full-text link. |
|  | The deposit is logged with timestamp, depositing user, target collection, status, and IR item URI. |

# **Error Scenarios** {#error-scenarios}

| ID | Condition | User-visible behavior | Log / admin |
| :---- | :---- | :---- | :---- |
| ES01 | Feature disabled or no endpoints | Hide upload button; 404 on direct URL | — |
| ES02 | IR HTTP error / SWORD error document | Message with IR status; no RDF write | Full response body in audit log |
| ES03 | Auth failure (401/403) | “Cannot authenticate to repository — contact administrator” | Never log password |
| ES04 | MIME / packaging rejected | Explain accepted types from collection metadata | — |
| ES05 | Missing title (minimum metadata) | Block at confirm step; prompt manual entry | — |
| ES06 | Deposit fails for any other reason | Gap G-06  | Gap G-06 |

Duplicate deposit (Gap G-03): if profile already has a publication with the same **`bibo:doi`** or same filename \+ date, **warn** and allow override (default recommendation).

# **Open Questions and Specification Gaps** {#open-questions-and-specification-gaps}

| \# | Gap | Description | Owner |
| :---- | :---- | :---- | :---- |
| G-01 | Metadata mapping: VIVO ontology → SWORD/IR | A full field mapping from VIVO's publication ontology (BIBO, VIVO-ISF) to the target IR's required and recommended metadata fields is needed. Special cases: multiple authors (VIVO uses RDF nodes; IR may want a flat list), publication date format, DOI handling, and abstract encoding. **Recommendation: Out of scope** for spec phase. Address during the Implementation phase. | Metadata Specialist / Developer |
| G-02 | Write-back to IR | Options: Deposit only vs update IR with VIVO URI Default recommendation: **Deposit only** | Product Owner |
| G-03 | Duplicate deposit detection | If the same publication already has an IR URI in VIVO, should the system warn before creating a new deposit? Options: warn only, block, or allow override**Recommendation:** If profile already has a publication with the same **`bibo:doi`** or same filename \+ date, **warn** and allow override | Product Owner |
| G-05 | SAF Deposit | Is supporting DSpace SAF a user need? | Product owner |
| G-06 | Actionable error for deposit failure | How are general failure errors communicated with other VIVO tools?How does the user investigate general failure errors? | Product owner |
| G-07 | Retrieving a record and URI via SWORD without depositing | We are planning to add this during the Revision phase, after the basic architecture and data flows are approved  | Consultant team |
| G-08 | Core vs extension module | Options: VIVO `api` package vs separate Vitro extension JAR Default recommendation: **VIVO `api` package** (matches Create-and-Link) | Consultant team |
| G-09 | In-progress UX | Options: Block profile link until complete vs stub record Default recommendation: **Stub with status note**; link when IR URI known | Consultant team |
| G-10 | Package by upload type | **Resolved:** packaging is determined by upload type — a PDF is deposited as binary with no packaging; a METS ZIP is deposited with `Packaging` set to the METS SIP profile URI. | Consultant team |
| G-11 | Endpoint config store | Options: JSON file vs RDF in configuration graph Default recommendation: **JSON file** in v0.1 for simplicity | Consultant team |
| G-12 | Auto protocol version | Options: Admin-only select vs ping-based Default recommendation: **Admin select `v2`** now; schema includes `auto` for later | Consultant team |
| G-13 | PDF metadata | **Resolved:** PDFs are deposited without metadata and VIVO does not extract metadata from the upload; the researcher enters the VIVO profile-record metadata in the wizard. Automated extraction is deferred. | Consultant team |
| G-14 | Multiple IR endpoints | Options: Single vs pick-list in wizard Default recommendation: **Support multiple** enabled endpoints (see  BS01) | Consultant team |

## Suggested epics

Parallelizable units of work for a single delivery:

| Epic | Deliverable | Repos |
| :---- | :---- | :---- |
| **0 — Spike** | JavaClient2.0 dependency proof; manual Service Document \+ deposit against a test IR | `VIVO/api` |
| **1 — Admin config** | Endpoint CRUD, Test connection, Site Admin link, permission | `VIVO/api`, `Vitro/api`, `Vitro/home` |
| **2 — Upload \+ metadata** | Parser (PDF vs METS ZIP classification), Wilma upload/confirm UI, researcher-entered metadata | `VIVO/api`, `VIVO/webapp` |
| **3 — Deposit \+ RDF** | `SwordDepositService`, receipt handling, publication \+ IR link on profile | `VIVO/api` |
| **4 — Hardening** | Error scenarios, duplicate detection, in-progress handling, audit log | `VIVO/api` |
| **5 — SWORD v3** | `SwordV3ClientAdapter`, OAuth, admin auto-detect | `VIVO/api` (future) |
