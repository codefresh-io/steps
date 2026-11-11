import os
import sys
import json
import requests


def exportResults(status): 
    print("\nExporting Results")

    qualitygates_status_json = json.dumps(status) 
    qualitygates_status= status['projectStatus']['status']

    env_file_path = "/meta/env_vars_to_export"

    if not os.path.exists(env_file_path):
        print(f"Quality Gates status is \n'{qualitygates_status}'")     
        print(f"Quality Gates status JSON is \n'{qualitygates_status_json}'")        
    else:
        env_file = open(env_file_path, "a")
        qualitygates_status_json_file_path = f"/codefresh/volume/sonarqualitygates-{os.getenv('CF_SHORT_REVISION')}.json"          
        env_file.write("SONAR_QUALITYGATES_STATUS=" + qualitygates_status + "\n")
        env_file.write("SONAR_QUALITYGATES_STATUS_JSON_PATH=" + qualitygates_status_json_file_path + "\n")
        env_file.close()

        qualitygates_status_json_file = open(qualitygates_status_json_file_path, "w") 
        json.dump(status, qualitygates_status_json_file, indent = 4) 
        qualitygates_status_json_file.close() 

def actBasedOnStatus(status):
    qualitygates_status = status['projectStatus']['status']
    if qualitygates_status == 'ERROR':
        print(f"Quality Gates status is '{qualitygates_status}'. FAILLING THE PROCESS")
        print(f'This the full Quality Gate report:\n { json.dumps(status, indent=4, sort_keys=True) }')
        sys.exit(1)
    if qualitygates_status == 'WARN':
        print(f"Quality Gate status is '{qualitygates_status}'.")
        print(f'This the full Quality Gate report:\n { json.dumps(status, indent=4, sort_keys=True) }')

    if qualitygates_status == 'OK':
        print(f"Quality Gate status is '{qualitygates_status}'.")


def main():
    branch = os.getenv('CF_BRANCH', None)
    pr = os.getenv('CF_PULL_REQUEST_NUMBER', None)
    sonar_project = os.getenv('SONAR_PROJECT_KEY')
    sonarcloud_token = os.getenv('SONAR_TOKEN')
    sonarqube_password = os.getenv('SONAR_PASSWORD')
    sonarqube_username = os.getenv('SONAR_USERNAME')
    sonar_url = os.getenv('SONAR_HOST_URL', 'https://sonarcloud.io')

    # Same request and auth as python-sonarqube-api 1.2.1, which this step used before:
    # a token goes as the basic-auth login with an empty password; otherwise username/password.
    if sonarcloud_token:
        auth = (sonarcloud_token, "")
    elif sonarqube_username and sonarqube_password:
        auth = (sonarqube_username, sonarqube_password)
    else:
        auth = None

    if pr is not None:
        print(f"PR Quality Gate for PR #{pr}")
        branch = None # since the QG check accepts only branch or PR

    # Docs: https://next.sonarqube.com/sonarqube/web_api/api/qualitygates/project_status
    # requests drops parameters whose value is None, so only one of branch/pullRequest is sent.
    url = sonar_url.rstrip("/") + "/api/qualitygates/project_status"
    params = {"projectKey": sonar_project, "branch": branch, "pullRequest": pr}
    try:
        response = requests.get(url, params=params, auth=auth, timeout=60)
    except requests.exceptions.RequestException as exc:
        print(f"Failed to call {url}: {exc}")
        sys.exit(1)
    if not response.ok:
        print(f"Failed to get Quality Gates status: HTTP {response.status_code} from {url}\n{response.text}")
        sys.exit(1)
    qualitygates_status = response.json()
    exportResults(qualitygates_status)
    actBasedOnStatus(qualitygates_status)

if __name__ == "__main__":
    main()