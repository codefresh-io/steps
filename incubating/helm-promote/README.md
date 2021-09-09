# helm-promote

A Codefresh pipeline step to promote images and dependencies between helm charts in different directories and bump the chart version.

## Environment Variables

The following environment variables must be set:

- PROMOTE_IMAGES: A comma-seperated list of images keys to search for and replace between values.yamls
- PROMOTE_TO: The directory of the helm chart to get values from
- PROMOTE_FROM: The directory of the helm chart to insert values in to


The following environment variables are optional:
- BUMP_VERSION: The part of the version to bump (major|minor|patch). By default will bump 'patch'
- CHART_YAML: Will use 'Chart.yaml' by default
- FROM_CHART_YAML: The chart YAML name to use for the 'from' chart. Will use 'CHART_YAML' by default
- FROM_VALUES_YAML: The values YAML name to use for the 'from' chart. Will use 'VALUES_YAML' by default
- IMAGE_FORMAT: The format to search and replaces images with in the values yaml, replaces '{{IMAGE}}' with a PROMOTE_IMAGE at runtime. By default will use '{{IMAGE}}.image.tag'
- PROMOTE_SUBCHARTS: The dependency (sub)charts tags to search for and replace between Chart.yamls. Use this when your subchart name does not match your image name. By default will be the same as PROMOTE_IMAGES
- TO_CHART_YAML: The chart YAML name to use for the 'to' chart. Will use 'CHART_YAML' by default
- TO_VALUES_YAML: The values YAML name to use for the 'to' chart. Will use 'VALUES_YAML' by default
- VALUES_YAML: Will use 'values.yaml' by default

## Example

```yaml
HelmPromote:
    title: "Promote helm chart from dev to test"
    type: helm-promote
    arguments:
        PROMOTE_FROM: dev
        PROMOTE_TO: test
        PROMOTE_IMAGES: frontend,middleware,backend
```