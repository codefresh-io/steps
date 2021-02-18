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

## Example

```
create_pipeline:
  title: "Creating pipeline"
  image: lrochette/ptm:pipeline_trigger_merge
  working_directory: ${{clone}}
  stage: clone
  commands:
    - /merge.sh
  environment:
    - TRIGGERS=trig1.yml trig2.yml ./trigger_dir
    - SPEC=spec.yml
```

There is a full example in the sample directory.

The foobar trigger does not exist and should give a warning
creator.yml is the main pipeline to create/merge the spec and the triggers.
