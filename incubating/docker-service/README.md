# Codefresh docker-service plugin

Use Codefresh docker-service plugin to create docker daemon and then use run on it any of 
`docker build|run|...` or `docker-compose` on your repository

## codefresh/docker-service Docker Image details
includes `docker`, `docker-machine` and `docker-compose`

`docker-service-create` command accepts same parameters as `docker-machine create` (i.e --driver , --engine-opt, etc) and starts a docker daemon
on a provider specified by "--driver" parameter - see https://docs.docker.com/machine/reference/create/
Then it saves docker-machine environment files to Codefresh Volume, so every `docker` command will use this created docker daemon

`docker-service-delete` command deletes all previously created docker-machine environment

`docker-service-clean` commands deletes all docker-machine data from Codefresh image - just cleans ${MACHINE_STORAGE_PATH}/ directory

## Usage

Set environment variable and add the following step to your Codefresh pipeline:

```yaml
---
version: '1.0'

steps:

  ...

  # 
  create-my-docker:
    image: codefreshplugins/docker-service
    commands: 
        - docker-service-create  --driver amazonec2 --amazonec2-instance-type m4.large my-docker
    
  build-on-my-docker:
    image: codefreshplugins/docker-service
    commands:
        - docker build -t mycompany/repo:${{CF_BRANCH}} ${{CF_VOLUME_PATH}}/

  run-on-my-docker:
    image: codefreshplugins/docker-service
    commands:
        - docker run -d mycompany/repo:${{CF_BRANCH}}


  delete-my-docker:
     image: codefreshplugins/docker-service
     commands:
        - docker-service-delete my-docker

  clean:
     image: codefreshplugins/docker-service
     commands:
        - docker-service-clean
  ...

```
## Environment Variables

- DOCKER_MACHINE_NAME
- Codefresh variables: https://docs.codefresh.io/docs/variables
- docker-machine drivers envs: https://docs.docker.com/machine/drivers/
