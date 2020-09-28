import os
import json
import yaml
import sys
import requests
import re
import in_place
from google.oauth2 import service_account
from google.cloud import secretmanager
from google.protobuf.json_format import MessageToDict


# Add key value to dict
def append_to_dictionary(target_dict, key, value):
    target_dict[key] = value
    
    return target_dict

def append_to_dictionary_array(target_dict, key, name, ref):
    target_dict['env'].append({
        'name': key,
        'valueFrom': {
            ref: {
                'key': key,
                'name': name
            }
        }
    })

    return target_dict


def write_file(output_file_path, merged_dict):
    with open(output_file_path, 'w') as f:
        yaml.dump(merged_dict, f)


def get_shared_config(cf_api_key, context_name, decrypt):
    print('Fetching Codefresh Shared Config...')

    url = 'https://g.codefresh.io/api/contexts/{}?decrypt={}'.format(context_name, decrypt)

    payload = {}
    headers = {
        'Authorization': 'Bearer {}'.format(cf_api_key),
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    response_dict = json.loads(response.text)

    return response_dict


def add_google_kms_secrets_to_dicts(secrets, secrets_env_dict, secrets_name, credentials, project_id):

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient(credentials=credentials)

    # Get Secrets from Project
    parent = f"projects/{project_id}"

    response = client.list_secrets(request={"parent": parent})

    my_dict = MessageToDict(response._pb, preserving_proto_field_name=True)

    # Search secrets for correct label

    for secret in my_dict['secrets']:
        if 'test-api-secret' in secret['labels']['secret-name']:
            version = '{}/versions/latest'.format(secret['name'])
            response = client.access_secret_version(name=version)
            secret_value = response.payload.data.decode('UTF-8')
            secret_name = secret['name'].split('/', 3)[3]
            append_to_dictionary(secrets, secret_name, secret_value)
            append_to_dictionary_array(secrets_env_dict, secret_name, secrets_name, 'secretKeyRef')
    
    return secrets, secrets_env_dict


def main():

    cf_api_key = os.getenv('CF_API_KEY')
    cf_build_id = os.getenv('CF_BUILD_ID')
    cf_build_number = os.getenv('CF_BUILD_NUMBER')
    cf_build_timestamp = os.getenv('CF_BUILD_TIMESTAMP')
    cf_build_url = os.getenv('CF_BUILD_URL')
    cf_pipeline_name = os.getenv('CF_PIPELINE_NAME')
    google_project_name = os.getenv('GOOGLE_PROJECT_NAME')
    google_sa_json_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    working_directory = os.getenv('WORKING_DIRECTORY', '.')
    templates_directory = os.getenv('TEMPLATES_DIRECTORY', './templates')
    deployment_file = os.getenv('DEPLOYMENT_FILE', 'deployment.yaml')
    config_yaml_path = os.path.join(templates_directory, 'configmap.yaml')
    secrets_yaml_path = os.path.join(templates_directory, 'secrets.yaml')
    service_name =  os.getenv('SERVICE_NAME')


    # Import variables from environment

    variables = os.environ
    configmap_name = '{}-{}'.format(service_name, cf_build_number)
    secrets_name = '{}-{}'.format(service_name, cf_build_number)

    # Import Shared Configs/Secrets from name in YAML

    deployment_yaml_path = os.path.join(working_directory, deployment_file)

    with open(deployment_yaml_path) as f:
        deployment_dict = yaml.safe_load(f)

    # Find config names in deployment.yaml

    regex = r'\{(.*?)\}'

    for volume in deployment_dict['spec']['template']['spec']['volumes']:
        if 'configMap' in volume:
            config_context = re.findall(regex, volume['configMap']['name'])[0]
        elif 'secret' in volume:
            secret_context = re.findall(regex, volume['secret']['secretName'])[0]

    config_items = get_shared_config(cf_api_key, config_context, 'false')

    secret_items = get_shared_config(cf_api_key, secret_context, 'true')
    
    # Create configmap and secrets dictionaries

    configmap = {}
    secrets = {}

    configmap_env_dict = {}
    configmap_env_dict['env'] = []
    secrets_env_dict = {}
    secrets_env_dict['env'] = []

    # Append key values to correct dicts
    for variable in variables:
        if variable.startswith('POP_CONFIG'):
            append_to_dictionary(configmap, variable.split('_',2)[-1], os.environ[variable])
            append_to_dictionary_array(configmap_env_dict, variable.split('_',2)[-1], configmap_name, 'configMapKeyRef')
        elif variable.startswith('POP_SECRET'):
            append_to_dictionary(secrets, variable.split('_',2)[-1], os.environ[variable])
            append_to_dictionary_array(secrets_env_dict, variable.split('_',2)[-1], secrets_name, 'secretKeyRef')

    # Get Shared Configs and append to dictionaries
    if config_items:
        for key in config_items['spec']['data']:
            append_to_dictionary(configmap, key, config_items['spec']['data'][key])
            append_to_dictionary_array(configmap_env_dict, key, configmap_name, 'configMapKeyRef')
    if secret_items:
        for key in secret_items['spec']['data']:
            append_to_dictionary(secrets, key, secret_items['spec']['data'][key])
            append_to_dictionary_array(secrets_env_dict, key, secrets_name, 'secretKeyRef')

    # Get Secrets from Google KMS

    if google_project_name:
        print('Fetching Secrets from Google Secret Manager...')
        google_credentials = service_account.Credentials.from_service_account_file(google_sa_json_path)
        add_google_kms_secrets_to_dicts(secrets, secrets_env_dict, secrets_name, google_credentials, google_project_name)


    # Open YAML file for editing
    with open(config_yaml_path) as f:
        configmap_dict = yaml.safe_load(f)

    with open(secrets_yaml_path) as f:
        secrets_dict = yaml.safe_load(f)

    configmap_dict['data'] = configmap
    secrets_dict['data'] = secrets

    # Rename ConfigMap

    configmap_dict['name'] = configmap_name

    # Rename Secrets

    secrets_dict['name'] = secrets_name

    # Define metadata
    dict_metadata = {
        'codefresh.io/build': cf_build_id, 
        'codefresh.io/pipeline': cf_pipeline_name,
        'codefresh.io/revision': cf_build_number,
        'codefresh.io/timestamp': cf_build_timestamp, 
        'codefresh.io/url': cf_build_url
        }

    # Update ConfigMap metadata
    configmap_dict['metadata'] = dict_metadata

    # Update Secrets metadata
    secrets_dict['metadata'] = dict_metadata

    # # Write ConfigMap file
    write_file(os.path.join(working_directory, 'configmap-0.yaml'), configmap_dict)

    # # Write Secrets file
    write_file(os.path.join(working_directory, 'secrets-0.yaml'), secrets_dict)

    # Edit Deployment YAML with new names for ConfigMap and Secret

    deployment_dict['spec']['template']['spec']['containers'][0]['env'].extend(configmap_env_dict['env'])
    deployment_dict['spec']['template']['spec']['containers'][0]['env'].extend(secrets_env_dict['env'])

    for volume in deployment_dict['spec']['template']['spec']['volumes']:
        if 'configMap' in volume:
            volume['configMap']['name'] = configmap_name   
        elif 'secret' in volume:
            volume['secret']['secretName'] = secrets_name

    write_file(os.path.join(working_directory, 'deployment-{}.yaml'.format(cf_build_number)), deployment_dict)

    # Interpolate remaining variales in new deployment.yaml file

    with in_place.InPlace(os.path.join(working_directory, 'deployment-{}.yaml'.format(cf_build_number))) as f:
        for line in f:
            existing_value = re.findall(regex, line)
            if len(existing_value):
                existing_value_string = ''.join(map(str, existing_value))
                conformed_value = existing_value_string.upper().replace('.', '_')
                if conformed_value in variables:
                    new_line = line.replace('${'+ existing_value_string + '}', os.getenv(conformed_value))
                    f.write(new_line)
                else:
                    f.write(line)
            else:
                f.write(line)


if __name__ == "__main__":
    main()