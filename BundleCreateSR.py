import requests
import json

"""

version: 0.1
Date: 15-3-2022
Author:  Danny Ruttle

What this code does:

Resource manipulation to RESTful FHIR APIs


To Do:
1. Add class to update resources 
2. Read message from text file
2.a. Decide how to handle booleans
3. Add config file
4. Add get functionality
"""

class FHIRBundleCreate(object):

    def __init__(self):
        self.baseURL = "http://hapi.fhir.org/baseR4/"

    def run(self, resource):
        payload = ""
        resToCall = ""
        if resource == "SRPayload":
            config = self.SRPayload()
            resToCall = config[0]
            payload = config[1]
        elif resource == "PractPayload":
            config = self.PractPayload()
            resToCall = config[0]
            payload = config[1]
        elif resource == "PatPayload":
            config = self.PatPayload()
            resToCall = config[0]
            payload = config[1]

        url = "/".join((self.baseURL, resToCall))
        headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json',
            'If-None-Exist': '',

        }
        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.headers)
        print(response.status_code)
        print(response.reason)
        print(response.text)

    def PatPayload(self):

        return ["Patient", json.dumps(
            {
                "resourceType": "Patient",
                "id": "genetics-example1",
                "meta": {
                    "lastUpdated": "2012-05-29T23:45:32Z"
                },
                "text": {
                    "status": "generated",
                    "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Everywoman, Eve. SSN:\n      444222222</div>"
                },
                "identifier": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                    "code": "SS"
                                }
                            ]
                        },
                        "system": "http://hl7.org/fhir/sid/us-ssn",
                        "value": "444222222"
                    }
                ],
                "active": "true",
                "name": [
                    {
                        "use": "official",
                        "family": "Everywoman",
                        "given": [
                            "Eve"
                        ]
                    }
                ],
                "telecom": [
                    {
                        "system": "phone",
                        "value": "555-555-2003",
                        "use": "work"
                    }
                ],
                "gender": "female",
                "birthDate": "1973-05-31",
                "address": [
                    {
                        "use": "home",
                        "line": [
                            "2222 Home Street"
                        ]
                    }
                ],
                #"managingOrganization": {
                #    "reference": "Organization/hl7"
                #}
            })
                ]

    def PractPayload(self):

        return ["Practitioner", json.dumps(
            {
                  "resourceType": "Practitioner",
                  "id": "genomicsprac01",
                  "text": {
                    "status": "generated",
                    "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><b>Generated Narrative</b></p><div style=\"display: inline-block; background-color: #d9e0e7; padding: 6px; margin: 4px; border: 1px solid #8da1b4; border-radius: 5px; line-height: 60%\"><p style=\"margin-bottom: 0px\">Resource &quot;f201&quot; </p></div><p><b>identifier</b>: UZI-nummer: 12345678901 (OFFICIAL)</p><p><b>active</b>: true</p><p><b>name</b>: Dokter Bronsig(OFFICIAL)</p><p><b>telecom</b>: <a href=\"tel:+31715269111\">+31715269111</a></p><p><b>address</b>: Walvisbaai 3 C4 - Automatisering Den helder 2333ZA NLD (WORK)</p><p><b>gender</b>: male</p><p><b>birthDate</b>: 1956-12-24</p><h3>Qualifications</h3><table class=\"grid\"><tr><td>-</td><td><b>Code</b></td></tr><tr><td>*</td><td>Pulmonologist <span style=\"background: LightGoldenRodYellow; margin: 4px; border: 1px solid khaki\"> (<a href=\"https://browser.ihtsdotools.org/\">SNOMED CT</a>#41672002)</span></td></tr></table></div>"
                  },
                  "identifier": [
                    {
                      "use": "official",
                      "type": {
                        "text": "UZI-nummer"
                      },
                      "system": "urn:oid:2.16.528.1.1007.3.1",
                      "value": "12345678901"
                    }
                  ],
                  "active": "true",
                  "name": [
                    {
                      "use": "official",
                      "text": "Dokter Bronsig",
                      "family": "Bronsig",
                      "given": [
                        "Arend"
                      ],
                      "prefix": [
                        "Dr."
                      ]
                    }
                  ],
                  "telecom": [
                    {
                      "system": "phone",
                      "value": "+31715269111",
                      "use": "work"
                    }
                  ],
                  "address": [
                    {
                      "use": "work",
                      "line": [
                        "Walvisbaai 3",
                        "C4 - Automatisering"
                      ],
                      "city": "Den helder",
                      "postalCode": "2333ZA",
                      "country": "NLD"
                    }
                  ],
                  "gender": "male",
                  "birthDate": "1956-12-24",
                  "qualification": [
                    {
                      "code": {
                        "coding": [
                          {
                            "system": "http://snomed.info/sct",
                            "code": "41672002",
                            "display": "Pulmonologist"
                          }
                        ]
                      }
                    }
                  ]
                })
                ]

    def SRPayload(self):
        return ["", json.dumps(

            {
                "resourceType": "Bundle",
                #"type": "transaction",
                "entry": [
            {
                "resource" : {
            "resourceType": "ServiceRequest",
            "id": "209b1587-251d-4ac8-9d6d-35660e9476fb",
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
            "subject": {
                "reference": "Patient/899962"
            },
            "authoredOn": "2016-10-10T15:00:00-07:00",
            "requester": {
                "reference": "Practitioner/12345"
            }
                },

        "request": {
                   "method": "PUT",
                   "url": "ServiceRequest"
               }
            }

                ]

        }

        )]

class FHIRUpdate(object):
    pass

def __init__(self):
    pass

if __name__ == "__main__":
    Fres = FHIRBundleCreate()
    Fres.run("SRPayload")
