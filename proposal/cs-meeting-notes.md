# CollectionSpace Enhancement Requirements

# 2026-04-03

Jess/Kristina

* For now:  
  * OAI-PMH in Publish To: Field  
  * Records opted in on an individual level  
  * Include documentation specs for bulk updates  
* Data updates: Jobs can be run on a search of records  
  * Data update to turn on OAI publishing  
* How should we use OAI-PMH sets in this feature?  
  * Is “Sponsor” the harvesting repository?  
    * Free text field that you can enter into a resource record  
    * Probably matching to a donor  
* Core of CSpace is Nuxeo \- data handling  
  * Idea to add a data job that runs on a schedule within CSpace with a separate data store  
  * CSpace uses ElasticSearch  
  * API: Return a record,   
    * ASpace: (API call class defines the set, retrieves records, apply mapper class like DC, etc, return data)  
    * CSpace: Job call to prepare the set of records to be retrieved by the OAI request  
    * OAI PMH spec has its own link structure / syntax / request format, it’s different from the CSpace API.  
    * Base URL of OAI endpoint would be API call, maybe?  
    * CSpace Gateway \- another way of interacting with CSpace from outside \- enables the public browser  
* Mapping inside the application  
  * DC mapping not user configurable  
  * Minimum specification  
* IF you want OAI to be available, do a search that includes what you want, paste the search query into a field  
* Reports create external files that require you to write an SQL query to get back into CSpace  
* Ensuring that objects deleted from CSpace are also deleted in the discovery service  
  * Deleted Set  
  * Update Set  
  * Look at how much of this is default with OAI Endpoint  
  * The mapped records should pull created and updated dates of the record  
    * Up to the harvester how to harvest the data  
    * Deletes are still tough \- 2 types of Deletes in CSpace  
      * Soft delete, could return a deleted status in the record  
      * Real delete, everything is gone including the Identifier  
      * Uncheck Publish To:  
    * Sample documentation [https://docs.archivesspace.org/architecture/oai-pmh/](https://docs.archivesspace.org/architecture/oai-pmh/)   
    * Diff list identifiers to see what has been deleted  
* Search interface clarification  
  * Build and share as a proof of concept on GitHub, with robust documentation about how to implement at your institution  
* Linked to the wrong thing for C3 below. Correct link: [https://github.com/lyrasisorghome/InteroperabilityProject/issues/51](https://github.com/lyrasisorghome/InteroperabilityProject/issues/51)   
  * Expectations for when vocabulary terms don’t exactly match  
  * Could meet with prior Litchfield Historical Society dev consultant  
* CSpace needs to be able to export data in a variety of formats  
  * Once you start to think about integrations, it gets clunky  
  * But lots of requests from users to get all the data  
  * If Lyrasis offers as a service, we would be able to provide something useful for people. But just data exports not as useful \- users need more support.

# 2026-03-27

CSpace program team

* User stories approved in Feb:  
  1. As an administrator of CollectionSpace I would like to make my CollectionSpace records and digital content available to my institution’s OAI-PMH compliant discovery system.  
  2. As an administrator of both CollectionSpace and ArchivesSpace, I want to offer a single search interface for data from both so that users can search for more historical collections in one place.  
  3. As a user of a shared discovery platform containing records from both CollectionSpace and ArchivesSpace, I want to conduct a search and bring up relevant records from each.   
  4. As an institution interested in adopting a Lyrasis CST I would like to know how to integrate it with local systems.  
* Draft behavior docs:  
  1. [C1](https://github.com/lyrasisorghome/InteroperabilityProject/issues/46)  
     * Where in the staff interface should we include the interface for configuring OAI-PMH?  
       * Tools \+1  
       * Could go in admin  
       * What would staff configure:  
         * Whether OAI-PMH is enabled or not; turn of certain fields?  
         * Look at ASpace example: Post screenshots to this GH issue  
     * To configure: Are there other permissions required besides Exports? Is there a new permission required?[CSpace Roles and Permissions.png](https://drive.google.com/file/d/1C6XzUB71VGEnYuKPDCIaHkN-hXMte5h-/view?usp=sharing)	  
     * Should I follow the [OAI-PMH repository guidelines](https://www.openarchives.org/OAI/2.0/guidelines-repository.htm) to define data requirements? Or is there more from the CollectionSpace side that I need to know/understand? Or something about the user base that folks would want certain data included that is beyond the basic repo guidelines?  
       * Draft Dublin Core mapping to be used [https://collectionspace.atlassian.net/wiki/spaces/CPD/pages/4081451009/Open+for+Internal+Comment+Dublin+Core+Mapping](https://collectionspace.atlassian.net/wiki/spaces/CPD/pages/4081451009/Open+for+Internal+Comment+Dublin+Core+Mapping)  
       * Should support what is published now in the public browser  
       * You should support DC but can support other profiles. What namespace would we use to map fields outside of DC mapping?  
       * There is an xml export \- could remove fields from this / configuration  
     * Do we need a new option under “Publish to:” for OAI-PMH?  
       * Not a place to define/allow sets  
       *   
     * Frequency: Is there a limit to how often records could be harvested?  
       * Include this as a requirement; no specific numbers yet  
       * How frequently data available for harvesting gets updated  
       * Base requirements on repository implementation guidelines  
       * Part of this is how the harvester set up \- depends on harvester. But when available for updating \- also a distinction.  
     * Data limits: Is there a limit to how much data can be harvested?  
       * Does OAI-PMH enable harvesting of actual digital objects, or just the metadata around them?  
         * Published Thumbnails (links to them)  
     * Review [minimal repository implementation](https://www.openarchives.org/OAI/2.0/guidelines-repository.htm):  
       * Dublin Core  
       * \<about\> containers  
       * Defining sets  
         * Objects to different repositories  
         * Tie a query to a set?  
         * Based on Object Profiles?  
         * Probably out of scope / not a need for this part of the project. Could be a phase II. Publish To: can define sets for Phase I.  
       * Response Compression  
       * Flow control  
       * Jess will meet with Kristina to talk through this  
     * Other OAI-PMH concerns:  
       * Datestamp granularity  
       * Incomplete-List responses and the user of resumptionToken elements  
     * Requirements for ETL Process  
       * Pulling only changed records; remove IDs that have been removed  
       * Support reporting with a Deleted status  
       * How to handle incomplete requests  
       * Not real-time  
       * Harvest should not impact the system \- data exported to a different index on a regular basis  
  2. [C2](https://github.com/lyrasisorghome/InteroperabilityProject/issues/47)  
     * Should I write a scenario that connects CSpace and ASpace to [archlight](https://arclight.sites.stanford.edu/) or [blacklight](https://projectblacklight.org/)?  
  3. [C3](https://github.com/lyrasisorghome/InteroperabilityProject/issues/50)  
     * Do we need a new Publish To: option for this?  
     * Looking into solr semantic search and the requirements for using it  
  4. C4 \- work will begin in April on C4