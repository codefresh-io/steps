import os
import sys
import json
import requests
import logging
import urllib.parse

API_NAMESPACE=409723
env_file_path = "/meta/env_vars_to_export"

def exportVariable(name, value):
    if os.path.exists(env_file_path):
        file=open(env_file_path, "a")
    else:
        file=open("/tmp/env_vars_to_export", "a")
    file.write(f"{name}={value}\n")
    file.close()

def exportJson(name, json):
    if os.path.exists(env_file_path):
        json_file = open("/codefresh/volume/%s" %(name), "a")
    else:
        json_file = open("/tmp/%s" % (name), "a")
        json_file.write(json)
        json_file.close()

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

    exportVariable("CR_NUMBER", CR_NUMBER)
    exportVariable("CR_SYSID", CR_SYSID)
    exportVariable("CR_CREATE_JSON", FULL_JSON)

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

def processSearchStandardTemplateResponse(name, response):
    logging.info("Processing answer from Standard Template search")
    logging.debug("Template search returned code %s" % (response.status_code))
    if (response.status_code != 200 and response.status_code != 201):
        logging.critical("Standard Change Template for '%s' errored out with code %s", name, response.status_code)
        logging.critical("%s" + response.text)
        sys.exit(response.status_code)
    data=response.json()
    logging.debug("Full JSON answer: %s", data)

    if len(data["result"]) ==0 :
        logging.critical("Standard Change Template '%s' was not found", name)
        sys.exit(1)

    logging.info("Standard template search successful")
    STD_SYSID=data["result"][0]["sys_id"]
    return STD_SYSID

def processCreateStandardChangeRequestResponse(response):
    logging.info("Processing answer from standard CR creation REST call")
    logging.debug("Change Request returned code %s" % (response.status_code))
    if (response.status_code != 200 and response.status_code != 201):
        logging.critical("Change Request creation failed with code %s", response.status_code)
        logging.critical("%s", response.text)
        sys.exit(response.status_code)

    logging.info("Change Request creation successful")
    data=response.json()
    FULL_JSON=json.dumps(data, indent=2)
    CR_NUMBER=data["result"]["number"]["value"]
    CR_SYSID=data["result"]["sys_id"]["value"]
    exportVariable("CR_NUMBER", CR_NUMBER)
    exportVariable("CR_SYSID", CR_SYSID)
    exportVariable("CR_CREATE_JSON", FULL_JSON)
    return CR_NUMBER

# Call SNow REST API to create a new Standard Change Request
# Fields required are pasted in the data
def createStandardChangeRequest(user, password, baseUrl, data, standardName):
    logging.info("Creating a new Standard Change Request using '%s' template", standardName)
    encodedName=urllib.parse.quote_plus(standardName)

    url="%s/now/table/std_change_record_producer?sysparm_query=sys_name=%s" % (baseUrl, encodedName)

    logging.debug("Standard Change URL %s:",url)
    resp=requests.get(url,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    sysid=processSearchStandardTemplateResponse(name=standardName, response=resp)
    logging.info("Template found: %s", sysid)

    if (bool(data)):
        crBody=json.loads(data)
        logging.debug("Data: %s", data)
    else:
        crBody= {}
        logging.debug("  Data: None")
    crBody["cf_build_id"] = os.getenv('CF_BUILD_ID')


    url="%s/sn_chg_rest/change/standard/%s" % (baseUrl, sysid)

    logging.debug("URL %s:",url)
    logging.debug("User: %s", user)
    logging.debug("Body: %s", crBody)

    resp=requests.post(url,
        json = crBody,
        headers = {"content-type":"application/json"},
        auth=(user, password))
    return processCreateStandardChangeRequestResponse(response=resp)


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
        exportVariable("CR_CLOSE_FULL_JSON", "/codefresh/volume/servicenow-cr-close.json")
        exportJson("servicenow-cr-close.json", FULL_JSON)
    elif (action == "update" ):
        exportVariable("CR_UPDATE_FULL_JSON", "/codefresh/volume/servicenow-cr-update.json")
        exportJson("servicenow-cr-update.json", FULL_JSON)
    else:
        print("ERROR: action unknown. Should not be here. Error should have been caught earlier")

    exportVariable("CR_NUMBER", CR_NUMBER)
    exportVariable("CR_SYSID", CR_SYSID)


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

def checkUser(username):
    logging.debug("Entering checkUser: ")
    logging.debug("  CR_USER: %s" % (username))

    if ( username == None ):
        logging.error("FATAL: CR_USER is not defined.")
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
    STD_NAME = os.getenv('STD_CR_TEMPLATE')
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

    checkUser(USER)

    if ACTION == "createcr":
        # Used only later in the callback but eant to check for error early
        checkToken(TOKEN)
        checkConflictPolicy(POLICY)

        if STD_NAME:
            cr_number=createStandardChangeRequest(user=USER,
                standardName=STD_NAME,
                password=PASSWORD,
                baseUrl=getBaseUrl(instance=INSTANCE),
                data=DATA
            )
        else:
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
