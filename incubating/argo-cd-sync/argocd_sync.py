from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import os

RUNTIME     = os.getenv('RUNTIME')
APPLICATION = os.getenv('APPLICATION')

CF_URL      = os.getenv('CF_URL', 'https://g.codefresh.io')
CF_API_KEY  = os.getenv('CF_API_KEY')
CF_STEP_NAME= os.getenv('CF_STEP_NAME', 'STEP_NAME')

#######################################################################


def main():
    ingress_host = get_runtime_ingress_host()
    execute_argocd_sync(ingress_host)
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


def get_runtime_ingress_host():
    ingress_host = None
    runtime = get_runtime()
    ingress_host = runtime['runtime']['ingressHost']
    return ingress_host


def get_link_to_apps_dashboard():
    runtime = get_runtime()
    runtime_ns = runtime['runtime']['metadata']['namespace']
    url_to_app = CF_URL+'/2.0/applications-dashboard/'+RUNTIME+'/'+runtime_ns+'/'+APPLICATION+'/timeline'
    return url_to_app


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
    print("Syncing app: ", variables)
    result = client.execute(query, variable_values=variables)
    print(result)


def export_variable(var_name, var_value):
    path = os.getenv('CF_VOLUME_PATH') if os.getenv('CF_VOLUME_PATH') != None else './'
    with open(path+'/env_vars_to_export', 'a') as a_writer:
        a_writer.write(var_name + "=" + var_value+'\n')
    
    if os.getenv('CF_VOLUME_PATH') == None: os.mkdir('/meta') 
    with open('/meta/env_vars_to_export', 'a') as a_writer:
        a_writer.write(var_name + "=" + var_value+'\n')

    print("Exporting variable: "+var_name+"="+var_value)  

##############################################################

if __name__ == "__main__":
    main()
