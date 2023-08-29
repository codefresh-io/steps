# cf-azure-files-plugin

Plugin for pushing files to Azure Files service.

## Usage
Firstly provide all the required variables:  
- `ACCOUNT_NAME` - storage account name
- `ACCOUNT_KEY` - storage account key
- `SHARE_NAME` - file share name
- `PATH_TO_FILE` - path to your local file you are going to upload. It can start with `/` to resolve path from root, either file will be searched relatively to you repo.  

Also there are some optional variables: 
- `DIRECTORY` - path to directory to upload within the file share. Specify a target folder in format `fold1/fold2/fold3`. If not specified files will be uploaded to the file share root 
- `ADD_TIMESTAMP` - either add timestamp to filename or no

Example:

```
AZ_NAME=myname
AZ_ACCOUNT_KEY=random_key
AZ_SHARE_NAME=shared-resource1
AZ_DIRECTORY=foo/bar
AZ_PATH_TO_FILE=src/very_important_data.txt
AZ_ADD_TIMESTAMP=True
```

```yaml
  version: '1.0'
  ...
  steps:
    ...
    push_to_azure:
      title: Pushing to Azure files
      stage: azure
      image: codefresh/azure-files-plugin
      environment:
        - ACCOUNT_NAME=${{AZ_NAME}}
        - ACCOUNT_KEY=${{AZ_ACCOUNT_KEY}}
        - SHARE_NAME=${{AZ_SHARE_NAME}}
        - DIRECTORY=${{AZ_DIRECTORY}}
        - PATH_TO_FILE=${{AZ_PATH_TO_FILE}}
        - ADD_TIMESTAMP=${{AZ_ADD_TIMESTAMP}}
```

## Environment Variables

| Variables      | Required | Default | Description                                                                             |
|----------------|----------|---------|-----------------------------------------------------------------------------------------|
| ACCOUNT_NAME   | YES      |         | Storage account name                                                         |
| ACCOUNT_KEY    | YES      |         | Storage account key                                                          |
| SHARE_NAME     | YES      |         | File share name                            |
| DIRECTORY      | NO       | Share root | Path to directory within file share
| PATH_TO_FILE   | YES      |         | Local path to the file you are going to push 
| ADD_TIMESTAMP  | NO       |         | Fill with some truly (True) value if you need to attach time stamp to the file name                                                        

