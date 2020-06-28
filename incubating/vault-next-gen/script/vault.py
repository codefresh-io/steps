import hvac
import os
import sys
import json

from step_utility import StepUtility

class Secret:
    def __init__(self, export_name, path, secret_name, secret_value):
        self.export_name = export_name
        self.path = path
        self.secret_name = secret_name
        self.secret_value = secret_value

class Environment:
    def __init__(self, vault_addr, vault_auth_method, vault_token,
        approle_role_id, approle_secret_id,
        mount_point, vault_kv_version, verbose):
        self.vault_addr = vault_addr
        self.vault_auth_method = vault_auth_method
        self.vault_token = vault_token
        self.approle_role_id = approle_role_id
        self.approle_secret_id = approle_secret_id
        self.mount_point = mount_point
        self.vault_kv_version = vault_kv_version
        self.verbose = verbose


def main():
    print("Got to the main call")
    env, current_environment = environment_setup()
    secrets, path_set = secrets_setup(env)
    client = vault_authentication(current_environment)
    retrieved_secrets = get_secrets(client, current_environment, secrets, path_set)
    export_secrets(retrieved_secrets)


def environment_setup():
    # Grab all of the environment variables
    env = os.environ
    vault_addr = StepUtility.getEnvironmentVariable('VAULT_ADDR', env)
    vault_auth_method = StepUtility.getEnvironmentVariable('VAULT_AUTH_METHOD', env)
    vault_token = StepUtility.getEnvironmentVariable('VAULT_TOKEN', env)
    approle_role_id = StepUtility.getEnvironmentVariable('APPROLE_ROLE_ID', env)
    approle_secret_id = StepUtility.getEnvironmentVariable('APPROLE_SECRET_ID', env) 
    mount_point = StepUtility.getEnvironmentVariable('MOUNT_POINT', env)
    vault_kv_version = StepUtility.getEnvironmentVariable('VAULT_KV_VERSION', env)
    verbose = StepUtility.getEnvironmentVariable('VERBOSE', env)
    current_environment = Environment(
        vault_addr, 
        vault_auth_method, 
        vault_token,
        approle_role_id,
        approle_secret_id,
        mount_point,
        vault_kv_version,
        verbose)
    #print(env)
    return env, current_environment


def secrets_setup(env):
    # Desired secrets values are prefixed with SECRETSVALUES_ as part of the step arguments
    secrets = []
    path_set = set()
    for key, val in sorted(env.items()):
        key_upper = key.upper()
        if key_upper.startswith("SECRETSVALUES_"):
            export_name = key.replace("SECRETSVALUES_", "")
            delim_index = val.find(":")
            path = val[0:delim_index]
            path_set.add(path)
            secret_name = val[delim_index+1:len(val)]
            secrets.append(Secret(
                export_name,
                path,
                secret_name,
                ""
            ))
    return secrets, path_set


def vault_authentication(current_environment):
    # Authenticate the client - exit program if authentication fails
    client = hvac.Client(url=current_environment.vault_addr)
    if current_environment.vault_auth_method.upper() == "TOKEN":
        print("Authentication Mode: TOKEN")
        client.token = current_environment.vault_token
    elif current_environment.vault_auth_method.upper() == "APPROLE":
        print("Authentication Mode: APPROLE")
        try:
            client.auth_approle(current_environment.approle_role_id, current_environment.approle_secret_id)
        except Exception as exc:
            print('{}: {}'.format(type(exc).__name__, exc))
            print("Exiting Step: Failed to authenticate with Approle to Vault instance")
            sys.exit(1)
    else:
        print("Authentication Mode not passed, defaulting to Token auth")
        client.token = current_environment.vault_token
        

    # Verify that we connected successfully to Vault, otherwise exit the step
    if not client.is_authenticated():
        print("Exiting Step: Failed to authenticate with Vault instance")
        sys.exit(1)
    else:
        print("Successfully authenticated with Vault instance")
    return client


def get_secrets(client, current_environment, secrets, path_set):
    if current_environment.verbose == "True":        
        # Test printing of desired secret information when debug is enabled
        print("\n---- DEBUG ---- Unique Paths")
        print(path_set)
        print("\n---- DEBUG ---- Requested Secrets")
        for current_secret in secrets:
            print(json.dumps(current_secret.__dict__))
        print()

    # This will store all the key/values retrieved from the paths
    vault_retrieved_values = dict()
    # Iterate over each unique path passed in through the environment variables
    for current_path in path_set:
        print("Retrieving secrets from path: " + current_path)
        secret_version_response = client.secrets.kv.v2.read_secret_version(
            mount_point=current_environment.mount_point, path=current_path
        )

        print("\n---- DEBUG REMOVE ---- Response")
        print(secret_version_response)

        vault_retrieved_values = secret_version_response['data']['data']
        # Loop through the list of secret requests and find keys that match
        for current_secret in secrets:
            for key, value in vault_retrieved_values.items():
                if current_secret.path == current_path and current_secret.secret_name == key:
                    print("Successful retrieval for path: " + current_secret.path + "  secret: " + current_secret.secret_name)
                    current_secret.secret_value = value    

    return secrets


def export_secrets(retrieved_secrets):
    # Export secrets here
    print("\n---- DEBUG REMOVE ---- Secrets")
    for current_secret in retrieved_secrets:
        print(json.dumps(current_secret.__dict__))
    print()


# Entrypoint for the application
if __name__ == "__main__":
    main()