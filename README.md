# GenomicsFHIR

What this code does:
1. Creates and updates FHIR resources
2. Returns the server id for each FHIR resource created or updated and logs it

ChangeLog:
06-04-2022 - added capability to support Create/Update of Requesting Organization

To Do:
1. Add commandline parameters/args to allow the code to be run from the command line.  Currently the code is run by editing the __main__ method directly.
2. Fix bug for GET request within RequestingOrganization Creation
3. Simplify configuration for adding new FHIR resources - currently this requires a change in 3 places....
 
Guidance:
This software has been created to build up a set of resource dependencies/references to support testing of complex pathology/genomics scenarios.
Resources such as the pathology ServiceRequest include references to Patient, Specimen, Practitioner, etc which in return may have references to other Resources such as
Organization and Location Resources, etc.

The initial approach for supporting Genomics work involved "contained resources" whereby the details of the Patient, Specimen, etc are provided in a single large message, 
however this has a number of issues:

  1. When querying the Resource from the FHIR server only the business identifier for the contained resource is returned (e.g. NHS/patient idintifier for a Patient).
  2. The FHIR server doesn't issue its own IDs to contained resources and without IDs it isn't possible to retrieve the whole detail for Patient, Specimen, etc.

The approach requires that all dependencies that can be referenced by an ID are identified up front.  This allows all POSTed Resources to be uploaded into the FHIR
server.  The IDs issued by the FHIR server need to be saved, so they can be used for update and retrieval during the testing of information flows.

The IDs need to be maintained in order to support repeatability of tests with different content.  Once the server issues an ID these need to be included in the Resources 
themselves, e.g.

  {"resourceType": "Patient",
  "id": "2866353", .....}

If new Resources are identified which the software doesn't support is is straightforward to add them to the code and map them into the processing.

The referenced Resources are stored externally to the code as valid json files in an "inputs" directory and there must be a corresponding entry in the config file 
for each one, e.g.

  Patient:C:\\Users\\Danny\\PycharmProjects\\Genomics\\inputs\\Patient.json

Note that when updating an external Resource on the FHIR server, the ID in the raw json file MUST match the ID passed in to the Update() method.

ID Snippets:

The ServiceRequest (and later DiagnosticReport) Resource is stored in the Python code itself as a Python dictionary.  There are placeholders in the dictionary for the
ID snippets that reference the IDs to be used during testing.  The snippets are also stored in config, e.g.

  patientRef:{"reference": "Patient/2866353"}
  
In the code the references are assigned to variables referenced from the dictionary within the Python code, as shown below:
  
....},
            # Patient
            "subject": self.patientRef,
            "authoredOn": "2022-03-30T15:00:00-07:00",
            # Practitioner
            "requester": self.practitionerRef,
            # Specimen
            "specimen": self.specimenRef
        }....
