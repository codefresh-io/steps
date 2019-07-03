import json
import os
import sys
import subprocess
from azure.keyvault import KeyVaultClient
from azure.common.credentials import ServicePrincipalCredentials


def main():
    client_id = os.getenv('AZURE_CLIENT_ID')
    service_principal_secret = os.getenv('AZURE_SECRET')
    tenant = os.getenv('AZURE_TENANT')
    secret_id = os.getenv('AZURE_SECRET_ID')
    secret_version = os.getenv('AZURE_SECRET_VERSION')
    vault_url = os.getenv('AZURE_VAULT_URL')

    # Get Service Principal Credentials

    credentials = ServicePrincipalCredentials(
        client_id = client_id,
        secret = service_principal_secret,
        tenant = tenant
    )
    
    # Auth with Service Principal
    client = KeyVaultClient(credentials)

    # Get Azure Secret from Azure Vault
    # VAULT_URL must be in the format 'https://<vaultname>.vault.azure.net'
    # SECRET_VERSION is required, and can be obtained with the KeyVaultClient.get_secret_versions(self, vault_url, secret_id) API
    secret_bundle = client.get_secret(vault_url, secret_id, secret_version)
    secret = secret_bundle.value

    file_path = '/codefresh/volume/env_vars_to_export'
    with open(file_path, 'a') as file:
        file.write("{}={}\n".format(secret_id, secret))

if __name__ == "__main__":
    main()
