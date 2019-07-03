# Makisu plugin

The plugin makes using [Makisu build tool](https://github.com/uber/makisu) easier in a Codefresh pipeline. 

### Requirements

The plugin requires access to the docker daemon enabled, so one have to request it from Codefresh administrators, unless the user uses a Hybrid solution (running builds on his own infrastructure.

### Basic usage

This example covers the most common case - to build and push an image using Makisu distributed cache and flexible layer generation features.

```
makisuBuildStep:
  image: codefresh/cfstep-makisu
  environment:
    - REGISTRY_HOSTNAME=docker.io
    - R_USER=my_username
    - R_PASSWORD=my_password
    - IMAGE_NAME_TAG=image/name:tag
```

By default the makisu context is the main clone directory, but it can be changed with the WORKING_DIRECTORY environment variable. The dockerfile path can also be specified by the DOCKERFILE variable

### Advanced usage

If a user needs more flexibility, it is not a problem to add custom flags to the makisu buildcommand:

```
....
  environment:
    - CUSTOM_FLAGS='--compression=speed ...' 
```

or to completely override the makisu command:

```
makisuBuildStep:
  image: codefresh/cfstep-makisu
  environment:
    - REGISTRY_HOSTNAME=docker.io
    - R_USER=my_username
    - R_PASSWORD=my_password
    - MAKISU_COMMAND='makisu build -t myimage/name:tag --storage /codefresh/volume/makisu --modifyfs=true --commit=explicit --registry-config=/makisu-internal/registry-conf.yml --push docker.io --compression=speed .'
```