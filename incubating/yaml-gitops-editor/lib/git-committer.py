import fileinput
import requests
import json
import os
import random
import sys
import subprocess
import time
from github import Github
from git import Repo


def run_command(full_command):
    proc = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.communicate()
    print(output)
    if proc.returncode != 0:
        sys.exit(1)
    return b''.join(output).strip().decode()  # only save stdout into output, ignore stderr

# def pr_merge(github_token):
#     g = Github(github_token)

def get_credentials(codefresh_url, codefresh_api_token, git_context):
    url = '{}/api/contexts/{}?decrypt=true'.format(codefresh_url, git_context)

    payload = {}
    headers = {
    'Authorization': 'Bearer {}'.format(codefresh_api_token),
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    return response


def main():

    branch = os.getenv('BRANCH')
    codefresh_api_token = os.getenv('CF_API_TOKEN')
    codefresh_build_id = os.getenv('CF_BUILD_ID')
    codefresh_url = os.getenv('CODEFRESH_URL')
    create_pull_request = os.getenv('CREATE_PULL_REQUEST')
    directory = os.getenv('CF_VOLUME_PATH')
    git_context = os.getenv('GIT_CONTEXT')
    organization = os.getenv('CF_REPO_OWNER')
    repository = os.getenv('CF_REPO_NAME')
    target_branch = os.getenv('TARGET_BRANCH')
    yaml_file = os.getenv('YAMLFILE')

    # Fetch GIT Creedentials
    context_response = get_credentials(codefresh_url, codefresh_api_token, git_context)
    json_data = json.loads(context_response.text)

    if json_data['spec']['type']  == 'git.github':
        token = json_data['spec']['data']['auth']['password']

        # Create commit
        repo_dir = os.path.join(directory, repository)
        repo = Repo(repo_dir)

        file_list = [
            os.path.join(repo_dir, yaml_file)
        ]
        commit_message = 'Commit created by Codefresh Build: {}'.format(codefresh_build_id)
        repo.index.add(file_list)
        repo.index.commit(commit_message)

        # Push commit
        origin = repo.remote('origin')
        origin.push()

        if create_pull_request:
            # PyGitHub Auth
            g = Github(token)



            # Set repo
            repo = g.get_repo('{}/{}'.format(organization, repository))
            # Create pull request
            create_pull = repo.create_pull(title='Pull Request from Codefresh GitOps Committer Step, Build ID: {}'.format(codefresh_build_id), head=branch, base=target_branch, body='Automated Pull Request from Codefresh Build: {}'.format(codefresh_build_id), maintainer_can_modify=True)

            # Get pull request information
            print('Created Pull Request: {}'.format(repo.get_pull(create_pull.number)))


if __name__ == "__main__":
    main()