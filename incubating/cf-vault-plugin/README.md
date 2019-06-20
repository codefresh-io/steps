# cf-vault-plugin

Use Codefresh [Vault](https://www.vaultproject.io) plugin to make key-value pairs stored in a vault available as environment variables for further steps.

NOTE: this plugin currently supports token authentication and Key/Value secrets engine only.


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
version: '1.0'

steps:

  ...

  Vault_to_Env:
    title: Importing vault values
    image: codefreshplugins/cf-vault-plugin
    environment:
      - VAULT_ADDR=${{VAULT_ADDR}}
      - VAULT_PATH=${{VAULT_PATH}}
      - VAULT_AUTH_TOKEN=${{VAULT_AUTH_TOKEN}}

  ...

```

## Environment Variables

| Variables      | Required | Default | Description                                                                             |
|----------------|----------|---------|-----------------------------------------------------------------------------------------|
| VAULT_ADDR     | YES      |         | Vault server URI                                                                         |
| VAULT_PATH   | YES      |         | Path to secrets in vault                                                                       |
| VAULT_AUTH_TOKEN   | YES      |         | Vault authentication token                            |
| VAULT_CLIENT_CERT_BASE64      | NO       |         | Base64 encoded client cerificate                                                             |
| VAULT_CLIENT_KEY_BASE64  | NO       |         | Base64 encoded client key                                                          
