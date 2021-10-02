#!/usr/bin/env python3
## Original author: Ling Cong Xiang (github.com/Raphx)
##
## Modified by: Jesse Antoszyk (github.com/jcantosz)
##   Updated assume_role, and step definition YAML

"""Main entrypoint"""

import functools
import io
import json
import os

import boto3

AWS_ROLE_ARN = 'AWS_ROLE_ARN'
SECRETS = 'SECRETS'
AWS_WEB_IDENTITY_TOKEN_FILE = "AWS_WEB_IDENTITY_TOKEN_FILE"


def should_assume_role(role_arn):
    """
    Handles the case when AWS_ROLE_ARN Codefresh input
    parameter is omitted, which will cause the role ARN to
    contain the literal string "${{AWS_ROLE_ARN}}".

    In this case, we do not want to assume role.
    """
    if role_arn == '${{AWS_ROLE_ARN}}':
        return False

    return True


def assume_role(role_arn):
    """
    Assume a role and return the temporary credentials.
    """

    roleSessionName='cfstep-aws-secrets-manager'
    client = boto3.client('sts')
    response = None
    # if AWS_ACCESS_KEY_ID explicitly set, take priority
    if "AWS_ACCESS_KEY_ID" in os.environ and os.environ["AWS_ACCESS_KEY_ID"]:
        print("Reading secrets from secret access key provided")
        response = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=roleSessionName
            )
    # If not explicitly set but there is a service acocunt token, use that
    elif AWS_WEB_IDENTITY_TOKEN_FILE in os.environ:
        print("Reading secrets from service account (IAM) token")

        webtokenPath = os.environ.get(AWS_WEB_IDENTITY_TOKEN_FILE)
        file = open(webtokenPath, mode='r')
        webtoken = file.read()
        file.close()

        response = client.assume_role_with_web_identity(
            RoleArn=role_arn,
            RoleSessionName=roleSessionName,
            WebIdentityToken=webtoken
        )
    else:
        raise Exception("Cannot authenticate with AWS secrets manager, ensure that you have set environment variables AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or AWS_WEB_IDENTITY_TOKEN_FILE")

    return (
            response['Credentials']['AccessKeyId'],
            response['Credentials']['SecretAccessKey'],
            response['Credentials']['SessionToken']
        )


@functools.lru_cache
def get_secret_value(creds, secret_arn):
    """
    Get secret value for a secret from AWS Secrets Manager.

    Return the secret value response.
    """
    print('Getting secrets for {}'.format(secret_arn))

    client = boto3.client('secretsmanager')

    if creds:
        client = boto3.client(
            'secretsmanager',
            aws_access_key_id=creds[0],
            aws_secret_access_key=creds[1],
            aws_session_token=creds[2]
        )

    return client.get_secret_value(SecretId=secret_arn)


def write_to_cf_volume(results):
    """
    Write environment variables that are to be exported in
    Codefresh.
    """
    with io.open('/meta/env_vars_to_export', 'a') as file:
        file.writelines(results)


def main():
    """
    Main entrypoint.
    """
    creds = ()

    if (aws_iam_role_arn := os.environ.get(AWS_ROLE_ARN)) and should_assume_role(aws_iam_role_arn):
        creds = assume_role(aws_iam_role_arn)

    secrets = os.environ.get(SECRETS) or []

    results = []

    for secret in secrets.split('|'):
        arn, key, store_to = secret.split('#')

        response = get_secret_value(creds, arn)

        print("Storing secret value for key '{}' into ${}".format(key, store_to))
        secret_string = json.loads(response['SecretString'])
        value = secret_string[key]

        results.append('{}={}\n'.format(store_to, value))

    write_to_cf_volume(results)


if __name__ == '__main__':
    main()
