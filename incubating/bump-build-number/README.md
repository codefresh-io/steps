# Codefresh Bump Build Number

This step will help you maintain a build number [annotation](https://codefresh.io/docs/docs/codefresh-yaml/annotations/) at the pipeline level. The build number will be updated every time that the step is executed using the codefresh CLI. It is strongly recommended that you add a conditional expression to only increment the build number on a certain branch.

The build number is exported for future step use to the following variable: CF_BUILD_NUMBER

## Prerequisites

- If you want to seed the build number at something other than 1, create an annotation with the name of your choice at the pipeline level and set it appropriately

## Important Notes
- Annotations must be deleted from the CLI
- Annotations can be updated in the UI by creating an annotation with the same name and type with a new value

### Step arguments

Name|Required|Description
---|---|---
ANNOTATION_NAME | No | Can customize the name of the build number annotation

### Codefresh.yml

```yaml
version: '1.0.0'
steps:
  BumpBuildNumber:
    title: Bump Build Number
    type: bump-build-number
    arguments:
      ANNOTATION_NAME: '${{CF_BRANCH}}'
```