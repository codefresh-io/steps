# cfstep-azure-key-vault
Codefresh Pipeline Step for pulling secrets from Azure Key Vault and export them as environment variables for the next steps.

You must create a Service Principal with a Secret to use this plugin, and add the 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' as the pipeline variables or as the step arguments.

https://docs.microsoft.com/en-us/azure-stack/operator/azure-stack-create-service-principals#manage-service-principal-for-azure-ad

You must grant the Service Principal `Get` permissions for `Keys` for the Key Vault you'd like to access from step.

## Variable List

| ENVIRONMENT VARIABLE | DEFAULT | TYPE | REQUIRED | DESCRIPTION |
|----------------------------|----------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------|
| AZURE_CLIENT_ID | null | string | Yes | Application (client) ID for Service Principal |
| AZURE_CLIENT_SECRET | null | string | Yes | Client Secret for Service Principal |
| AZURE_TENANT_ID | null | string | Yes | Directory (tenant) ID for Service Principal|
| AZURE_VAUTL_NAME | null | string | Yes | Name of the Azure vault |
| SECRETS | null | string | Yes | Comma separated list the secrets to get |
