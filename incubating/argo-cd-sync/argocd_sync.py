from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import os
import logging
import time

RUNTIME     = os.getenv('RUNTIME')
APPLICATION = os.getenv('APPLICATION')
WAIT_HEALTHY = True if os.getenv('WAIT_HEALTHY', "false").lower() == "true" else False
INTERVAL    = os.getenv('INTERVAL')
MAX_CHECKS  = os.getenv('MAX_CHECKS')
CF_URL      = os.getenv('CF_URL', 'https://g.codefresh.io')
CF_API_KEY  = os.getenv('CF_API_KEY')
CF_STEP_NAME= os.getenv('CF_STEP_NAME', 'STEP_NAME')
LOG_LEVEL   = os.getenv('LOG_LEVEL', "info")

#######################################################################


def main():
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(format = log_format, level = LOG_LEVEL.upper())

    ingress_host = get_runtime_ingress_host()
    execute_argocd_sync(ingress_host)
    namespace=get_runtime_ns()
    status = get_app_status(namespace)
    if WAIT_HEALTHY:
        time.sleep(INTERVAL)
        status = get_app_status(namespace)
        logging.info("App status is %s", status)
        loop=0
        while status != "HEALTHY" and loop < MAX_CHECKS:
            status=get_app_status(namespace)
            time.sleep(INTERVAL)
            logging.info("App status is %s after %d checks", status, loop)
            loop += 1

    export_variable('HEALTH_STATUS', status)

    ## Generating link to the Apps Dashboard
    CF_OUTPUT_URL_VAR = CF_STEP_NAME + '_CF_OUTPUT_URL'
    link_to_app = get_link_to_apps_dashboard()
    export_variable(CF_OUTPUT_URL_VAR, link_to_app)


#######################################################################
def get_app_status(namespace):
    ## Get the health status of the app
    gql_api_endpoint = CF_URL + '/2.0/api/graphql'
    transport = RequestsHTTPTransport(
        url=gql_api_endpoint,
        headers={'authorization': CF_API_KEY},
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    query = get_query('get_app_status') ## gets gql query
    variables = {
        "runtime":  RUNTIME,
        "name": APPLICATION,
        "namespace": namespace
    }
    result = client.execute(query, variable_values=variables)

    health = result['application']['healthStatus']
    return health

def get_query(query_name):
    ## To do: get query content from a variable, failback to a file
    with open('queries/'+query_name+'.graphql', 'r') as file:
        query_content = file.read()
    return gql(query_content)


def get_runtime():
    transport = RequestsHTTPTransport(
        url = CF_URL + '/2.0/api/graphql',
        headers={'authorization': CF_API_KEY},
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    query = get_query('getRuntime') ## gets gql query
    variables = {
        "runtime": RUNTIME
    }
    runtime = client.execute(query, variable_values=variables)
    return runtime


def get_runtime_ingress_host():
    ingress_host = None
    runtime = get_runtime()
    ingress_host = runtime['runtime']['ingressHost']
    return ingress_host


def get_link_to_apps_dashboard():
    runtime = get_runtime()
    runtime_ns = runtime['runtime']['metadata']['namespace']
    url_to_app = CF_URL+'/2.0/applications-dashboard/'+ runtime_ns +'/'+ RUNTIME +'/'+APPLICATION+'/timeline'
    return url_to_app

def get_runtime_ns():
    runtime = get_runtime()
    runtime_ns = runtime['runtime']['metadata']['namespace']
    logging.debug("Runtime Namespace: %", runtime_ns)
    return runtime_ns

def execute_argocd_sync(ingress_host):
    runtime_api_endpoint = ingress_host + '/app-proxy/api/graphql'
    transport = RequestsHTTPTransport(
        url=runtime_api_endpoint,
        headers={'authorization': CF_API_KEY},
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    query = get_query('argocd_sync') ## gets gql query
    variables = {
        "applicationName": APPLICATION,
        "options": {
            "prune": True
        }
    }
    logging.info("Syncing app: %s", variables)
    result = client.execute(query, variable_values=variables)
    logging.info(result)


def export_variable(var_name, var_value):
    path = os.getenv('CF_VOLUME_PATH') if os.getenv('CF_VOLUME_PATH') != None else './'
    with open(path+'/env_vars_to_export', 'a') as a_writer:
        a_writer.write(var_name + "=" + var_value+'\n')

    if os.getenv('CF_VOLUME_PATH') == None: os.mkdir('/meta')
    with open('/meta/env_vars_to_export', 'a') as a_writer:
        a_writer.write(var_name + "=" + var_value+'\n')

    logging.info("Exporting variable: %s=%s", var_name, var_value)

##############################################################

if __name__ == "__main__":
    main()
