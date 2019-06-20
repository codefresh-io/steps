# cfstep-bintray
A Codefresh freestyle step to manage releases in JFrog Bintray

The plugin is available at Dockerhub at [https://hub.docker.com/r/codefresh/cfstep-bintray/](https://hub.docker.com/r/codefresh/cfstep-bintray/)

## Blog post

More details are available in the [Codefresh blog post](https://codefresh.io/devops-tutorial/deploying-to-jfrog-bintray/)

## Example usage

The plugin supports every command supported by the [JFrog CLI](https://www.jfrog.com/confluence/display/CLI/CLI+for+JFrog+Bintray)

Here is an example for Downloading from Bintray with the `dlv` command (Download version)

```
 DownloadNewVersion:
    stage: 'Bintray download'
    title: Download from Bintray
    image: codefreshplugins/cfstep-bintray:master
    working_directory: download-example/
    environment:
      - BINTRAY_COMMAND=dlv
      - BINTRAY_ARGS= codefresh-demo/test/cf-demo/v4.0 --unpublished
```

The following environment variables are expected to be present:

* `BINTRAY_USER` - username for Bintray
* `BINTRAY_KEY` - API key for bintray
