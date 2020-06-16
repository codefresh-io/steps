# cf-vault-plugin

Use Codefresh [Vault](https://www.vaultproject.io) plugin to make key-value pairs stored in a vault available as environment variables for further steps.

NOTE: this plugin currently supports token and approle authentication and Key/Value secrets engine only. This plugin will not renew a secret id TTL - it must be valid at the time of execution


## Usage

Set required and optional environment variables and add the following step to your Codefresh pipeline:

Example Variables:

The example below will authenticate to vault server `https://vault.testdomain.io:8200` using token `s.4wtaMJuZ7dv0c4XuRaasLUOG` and export all secrets found in path `secret/codefreshsecret` as ENV variables available for further steps.

```text
VAULT_ADDR=https://vault.testdomain.io:8200
VAULT_PATH=secret/codefreshsecret
VAULT_AUTH_TOKEN=s.4wtaMJuZ7dv0c4XuRaasLUOG
```


```yaml
---
  Vault_to_Env:
    title: Importing vault values
    type: vault
    arguments:
      VAULT_ADDR: ${{VAULT_ADDR}}
      VAULT_PATH: ${{VAULT_PATH}}
      VAULT_AUTH_TOKEN: ${{VAULT_AUTH_TOKEN}}
```

## Environment Variables

| Variables      | Required | Default | Description                                                                             |
|----------------|----------|---------|-----------------------------------------------------------------------------------------|
| VAULT_ADDR     | YES      |         | Vault server URI  |
| VAULT_PATH     | YES      |         | Path to secrets in vault. Can include multiple paths: "kv/firstpath;kv/secondpath"  |
| VAULT_PATH_DELIMITER  | NO  | | Delimiter if VAULT_PATH includes multiple paths separated by a delimiter  |
| VAULT_AUTH_METHOD | NO  | TOKEN | Authentication method: TOKEN OR APPROLE |
| VAULT_AUTH_TOKEN   | NO | | Vault authentication token |
| APPROLE_ROLE_ID | NO  | | Vault Approle Role ID (Must specify VAULT_AUTH_METHOD of APPROLE) |
| APPROLE_SECRET_ID | NO  | | Vault Approle Secret ID that must have a valid lease TTL  |
| VAULT_CLIENT_CERT_BASE64  | NO  | | Base64 encoded client cerificate |
| VAULT_CLIENT_KEY_BASE64 | NO  | | Base64 encoded client key |
| VAULT_FIELD_NAME  | NO  | | Vault key name to retrieve a single value |
| VAULT_VARIABLE_EXPORT_PREFIX  | NO  | | Prefix value that will prefix any exported values |                                                        
