import os
import sys
from sonarqube import SonarCloudClient
from sonarqube import SonarQubeClient
import json


def exportResults(status): 
    print("\nExporting Results")

    qualitygates_status_json = json.dumps(status) 
    qualitygates_status= status['projectStatus']['status']

    env_file_path = "/meta/env_vars_to_export"

    if not os.path.exists(env_file_path):
        print(f"Quality Gates status is \n'{qualitygates_status}'")     
        print(f"Quality Gates status JSON is \n'{qualitygates_status_json}'")        
        # for current_secret in formatted_secrets:            
        #     print(current_secret.export_name + "=" + current_secret.secret_value)
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
    qualitygates_status = 'ERROR'
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
    branch = os.getenv('CF_BRANCH', 'main')
    sonar_project = os.getenv('SONAR_PROJECT_KEY')
    sonarcloud_token = os.getenv('SONAR_TOKEN')
    sonarqube_password = os.getenv('SONAR_PASSWORD')
    sonarqube_username = os.getenv('SONAR_USERNAME')
    sonar_url = os.getenv('SONAR_HOST_URL', 'https://sonarcloud.io')

    if sonarcloud_token:
        sonar = SonarCloudClient(sonarcloud_url=sonar_url, token=sonarcloud_token)
    else:
        sonar = SonarQubeClient(sonarqube_url=sonar_url, username=sonarqube_username, password=sonarqube_password)

    # Code: https://github.com/shijl0925/python-sonarqube-api/blob/376cf1d6ef231ee084694c77dadf551733395d4f/sonarqube/community/qualitygates.py#L182
    # Docs: https://python-sonarqube-api.readthedocs.io/en/1.2.1/examples/qualitygates.html#
    qualitygates_status = sonar.qualitygates.get_project_qualitygates_status(projectKey=sonar_project, branch=branch)
    exportResults(qualitygates_status)
    actBasedOnStatus(qualitygates_status)

if __name__ == "__main__":
    main()