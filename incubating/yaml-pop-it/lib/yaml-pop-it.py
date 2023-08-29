import os
import yaml
import sys


# Add key value to dict
def append_to_dictionary(target_dict, key, value):
    target_dict[key] = value
    
    return target_dict


def write_file(output_file_path, merged_dict):
    with open(output_file_path, 'w') as f:
        yaml.dump(merged_dict, f)


def main():

    working_directory = os.getenv('WORKING_DIRECTORY')
    templates_directory = os.getenv('TEMPLATES_DIRECTORY', '/templates')
    config_yaml_path = os.path.join(templates_directory, 'configmap.yaml')
    secrets_yaml_path = os.path.join(templates_directory, 'secrets.yaml')

    # Import variables from environment

    variables = os.environ
    
    # Create configmap and secrets dict

    configmap = {}
    secrets = {}

    # Append key values to correct dicts

    for variable in variables:
        if variable.startswith('POP_CONFIG'):
            append_to_dictionary(configmap, variable.split('_',2)[-1], os.environ[variable])
        elif variable.startswith('POP_SECRET'):
            append_to_dictionary(secrets, variable.split('_',2)[-1], os.environ[variable])

    # Open YAML file for editing
    with open(config_yaml_path) as f:
        configmap_dict = yaml.safe_load(f)

    with open(secrets_yaml_path) as f:
        secrets_dict = yaml.safe_load(f)

    configmap_dict['data'] = configmap
    secrets_dict['data'] = secrets

    # Write ConfigMap file
    write_file(os.path.join(working_directory, 'configmap.yaml'), configmap_dict)

    # Write Secrets file
    write_file(os.path.join(working_directory, 'secrets.yaml'), secrets_dict)


if __name__ == "__main__":
    main()