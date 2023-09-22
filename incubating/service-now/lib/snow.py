import os
import sys
import json
import requests
import logging

API_NAMESPACE=409723
env_file_path = "/meta/env_vars_to_export"

def getBaseUrl(instance):
    baseUrl = "%s/api" %(instance);
    logging.debug("baseUrl: " + baseUrl)
    return baseUrl

def processCallbackResponse(response):
    logging.info("Processing answer from CR creation REST call")
    logging.debug("Callback returned code %s" % (response.status_code))
    if (response.status_code != 200 and response.status_code != 201):
        logging.error("Callback creation failed with code %s" % (response.status_code))
        logging.error("Error: " + response.text)
        sys.exit(response.status_code)

    logging.info("Callback creation successful")


def processCreateChangeRequestResponse(response):
    logging.debug("Processing answer from CR creation REST call")
    logging.debug("  Change Request returned code %s" % (response.status_code))
    if (response.status_code != 200 and response.status_code != 201):
        logging.error("  Change Request creation failed with code %s" % (response.status_code))
        logging.error("  ERROR: " + response.text)
        sys.exit(response.status_code)

    logging.info("  Change Request creation successful")
    data=response.json() # json.loads(response.text)
    CR_NUMBER=data["result"]["number"]
    CR_SYSID=data["result"]["sys_id"]
    FULL_JSON=json.dumps(data, indent=2)

    logging.info(f"    Change Request Number: {CR_NUMBER}")
    logging.info(f"    Change Request sys_id: {CR_SYSID}")
    logging.debug( "    Change Request full answer:\n" + FULL_JSON)

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

    logging.debug("Entering createChangeRequest:")

    if (bool(data)):
        crBody=json.loads(data)
        logging.debug("Data: " + data)
    else:
        crBody= {}
        logging.debug("  Data: None")
    crBody["cf_build_id"] = os.getenv('CF_BUILD_ID')


    url="%s/now/table/change_request" % (baseUrl)

    logging.debug(f"  URL: {url}")
    logging.debug(f"  User: {user}")
    logging.debug(f"  Body: {crBody}")

    resp=requests.post(url,
        json = crBody,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processCreateChangeRequestResponse(response=resp)

def processModifyChangeRequestResponse(response, action):

    logging.debug("Processing answer from CR %s REST call" %(action))
    logging.debug("  %s Change Request returned code %s" % (action,response.status_code))
    if (response.status_code != 200 and response.status_code != 201):
        logging.error("  %s Change Request creation failed with code %s" % (action, response.status_code))
        logging.error("  ERROR: " + response.text)
        sys.exit(response.status_code)

    logging.info("  %s Change Request successful" %(action))
    data=response.json() # json.loads(response.text)
    CR_NUMBER=data["result"]["number"]
    CR_SYSID=data["result"]["sys_id"]

    FULL_JSON=json.dumps(data, indent=2)

    if (action == "close" ):
        jsonVar="CR_CLOSE_FULL_JSON"
        jsonFileName="/codefresh/volume/servicenow-cr-close.json"
    elif (action == "update" ):
        jsonVar="CR_UPDATE_FULL_JSON"
        jsonFileName="/codefresh/volume/servicenow-cr-update.json"
    else:
        print("ERROR: action unknown. Should not be here. Error should have been caught earlier")
    if os.path.exists(env_file_path):
        env_file = open(env_file_path, "a")
        env_file.write(f"{jsonVar}=/codefresh/volume/servicenow-cr-close.json\n")
        env_file.write(f"CR_NUMBER={CR_NUMBER}\n")
        env_file.write(f"CR_SYSID={CR_SYSID}\n")

        env_file.close()

        json_file=open("/codefresh/volume/servicenow-cr-close.json", "w")
        json_file.write(FULL_JSON)
        json_file.close()

# Call SNow REST API to close a CR
# Fields required are pasted in the data
def closeChangeRequest(user, password, baseUrl, sysid, code, notes, data):
    logging.debug("Entering closeChangeRequest:")
    logging.debug(f"DATA: {data}")
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
    logging.debug("Entering updateChangeRequest:")
    logging.debug(f"DATA: {data}")
    if (bool(data)):
        crBody=json.loads(data)
    else:
        crBody= {}
        logging.error("WARNING: CR_DATA is empty. What are you updating exactly?")

    url="%s/now/table/change_request/%s" % (baseUrl, sysid)
    logging.debug(f"  update CR URL: {url}")
    resp=requests.patch(url,
        json = crBody,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processModifyChangeRequestResponse(response=resp, action="update")
# Use rest API to call scripted REST API to start a flow that will wait for CR
# to be approved or rejected, then callback Codefreh to approve/deny pipeline
#
def callback(user, password, baseUrl, number, cf_build_id, token, policy):

    logging.debug("Entering callback:")
    logging.debug("CR Number: " + number)
    logging.debug("CF Build ID: " + cf_build_id)

    url = "%s/%s/codefresh/callback" % (baseUrl, API_NAMESPACE)

    body = {
        "cr_number": number,
        "cf_build_id": cf_build_id,
        "cf_token": token,
        "cf_url": os.getenv("CF_URL"),
        "cr_policy": policy
    }
    logging.debug("Calling POST on " + url)
    logging.debug("Data: " + json.dumps(body))

    resp=requests.post(url,
        json = body,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    processCallbackResponse(response=resp)

def checkSysid(sysid):
    logging.debug("Entering checkSysid: ")
    logging.debug("  CR_SYSID: %s" % (sysid))

    if ( sysid == None ):
        print("FATAL: CR_SYSID is not defined.")
        sys.exit(1)

def checkToken(token):
    logging.debug("Entering checkToken: ")
    logging.debug("  TOKEN: %s" % (token))

    if ( token == None ):
        logging.error("FATAL: TOKEN is not defined.")
        sys.exit(1)

def checkConflictPolicy(policy):
    logging.debug("Entering checkConflictPolicy: ")
    logging.debug("  CR_CONFLICT_POLICY: %s" % (policy))

    if policy == "ignore" or policy == "reject" or policy == "wait":
            return
    else:
        logging.error("FATAL: CR_CONFLICT_POLICY invalid value. Accepted values are ignore, reject or wait.")
        sys.exit(1)

def main():
    global DEBUG

    ACTION   = os.getenv('ACTION').lower()
    USER     = os.getenv('SN_USER')
    PASSWORD = os.getenv('SN_PASSWORD')
    INSTANCE = os.getenv('SN_INSTANCE')
    DATA     = os.getenv('CR_DATA')
    DEBUG    = True if os.getenv('DEBUG', "false").lower() == "true" else False
    TOKEN    = os.getenv('TOKEN')
    POLICY   = os.getenv('CR_CONFLICT_POLICY')
    if DEBUG:
        LOG_LEVEL   = "debug"
    else:
        LOG_LEVEL   = os.getenv('LOG_LEVEL', "info")

    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(format = log_format, level = LOG_LEVEL.upper())

    logging.info("Starting ServiceNow plugin for Codefresh")
    logging.debug(f"  ACTION: {ACTION}")
    logging.debug(f"  DATA: {DATA}")
    logging.debug("  SYSID: %s" % (os.getenv('CR_SYSID')))


    if ACTION == "createcr":
        # Used only later in the callback but eant to check for error early
        checkToken(TOKEN)
        checkConflictPolicy(POLICY)

        createChangeRequest(user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            data=DATA
        )
    elif ACTION == "callback":
        callback(user=USER,
            password=PASSWORD,
            baseUrl=getBaseUrl(instance=INSTANCE),
            number=os.getenv('CR_NUMBER'),
            token=TOKEN,
            cf_build_id=os.getenv('CF_BUILD_ID'),
            policy=POLICY
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
            sysid=CR_SYSID,
            data=DATA
        )
    else:
        logging.error("FATAL: Unknown action: {ACTION}. Allowed values are createCR, closeCR or updateCR.")
        sys.exit(1)


if __name__ == "__main__":
    main()
