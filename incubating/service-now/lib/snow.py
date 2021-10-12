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


def processCreateChangeRequestResponse(response):

    print("Processing answer from CR creation REST call")
    print("  Change Request returned code %s" % (response.status_code))
    if (response.status_code != 200 and response.status_code != 201):
        print("  Change Request creation failed with code %s" % (response.status_code))
        print("  Error: " + response.text)
        return response.status_code

    print("  Change Request creation successful")
    data=response.json() # json.loads(response.text)
    CR_NUMBER=data["result"]["number"]
    CR_SYSID=data["result"]["sys_id"]
    FULL_JSON=json.dumps(data, indent=2)
    print(f"  Change Request Number: {CR_NUMBER}")
    print(f"  Change Request sys_id: {CR_SYSID}")
    print("  Change Request full answer:\n" + FULL_JSON)

    if os.path.exists(env_file_path):
        env_file = open(env_file_path, "a")
        env_file.write(f"CR_NUMBER={CR_NUMBER}\n")
        env_file.write(f"CR_SYSID={CR_SYSID}\n")
        env_file.write("CR_FULL_JSON=/codefresh/volume/servicenow-cr.json\n")
        env_file.close()

        json_file=open("/codefresh/volume/servicenow-cr.json", "w")
        json_file.write(FULL_JSON)
        json_file.close()

#
# Call SNow REST API to create a new Change Request
# Fields required are pasted in the data
def createChangeRequest(user, password, baseUrl, data):

    if DEBUG:
        print("Entering createChangeRequest:")

    if (bool(data)):
        crBody=json.loads(data)
        if DEBUG:
            print("Data: " + data)
    else:
        crBody= {}
        if DEBUG:
            print("  Data: None")
    crBody["cf_build_id"] = os.getenv('CF_BUILD_ID')


    url="%s/now/table/change_request" % (baseUrl)

    if DEBUG:
        print(f"  URL: {url}")
        print(f"  User: {user}")
        print(f"  Body: {crBody}")

    resp=requests.post(url,
        json = crBody,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processCreateChangeRequestResponse(response=resp)

def processModifyChangeRequestResponse(response, action):

    print("Processing answer from CR %s REST call" %(action))
    print("Close Change Request returned code %s" % (response.status_code))
    if (response.status_code != 200 and response.status_code != 201):
        print("%s Change Request creation failed with code %s" % (action, response.status_code))
        print("Error: " + response.text)
        return response.status_code

    print("%s Change Request creation successful" %(action))
    data=response.json() # json.loads(response.text)

    FULL_JSON=json.dumps(data, indent=2)

    if (action == "close" ):
        jsonVar="CR_CLOSE_FULL_JSON"
        jsonFileName="/codefresh/volume/servicenow-cr-close.json"
    elif (action == "update" ):
        jsonVar="CR_UPDATE_FULL_JSON"
        jsonFileName="/codefresh/volume/servicenow-cr-update.json"
    else:
        print("ERROR: action unknonw. Should not be here. Error should have been caught earlier")
    if os.path.exists(env_file_path):
        env_file = open(env_file_path, "a")
        env_file.write(f"{jsonVar}=/codefresh/volume/servicenow-cr-close.json\n")
        env_file.close()

        json_file=open("/codefresh/volume/servicenow-cr-close.json", "w")
        json_file.write(FULL_JSON)
        json_file.close()

# Call SNow REST API to close a CR
# Fields required are pasted in the data
def closeChangeRequest(user, password, baseUrl, sysid, code, notes, data):
    if DEBUG:
        print("Entering closeChangeRequest:")
        print(f"DATA: {data}")
    if (bool(data)):
        crBody=json.loads(data)
    else:
        crBody= {}
    crBody["state"] = 3
    crBody["close_code"] = code
    crBody["close_notes"] = notes
    url="%s/now/table/change_request/%s" % (baseUrl, sysid)
    resp=requests.patch(url,
        json = crBody,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processModifyChangeRequestResponse(response=resp, action="close")

# Call SNow REST API to update a CR
# Fields required are pasted in the data
def updateChangeRequest(user, password, baseUrl, sysid, data):
    if DEBUG:
        print("Entering closeChangeRequest:")
        print(f"DATA: {data}")
    if (bool(data)):
        crBody=json.loads(data)
    else:
        crBody= {}
        print("WARNING: CR_DATA is empty. What are you updating exactly?")

    url="%s/now/table/change_request/%s" % (baseUrl, sysid)
    resp=requests.patch(url,
        json = crBody,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processModifyChangeRequestResponse(response=resp, action="update")
# Use rest API to call scripted REST API to start a flow that will wait for CR
# to be approved or rejected, then callback Codefreh to approve/deny pipeline
#
def callback(user, password, baseUrl, number, cf_build_id, token):

    if DEBUG:
        print("Entering callback:")
        print("CR Number: " + number)
        print("CF Build ID: " + cf_build_id)

    url = "%s/%s/codefresh/callback" % (baseUrl, API_NAMESPACE)

    body = {
        "cr_number": number,
        "cf_build_id": cf_build_id,
        "cf_token": token,
        "cf_url": os.getenv("CF_URL")
    }
    if DEBUG:
        print("Calling POST on " + url)
        print("Data: " + json.dumps(body))

    resp=requests.post(url,
        json = body,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processCallbackResponse(response=resp)

def checkSysid(sysid):
    if DEBUG:
        print("Entering checkSysid: ")
        print("  CR_SYSID: %s" % (sysid))

    if ( sysid == None ):
        sys.exit("FATAL: CR_SYS_ID is not defined.")


def main():
    global DEBUG

    ACTION = os.getenv('ACTION').lower()
    USER = os.getenv('SN_USER')
    PASSWORD = os.getenv('SN_PASSWORD')
    INSTANCE = os.getenv('SN_INSTANCE')
    DATA     = os.getenv('CR_DATA')
    #DEBUG = True if os.getenv('debug', "false").lower == "true" else False

    if DEBUG:
        print(f"ACTION: {ACTION}")
        print(f"DATA: {DATA}")

    if ACTION == "createcr":
        createChangeRequest(user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            data=DATA)
    elif ACTION == "callback":
        callback(user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            number=os.getenv('CR_NUMBER'),
            token=os.getenv('TOKEN'),
            cf_build_id=os.getenv('CF_BUILD_ID')
        )
    elif ACTION == "closecr":
        CR_SYSID= os.getenv('CR_SYSID')
        CODE=os.getenv('CR_CLOSE_CODE')
        NOTES=os.getenv('CR_CLOSE_NOTES')
        checkSysid(CR_SYSID)

        closeChangeRequest(
            user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            sysid=os.getenv('CR_SYSID'),
            code=CODE,
            notes=NOTES,
            data=DATA
        )
    elif ACTION == "updatecr":
        CR_SYSID= os.getenv('CR_SYSID')
        checkSysid(CR_SYSID)

        updateChangeRequest(
            user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            sysid=os.getenv('CR_SYSID'),
            data=DATA
        )
    else:
        sys.exit(f"FATAL: Unknown action: {ACTION}. Allowed values are createCR, closeCR or updateCR.")


if __name__ == "__main__":
    main()
