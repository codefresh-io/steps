# Codefresh webhook plugin

Plugin which simply send notification 

## Using example

send basic variables
```yaml
version: '1.0'
fail_fast: false
...
steps:
  ...
  TestPlugin:
    title: TestPlugin
    image: codefreshplugins/cf-webhook:latest
    environment: 
        - "WEBHOOK_URL=http://example.com/api/endpoint"
```

send custom request
```yaml
version: '1.0'
fail_fast: false
...
steps:
  ...
  TestPlugin:
    title: TestPlugin
    image: codefreshplugins/cf-webhook:latest
    environment: 
        - "WEBHOOK_URL=http://example.com/api/endpoint"
        - "HEADER_Content-Type=plain/text"
        - "HEADER_X-Auth-Token={{apiKey}}"
        - "WEBHOOK_URL={{status}}"
```

## Required variables

- `WEBHOOK_URL` - webhook uri

## Optional variables

- `WEBHOOK_METHOD` - HTTP method (GET, POST, PUT, PATCH), default: **POST**
- Auth
  - **HTTP Basic Authentication** 
    - `WEBHOOK_USERNAME` - username 
    - `WEBHOOK_PASSWORD` - password
  - **HTTP Token**
    - `WEBHOOK_TOKEN` - token will be provided in header *Authorization*
- `WEBHOOK_BODY` - body of http request, default: JSON with [full variables list](#variables)    
- `HEADER_headerName` - provide headers for request, example: `HEADER_Content-type`, `HEADER_X-Auth-Token`,   
default **HEADER_Content-Type=application/json**
- `QUERY_paramName` - provide variables into queryString, example: `QUERY_id`, `QUERY_name` will be processed as `/?id=xxx&name=yyy` 


## Variables
In **HEADER**, **QUERY** and **WEBHOOK_BODY** variables you can use next templates constants
- `{{build.trigger}}` 
- `{{build.initiator}}`  
- `{{build.id}}` 
- `{{build.timestamp}}`  
- `{{build.url}}` 
- `{{repo.owner}}`  
- `{{repo.name}}`  
- `{{branch}}` 
- `{{revision}}`  
- `{{commit.author}}` 
- `{{commit.url}}` 
- `{{commit.message}}`
- `{{status}}` - build status
- `{{causes}}` - build failed causes  
