# Security advisory: command injection in the codefresh-run and helm pipeline steps

<!--
Draft for review. Before publishing:
- Fill in every [TBD] placeholder (advisory ID, CVE, dates, fixed image release date, credit).
- Confirm the severity with the security team.
- Publish only after the fixed step versions are released and all cfstep-helm images are rebuilt.
- Keep exploit details out: this advisory intentionally doesn't include payloads or details from the pentest report.
-->

| | |
|---|---|
| **Advisory ID** | [TBD] |
| **CVE** | [TBD] |
| **Severity** | High |
| **Published** | [TBD] |
| **Affected products** | Codefresh pipelines (SaaS, hybrid, and on-premises) that use the `codefresh-run` or `helm` steps |
| **Internal reference** | CF-2507 |

## Summary

We found and fixed a command injection issue in two official Codefresh pipeline steps: **Run a Codefresh pipeline** (`codefresh-run`) and **Release a Helm chart** (`helm`).

Both steps built shell commands from their arguments without escaping them. When a pipeline passes data that someone outside your team can control, such as a Git branch name or a commit message, to one of these arguments, that person can run their own commands in the pipeline build. They only need permission to push to a repository that triggers the pipeline. They don't need a Codefresh account.

A successful attack runs with the permissions of the pipeline build. This includes access to the Codefresh API key of the user or service account that runs the pipeline, and to any secrets, registries, and clusters the build can reach.

We aren't aware of this issue being exploited. We recommend that you upgrade as soon as possible.

## Are you affected?

You're affected if **all** of the following are true:

1. A pipeline uses the `codefresh-run` step at version 1.6.0 or earlier, or the `helm` step at version 1.1.12 or earlier, or runs a `cfstep-helm` image directly as a freestyle step.
2. At least one step argument contains a value that someone outside your team can influence. Common examples:
   - `${{CF_BRANCH}}`, `${{CF_COMMIT_MESSAGE}}`, `${{CF_PULL_REQUEST_TITLE}}`, or other `${{CF_PULL_REQUEST_*}}` variables
   - variables derived from Git data, webhook payloads, or other external input
3. The pipeline runs automatically for that input, for example a Git trigger that runs on any branch (the default branch filter is `/.*/gi`).

The documented `codefresh-run` example uses `BRANCH: '${{CF_BRANCH}}'`. If your pipelines follow this example and use a Git trigger, assume you're affected.

| Step | Affected arguments |
|---|---|
| `codefresh-run` | `PIPELINE_ID`, `TRIGGER_ID`, `BRANCH`, `SHA`, `RUNTIME_NAME`, `PACK_NAME`, `VARIABLE`, `SECRETS`, `VARIABLE_FILE`, `CONTEXT`, `ONLY`, `SKIP`, `YAML`, and `TIMEOUT_MINS` |
| `helm` | All string arguments, including `kube_context`, `release_name`, `namespace`, `chart_name`, `chart_version`, `custom_values`, `custom_value_files`, `cmd_ps`, and repository URLs |

## Fixed versions

| Component | Fixed version |
|---|---|
| `codefresh-run` step | 1.7.0 |
| `helm` step | 1.1.13 |
| `quay.io/codefreshplugins/cfstep-helm` images | All tags rebuilt on [TBD] |
| `quay.io/codefreshplugins/cfstep-helm-debian` images | All tags rebuilt on [TBD] |

The fixed steps pass argument values to the container as environment variables and never place them in a shell command. The `cfstep-helm` images escape every value they add to the generated Helm commands.

## What you need to do

### SaaS and hybrid runtimes

1. **Pipelines that don't pin a step version** (`type: codefresh-run`, `type: helm`) use the fixed versions automatically. Check them for the [behavior changes](#behavior-changes) below.
2. **Pipelines that pin a step version** (for example `type: codefresh-run:1.6.0` or `type: helm:1.1.12`): update them to `codefresh-run:1.7.0` and `helm:1.1.13` or later, or remove the version to always use the latest one.
3. **Pipelines that run `cfstep-helm` images directly**: pull the image again. If you pin the image by digest, or copy it to your own registry, update the digest or mirror the rebuilt image.

The rebuilt `cfstep-helm` images also protect older `helm` step versions from command injection. We still recommend upgrading to `helm` 1.1.13, because older versions of the step template can let a crafted value add unexpected settings to the generated step.

### If a pipeline stops working after the upgrade

If a pipeline relies on the shell evaluating argument values (see [Behavior changes](#behavior-changes)), you can temporarily get the previous behavior back while you update it:

| Step | Setting |
|---|---|
| `codefresh-run` 1.7.0 or later | `LEGACY_SHELL_EXPANSION: true` |
| `helm` 1.1.13 or later | `legacy_shell_expansion: true` |
| `cfstep-helm` image used directly | environment variable `LEGACY_SHELL_EXPANSION=true` |

When the option is enabled, the step log shows a warning with the names of the arguments that still use shell syntax. Update those arguments, then remove the option.

> **Warning:** this option brings the vulnerability back for that step. Use it only for pipelines that don't receive values from outside your team, and only for as long as you need to migrate. We'll remove the option in a later version of the steps.

Older `helm` step versions don't accept the new argument. To use it, upgrade the step to `helm` 1.1.13.

### On-premises installations

In addition to the steps above, make sure your installation uses the rebuilt `cfstep-helm` and `cfstep-helm-debian` images. If you mirror images to a private registry, mirror them again after [TBD].

### Check for signs of abuse

If you were affected, review recent builds of pipelines that use these steps:

- Look for builds triggered by branch names or commit messages that contain shell characters, such as `$(`, backticks, `;`, `|`, or `&&`.
- Look for unexpected network connections or commands in the logs of the `codefresh-run` and `helm` steps.

If you find anything suspicious, rotate the Codefresh API keys of the users and service accounts that run those pipelines, and rotate any secrets the affected builds could access.

## Behavior changes

The fix changes how argument values are handled. Most pipelines keep working without changes. Check your pipelines if they rely on any of the following. Until you update them, you can use the [temporary option](#if-a-pipeline-stops-working-after-the-upgrade) to keep the previous behavior.

- **Shell expansion in arguments.** `$VAR`, `$(...)`, backticks, wildcards (`*`), and `~` are now passed literally. Use Codefresh variables (`${{VAR}}`) instead. The engine replaces them before the step runs, the same way as before. Variables you export with `cf_export` are available as `${{VAR}}` in later steps.
- **Several flags in one `codefresh-run` argument.** For example, `BRANCH: "main --no-cache"` now passes the whole value as the branch name. Use the dedicated arguments, such as `NO_CACHE: true`, instead.
- **`cmd_ps` in the `helm` step.** Quotes still work as before (`--description "my release"`), but shell operators and expansions are passed to Helm literally.

Some values that didn't work before now work correctly. These include `codefresh-run` variables with spaces, and `helm` values that contain `;`, spaces, or apostrophes. Quotes and escaped commas in `custom_values`, such as `pat.arr="{one,two,three}"` or `key="one\,two"`, keep working the same way.

The `codefresh-run` step also no longer prints secret values in the "Executing command" line of the build log.

## Workarounds

If you can't upgrade right away:

- Don't pass Git-derived values to the affected arguments. If you need a branch name, use `${{CF_BRANCH_TAG_NORMALIZED}}` instead of `${{CF_BRANCH}}`. It contains only characters that are valid in a Docker image tag, so it can't be used to inject commands. Don't rely on the `*_ESCAPED` variables for this: they aren't designed to make values safe for a shell.
- Restrict Git triggers to the branches you trust, instead of the default `/.*/gi` filter.
- Limit who can push to repositories that trigger pipelines with these steps.

## Timeline

| Date | Event |
|---|---|
| [TBD] | Issue reported during a security assessment |
| [TBD] | Fixed step versions released |
| [TBD] | All `cfstep-helm` images rebuilt |
| [TBD] | Advisory published |
| [TBD] | `LEGACY_SHELL_EXPANSION` / `legacy_shell_expansion` option removed |

## Credit

[TBD: confirm with the reporter whether and how they want to be credited.]

## Questions

If you have questions about this advisory, contact [Codefresh support](https://support.codefresh.io).