from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import os
import logging

RUNTIME     = os.getenv('RUNTIME')
APPLICATION = os.getenv('APPLICATION')

CF_URL      = os.getenv('CF_URL', 'https://g.codefresh.io')
CF_API_KEY  = os.getenv('CF_API_KEY')
CF_STEP_NAME= os.getenv('CF_STEP_NAME', 'STEP_NAME')
LOG_LEVEL   = os.getenv('LOG_LEVEL', "info")

#######################################################################


def main():
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(format = log_format, level = LOG_LEVEL.upper())

    get_app_status()

    ## Generating link to the Apps Dashboard
    CF_OUTPUT_URL_VAR = CF_STEP_NAME + '_CF_OUTPUT_URL'
    link_to_app = get_link_to_apps_dashboard()
    export_variable(CF_OUTPUT_URL_VAR, link_to_app)


#######################################################################

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

def get_runtime_ns():
    runtime = get_runtime()
    runtime_ns = runtime['runtime']['metadata']['namespace']
    logging.debug("Runtime Namespace: %", runtime_ns)
    return runtime_ns

def get_link_to_apps_dashboard():
    runtime_ns= get_runtime_ns()
    url_to_app = CF_URL+'/2.0/applications-dashboard/'+RUNTIME+'/'+runtime_ns+'/'+APPLICATION+'/timeline'
    return url_to_app

def get_app_status():
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
        "namespace": get_runtime_ns()
    }
    result = client.execute(query, variable_values=variables)

    health = result['application']['healthStatus']
    sync   = result['application']['syncStatus']
    export_variable('HEALTH_STATUS', health)
    export_variable('SYNC_STATUS', sync)


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
