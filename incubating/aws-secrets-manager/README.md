# Codefresh Step for AWS Secrets Manager
Adapted from: [moneylion/cfstep-aws-secrets-manager](https://github.com/moneylion/cfstep-aws-secrets-manager)

Codefresh Step to fetch secrets from AWS Secrets Manager.

View [changelog](./CHANGELOG.md).

## Usage

Include this Step in your pipeline, for example:

```yaml
steps:
  FetchSecrets:
    title: Fetch secrets from AWS Secrets Manager
    type: aws-secrets-manager
    arguments:
      AWS_ACCESS_KEY_ID: ${{AWS_ACCESS_KEY_ID}}
      AWS_SECRET_ACCESS_KEY: ${{AWS_SECRET_ACCESS_KEY}}
      AWS_DEFAULT_REGION: a-region-1
      secrets:
        - secret_arn: arn:aws:secret-1
          key: username
          store_in: USERNAME
        - secret_arn: arn:aws:secret-2
          key: password
          store_in: PASSWORD
  UseSecrets:
    title: Use the fetched secrets
    type: freestyle
    arguments:
      image: 'alpine'
      commands:
        # Access your secrets via $USERNAME and $PASSWORD
        - ...
```

This fetches the secrets, and places the referenced values into the environment variables `USERNAME` and `PASSWORD`, which can then be used in the subsequent steps within the pipeline.

### Step input

Specify the list of secrets to be fetched, under the `secrets` input parameter. Each secret is a map containing:

  - Secret's ARN (or friendly name)
  - JSON object key
  - Environment variable to store the referenced secret value in

For example, given the secret with an ARN `arn:aws:secret-1`, and a secret value:

```json
{
  "username": "admin",
  "password": "str0ngpassword"
}
```

Specifying this as one of the secrets:

```yaml
arguments:
  AWS_ACCESS_KEY_ID: ${{AWS_ACCESS_KEY_ID}}
  AWS_SECRET_ACCESS_KEY: ${{AWS_SECRET_ACCESS_KEY}}
  AWS_DEFAULT_REGION: a-region-1
  secrets:
    - secret_arn: arn:aws:secret-1
      key: username
      store_in: USERNAME
```

Fetches the secret, retrieves the JSON value under the key `username`, and store that value in the `USERNAME` environment variable. `$USERNAME` will now contain the value `admin`.

### Authenticating with AWS
This step can either authenticate with AWS using a pod's IAM role or via these pipeline variables:

  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_DEFAULT_REGION`

You may also override them via the Step's argument.

To assume an IAM role before fetching secrets, you may specify the role's ARN via `AWS_IAM_ROLE_ARN` pipeline variable, or similarly through the Step's argument:

```yaml
arguments:
  AWS_ACCESS_KEY_ID: ${{AWS_ACCESS_KEY_ID}}
  AWS_SECRET_ACCESS_KEY: ${{AWS_SECRET_ACCESS_KEY}}
  AWS_DEFAULT_REGION: a-region-1
  AWS_IAM_ROLE_ARN: 'arn:aws:role/some-role'  # Like this
  secrets:
    - secret_arn: arn:aws:secret-1
      key: username
      store_in: USERNAME
```
