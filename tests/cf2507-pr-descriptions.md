# CF-2507 PR descriptions

Three PRs, one per branch. `steps` and `cfstep-helm` are public repositories, so the descriptions explain the
class of the issue and the fix, but intentionally contain no working exploit or details from the pentest report.

---

## 1. codefresh-io/steps — `CF-2507-fix-interpolation-security` → `master`

**Title:** fix(CF-2507): prevent shell injection in codefresh-run and helm steps

### Summary

The `codefresh-run` step template interpolated raw argument values into a shell command. Arguments are often
derived from Git data (the documented example uses `BRANCH: '${{CF_BRANCH}}'`), so a crafted value, for example
a branch name, could execute arbitrary commands in the pipeline build container.

The `helm` step template rendered argument values inside single-quoted YAML strings, so a quote or a new line in a
value could add arbitrary keys to the generated step.

### Changes

**codefresh-run 1.6.0 → 1.7.0**
- All arguments are passed to the step containers as environment variables (`CFRUN_*`) and are referenced in the
  command only as `"$CFRUN_*"`. The command line contains no user input anymore.
- Array arguments (`VARIABLE`, `SECRETS`, `CONTEXT`, `ONLY`, `SKIP`) are passed as indexed variables
  (`CFRUN_VARIABLE_0`, ...).
- `TIMEOUT_MINS` in the second step goes through the environment as well.
- Environment entries and the `image` are rendered with `toJSON`, so values can't break out of the YAML string.
- Side effect: secret values are no longer printed in the "Executing command" log line.

**helm 1.1.12 → 1.1.13**
- Environment entries and the `image` are rendered with `toJSON` instead of `'...'`.
- `cmd_ps` documentation updated (schema description and README).
- The escaping of the generated Helm script is fixed in the `cfstep-helm` image (see related PRs).

**Temporary migration option (both steps)**
- `codefresh-run`: `LEGACY_SHELL_EXPANSION` (boolean, default `false`). When enabled, the arguments are interpolated
  exactly as in 1.6.0, and the step prints a warning with the names (not the values) of the arguments that contain
  shell syntax.
- `helm`: `legacy_shell_expansion` (boolean, default `false`), passed to the image as `LEGACY_SHELL_EXPANSION`.
- The option is unsafe with user-controlled values. It only gives users time to migrate pipelines that rely on shell
  expansion, and will be removed in a later version.

### Behavior changes

Argument values are now passed to the CLI literally:
- `$VAR`, `$(...)`, backticks, globs and `~` in arguments are no longer expanded by the shell.
  Use `${{VAR}}` instead of `$VAR`; it is substituted by the engine before the step runs, as before.
- Several flags can't be passed through a single argument anymore (e.g. `BRANCH: "main --no-cache"`).
- Values with spaces now work as a single argument (`VARIABLE: ["key=value with spaces"]` was split before).

Pipelines that need time to migrate can set `LEGACY_SHELL_EXPANSION: true` (`codefresh-run`) or
`legacy_shell_expansion: true` (`helm`) to get the previous behavior back temporarily.

Pipelines that pin `codefresh-run:1.6.0` or older are not affected by this PR and should be upgraded. Pinned `helm`
step versions get the new behavior from the rebuilt `cfstep-helm` images; they can't set the new argument, so they
need to upgrade to `helm:1.1.13` to use the migration option.

### Testing

- Rendered both templates with the production template engine (pikolo 0.15.16):
  - benign arguments: the rendered `helm` step is identical to the previous version; `codefresh run` receives the
    same arguments as before, except values with spaces, which are now passed correctly;
  - malicious arguments: the previous templates produced broken YAML or executed the injected commands, the new
    ones keep every value as a literal string.
- Executed the rendered `codefresh-run` commands in `quay.io/codefresh/cli:0.89.1` with a stubbed CLI the same way
  the engine does (`/bin/sh -c`, `set -e`): no injected command was executed, all values reached the CLI unchanged.
- `LEGACY_SHELL_EXPANSION: true`: the CLI receives exactly the same arguments as with `codefresh-run` 1.6.0
  (including `$VAR` and `$(...)` values), and the warning lists the arguments with shell syntax. With the default
  value the rendered steps are identical to the version without the option.
- `tests/cf2507-interpolation-security.yml`: verification pipeline covering all three PRs (not committed yet;
  it hasn't been run in Codefresh yet).

### Related PRs

- codefresh-contrib/cfstep-helm — `CF-2507-fix-interpolation-security` (alpine images)
- codefresh-contrib/cfstep-helm — `CF-2507-fix-interpolation-security-debian` (debian images)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

## 2. codefresh-contrib/cfstep-helm — `CF-2507-fix-interpolation-security` → `master`

**Title:** fix(CF-2507): prevent shell injection in generated helm script

### Summary

`EntrypointScriptBuilder` generates `/tmp/run` by interpolating environment values (`KUBE_CONTEXT`, `RELEASE_NAME`,
`NAMESPACE`, `custom_values`, `CMD_PS`, repository URLs, ...) into shell commands without escaping. When a pipeline
passes Git-derived data to the helm step, a crafted value could execute arbitrary commands in the build container.
`COMMIT_MESSAGE` was additionally interpolated into a `sed` expression, which allowed command execution through
the `e` flag of GNU sed.

### Changes

- Every value interpolated into the generated script is quoted with `shlex.quote`.
- `--set` / `--set-string` values are parsed with `shlex.split` before quoting. This keeps the existing quote and
  backslash removal (e.g. `pat.arr="{one,two,three}"`, `one\,two\,three`) without performing any expansion.
  A value that is not a single shell word is passed literally.
- `CMD_PS` is split and re-quoted token by token: quotes are respected, but `$VAR`, `$(...)` and shell operators are
  passed to Helm literally. Unbalanced quotes fail with `Failed to parse CMD_PS`.
- `COMMIT_MESSAGE` is passed to `awk` through the environment instead of being interpolated into shell/sed code.
  Multi-line commit messages now work (they broke `sed` before).
- `$PACKAGE`, `$HELMREPO_USERNAME:$HELMREPO_PASSWORD` and `$GOOGLE_APPLICATION_CREDENTIALS_JSON` are quoted.
- Temporary migration option `LEGACY_SHELL_EXPANSION` (`legacy_shell_expansion` step argument), disabled by
  default. An unset variable, including all older `helm` step versions, uses the safe behavior. When enabled, values
  provided by the user are interpolated as before, and a warning lists the names (not the values) of the variables
  that contain shell syntax. `COMMIT_MESSAGE` and internal variables stay escaped in both modes.
- Tests: new tests execute the generated script with stubbed `helm`/`kubectl` and assert that no injected command is
  executed and that Helm receives the expected arguments. `assertEquals` replaced with `assertEqual` (removed in
  Python 3.12, two tests were failing before this change).

### Behavior changes

- `$VAR`, `$(...)`, globs and `~` in values and in `CMD_PS` are no longer expanded, unless `LEGACY_SHELL_EXPANSION`
  is enabled.
- Values with `;` or spaces in `--set-string`, and values like `it's`, now work (they broke the command before).
- The script printed in the log ("Running the following script") now contains quotes. Credential masking still works.

The image tags stay the same (`cfstep-helm:<helm version>`), so after the images are rebuilt the fix applies to all
versions of the `helm` step, including the ones pinned to older step versions.

### Testing

- `python3 -m unittest tests/EntrypointScriptBuilderTest.py`: 26/26 locally and inside
  `quay.io/codefreshplugins/cfstep-helm:3.14.0` (Python 3.9, busybox awk).
- The new tests fail against `origin/master` (the injected commands are executed).
- With `LEGACY_SHELL_EXPANSION=true` Helm receives exactly the same arguments as with `origin/master`, including
  `$VAR` values and globs.
- Compared the arguments Helm receives before and after the change for typical values: identical, except for the
  cases that were broken before (listed above).
- Ran the image in `DRY_RUN` mode with malicious values for every input: no command was executed, Helm received
  the values literally.
- Not run: robot acceptance tests (they need real `helm`/`kubectl` binaries).

### Related PRs

- codefresh-io/steps — `CF-2507-fix-interpolation-security` (helm 1.1.13, codefresh-run 1.7.0)
- codefresh-contrib/cfstep-helm — `CF-2507-fix-interpolation-security-debian` (same fix for the debian images)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

## 3. codefresh-contrib/cfstep-helm — `CF-2507-fix-interpolation-security-debian` → `debian`

**Title:** fix(CF-2507): prevent shell injection in generated helm script (debian)

### Summary

Port of the master fix to the `debian` branch, which the `cfstep-helm-debian` images (`use_debian_image: true`) are
built from. Without it the debian images stay vulnerable after the rebuild.

`EntrypointScriptBuilder` generates `/tmp/run` by interpolating environment values into shell commands without
escaping, and `COMMIT_MESSAGE` was interpolated into a `sed` expression. When a pipeline passes Git-derived data to
the helm step, a crafted value could execute arbitrary commands in the build container.

### Changes

Same as the master PR:
- every value interpolated into the generated script is quoted with `shlex.quote`;
- `--set` / `--set-string` values keep the existing quote and backslash removal without expansions;
- `CMD_PS` is re-quoted token by token;
- `COMMIT_MESSAGE` is passed to `awk` through the environment;
- `$PACKAGE`, Helm repository credentials and `$GOOGLE_APPLICATION_CREDENTIALS_JSON` are quoted;
- the same temporary `LEGACY_SHELL_EXPANSION` migration option, disabled by default;
- the same tests as in the master PR.

The `debian` branch has an older `EntrypointScriptBuilder` (no per-repository credentials, no
`use_repos_for_auth_action`). The conflict in the `helm repo add` block was resolved by keeping the debian logic and
adding the escaping only. No functionality from master was ported.

### Behavior changes

Same as the master PR: `$VAR`, `$(...)`, globs and `~` in values and in `CMD_PS` are no longer expanded, unless
`LEGACY_SHELL_EXPANSION` is enabled.

### Testing

- `python3 -m unittest tests/EntrypointScriptBuilderTest.py`: 26/26 locally and inside
  `quay.io/codefreshplugins/cfstep-helm-debian:3.14.0` (Python 3.8, mawk).
- The new tests fail against `origin/debian` (the injected commands are executed).
- With `LEGACY_SHELL_EXPANSION=true` Helm receives exactly the same arguments as with `origin/debian`.
- Ran the image in `DRY_RUN` mode with malicious values for every input: no command was executed.

### Known issue (not related to this PR)

In the debian image `/bin/sh` is `dash`, and the engine runs step commands with `/bin/sh -c`. `dash` drops
environment variables with dots in the name, so `custom_values` (`CUSTOM_<key.with.dots>`) never reach the step when
`use_debian_image: true` is set. This happens before and after this change; it should be tracked separately.

### Related PRs

- codefresh-io/steps — `CF-2507-fix-interpolation-security` (helm 1.1.13, codefresh-run 1.7.0)
- codefresh-contrib/cfstep-helm — `CF-2507-fix-interpolation-security` (same fix for master / alpine images)

🤖 Generated with [Claude Code](https://claude.com/claude-code)