import hvac
import os
import sys
import json
import base64
import re

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
                 vault_client_cert_base64, vault_client_key_base64,
                 mount_point, vault_kv_version, new_line_replacement_string,
                 files_names,
                 secret_name_separator,
                 verbose):
        self.vault_addr = vault_addr
        self.vault_auth_method = vault_auth_method
        self.vault_token = vault_token
        self.approle_role_id = approle_role_id
        self.approle_secret_id = approle_secret_id
        self.vault_client_cert_base64 = vault_client_cert_base64
        self.vault_client_key_base64 = vault_client_key_base64
        self.mount_point = mount_point
        self.vault_kv_version = vault_kv_version
        self.new_line_replacement_string = new_line_replacement_string
        self.files_names = files_names
        self.secret_name_separator = secret_name_separator
        self.secret_template = re.compile(
            "%vault:(.*?)"+secret_name_separator+"(.*?)%")
        self.verbose = verbose


def main():
    env, current_environment = environment_setup()
    secrets, path_set = secrets_setup(env)
    client = vault_authentication(current_environment)
    retrieved_secrets = get_secrets(
        client, current_environment, secrets, path_set)
    formatted_secrets = format_secrets(
        retrieved_secrets, current_environment.new_line_replacement_string)
    export_secrets(formatted_secrets)
    proceed_files_with_secrets(client, current_environment)


def environment_setup():
    # Grab all of the environment variables
    env = os.environ
    vault_addr = StepUtility.getEnvironmentVariable('VAULT_ADDR', env)
    vault_auth_method = StepUtility.getEnvironmentVariable(
        'VAULT_AUTH_METHOD', env)
    vault_token = StepUtility.getEnvironmentVariable('VAULT_TOKEN', env)
    approle_role_id = StepUtility.getEnvironmentVariable(
        'APPROLE_ROLE_ID', env)
    approle_secret_id = StepUtility.getEnvironmentVariable(
        'APPROLE_SECRET_ID', env)
    vault_client_cert_base64 = StepUtility.getEnvironmentVariable(
        'VAULT_CLIENT_CERT_BASE64', env)
    vault_client_key_base64 = StepUtility.getEnvironmentVariable(
        'VAULT_CLIENT_KEY_BASE64', env)
    mount_point = StepUtility.getEnvironmentVariable('MOUNT_POINT', env)
    vault_kv_version = StepUtility.getEnvironmentVariable(
        'VAULT_KV_VERSION', env)
    new_line_replacement_string = StepUtility.getEnvironmentVariable(
        'NEW_LINE_REPLACEMENT_STRING', env)
    files_names = files_names_setup(env)
    secret_name_separator = StepUtility.getEnvironmentVariable(
        'SECRET_NAME_SEPARATOR', env)
    if secret_name_separator == "":
        secret_name_separator = ":"
    verbose = StepUtility.getEnvironmentVariable('VERBOSE', env)
    current_environment = Environment(
        vault_addr,
        vault_auth_method,
        vault_token,
        approle_role_id,
        approle_secret_id,
        vault_client_cert_base64,
        vault_client_key_base64,
        mount_point,
        vault_kv_version,
        new_line_replacement_string,
        files_names,
        secret_name_separator,
        verbose)
    return env, current_environment


def files_names_setup(env):
    # Desired files names are prefixed with SECRETSFILES_
    # as part of the step arguments
    files_names = []
    for key, val in sorted(env.items()):
        key_upper = key.upper()
        if key_upper.startswith("SECRETSFILES_"):
            file_name = val
            files_names.append(file_name)
    return files_names


def secrets_setup(env):
    # Desired secrets values are prefixed with SECRETSVALUES_
    # as part of the step arguments
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
    print("\nAuthentication")
    client = hvac.Client(url=current_environment.vault_addr)

    # Check for client certs and apply them
    if current_environment.vault_client_cert_base64 != "" and \
            current_environment.vault_client_key_base64 != "":
        try:
            client_certs = (
                base64.b64decode(current_environment.vault_client_cert_base64),
                base64.b64decode(current_environment.vault_client_key_base64)
            )
            client = hvac.Client(
                url=current_environment.vault_addr,
                cert=client_certs
            )
        except Exception as exc:
            StepUtility.printCleanException(exc)
            StepUtility.printFail(
                "Exiting Step - "
                "Failed to authenticate with certificates to Vault instance")
            sys.exit(1)

    if current_environment.vault_auth_method.upper() == "TOKEN":
        print("Mode: TOKEN")
        client.token = current_environment.vault_token
    elif current_environment.vault_auth_method.upper() == "APPROLE":
        print("Mode: APPROLE")
        try:
            client.auth_approle(current_environment.approle_role_id,
                                current_environment.approle_secret_id)
        except Exception as exc:
            StepUtility.printCleanException(exc)
            StepUtility.printFail(
                "Exiting Step - "
                "Failed to authenticate with Approle to Vault instance")
            sys.exit(1)
    else:
        print("Authentication Mode not passed, defaulting to Token auth")
        client.token = current_environment.vault_token

    # Verify that we connected successfully to Vault, otherwise exit the step
    if not client.is_authenticated():
        StepUtility.printFail(
            "Exiting Step - Failed to authenticate with Vault instance")
        sys.exit(1)
    else:
        print("Successfully authenticated with Vault instance")
    return client


def get_secrets(client, current_environment, secrets, path_set):
    if current_environment.verbose == "true":
        # Test printing of desired secret information when debug is enabled
        print("\n---- VERBOSE ---- Unique Paths")
        print(path_set)
        print("\n---- VERBOSE ---- Requested Secrets")
        for current_secret in secrets:
            print(json.dumps(current_secret.__dict__))
        print()

    # This will store all the key/values retrieved from the paths
    vault_retrieved_values = dict()
    # Iterate over each unique path passed in through the environment variables
    print("\nSecret Retrieval")
    read_secret_version = client.secrets.kv.v2.read_secret_version
    for current_path in path_set:
        print("Retrieving secrets from path: " + current_path)
        if current_environment.vault_kv_version == "1":
            try:
                secret_response = client.secrets.kv.v1.read_secret(
                    mount_point=current_environment.mount_point,
                    path=current_path
                )
                vault_retrieved_values = secret_response['data']
            except Exception as exc:
                StepUtility.printCleanException(exc)
                StepUtility.printFail(
                    "Exiting Step - "
                    "Failed to retrieve secrets from v1 path: " + current_path)
                StepUtility.printFail(
                    "Please verify mount point, path, and kv version")
                sys.exit(1)
        else:
            try:
                secret_version_response = read_secret_version(
                    mount_point=current_environment.mount_point,
                    path=current_path
                )
                vault_retrieved_values = secret_version_response['data']
                ['data']
            except Exception as exc:
                StepUtility.printCleanException(exc)
                StepUtility.printFail(
                    "Exiting Step - "
                    "Failed to retrieve secrets from v2 path: " + current_path)
                StepUtility.printFail(
                    "Please verify mount point, path, and kv version")
                sys.exit(1)

        # Loop through the list of secret requests and find keys that match
        for current_secret in secrets:
            for key, value in vault_retrieved_values.items():
                if current_secret.path == current_path and \
                        current_secret.secret_name == key:
                    print("Successful retrieval for \n\tpath: " +
                          current_secret.path + "\n\tsecret: " +
                          current_secret.secret_name)
                    current_secret.secret_value = value

    # Secrets should be retrieved now, check to make sure they all have a value
    for retrieved_secret in secrets:
        if retrieved_secret.secret_value == "":
            StepUtility.printFail("Exiting Step - "
                                  "Failed retrieval for \n\tpath: " +
                                  retrieved_secret.path + "\n\tsecret: " +
                                  retrieved_secret.secret_name)
            sys.exit(1)

    return secrets


def format_secrets(retrieved_secrets, new_line_replacement_string):
    for current_secret in retrieved_secrets:
        # Check if the value of the secret-key is a JSON,
        # if so, convert it to a string so it can be properly formatted
        if isinstance(current_secret.secret_value, dict):
            current_secret.secret_value = json.dumps(
                current_secret.secret_value)
        # Apply the corresponding char replacements
        if new_line_replacement_string == "":
            current_secret.secret_value = current_secret.secret_value.replace(
                "\n", "\\n")
        elif new_line_replacement_string.upper() == "SPACE":
            current_secret.secret_value = current_secret.secret_value.replace(
                "\n", " ")
        elif new_line_replacement_string.upper() == "EMPTY_STRING":
            current_secret.secret_value = current_secret.secret_value.replace(
                "\n", "")
        elif new_line_replacement_string.upper() == "BASE64":
            encoded = base64.b64encode(current_secret.secret_value.encode())
            current_secret.secret_value = str(encoded, "utf-8")
        else:
            current_secret.secret_value = current_secret.secret_value.replace(
                "\n", new_line_replacement_string)

    return retrieved_secrets


def export_secrets(formatted_secrets):
    # Export secrets here
    print("\nExporting Secrets")
    env_file_path = "/meta/env_vars_to_export"
    if not os.path.exists(env_file_path):
        for current_secret in formatted_secrets:
            print(current_secret.export_name +
                  "=" + current_secret.secret_value)
    else:
        env_file = open(env_file_path, "a")
        for current_secret in formatted_secrets:
            env_file.write(current_secret.export_name + "=" +
                           current_secret.secret_value + "\n")
        env_file.close()


def proceed_files_with_secrets(client, environment):
    files_names = environment.files_names
    for file_name in files_names:
        file_lines = load_file(file_name)
        secrets, path_set = collect_secrets(
            file_lines, environment.secret_template)
        retrieved_secrets = get_secrets(client, environment, secrets, path_set)
        formatted_secrets = format_secrets(
            retrieved_secrets,
            environment.new_line_replacement_string)
        secrets_dict = secrets_to_dict(
            formatted_secrets,
            environment.secret_name_separator)
        updated_file_lines = resolve_from_lines(
            secrets_dict,
            environment.secret_template,
            environment.secret_name_separator,
            file_lines)
        write_lines_to_file(updated_file_lines, file_name)


def load_file(file_path):
    lines = []
    with open(file_path) as fp:
        line = fp.readline()
        while line:
            lines.append(line)
            line = fp.readline()
    return lines


def collect_secrets(lines, secret_template):
    secrets = []
    path_set = set()
    for line in lines:
        match = secret_template.search(line)
        if match:
            path, field = match.groups()
            found_secret = Secret("", path, field, "")
            path_set.add(found_secret.path)
            secrets.append(found_secret)
    return secrets, path_set


def secrets_to_dict(secrets, secret_name_separator):
    secrets_dict = dict()
    for current_secret in secrets:
        secrets_dict[current_secret.path+secret_name_separator +
                     current_secret.secret_name] = current_secret.secret_value
    return secrets_dict


def resolve_from_lines(
        secrets_dict, secret_template, secret_name_separator, lines):
    def vault_value_replace(match):
        path, field = match.groups()
        return secrets_dict[path+secret_name_separator+field]

    new_lines = []
    for line in lines:
        new_line = secret_template.sub(vault_value_replace, line)
        new_lines.append(new_line)
    return new_lines


def write_lines_to_file(lines, file_path):
    with open(file_path, "w") as file_handle:
        file_handle.writelines("%s\n" % line for line in lines)


# Entrypoint for the application
if __name__ == "__main__":
    main()
