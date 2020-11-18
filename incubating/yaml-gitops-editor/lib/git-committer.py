import requests
import json
import os
from github import Github
from github import InputGitTreeElement
from git import Repo


def get_credentials(codefresh_url, codefresh_api_token, git_context):
    url = '{}/api/contexts/{}?decrypt=true'.format(codefresh_url, git_context)

    payload = {}
    headers = {
    'Authorization': 'Bearer {}'.format(codefresh_api_token),
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    return response


def main():

    branch = os.getenv('CF_BRANCH')
    codefresh_api_token = os.getenv('CF_API_KEY')
    codefresh_build_id = os.getenv('CF_BUILD_ID')
    codefresh_url = os.getenv('CODEFRESH_URL')
    create_pull_request = os.getenv('CREATE_PULL_REQUEST')
    directory = os.getenv('CF_VOLUME_PATH')
    git_context = os.getenv('GIT_CONTEXT')
    organization = os.getenv('CF_REPO_OWNER')
    repository = os.getenv('CF_REPO_NAME')
    revision = os.getenv('CF_REVISION')
    target_branch = os.getenv('TARGET_BRANCH')
    yaml_file = os.getenv('YAMLFILE')
    yaml_path = os.path.join(directory, repository, yaml_file)

    # Fetch GIT Creedentials
    context_response = get_credentials(codefresh_url, codefresh_api_token, git_context)
    json_data = json.loads(context_response.text)

    repo_dir = os.path.join(directory, repository)
    repo = '{}/{}'.format(organization, repository)

    if json_data['spec']['type']  == 'git.github':
        # PyGitHub Auth
        token = json_data['spec']['data']['auth']['password']
        g = Github(token)

        # Set repository
        repo = g.get_repo(repo)

        # Create commit
        target_file = (yaml_file)

        commit_message = 'Commit created by Codefresh Build: {}'.format(codefresh_build_id)

        original_contents = repo.get_contents(target_file, ref=revision)

        new_contents = open(yaml_path, 'r').read()

        repo.update_file(original_contents.path, commit_message, new_contents, original_contents.sha, branch=branch)

    # Basic Auth option for later
    # else:
    #     # Set repository
    #     repo = Repo(repo_dir)

    #     repo.git.checkout(branch)

    #     # Create commit
    #     file_list = [
    #         os.path.join(repo_dir, yaml_file)
    #     ]
    #     commit_message = 'Commit created by Codefresh Build: {}'.format(codefresh_build_id)
    #     repo.index.add(file_list)
    #     repo.index.commit(commit_message)

    #     # Push commit
    #     origin = repo.remote('origin')
    #     origin.push()

    if create_pull_request:
        # Create pull request
        create_pull = repo.create_pull(title='Pull Request from Codefresh GitOps Committer Step, Build ID: {}'.format(codefresh_build_id), head=branch, base=target_branch, body='Automated Pull Request from Codefresh Build: {}'.format(codefresh_build_id), maintainer_can_modify=True)

        # Get pull request information
        print('Created Pull Request: {}'.format(repo.get_pull(create_pull.number)))


if __name__ == "__main__":
    main()