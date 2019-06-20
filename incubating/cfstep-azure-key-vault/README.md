# cfstep-azure-key-vault
Codefresh Pipeline Step for pulling secrets from Azure Key Vault

You must create a Service Principal with a Secret to use this plugin.

https://docs.microsoft.com/en-us/azure-stack/operator/azure-stack-create-service-principals#manage-service-principal-for-azure-ad

You must grant the Service Principal `Get` permissions for `Keys` for the Key Vault you'd like to access from step.

## Variable List

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| AZURE_CLIENT_ID | null | string | Yes | Application (client) ID for Service Principal |
| AZURE_SECRET | null | string | Yes | Secret for Service Principal |
| AZURE_TENANT | null | string | Yes | Directory (tenant) ID for Service Principal|
| AZURE_SECRET_ID | null | string | Yes | Secret ID from Azure Key Vault |
| AZURE_SECRET_VERSION | null | string | Yes | Docker Registry Protocol |
| AZURE_VAULT_URL | null | string | Yes | Secret Version from Azure Key Vault |
