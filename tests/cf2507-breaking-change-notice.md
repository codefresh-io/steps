# Breaking change notice: argument handling in the codefresh-run and helm steps

<!--
Draft for review. Customer-facing notice about the breaking change, sent before (or together with) the release.
It intentionally doesn't describe the vulnerability: the security details go to the advisory
(cf2507-security-advisory.md), published after the fix is released.
Fill in every [TBD] placeholder before sending.
-->

**Subject:** Action may be needed: the codefresh-run and helm pipeline steps change how they handle argument values on [TBD]

Hi,

On **[TBD release date]** we're releasing new versions of two official pipeline steps, **Run a Codefresh pipeline** (`codefresh-run` 1.7.0) and **Release a Helm chart** (`helm` 1.1.13), together with rebuilt `cfstep-helm` images. This is a security hardening change.

Most pipelines keep working without any changes. This notice helps you check whether yours need an update, and explains how to update them.

## What's changing

Until now, these steps passed their argument values through a shell before using them. The shell evaluated some characters in the values. After the update, the steps use argument values exactly as you write them.

| You write | Before the update | After the update |
|---|---|---|
| `${{MY_VAR}}` | The value of `MY_VAR` | No change: the value of `MY_VAR` |
| `$MY_VAR` or `${MY_VAR}` | The value of `MY_VAR` | The text `$MY_VAR` |
| `$(command)` or `` `command` `` | The output of the command | The text `$(command)` |
| `values-*.yaml` | The matching file names | The text `values-*.yaml` |
| `~/file` | The path in the home directory | The text `~/file` |
| `"main --no-cache"` in one argument | Several flags | One value: `main --no-cache` |

Quotes and escaped commas in Helm values keep working the same way. For example, `profiles_arr="{one,two,three}"` and `profiles_str="one\,two\,three"` are passed to Helm as before.

## Who's affected

Your pipeline needs an update if a `codefresh-run` or `helm` step has an argument that uses `$VAR`, `$(...)`, backticks, `*`, or `~`. For the `helm` step, this includes `custom_values`, `custom_value_files`, `cmd_ps`, `kube_context`, `namespace`, and `release_name`.

These pipelines get the new behavior:

- Pipelines that use `type: codefresh-run` or `type: helm` without a version, from [TBD release date].
- All `helm` step versions, because the rebuilt `cfstep-helm` images are published with the same tags.
- Pipelines that run a `cfstep-helm` image directly in a freestyle step.

## How to check your pipelines

1. Export the pipelines you store in Codefresh:

   ```bash
   codefresh get pipelines --limit 1000 -o yaml > pipelines.yaml
   ```

2. For pipelines stored in Git, check their `codefresh.yml` files in your repositories.
3. In each `codefresh-run` and `helm` step, look at the `arguments` for `$` (not followed by `{{`), `` ` ``, `*`, and `~`. For example:

   ```bash
   grep -nE '\$[A-Za-z_(]|\$\{[^{]|`' pipelines.yaml
   ```

   This also finds `$VAR` in the `commands` of freestyle steps. Those don't change, so you can ignore them.

You can also run a pipeline with the new step versions and look for a warning in the step log (see [Temporary option](#temporary-option) below).

## How to update your pipelines

| Before | After |
|---|---|
| `custom_values: [image_tag=$MY_TAG]` | `custom_values: [image_tag=${{MY_TAG}}]` |
| `VARIABLE: [IMAGE=$IMAGE_NAME]` | `VARIABLE: [IMAGE=${{IMAGE_NAME}}]` |
| `cmd_ps: --set version=$(cat VERSION)` | Read the file in a previous step: `cf_export VERSION=$(cat VERSION)`, then use `cmd_ps: --set version=${{VERSION}}` |
| `cmd_ps: --values values-*.yaml` | List the files in `custom_value_files` |
| `BRANCH: main --no-cache` | `BRANCH: main` and `NO_CACHE: true` |

Variables you export with `cf_export` are available as `${{VAR}}` in all later steps.

## Temporary option

If you need more time to update a pipeline, you can get the previous behavior back for that step:

| Step | Setting |
|---|---|
| `codefresh-run` 1.7.0 or later | `LEGACY_SHELL_EXPANSION: true` |
| `helm` 1.1.13 or later | `legacy_shell_expansion: true` |
| `cfstep-helm` image used directly | environment variable `LEGACY_SHELL_EXPANSION=true` |

For example:

```yaml
deploy:
  type: helm:1.1.13
  arguments:
    chart_name: my-chart
    release_name: my-release
    kube_context: my-cluster
    custom_values:
      - image_tag=$MY_TAG
    legacy_shell_expansion: true  # Temporary: remove after replacing $MY_TAG with ${{MY_TAG}}
```

When the option is enabled, the step log shows a warning with the names of the arguments that still need an update. If the warning says that no arguments use shell syntax, you can remove the option right away.

This option is for migration only. It's less secure, and we'll remove it on **[TBD removal date]**. Please update your pipelines before then.

Older `helm` step versions don't accept the new argument. To use it, upgrade the step to `helm` 1.1.13.

## Timeline

| Date | What happens |
|---|---|
| [TBD] | This notice |
| [TBD] | New step versions and rebuilt `cfstep-helm` images released |
| [TBD] | The temporary option is removed |

## Questions

If you have questions or need help updating your pipelines, contact [Codefresh support](https://support.codefresh.io).

Happy deployments!