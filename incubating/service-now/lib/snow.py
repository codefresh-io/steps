import os
import sys
import json
import requests

APP_NAME = "x_409723_codefresh"
DEBUG = True

def getBaseUrl(instance):
    baseUrl = "%s/api/%s" %(instance, APP_NAME);
    if DEBUG:
        print("baseUrl: " + baseUrl)
    return baseUrl

def processResponse(function, response):
    if (response.status_code != 200):
        print(f"{function} failed with code {response.status_code}")
        print(f"Error: {response.text}")

def createChangeRequest(user, password, baseUrl, title, description):
    crBody= {
        "cf_build_id": os.getenv('CF_BUILD_ID'), 
        "title":  title,
        "description" : description
    }
    url="%s/codefresh/createChange" % (baseUrl)

    if DEBUG:
        print(f"Entering createChangeRequest:")
        print(f"URL: {url}")
        print(f"User: {user}")
        print(f"Body: {crBody}")

    resp=requests.post(url,
        json = crBody,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processResponse(function="createChangeRequest", response=resp)

def main():
    global DEBUG

    ACTION = os.getenv('action', 'createCR').lower()
    USER = os.getenv('SN_USER')
    PASSWORD = os.getenv('SN_PASSWORD')
    INSTANCE = os.getenv('SN_INSTANCE')
    #DEBUG = True if os.getenv('debug', "false").lower == "true" else False
    TITLE = os.getenv('action', 'Change Request created by Codefresh')
    DESCRIPTION = os.getenv('description', '')

    if ACTION == "createcr":
        createChangeRequest(user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            title=TITLE,
            description=DESCRIPTION)
if __name__ == "__main__":
    main()
