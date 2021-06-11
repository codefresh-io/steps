import os
import sys
import json
import requests

DEBUG = True
API_NAMESPACE=409723

def getBaseUrl(instance):
    baseUrl = "%s/api" %(instance);
    if DEBUG:
        print("baseUrl: " + baseUrl)
    return baseUrl

def processResponse(function, response):
    status = 'OK'
    env_file_path = "/meta/env_vars_to_export"

    if (response.status_code != 200):
        print(f"{function} failed with code {response.status_code}")
        print(f"Error: {response.text}")
        status= 'ERROR'
        return response.status_code
    else:
        print(f"Change Request Number: {response.body.number})
        print(f"Change Request Number: {response.body.sys_id})
        print(f"Change Request full answer: \n{response.body})

    if not os.path.exists(env_file_path):
        print(f"Create Change Request status is \n'{status}'")
    else:
        env_file = open(env_file_path, "a")
        qualitygates_status_json_file_path = f"/codefresh/volume/servicenow-cr.json"
        env_file.write("CR_NUMBER=" +response.body.number + "\n")
        env_file.write("CR_SYS_ID=" +response.body.sys_id + "\n)
        env_file.write("CR_FULL_JSON=/codefresh/volume/servicenow-cr.json"+ "\n)  
        env_file.close()

        json_file=open("/codefresh/volume/servicenow-cr.json", "w")
        json_file.write(response.body)
        json_file.close()

def createChangeRequest(user, password, baseUrl, endpoint, title, data, description):

    if DEBUG:
        print(f"Entering createChangeRequest:")
        print(f"Body: {data}")

    if (bool(data)):
        crBody=json.loads(data)
    else:
        crBody= {}

    crBody["cf_build_id"] = os.getenv('CF_BUILD_ID')


    url="%s/now/table/change_request" % (baseUrl, endpoint)

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
    ENDPOINT = os.getenv('endpoint')
    BODY     = os.getenv('body')

    #DEBUG = True if os.getenv('debug', "false").lower == "true" else False
    TITLE = os.getenv('title', 'Change Request created by Codefresh')
    DESCRIPTION = os.getenv('description', '')

    if ACTION == "createcr":
        createChangeRequest(user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            endpoint=ENDPOINT,
            title=TITLE,
            body=BODY,
            description=DESCRIPTION)
if __name__ == "__main__":
    main()
