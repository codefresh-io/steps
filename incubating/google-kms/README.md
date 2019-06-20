# Сodefresh Google KMS plugin

This plugin facilitates work with Google Key Management Service for such operations like **encryption** and **decryption**

## Usage

kms [OPERATION] [VALUE_1] [VALUE_n...]

Set the plugin required environment variables for the pipeline and use the plugin as a freestyle step with a command like:

```yaml
GoogleKMS:
    image: codefreshplugins/google-kms
    commands: 
      - kms encrypt VALUE_1 VALUE_n
```
where VALUE_1 and VALUE_n are the **names** of the environment variables containing the values you need to encrypt or decrypt.

The operation is mutable and when the step finishes, the variables with the same names will contain encrypted values. For decryption the process is similar

## Required environment variables

- `KMS_PROJECT` - GCP project name in which your KMS entities are present
- `KMS_LOCATION` - Google KMS location
- `KMS_KEYRING` - Google KMS keyring
- `KMS_KEY` - Google KMS key
- `GCP_SA_KEY` - [Google Service Account Key (JSON)](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)
