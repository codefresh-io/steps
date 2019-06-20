{{#if failure}}
## Build failed
Failure on {{#each buildCauses}}`{{this}}` {{/each}}
{{else}}
## Build successful
{{/if}}
`{{buildInitiator}}` via _{{buildTrigger}}_  
repo **{{repoName}}** in `{{branch}}`  
```text
{{commitMessage}}
```
[**`> Build Details`**]({{buildUrl}})   
[`> Commit`]({{commitUrl}})
