import json, sys, os
import cfg_parser
import requests
from datetime import datetime

"""

version: 0.1
Date: 30-3-2022
Author:  Danny Ruttle

What this code does:
1. Creates and updates FHIR resources
2. Returns the server id for each FHIR resource created or updated and logs it

To Do:
1. Add commandline parameters/args to allow the code to be run from the command line.  Currently the code is run by editing the __main__ method directly.
 
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
"""

# used to map Resources to to class methods
ResourceDict = {"ServiceRequest" : "SRPayload",
                    "Patient" : "PatientPayload",
                    "Specimen" : "SpecimenPayload",
                    "Practitioner" : "PractitionerPayload",
                    "ReqOrganization" : "ReqOrgPayload" }

def Create(Resource):
    Fres = FHIRManage()
    ResourceToCreate = Resource
    cp = Fres.readConfig("C:\\Users\\Danny\\PycharmProjects\\Genomics\\SRconfig.txt")
    Response = Fres.run(ResourceDict[Resource], 'POST')
    ResDict = json.loads(Response)
    id = ResDict["id"]  # resource ID on the server

    # now retrieve the content
    Fget = FHIRGet()
    Response = Fget.getResource(cp["BaseURL"], ResourceToCreate, id)
    FHIRlog = WriteLog().log("GET response %s: %s\n" % (ResourceToCreate, id))
    print("\n###GET RESPONSE for POST ###:\n%s" % Response)

def Update(Resource, id):
    Fres = FHIRManage()
    ResourceToCreate = Resource
    cp = Fres.readConfig("C:\\Users\\Danny\\PycharmProjects\\Genomics\\SRconfig.txt")
    Response = Fres.run(ResourceDict[Resource], 'PUT', id)
    ResDict = json.loads(Response)
    id = ResDict["id"]  # resource ID on the server

    # now retrieve the content
    Fget = FHIRGet()
    Response = Fget.getResource(cp["BaseURL"], ResourceToCreate, id)
    FHIRlog = WriteLog().log("GET response %s: %s\n" % (ResourceToCreate, id))
    print("\n###GET RESPONSE for PUT ###:\n%s" % Response)


class WriteLog(object):
    def log(self, text):
        fh = open("C:\\Users\\Danny\\PycharmProjects\\Genomics\\outputs\\FHIRlog.txt","a")
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        fh.write("%s: %s" % (date_time, text))
        fh.close()


class FHIRManage(object):

    def __init__(self):
        self.baseURL = "" #"https://server.fire.ly"
        self.patient = "{}"
        self.practitioner = "{}"
        self.specimen = "{}"
        self.configDict = {}


    def readConfig(self, config):
        """

        :param config: string - full path to config file with FHIR resources listed
        :return: None
        """
        cp = cfg_parser.config_parser()
        self.configDict = cp.read(config)

        self.baseURL = self.configDict.setdefault("BaseURL", "no baseURL")

        # get source json for each resource when creating
        self.patient = self.configDict.setdefault("Patient",{})
        self.patient = self.openFile(self.patient)

        self.practitioner = self.configDict.setdefault("Practitioner",{})
        self.practitioner = self.openFile(self.practitioner)

        self.specimen = self.configDict.setdefault("Specimen",{})
        self.specimen = self.openFile(self.specimen)

        self.organization = self.configDict.setdefault("Organization",{})
        self.organization = self.openFile(self.organization)

        self.requestOrganization = self.configDict.setdefault("RequestOrganization",{})
        self.requestOrganization = self.openFile(self.requestOrganization)

        # get id/refs for dependent resources
        self.patientRef = self.configDict.setdefault("patientRef","")
        self.patientRef = eval(self.patientRef)

        self.practitionerRef = self.configDict.setdefault("practitionerRef", "")
        self.practitionerRef = eval(self.practitionerRef)

        self.specimenRef = self.configDict.setdefault("specimenRef", "")
        self.specimenRef = eval(self.specimenRef)

        self.manOrgRef = self.configDict.setdefault("manOrgRef", "")
        self.manOrgRef = eval(self.manOrgRef)

        self.reqOrgRef = self.configDict.setdefault("reqOrgRef", "")
        self.reqOrgRef = eval(self.reqOrgRef)

        # add other dependencies here

        return self.configDict


    def openFile(self, file):
        if file != {}:
            f = open(file, "r")
            try:
                outFile = json.load(f)
            except json.decoder.JSONDecodeError:
                print("\nInvalid json in file: %s" % file)
                sys.exit()
            return outFile


    def run(self, resource, method, id=None):
        """

        :param resource: Type of FHIR Resource
        :param method: HTTP METHOD
        :param id: optional - only required for PUT/updates
        :return:
        """
        # Map unquoted booleans to strings
        true = "true"
        false = "false"
        payload = ""
        resToCall = ""
        if resource == "SRPayload":
            config = self.SRPayload()
            resToCall = config[0]
            payload = config[1]
        elif resource == "PatientPayload":
            config = self.PatientPayload()
            resToCall = config[0]
            payload = config[1]
        elif resource == "ManageOrgPayload":
            config = self.ManageOrgPayload()
            resToCall = config[0]
            payload = config[1]
        elif resource == "ReqOrgPayload":
            config = self.ReqOrgPayload()
            resToCall = config[0]
            payload = config[1]
        elif resource == "PractitionerPayload":
            config = self.PractitionerPayload()
            resToCall = config[0]
            payload = config[1]
        elif resource == "SpecimenPayload":
            config = self.SpecimenPayload()
            resToCall = config[0]
            payload = config[1]

        print("\n### %s Payload ###: %s" % (method, payload))

        #HAPI approach
        if self.baseURL == "http://hapi.fhir.org/baseR4":
            try:
                # for PUT/updates which will have an id
                url = "/".join((self.baseURL, resToCall,id))
            except:
                # fall back to url without an id for POST/create
                url = "/".join((self.baseURL, resToCall))
        elif self.baseURL == "https://server.fire.ly":
            # firely approach
            url = "/".join((self.baseURL, resToCall))
            if id:
                url = "%s?id=%s" % (url, id)
        elif self.baseURL == "https://simplifier.net/validate?scope=hl7.fhir.r4.core@4.0.1":
            url = self.baseURL

        print("\n### URL ###: %s" % url)

        headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        }
        print("\n### %s headers: %s" % (method, headers))
        response = requests.request(method, url, headers=headers, data=payload)

        print("\n### POST RESPONSE headers ###: %s" % response.headers)
        print("\n### POST RESPONSE status code ###: %s" % response.status_code)
        print("\n### POST RESPONSE reason ###: %s" % response.reason)
        print("\n### POST RESPONSE text ###: %s" % response.text)
        return response.text

    def PatientPayload(self):

        return ["Patient", json.dumps(self.patient)]

    def PractitionerPayload(self):

        return ["Practitioner", json.dumps(self.practitioner)]

    def ManageOrgPayload(self):

        return ["Organization", json.dumps(self.organization)]

    def ReqOrgPayload(self):

        return ["Organization", json.dumps(self.requestOrganization)]

    def SpecimenPayload(self):

        return ["Specimen", json.dumps(self.specimen)]


    def SRPayload(self):
        return ["ServiceRequest", json.dumps({
            "resourceType": "ServiceRequest",
            "id": "9b79fd8c-2955-453f-8007-f8b1c7b9596d",
            "text": {
                "status": "generated",
                "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><b>Generated Narrative with Details</b></p><p><b>id</b>: example-pgx</p><p><b>status</b>: active</p><p><b>intent</b>: original-order</p><p><b>code</b>: CYP2D6 gene targeted mutation analysis <span>(Details : {LOINC code '47403-1' = 'CYP2D6 gene mutation analysis in Blood or Tissue by Molecular genetics method Narrative', given as 'CYP2D6 gene targeted mutation analysis'})</span></p><p><b>subject</b>: <a>Patient/899962</a></p><p><b>authoredOn</b>: 10/10/2016 3:00:00 PM</p><p><b>requester</b>: <a>Practitioner/12345</a></p></div>"
            },
            "identifier" : [
                {
                    "value": "45678"
                },
                {
                "assigner" : self.reqOrgRef,
                }
            ],

            "status": "active",
            "priority": "routine",
            "intent": "original-order",
            "code": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "76164006",
                            "display": "Biopsy of colon (procedure)"
                        }
                    ],
                    "text": "Biopsy of colon"
                },
            # Patient
            "subject": self.patientRef,
            "authoredOn": "2022-03-30T15:00:00-07:00",
            # Practitioner
            "requester": self.practitionerRef,
            # Specimen
            "specimen": self.specimenRef
        })
        ]


class FHIRGet(object):

    def getResource(self, baseURL, ResType, id):
        url = "/".join((baseURL, ResType, id))
        print("\n### GET URL ###: %s" % url)
        headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        }
        response = requests.request("GET", url, headers=headers)
        return response.text

if __name__ == "__main__":

    #Update("Patient","2866353")
    #Update("Specimen", "2873554")
    #Create("Practitioner")
    #Create("ReqOrganization")
    Create("ServiceRequest")
