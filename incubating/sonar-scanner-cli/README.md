# sonar-scanner-cli

Requires sonarqube.properties file as command line args are not supported by CLI developers at this time.

See: https://github.com/SonarSource/sonar-scanner-cli-docker/pull/50

sonar-project.properties

https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/

```
# must be unique in a given SonarQube instance
sonar.projectKey=my:project

# --- optional properties ---

# defaults to project key
#sonar.projectName=My project
# defaults to 'not provided'
#sonar.projectVersion=1.0
 
# Path is relative to the sonar-project.properties file. Defaults to .
#sonar.sources=.
 
# Encoding of the source code. Default is default system encoding
#sonar.sourceEncoding=UTF-8
```

Based on: 

GIT 

- https://github.com/SonarSource/sonar-scanner-cli-docker
- https://github.com/SonarSource/sonar-scanner-cli

DockerHub - https://hub.docker.com/r/sonarsource/sonar-scanner-cli

Documentation - https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
