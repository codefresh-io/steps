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
import base64


def append_to_dictionary(target_dict, key, value, secret):
    if secret:
        target_dict[key] = base64.b64encode(bytes(value, 'utf-8')).decode("utf-8")
    else:
        target_dict[key] = value
    
    return target_dict


def append_to_dictionary_array(target_dict, key, name, ref):
    target_dict['spec']['template']['spec']['containers'][0]['env'].append({
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


def add_google_kms_secrets_to_dicts(secrets, secrets_env_dict, secrets_name, credentials, project_id, key, value):

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient(credentials=credentials)

    # Get Secrets from Project
    parent = f"projects/{project_id}"

    response = client.list_secrets(request={"parent": parent})

    my_dict = MessageToDict(response._pb, preserving_proto_field_name=True)

    # Search secrets for correct label
    for secret in my_dict['secrets']:
        if key in secret['labels']:
            if value in secret['labels'][key]:
                version = '{}/versions/latest'.format(secret['name'])
                response = client.access_secret_version(name=version)
                secret_value = response.payload.data.decode('UTF-8')
                secret_name = secret['name'].split('/', 3)[3]
                append_to_dictionary(secrets, secret_name, secret_value, True)
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
    templates_directory = os.getenv('TEMPLATES_DIRECTORY', '/templates')
    deployment_file = os.getenv('DEPLOYMENT_FILE', 'deployment.yaml')
    config_yaml_path = os.path.join(templates_directory, 'configmap.yaml')
    secrets_yaml_path = os.path.join(templates_directory, 'secrets.yaml')
    service_name =  os.getenv('SERVICE_NAME')
    google_label_key = os.getenv('GOOGLE_LABEL_KEY', 'secret-name')
    google_label_value = os.getenv('GOOGLE_LABEL_VALUE')

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
    
    # Create configmap and secrets dictionaries
    configmap = {}
    secrets = {}

    #configmap_env_dict = {}
    #configmap_env_dict['env'] = []
    deployment_dict['spec']['template']['spec']['containers'][0]['env'] = []

    # Append key values to correct dicts
    for variable in variables:
        if variable.startswith('POP_CONFIG'):
            print('Importing ConfigMap Pop: {}'.format(variable.split('_',2)[-1]))
            append_to_dictionary(configmap, variable.split('_',2)[-1], os.environ[variable], False)
        elif variable.startswith('POP_SECRET'):
            print('Importing Secret Pop: {}'.format(variable.split('_',2)[-1]))
            append_to_dictionary(secrets, variable.split('_',2)[-1], os.environ[variable], True)
            append_to_dictionary_array(deployment_dict, variable.split('_',2)[-1], secrets_name, 'secretKeyRef')

    # Get Shared Configs and append to dictionaries
    config_items = get_shared_config(cf_api_key, config_context, 'false')
    secret_items = get_shared_config(cf_api_key, secret_context, 'true')

    if config_items:
        for key in config_items['spec']['data']:
            append_to_dictionary(configmap, key, config_items['spec']['data'][key], False)
    if secret_items:
        try: 
            for key in secret_items['spec']['data']:
                append_to_dictionary(secrets, key, secret_items['spec']['data'][key], True)
                append_to_dictionary_array(deployment_dict, key, secrets_name, 'secretKeyRef')
        except:
            print('No Codefresh Shared Secrets Found.')
            pass

    # Get Secrets from Google KMS
    if google_project_name:
        if google_label_value is None:
            google_label_value = secret_context.lower().replace('_', '-')
        print('Fetching Secrets from Google Secret Manager for Label: {} Key: {}'.format(google_label_key, google_label_value))
        google_credentials = service_account.Credentials.from_service_account_file(google_sa_json_path)
        add_google_kms_secrets_to_dicts(secrets, deployment_dict, secrets_name, google_credentials, google_project_name, google_label_key, google_label_value)

    # Open YAML file for editing
    with open(config_yaml_path) as f:
        configmap_dict = yaml.safe_load(f)

    with open(secrets_yaml_path) as f:
        secrets_dict = yaml.safe_load(f)

    configmap_dict['data'] = configmap
    secrets_dict['data'] = secrets

    # Rename ConfigMap
    configmap_dict['metadata']['name'] = configmap_name

    # Rename Secrets
    secrets_dict['metadata']['name'] = secrets_name

    # Define annotations
    dict_annotations = {
        'codefresh.io/build': cf_build_id, 
        'codefresh.io/pipeline': cf_pipeline_name,
        'codefresh.io/revision': cf_build_number,
        'codefresh.io/timestamp': cf_build_timestamp, 
        'codefresh.io/url': cf_build_url
        }

    # Update ConfigMap metadata
    configmap_dict['metadata']['annotations'] = dict_annotations

    # Update Secrets metadata
    secrets_dict['metadata']['annotations'] = dict_annotations

    # # Write ConfigMap file
    write_file(os.path.join(working_directory, '{}-configmap-{}.yaml'.format(service_name, cf_build_number)), configmap_dict)

    # # Write Secrets file
    write_file(os.path.join(working_directory, '{}-secrets-{}.yaml'.format(service_name, cf_build_number)), secrets_dict)

    # Edit Deployment YAML with new names for ConfigMap and Secret
    deployment_dict['spec']['template']['spec']['containers'][0]['envFrom'] = []
    deployment_dict['spec']['template']['spec']['containers'][0]['envFrom'].append({
        'configMapRef':{
            'name':  configmap_name
        }
    })

    for volume in deployment_dict['spec']['template']['spec']['volumes']:
        if 'configMap' in volume:
            volume['configMap']['name'] = configmap_name   
        elif 'secret' in volume:
            volume['secret']['secretName'] = secrets_name

    write_file(os.path.join(working_directory, '{}-deployment-{}.yaml'.format(service_name, cf_build_number)), deployment_dict)

    # Interpolate remaining variales in new deployment.yaml file
    with in_place.InPlace(os.path.join(working_directory, '{}-deployment-{}.yaml'.format(service_name, cf_build_number))) as f:
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