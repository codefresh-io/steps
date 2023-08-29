import requests
import os
import sys


def main():

    # Global Step Parameters
    api_token = os.getenv('API_TOKEN')
    cf_build_id = os.getenv('CF_BUILD_ID')
    certificate_path = os.getenv('CERTIFICATE_PATH')
    dynatrace_domain = os.getenv('DYNATRACE_DOMAIN')
    dynatrace_environment_id =  os.getenv('DYNATRACE_ENVIRONMENT_ID')
    
    # Dynatrace Events Data Parameters
    event_type = os.getenv('EVENT_TYPE')
    description = os.getenv('DESCRIPTION')
    title = os.getenv('TITLE')
    source = os.getenv('SOURCE')
    annotationType = os.getenv('ANNOTATION_TYPE')
    annotationDescription = os.getenv('ANNOTATION_DESCRIPTION')
    deploymentName = os.getenv('DEPLOYMENT_NAME')
    deploymentVersion = os.getenv('DEPLOYMENT_VERSION')
    deploymentProject = os.getenv('DEPLOYMENT_PROJECT')
    ciBackLink = os.getenv('CI_BACK_LINK')
    cf_build_url = os.getenv('CF_BUILD_URL')
    remediationAction = os.getenv('REMEDIATION_ACTION')
    original = os.getenv('ORIGINAL')
    configuration = os.getenv('CONFIGURATION')
    entityids = os.getenv('ENTITYIDS').split(';')
    metypes = ('METYPES').split(';')
    keys = ('KEYS').split(';')

    # Create URL
    endpoint = '/api/v1/events'

    if dynatrace_environment_id:
        url = 'https://' + dynatrace_environment_id + '.live.dynatrace.com' + endpoint
    else:
        url = 'https://' + dynatrace_domain + endpoint

    # Create Payload
    data = {
        "eventType": event_type,
        "source": source,
        "description": description,
        "attachRules": {}
    }

    if event_type == 'CUSTOM_ANNOTATION':
        data['annotationType'] = annotationType
        data['annotationDescription'] = annotationDescription

    elif event_type == 'CUSTOM_CONFIGURATION':
        data['configuration'] = configuration
        data['original'] = original

    elif event_type == 'CUSTOM_DEPLOYMENT':
        data['deploymentName'] = deploymentName
        data['deploymentVersion'] = deploymentVersion
        data['deploymentProject'] = deploymentProject
        if ciBackLink:
            data['ciBackLink'] = ciBackLink
        else:
            data['ciBackLink'] = cf_build_url
        data['remediationAction'] = remediationAction

    elif event_type == 'CUSTOM_INFO':
        data['title'] = title

    elif event_type == 'ERROR_EVENT':
        data['title'] = title

    if entityids:
        for entityid in entityids:
            e_id_data = []
            e_id_data.append(entityid)
        
        data['attachRules']['entityIds'] = e_id_data

    elif metypes:
        data['attachRules']['tagRule'] = []

        for metype in metypes:
            data['attachRules']['tagRule'][0]['meTypes'].append(metype)
        
        for key in keys:
            tag = {
                "context": "CONTEXTLESS",
                "key": key
            }
            data['attachRules']['tagRule'][0]['tags'].append(tag)

    print(data)
    
    # Send Event
    if certificate_path:
        r = requests.post(url, headers={'Authorization': "Api-Token " + api_token}, verify=certificate_path, json=data)
    else:
        r = requests.post(url, headers={'Authorization': "Api-Token " + api_token}, json=data)

    # Print Response
    print(r.status_code)
    print(r.text)
    print(r.json)

    if r.status_code == 200:
        print('Event Created.')
        sys.exit(0)
    else:
        print('!!!FAILED TO CREATE EVENT!!!')
        sys.exit(1)



if __name__ == "__main__":
    main()