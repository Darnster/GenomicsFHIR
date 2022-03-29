import json, sys, os
import cfg_parser
import requests
from datetime import datetime

"""

version: 0.1
Date: 29-3-2022
Author:  Danny Ruttle

What this code does:
1. Creates FHIR reseources
2. Returns the server id for each resource created and log it


To Do:
1. Add class to update resources 
2.a. Decide how to handle booleans
3. Add config file
4. Add get functionality
"""


def CreateSR():
    Fres = FHIRCreate()
    ResourceToCreate = "ServiceRequest"
    cp = Fres.readConfig("C:\\Users\\Danny\\PycharmProjects\\Genomics\\SRconfig.txt")
    Response = Fres.run("SRPayload")
    ResDict = json.loads(Response)
    id = ResDict["id"]  # resource ID on the server

    # now retrieve the content
    Fget = FHIRGet()
    Response = Fget.getResource(cp["BaseURL"], ResourceToCreate, id)
    FHIRlog = WriteLog().log("GET response %s: %s\n" % (ResourceToCreate, id))


def CreatePatient():
    Fres = FHIRCreate()
    ResourceToCreate = "Patient"
    cp = Fres.readConfig("C:\\Users\\Danny\\PycharmProjects\\Genomics\\SRconfig.txt")
    Response = Fres.run("PatientPayload")
    ResDict = json.loads(Response)
    id = ResDict["id"]  # resource ID on the server

    # now retrieve the content
    Fget = FHIRGet()
    Response = Fget.getResource(cp["BaseURL"], ResourceToCreate, id)
    FHIRlog = WriteLog().log("GET response %s: %s\n" % (ResourceToCreate, id))



class WriteLog(object):
    def log(self, text):
        fh = open("C:\\Users\\Danny\\PycharmProjects\\Genomics\\outputs\\FHIRlog.txt","a")
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        fh.write("%s: %s" % (date_time, text))
        fh.close()

class FHIRCreate(object):

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

        # get source json for each resource when creating
        self.patient = self.configDict.setdefault("Patient",{})
        self.patient = self.openFile(self.patient)
        self.practitioner = self.configDict.setdefault("Practitioner",{})
        self.practitioner = self.openFile(self.practitioner)
        self.specimen = self.configDict.setdefault("Specimen",{})
        self.specimen = self.openFile(self.specimen)
        self.organization = self.configDict.setdefault("Organization",{})
        self.organization = self.openFile(self.organization)
        self.baseURL = self.configDict.setdefault("BaseURL","no baseURL")

        # get id/refs for dependent resources
        self.patientRef = self.configDict.setdefault("patientRef",{})
        self.patientRef = self.openFile(self.patientRef)

        print(self.patientRef)

        return self.configDict

    def openFile(self, file):
        if file != {}:
            f = open(file, "r")
            outFile = json.load(f)
            return outFile


    def run(self, resource):
        """

        :param resource:
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
            config = self.manageOrgPayload()
            resToCall = config[0]
            payload = config[1]
        elif resource == "PractitionerPayload":
            config = self.PractitionerPayload()
            resToCall = config[0]
            payload = config[1]

        print(payload)
        #sys.exit()
        url = "/".join((self.baseURL, resToCall))
        print(url)
        headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json',
            'If-None-Exist': ''
        }
        print(headers)
        response = requests.request("POST", url, headers=headers, data=payload)

        print("POST RESPONSE headers: %s" % response.headers)
        print("POST RESPONSE status code: %s" % response.status_code)
        print("POST RESPONSE reason: %s" % response.reason)
        print("POST RESPONSE text: %s" % response.text)
        return response.text

    def PatientPayload(self):

        return ["Patient", json.dumps(self.patient)]

    def PractitionerPayload(self):

        return ["Practitioner", json.dumps(self.practitioner)]

    def manageOrgPayload(self):

        return ["Organization", json.dumps(self.organization)]

    def SRPayload(self):
        return ["ServiceRequest", json.dumps({
            "resourceType": "ServiceRequest",
            "id": "309b1587-251d-4ac8-9d6d-35660e9476fb",
            "text": {
                "status": "generated",
                "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><b>Generated Narrative with Details</b></p><p><b>id</b>: example-pgx</p><p><b>status</b>: active</p><p><b>intent</b>: original-order</p><p><b>code</b>: CYP2D6 gene targeted mutation analysis <span>(Details : {LOINC code '47403-1' = 'CYP2D6 gene mutation analysis in Blood or Tissue by Molecular genetics method Narrative', given as 'CYP2D6 gene targeted mutation analysis'})</span></p><p><b>subject</b>: <a>Patient/899962</a></p><p><b>authoredOn</b>: 10/10/2016 3:00:00 PM</p><p><b>requester</b>: <a>Practitioner/12345</a></p></div>"
            },
            "status": "active",
            "priority": "routine",
            "intent": "original-order",
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "47403-1",
                        "display": "CYP2D6 gene targeted mutation analysis"
                    }
                ]
            },
            # Patient
            "subject": self.patientRef,
            #"authoredOn": "2016-10-10T15:00:00-07:00",
            # Practitioner
            #"requester": self.practitionerRef,
            # Specimen
            #"specimen": self.specimenRef
        })
        ]


class FHIRGet(object):

    def getResource(self, baseURL, ResType, id):
        url = "/".join((baseURL, ResType, id))
        print(url)
        headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json',
            'If-None-Exist': ''
        }
        response = requests.request("GET", url, headers=headers)
        return response.text


class FHIRUpdate(object):
    pass

def __init__(self):
    pass

if __name__ == "__main__":
    CreateSR()

    # manageOrgPayload
    # PractPayload
    # SRPayload
    # SpecimenPayload - to do