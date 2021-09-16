# pipeline-trigger-merge

A Codefresh pipeline step to merge a pipeline spec with a list of triggers. Then create (or update) the pipeline in Codefresh from the merged spec file.

## Environment Variables

The following environment variables must be set

- SPEC: the filename of the pipeline spec.
- TRIGGERS: a space separated list of files and directories. All files in the directories will be included recursively. Unknown files will be ignored. The trigger files must be following the format:
```
spec:
  triggers:
    - name: TRIG_NAME
    ...
```

Can also be run in a mode where changes from the last commit are applied.
- SPEC: The filename of the pipeline spec
- ONLY_CHANGED: Enabled this mode. Loop through changed files from git instead of applying a single spec.
- TRIGGERS_SUBDIR: The subdirectory that holds a pipeline's triggers if looping. Defaults to 'triggers'.


## Example

```yaml
CreatePipeline:
  title: "Creating pipeline"
  type: pipeline-trigger-merge
  working_directory: ${{Clone}}
  stage: clone
  arguments:
    TRIGGERS: trig1.yml trig2.yml ./trigger_dir
    SPEC: spec.yml
```

There is a full example in the sample directory.

The foobar trigger does not exist and should give a warning
creator.yml is the main pipeline to create/merge the spec and the triggers.

Example of "ONLY_CHANGED" mode:
```yaml
MergeTriggersIntoPipelines:
  title: "Merge the triggers into the pipeline spec(s)"
  type: pipeline-trigger-merge
  working_directory: ${{Clone}}
  arguments:
    SPEC: spec.yml
    ONLY_CHANGED: true
    TRIGGERS_SUBDIR: "triggers"
```