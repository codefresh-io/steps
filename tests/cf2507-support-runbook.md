# Support runbook: codefresh-run and helm steps no longer evaluate shell syntax in arguments

<!--
Internal. For the support team. Fill in every [TBD] placeholder before sharing.
Customer-facing texts: cf2507-breaking-change-notice.md (breaking change notice) and
cf2507-security-advisory.md (security advisory, published after the release).
-->

| | |
|---|---|
| **Released** | [TBD] |
| **Affected steps** | `codefresh-run` 1.7.0 and later; `helm` (all versions) after the `cfstep-helm` images were rebuilt on [TBD]; `cfstep-helm` / `cfstep-helm-debian` images used directly |
| **Temporary option removed on** | [TBD] |
| **Escalation** | [TBD: team / channel] |

## What changed

As a security fix, the `codefresh-run` and `helm` steps now use argument values exactly as written. Before, the values went through a shell, which evaluated `$VAR`, `$(...)`, backticks, wildcards (`*`), and `~`. Pipelines that relied on this get the literal text now, for example `$MY_TAG` instead of `1.2.3`.

`${{VAR}}` (Codefresh variables) works exactly as before.

## How to identify the issue

It's most likely this issue if **all** of the following are true:

1. The failing step is `codefresh-run` or `helm`, or a freestyle step that uses a `cfstep-helm` image.
2. The pipeline worked before [TBD release date] and its YAML didn't change.
3. A step argument contains `$` that isn't part of `${{...}}`, a backtick, `*`, or `~`.

Typical symptoms:

| Step | What the customer sees |
|---|---|
| `helm` | Values contain the literal text, e.g. image `my-repo:$MY_TAG` and `InvalidImageName` in Kubernetes |
| `helm` | `no context exists with the name: "$MY_CONTEXT"` |
| `helm` | `open values-*.yaml: no such file or directory` |
| `helm` | Helm complains about unexpected arguments when `cmd_ps` contains `;`, `&&`, or `\|` |
| `helm` | `Failed to parse CMD_PS: No closing quotation` (new error, `cmd_ps` has an unclosed quote) |
| `codefresh-run` | The child pipeline receives `$VAR` as a variable value instead of the real value |
| `codefresh-run` | The child pipeline isn't found, or the wrong branch is used, when `PIPELINE_ID` or `BRANCH` contains `$VAR` |
| `codefresh-run` | `codefresh wait` rejects the timeout when `TIMEOUT_MINS` contains `$VAR` |

To confirm, open the step log:

- **`helm`**: in the "Running the following script" section, the values appear in single quotes, e.g. `--set 'image.tag=$MY_TAG'`.
- **`codefresh-run`**: the "Executing command" line shows `"$CFRUN_..."` placeholders. Compare them with the step `arguments` in the pipeline YAML.

### Not this issue

- **`helm` with `use_debian_image: true` ignores `custom_values` written with dots in the key** (e.g. `image.tag=1.2.3`, no `$` involved). This is a separate known issue, CF-2559. Fix: use the documented format with underscores (`image_tag=1.2.3`); the step converts `_` to `.`.
- The step failed before [TBD release date] as well, or the pipeline YAML changed recently.

## What to tell the customer

Short explanation you can use as is:

> We recently released a security update for the `codefresh-run` and `helm` steps. The steps now use argument values exactly as they're written, instead of passing them through a shell. Your pipeline uses shell syntax (`$VAR`) in a step argument, so the step now receives the text `$VAR` instead of its value.
>
> You can fix this by replacing the shell variables with Codefresh variables (`${{VAR}}`). If you need more time, you can temporarily restore the previous behavior with the option below.

Don't share details about the vulnerability beyond what's in the published advisory: [TBD advisory link].

## Workaround: temporary legacy mode

The customer adds one setting to the affected step:

| Step | Setting |
|---|---|
| `codefresh-run` 1.7.0 or later | `LEGACY_SHELL_EXPANSION: true` |
| `helm` 1.1.13 or later | `legacy_shell_expansion: true` |
| `cfstep-helm` image used directly | environment variable `LEGACY_SHELL_EXPANSION=true` |

```yaml
deploy:
  type: helm:1.1.13
  arguments:
    # ...existing arguments...
    legacy_shell_expansion: true  # Temporary
```

```yaml
run_child:
  type: codefresh-run
  arguments:
    # ...existing arguments...
    LEGACY_SHELL_EXPANSION: true  # Temporary
```

Things to tell the customer:

- **Older `helm` step versions** (`helm:1.1.12` and earlier) don't accept the new argument and fail with a validation error. Upgrade the step to `helm:1.1.13` first.
- **The option is less secure**: it brings back the behavior that the security update fixed. Recommend it only as a short-term fix, and only for pipelines that don't receive values from outside the customer's team (for example, branch names from a Git trigger).
- **The option will be removed** on [TBD removal date].
- **With the option enabled**, the step log shows `WARNING: legacy_shell_expansion is enabled` (`helm`) or `WARNING: LEGACY_SHELL_EXPANSION is enabled` (`codefresh-run`), followed by the names of the arguments that still use shell syntax. That's the list of what needs to change.

## How to update the pipeline and disable legacy mode

1. Enable the temporary option (above) and run the pipeline once.
2. In the step log, find the warning. It lists the arguments to update, for example `CUSTOM_image_tag, CMD_PS` (`helm`) or `BRANCH VARIABLE` (`codefresh-run`). If it says that no arguments use shell syntax, skip to step 4.
3. Update each listed argument:

   | Before | After |
   |---|---|
   | `image_tag=$MY_TAG` | `image_tag=${{MY_TAG}}` |
   | `VARIABLE: [IMAGE=$IMAGE_NAME]` | `VARIABLE: [IMAGE=${{IMAGE_NAME}}]` |
   | `--set version=$(cat VERSION)` in `cmd_ps` | Add `cf_export VERSION=$(cat VERSION)` to an earlier freestyle step, then use `--set version=${{VERSION}}` |
   | `--values values-*.yaml` in `cmd_ps` | List the files in `custom_value_files` |
   | `kube_context: $MY_CONTEXT` | `kube_context: ${{MY_CONTEXT}}` |
   | `BRANCH: main --no-cache` | `BRANCH: main` and `NO_CACHE: true` |

   Variables exported with `cf_export` in an earlier step are available as `${{VAR}}` in later steps. Pipeline and trigger variables are available as `${{VAR}}` too.

4. Remove `legacy_shell_expansion` / `LEGACY_SHELL_EXPANSION` from the step and run the pipeline again.
5. Confirm that the warning is gone and the step works.

## Escalate if

- The pipeline still fails after the arguments are updated and legacy mode is removed.
- Legacy mode doesn't restore the previous behavior.
- The customer reports unexpected commands or network calls in the logs of these steps, or suspects their pipeline was abused. Escalate to the security team: [TBD].

## FAQ

**Why can't we just keep the old behavior by default?**
Because it lets anyone who can push a branch to the customer's repository run commands in their pipeline. The temporary option exists only to give customers time to migrate.

**Does this affect freestyle steps?**
No. `commands` in freestyle steps work as before. Only the arguments of the `codefresh-run` and `helm` steps changed.

**The customer pinned an old `helm` step version. Why did it change?**
The step runs the `cfstep-helm` image, and the rebuilt image is published under the same tags. Every `helm` step version uses the new behavior.

**The customer pinned `codefresh-run:1.6.0`. Are they affected?**
Not by the breaking change: the old version keeps its old behavior. Recommend upgrading to 1.7.0, because 1.6.0 and earlier contain the security issue.