import os
import sys
import json
import requests

DEBUG = True
API_NAMESPACE=409723
env_file_path = "/meta/env_vars_to_export"

def getBaseUrl(instance):
    baseUrl = "%s/api" %(instance);
    if DEBUG:
        print("baseUrl: " + baseUrl)
    return baseUrl

def processCallbackResponse(response):
    print("Processing answer from CR creation REST call")
    print("Callback returned code %s" % (response.status_code))
    if (response.status_code != 200 and response.status_code != 201):
        print("Callback creation failed with code %s" % (response.status_code))
        print("Error: " + response.text)
        return response.status_code

    print("Callback creation successful")


def processChangeRequestResponse(response):

    print("Processing answer from CR creation REST call")
    print("Change Request returned code %s" % (response.status_code))
    if (response.status_code != 200 and response.status_code != 201):
        print("Change Request creation failed with code %s" % (response.status_code))
        print("Error: " + response.text)
        return response.status_code

    print("Change Request creation successful")
    data=response.json() # json.loads(response.text)
    CR_NUMBER=data["result"]["number"]
    CR_SYSID=data["result"]["sys_id"]
    FULL_JSON=json.dumps(data, indent=2)
    print(f"Change Request Number: {CR_NUMBER}")
    print(f"Change Request sys_id: {CR_SYSID}")
    print("Change Request full answer:\n" + FULL_JSON)

    if os.path.exists(env_file_path):
        env_file = open(env_file_path, "a")
        env_file.write(f"CR_NUMBER={CR_NUMBER}\n")
        env_file.write(f"CR_SYS_ID={CR_SYSID}\n")
        env_file.write("CR_FULL_JSON=/codefresh/volume/servicenow-cr.json\n")
        env_file.close()

        json_file=open("/codefresh/volume/servicenow-cr.json", "w")
        json_file.write(FULL_JSON)
        json_file.close()

#
# Call SNow REST API to create a new Change Request
# Fields required are past in the data
def createChangeRequest(user, password, baseUrl, title, data, description):

    if DEBUG:
        print("Entering createChangeRequest:")
        print("Body: " + data)

    if (bool(data)):
        crBody=json.loads(data)
    else:
        crBody= {}

    crBody["cf_build_id"] = os.getenv('CF_BUILD_ID')


    url="%s/now/table/change_request" % (baseUrl)

    if DEBUG:
        print(f"Entering createChangeRequest:")
        print(f"URL: {url}")
        print(f"User: {user}")
        print(f"Body: {crBody}")

    resp=requests.post(url,
        json = crBody,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processChangeRequestResponse(response=resp)

# Use rest API to call scripted REST API to start a flow that will wait for CR
# to be approved or rejected, then callback Codefreh to approve/deny pipeline
#
def callback(user, password, baseUrl, number, cf_build_id, "token"):

    if DEBUG:
        print("Entering callback:")
        print("CR Number: " + number)
        print("CF Build ID: " + cf_build_id)

    url="%s/%s/codefresh/callback" % (baseUrl, API_NAMESPACE)

    resp=requests.post(url,
        json = {
            "number": {number},
            "cf_build_id": {cf_build_id}},
            "cf_token": {token}
            "cf_url": os.getenv("CF_URL")
        },
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processCallbackResponse(response=resp)

def main():
    global DEBUG

    ACTION = os.getenv('action', 'createCR').lower()
    USER = os.getenv('SN_USER')
    PASSWORD = os.getenv('SN_PASSWORD')
    INSTANCE = os.getenv('SN_INSTANCE')
    DATA     = os.getenv('data')

    #DEBUG = True if os.getenv('debug', "false").lower == "true" else False
    TITLE = os.getenv('title', 'Change Request created by Codefresh')
    DESCRIPTION = os.getenv('description', '')

    if ACTION == "createcr":
        createChangeRequest(user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            title=TITLE,
            data=DATA,
            description=DESCRIPTION)
    elif ACTION == "callback":
        CR_NUMBER = os.getenv('CR_NUMBER');
        CF_BUILDID = os.gentenv('CF_BUILD_ID')
        createChangeRequest(user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            number=CR_NUMBER)

    else:
        sys.exit(f"Unknown action: {ACTION}")


if __name__ == "__main__":
    main()
