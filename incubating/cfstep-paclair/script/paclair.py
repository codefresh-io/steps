import json
import yaml
import os
import re
import requests
import sys
import subprocess
import time
import warnings
import boto3
import base64

def get_ecr_credentials(image):
    client = boto3.client('ecr')
    response = client.describe_repositories()
    registry_list = [item for item in response['repositories'] if item.get('repositoryName')==image]

    auth_token = client.get_authorization_token(
                                                registryIds=[
                                                    registry_list[0]['registryId'],
                                                    ]
                                                )

    token_url = auth_token['authorizationData'][0]['proxyEndpoint']
    registry = token_url.replace('https://','')
    token = auth_token['authorizationData'][0]['authorizationToken']
    token_type = 'Basic'

    return(registry, token, token_type ,token_url)


def run_command(full_command):
    proc = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.communicate()
    print(output)
    if proc.returncode != 0:
        sys.exit(1)
    return b''.join(output).strip().decode()  # only save stdout into output, ignore stderr


def create_annotation_list(json_data):
    annotations = []
    annotation_list = ''
    for key, value in json_data.items():
        annotations.append("-l CLAIR_VULNS_{}={}".format(key.upper(), value))
        annotation_list = ' '.join(annotations)
    return annotation_list


def get_severity_weight(severity_level):

    dict = {
        "CRITICAL":6,
        "HIGH":5 ,
        "MEDIUM":4,
        "LOW":3,
        "NEGLIGIBLE":2,
        "UNKNOWN":1
    }

    weight = dict.get(severity_level, 0)

    return weight


def get_max_severity_weight(json_data):

    severity_weight_list = []

    for key, value in json_data.items():
        severity_weight_list.append(get_severity_weight(str(key).upper()))

    return max(severity_weight_list)


def annotate_image(docker_image_id, annotation_list):

    annotate_image_exec = ("codefresh annotate image {} {}"
                           .format(docker_image_id,
                                   annotation_list
                                   )
                           )

    run_command(annotate_image_exec)


def main(command):
    api_prefix = os.getenv('API_PREFIX', '')
    clair_url = os.getenv('CLAIR_URL', 'http://clair:6060')
    image = os.getenv('IMAGE')
    protocol = os.getenv('PROTOCOL', 'https')
    registry = os.getenv('REGISTRY', 'r.cfcr.io') 
    registry_username = os.getenv('REGISTRY_USERNAME')
    registry_password = os.getenv('REGISTRY_PASSWORD')
    severity_threshold = os.getenv('SEVERITY_THRESHOLD')
    tag = os.getenv('TAG')
    token = os.getenv('TOKEN')
    token_type = os.getenv('TOKEN_TYPE', 'Bearer')
    token_url = os.getenv('TOKEN_URL')

    # Build paclair config

    if registry == 'ecr':
        registry, token, token_type, token_url = get_ecr_credentials(image)
        cf_account = None
    else:
        cf_account = os.getenv('CF_ACCOUNT')

    data = {
                'General': {
                    'clair_url':clair_url,
                },
                'Plugins': {
                    'Docker': {
                        'class': 'paclair.plugins.docker_plugin.DockerPlugin',
                        'registries': { 
                            registry: {
                                'api_prefix': api_prefix,
                                'auth': [
                                    registry_username,
                                    registry_password
                                ],
                                'protocol':protocol,
                                'token':token,
                                'token_type':token_type,
                                'token_url':token_url,
                            }
                        }
                    }
                }
            }

    with open('/etc/paclair.conf', 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)

    if cf_account:
        full_registry = '/'.join([registry, cf_account])
    else:
        full_registry = registry
    
    docker_image_id = '{}:{}'.format(image, tag)

    base_command = ("paclair Docker {}/{}"
                        .format(
                                full_registry,
                                docker_image_id
                                )
                        )
    
    if command == 'scan':
        command_array = ['push', 'analyse --output-format html', 'analyse --output-format stats', 'delete']
        for command in command_array:
            if 'stats' in command:
                if cf_account:
                    output = run_command(' '.join([base_command, command]))
                    if output:
                        l = output.strip().split('\n')
                        json_data = {i.strip().split(':')[0]: int(i.strip().split(':')[1]) for i in l}
                        annotations = create_annotation_list(json_data)
                        annotate_image(docker_image_id, annotations)
                        if severity_threshold:
                            print('Running Severity Analysis...')
                            if get_max_severity_weight(json_data) >= get_severity_weight(severity_threshold.upper()):
                                raise ValueError('Severity Check Failed!')
                            else:
                                print('Severity Check Passed!')
                    else:
                        warnings.warn('No Vulnerabilities Returned from Clair Scan.')
                else:
                    output = run_command(' '.join([base_command, command]))
                    print(output)
            if 'html' in command:
                if not os.path.exists('reports'):
                    os.makedirs('reports')
                output = run_command(' '.join([base_command, command]))
                report_name = 'clair-scan-{}-{}.html'.format(image.replace('/', '-'), tag)
                with open('reports/{}'.format(report_name), 'w') as f:
                    f.write(str(output))
                    f.close()
            else:
                output = run_command(' '.join([base_command, command]))
                print(output)
    else: 
        output = run_command(' '.join([base_command, command]))
        print(output)

if __name__ == "__main__":
    main(sys.argv[1])
