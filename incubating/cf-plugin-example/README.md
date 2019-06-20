# cf-plugin-example
## Codefresh Plugin Example

### Description:
This is an example plugin for use in Codefresh freestyle steps.

The plugin expects one environment variable as input: PLUGIN_RESULT.

If PLUGIN_RESULT is set to SUCCESS - the plugin will return a success return code.

If PLUGIN_RESULT is set to anything else  - plugin will fail.

This sample plugin is also using Codefresh built-in variable CF_ACCOUNT to output the name of the Codefresh account that the calling pipeline belongs to.

Look here for the list of available variables: https://codefresh.io/docs/docs/codefresh-yaml/variables/

### Example of usage:
```yaml
version: '1.0'
steps:
  use_plugin:
    image: codefresh/plugin-example
    working_directory: ${{main_clone}}
    description: Example plugin
    environment:
      - PLUGIN_RESULT=SUCCESS
