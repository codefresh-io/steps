import os
import sys
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


def main():
# To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials
  for azure_var in ['AZURE_CLIENT_ID','AZURE_CLIENT_SECRET','AZURE_TENANT_ID']:
    if os.getenv(azure_var) is None:
      print("The '{}' variable is not set".format(azure_var))
      sys.exit(1)

  credential = DefaultAzureCredential()

  vault_name = os.getenv('AZURE_VAULT_NAME')

  cf_volume_path = os.getenv('CF_VOLUME_PATH')

  vault_url = "https://{}.vault.azure.net/".format(vault_name)

  secret_client = SecretClient(vault_url=vault_url, credential=credential)

  secrets = os.getenv('SECRETS').split(",")

  for secret_name in secrets:
    secret = secret_client.get_secret(secret_name)

    print("Export '{}' secret".format(secret_name))
    file_path = '{}/env_vars_to_export'.format(cf_volume_path)
    with open(file_path, 'a') as file:
        file.write("{}={}\n".format(secret_name, secret.value))


if __name__ == "__main__":
    main()
