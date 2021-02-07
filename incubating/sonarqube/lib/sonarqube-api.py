import os
from sonarqube import SonarCloudClient
from sonarqube import SonarQubeClient

branch = os.getenv('CF_BRANCH')
project = os.getenv('PROJECT')
sonarcloud_token = os.getenv('SONARCLOUD_TOKEN')
sonarqube_password = os.getenv('SONARQUBE_PASSWORD')
sonarqube_username = os.getenv('SONARQUBE_USERNAME')
sonarqube_url = os.getenv('SONARQUBE_URL', 'https://sonarcloud.io')

if sonarcloud_token:
    sonar = SonarCloudClient(sonarcloud_url=sonarqube_url, token=sonarcloud_token)
else:
    sonar = SonarQubeClient(sonarqube_url=sonarqube_url, username=sonarqube_username, password=sonarqube_password)

qualitygates_status = sonar.qualitygates.get_project_qualitygates_status(projectKey=project, branch=branch)

print(qualitygates_status)
