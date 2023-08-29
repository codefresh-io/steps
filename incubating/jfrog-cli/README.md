# jfrog-cli

A Codefresh pipeline step to publish build information to JFrog Artifactory.

To add a Docker image to the build publish this requires either Hybrid or Dedicated Runtime.
This requirement is due to the fact a Docker daemon must be available to complete Docker commands used by JFrog CLI.

There is also and option to scan your published build using JFrog Xray.
If the build does not pass Security Policy the build will fail.