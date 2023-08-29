# Trigger Jenkins Job

The plugin is to facilitate a single task - trigger a Jenkins job from a Codefresh pipeline

NAME:
   run-jenkins-jobs

DESCRIPTION:
   Trigger Jenkins Job

## Mandatory Parameters:

    jenkins_url     - Jenkins Master URL
    jenkins_username    - Jenkins User Name
    jenkins_token   - Jenkins Token
    jenkins_job_name     - Jenkins Job Name
    jenkins_parameterized_job - Jenkins job type(true/false)
    jenkins_build_params   - Jenkins parameters for parameterized job

## Usage Example:

version: '1.0'
steps:
   RunJenkins:
      title: Triggering Jenkins Job
      type: run-jenkins-jobs
      arguments:
      jenkins_url: 'http://yourjenkins.com:80'
      jenkins_token: usertoken
      jenkins_job_name: jobname2
      jenkins_username: username
      jenkins_parameterized_job: true
      jenkins_build_params:
         - KEY1=VAL1
         - KEY2=VAL2
         - KEY3=VAL3
