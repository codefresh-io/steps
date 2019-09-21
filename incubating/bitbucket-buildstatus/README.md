# Bitbucket Build Status

## Description:
This plugin enables codefresh pipelines to update the Build Status of a commit in Commit.

Can be used to trigger pipelines for CI, Pull Request merge check etc.

## Usage

It can be used with two different approaches, as a docker image or as a Codefresh step.

### Parameters

Both, Codefresh step and docker image, are configurable through parameters in order to perform the action.

|Name|Required|Description|Available Options|
|----|--------|-----------|-----------------|
|BB_BSN_REPO_AUTH_USER|No|Bitbucket API Authorization Username|-|
|BB_BSN_REPO_AUTH_PASSWORD|Yes|Bitbucket API Authorization Password|-|
|BB_BSN_REPO_AUTH_PASSWORD|Yes|Build Status|`SUCCESSFUL` `FAILED` `INPROGRESS` `STOPPED`|

### Docker Image

#### Example

The following step can be used in any Codefresh pipeline and uses the docker image approach.

```yaml
version: '1.0'
steps:
    UpdateBuildStatus:
      image: codefreshplugins/bitbucket-buildstatus
      environment:
        - BB_BSN_REPO_AUTH_USER=${{BB_BSN_REPO_AUTH_USER}}
        - BB_BSN_REPO_AUTH_PASSWORD=${{BB_BSN_REPO_AUTH_USER}}
        - CF_BUILD_STATUS=${{CF_BUILD_STATUS}}
```

#### Advanced Example

Advanced usage is also available which updates Bitbucket Build Status.

```yaml
version: '1.0'
mode: parallel
steps:
    BB_Update_BuildStatus_InProgress:
    fail_fast: false
    image: codefreshplugins/bitbucket-buildstatus
    environment:
        - BB_BSN_REPO_AUTH_USER=${{BB_BSN_REPO_AUTH_USER}}
        - BB_BSN_REPO_AUTH_PASSWORD=${{BB_BSN_REPO_AUTH_USER}}
        - CF_BUILD_STATUS='INPROGRESS'

    ## [Some more steps...]

    BB_Update_BuildStatus_Finished:
    type: parallel
    fail_fast: false
    when:
        condition:
        all:
            myCondition: workflow.result == 'finished'
    steps:
        BB_Update_BuildStatus_Successful:
            image: codefreshplugins/bitbucket-buildstatus
            when:
                condition:
                all:
                    myCondition: workflow.result == 'success'
            environment:
                - BB_BSN_REPO_AUTH_USER=${{BB_BSN_REPO_AUTH_USER}}
                - BB_BSN_REPO_AUTH_PASSWORD=${{BB_BSN_REPO_AUTH_USER}}
                - CF_BUILD_STATUS=SUCCESSFULL
        BB_Update_BuildStatus_Failed:
            image: codefreshplugins/bitbucket-buildstatus
            when:
                condition:
                all:
                    myCondition: workflow.result == 'failure'
            environment:
                - BB_BSN_REPO_AUTH_USER=${{BB_BSN_REPO_AUTH_USER}}
                - BB_BSN_REPO_AUTH_PASSWORD=${{BB_BSN_REPO_AUTH_USER}}
                - CF_BUILD_STATUS='FAILED'
```

### Codefresh Step

Also, a Codefresh step is available to use which uses docker image `codefreshplugins/bitbucket-buildstatus`

#### Example


```yaml
version: '1.0'
steps:
    BB_Update_BuildStatus:
    type: bitbucket-buildstatus
    arguments:
        BB_BSN_REPO_AUTH_USER: ${{BB_BSN_REPO_AUTH_USER}}
        BB_BSN_REPO_AUTH_PASSWORD: ${{BB_BSN_REPO_AUTH_USER}}
        CF_BUILD_STATUS: ${{CF_BUILD_STATUS}}

```

#### Advanced Example

```yaml
version: '1.0'
mode: parallel
steps:
    BB_Update_BuildStatus_InProgress:
    type: bitbucket-buildstatus
    fail_fast: false
    arguments:
        BB_BSN_REPO_AUTH_USER: ${{BB_BSN_REPO_AUTH_USER}}
        BB_BSN_REPO_AUTH_PASSWORD: ${{BB_BSN_REPO_AUTH_USER}}
        CF_BUILD_STATUS: 'INPROGRESS'

    ## [Some more steps...]
    
    BB_Update_BuildStatus_Finished:
    type: parallel
    fail_fast: false
    when:
        condition:
        all:
            myCondition: workflow.result == 'finished'
    steps:
        BB_Update_BuildStatus_Successful:
            type: bitbucket-buildstatus
            when:
                condition:
                all:
                    myCondition: workflow.result == 'success'
            arguments:
                BB_BSN_REPO_AUTH_USER: ${{BB_BSN_REPO_AUTH_USER}}
                BB_BSN_REPO_AUTH_PASSWORD: ${{BB_BSN_REPO_AUTH_USER}}
                CF_BUILD_STATUS: 'SUCCESSFULL'
        BB_Update_BuildStatus_Failed:
            type: bitbucket-buildstatus
            when:
                condition:
                all:
                    myCondition: workflow.result == 'failure'
            arguments:
                BB_BSN_REPO_AUTH_USER: ${{BB_BSN_REPO_AUTH_USER}}
                BB_BSN_REPO_AUTH_PASSWORD: ${{BB_BSN_REPO_AUTH_USER}}
                CF_BUILD_STATUS: 'FAILED'

```

## Maintainers


[Yiannis Demetriades](https://github.com/ydemetriades)
