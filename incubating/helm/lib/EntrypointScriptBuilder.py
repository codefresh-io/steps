import json
import os
import errno
import sys
import urllib.request
import urllib.parse

class EntrypointScriptBuilder(object):

    def __init__(self, env):
        self.action = env.get('ACTION', 'install').lower()
        self.kube_context = env.get('KUBE_CONTEXT')
        self.chart_ref = env.get('CHART_REF', env.get('CHART_NAME'))
        self.chart_repo_url = env.get('CHART_REPO_URL')
        self.chart_version = env.get('CHART_VERSION')
        self.app_version = env.get('APP_VERSION')
        self.release_name = env.get('RELEASE_NAME')
        self.namespace = env.get('NAMESPACE')
        self.tiller_namespace = env.get('TILLER_NAMESPACE')
        self.dry_run = env.get('DRY_RUN')
        self.recreate_pods = env.get('RECREATE_PODS')
        self.cmd_ps = env.get('CMD_PS')
        self.google_application_credentials_json = env.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        self.chart = env.get('CHART_JSON')
        self.azure_helm_token = None

        # Save chart data in files
        if not self.chart is None:
            self.chart = json.loads(self.chart)

            self.chart_ref = '/opt/chart'
            os.mkdir('/opt/chart');
            sys.stderr.write('Chart files will be placed in /opt/chart\n');
            for item in self.chart:
                if item['name'] == 'values':
                    item['name'] = 'values.yaml'
                item['name'] = item['name'].replace('Charts/', 'charts/')

                sys.stderr.write(item['name'] + '\n');

                if not os.path.exists(os.path.dirname('/opt/chart/' + item['name'])):
                    try:
                        os.makedirs(os.path.dirname('/opt/chart/' + item['name']))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise

                file = open('/opt/chart/' + item['name'], 'w')
                data = item['data'] if 'data' in item.keys() else ''
                file.write(data)
                file.close()

        # Values files (-f/--values) sourced from vars prefixed with "CUSTOMFILE_" or "VALUESFILE_"
        custom_valuesfiles = []
        for key, val in sorted(env.items()):
            key_upper = key.upper()
            if key_upper.startswith('CUSTOMFILE_') or key_upper.startswith('VALUESFILE_'):
                custom_valuesfiles.append(val)
        self.custom_valuesfiles = custom_valuesfiles

        # Specific value overrides (--set) sourced from vars prefixed with "CUSTOM_" or "VALUE_"
        custom_values = {}
        for key, val in sorted(env.items()):
            key_upper = key.upper()
            if key_upper.startswith('CUSTOM_'):
                cli_set_key = key[7:]
            elif key_upper.startswith('VALUE_'):
                cli_set_key = key[6:]
            else:
                continue
            cli_set_key = cli_set_key.replace('_', '.')
            cli_set_key = cli_set_key.replace('..', '_')
            custom_values[cli_set_key] = val
        self.custom_values = custom_values

        # Specific value overrides (--set-string) sourced from vars prefixed with or "VALUESTRING_"
        string_values = {}
        for key, val in sorted(env.items()):
            key_upper = key.upper()
            if key_upper.startswith('VALUESTRING_'):
                cli_set_key = key[12:]
            else:
                continue
            cli_set_key = cli_set_key.replace('_', '.')
            cli_set_key = cli_set_key.replace('..', '_')
            string_values[cli_set_key] = val
        self.string_values = string_values

        # Extract Helm repos to add from attached Helm repo contexts prefixed with "CF_CTX_" and suffixed with "_URL"
        helm_repos = {}
        chart_repo_url = self.chart_repo_url

        if chart_repo_url and chart_repo_url.startswith('az://'):
            if not self.azure_helm_token:
                self.azure_helm_token = self._get_azure_helm_token(chart_repo_url)
            chart_repo_url = chart_repo_url.strip('/').replace('az://', 'https://00000000-0000-0000-0000-000000000000:%s@' % self.azure_helm_token, 1) + '/helm/v1/repo'

        helm_repo_username = env.get('HELMREPO_USERNAME')
        helm_repo_password = env.get('HELMREPO_PASSWORD')
        for key, val in sorted(env.items()):
            key_upper = key.upper()
            if key_upper.startswith('CF_CTX_') and key_upper.endswith('_URL'):
                repo_name = key_upper.replace('CF_CTX_', '', 1).replace('_URL', '', 1).replace('_', '-').lower()
                repo_url = val
                if not repo_url.endswith('/'):
                    repo_url += '/'
                if repo_url.startswith('http://') or repo_url.startswith('https://'):
                    if helm_repo_username is not None and helm_repo_password is not None:
                        repo_url = repo_url.replace('://', '://%s:%s@' % (helm_repo_username, helm_repo_password), 1)

                # Modify azure URL to use https and contain token
                elif repo_url.startswith('az://'):
                    if not self.azure_helm_token:
                        self.azure_helm_token = self._get_azure_helm_token(repo_url)
                    repo_url = repo_url.replace('az://', 'https://00000000-0000-0000-0000-000000000000:%s@' % self.azure_helm_token, 1) + 'helm/v1/repo'

                helm_repos[repo_name] = repo_url
                if self.chart_repo_url is None:
                    chart_repo_url = repo_url

        self.chart_repo_url = chart_repo_url
        self.helm_repos = helm_repos

        # Workaround a bug in Helm where url that doesn't end with / breaks --repo flags
        if self.chart_repo_url is not None and not self.chart_repo_url.endswith('/'):
            self.chart_repo_url += '/'

    def _get_azure_helm_token(self, repo_url):
        service = repo_url.replace('az://', '').strip('/')
        sys.stderr.write('Obtaining one-time token for Azure Helm repo service %s ...\n' % service)
        if self.dry_run:
            return 'xXxXx'
        cf_build_url = os.getenv('CF_BUILD_URL', 'https://g.codefresh.io')
        if 'local' in cf_build_url:
            cf_build_url = 'http://' + os.getenv('CF_HOST_IP')
        cf_build_url_parsed = urllib.parse.urlparse(cf_build_url)
        token_url = '%s://%s/api/clusters/aks/helm/repos/%s/token' % (cf_build_url_parsed.scheme, cf_build_url_parsed.netloc, service)
        request = urllib.request.Request(token_url)
        request.add_header('Authorization', os.getenv('CF_API_KEY'))
        data = json.load(urllib.request.urlopen(request))
        return data['access_token']

    def _build_export_commands(self):
        lines = []
        lines.append('export HELM_REPO_ACCESS_TOKEN=$CF_API_KEY')
        lines.append('export HELM_REPO_AUTH_HEADER=Authorization')
        if self.google_application_credentials_json is not None:
            lines.append('echo -E $GOOGLE_APPLICATION_CREDENTIALS_JSON > /tmp/google-creds.json')
            lines.append('export GOOGLE_APPLICATION_CREDENTIALS=/tmp/google-creds.json')
        return lines

    def _build_kubectl_commands(self):
        lines = []
        if self.action in ['install', 'promotion']:
            if self.kube_context is None:
                raise Exception('Must set KUBE_CONTEXT in environment (Name of Kubernetes cluster as named in Codefresh)')
            kubectl_cmd = 'kubectl config use-context "%s"' % self.kube_context
            if self.dry_run:
                kubectl_cmd = 'echo ' + kubectl_cmd
            lines.append(kubectl_cmd)
        return lines

    def _build_version_commands(self):
        lines = []

        kubectl_version_cmd = 'kubectl version'
        if self.dry_run:
            kubectl_version_cmd = 'echo ' + kubectl_version_cmd
        lines.append(kubectl_version_cmd)

        helm_version_cmd = 'helm version'
        if self.dry_run:
            helm_version_cmd = 'echo ' + helm_version_cmd
        lines.append(helm_version_cmd)

        return lines

    def _build_helm_commands(self):
        lines = []

        if self.action == 'auth':
            return lines

        if self.chart_ref is None:
            raise Exception('Must set CHART_REF in the environment (this should be a reference to the chart as Helm CLI expects)')

        # Add Helm repos locally
        for repo_name, repo_url in sorted(self.helm_repos.items()):
            helm_repo_add_cmd = 'helm repo add %s %s' % (repo_name, repo_url)
            if self.dry_run:
                helm_repo_add_cmd = 'echo ' + helm_repo_add_cmd
            lines.append(helm_repo_add_cmd)

        if self.action == 'install':
            lines += self._build_helm_install_commands()
        if self.action == 'promotion':
            lines += self._build_helm_promotion_commands()
        elif self.action == 'push':
            lines += self._build_helm_push_commands()

        return lines

    def _build_helm_promotion_commands(self):
        lines = []

        if self.release_name is None:
            raise Exception('Must set RELEASE_NAME in the environment (desired Helm release name)')

        helm_promote_cmd = 'helm upgrade %s %s --install ' % (self.release_name, self.chart_ref)
        if self.tiller_namespace is not None:
            helm_promote_cmd += '--tiller-namespace %s ' % self.tiller_namespace
        if self.namespace is not None:
            helm_promote_cmd += '--namespace %s ' % self.namespace
        for custom_valuesfile in self.custom_valuesfiles:
            helm_promote_cmd += '--values %s ' % custom_valuesfile
        for cli_set_key, val in sorted(self.custom_values.items()):
            helm_promote_cmd += '--set %s=%s ' % (cli_set_key, val)
        for cli_set_key, val in sorted(self.string_values.items()):
            helm_promote_cmd += '--set-string %s=%s ' % (cli_set_key, val)
        if self.recreate_pods:
            helm_promote_cmd += '--recreate-pods '
        if self.cmd_ps is not None:
            helm_promote_cmd += self.cmd_ps
        if self.dry_run:
            helm_promote_cmd = 'echo ' + helm_upgrade_cmd
        lines.append(helm_promote_cmd)

        return lines

    def _build_helm_install_commands(self):
        lines = []

        if self.release_name is None:
            raise Exception('Must set RELEASE_NAME in the environment (desired Helm release name)')

        # Only build dependencies if CHART_REPO_URL is not specified
        if self.chart_repo_url is None:
            helm_dep_build_cmd = 'helm dependency build %s' % self.chart_ref
            if self.dry_run:
                helm_dep_build_cmd = 'echo ' + helm_dep_build_cmd
            lines.append(helm_dep_build_cmd)

        helm_upgrade_cmd = 'helm upgrade %s %s --install --force --reset-values ' % (self.release_name, self.chart_ref)
        if self.chart_repo_url is not None:
            helm_upgrade_cmd += '--repo %s ' % self.chart_repo_url
        if self.chart_version is not None:
            helm_upgrade_cmd += '--version %s ' % self.chart_version
        if self.namespace is not None:
            helm_upgrade_cmd += '--namespace %s ' % self.namespace
        for custom_valuesfile in self.custom_valuesfiles:
            helm_upgrade_cmd += '--values %s ' % custom_valuesfile
        for cli_set_key, val in sorted(self.custom_values.items()):
            helm_upgrade_cmd += '--set %s=%s ' % (cli_set_key, val)
        for cli_set_key, val in sorted(self.string_values.items()):
            helm_upgrade_cmd += '--set-string %s=%s ' % (cli_set_key, val)
        if self.recreate_pods:
            helm_upgrade_cmd += '--recreate-pods '
        if self.cmd_ps is not None:
            helm_upgrade_cmd += self.cmd_ps
        if self.dry_run:
            helm_upgrade_cmd = 'echo ' + helm_upgrade_cmd
        lines.append(helm_upgrade_cmd)

        return lines

    def _build_helm_push_commands(self):
        lines = []

        if self.chart_repo_url is None:
            raise Exception('Must set CHART_REPO_URL in the environment, otherwise attach a Helm Repo context (prefixed with CF_CTX_)')

        helm_repo_add_cmd = 'helm repo add remote %s' % self.chart_repo_url
        if self.dry_run:
            helm_repo_add_cmd = 'echo ' + helm_repo_add_cmd
        lines.append(helm_repo_add_cmd)

        helm_dep_build_cmd = 'helm dependency build %s' % self.chart_ref
        if self.dry_run:
            helm_dep_build_cmd = 'echo ' + helm_dep_build_cmd
        lines.append(helm_dep_build_cmd)

        if self.dry_run:
            package_var = 'dryrun-0.0.1.tgz'
        else:
            package_var = '$(helm package %s ' % self.chart_ref
            if self.chart_version is not None:
                package_var += '--version ' + self.chart_version + ' '
            if self.app_version is not None:
                package_var += '--app-version ' + self.app_version + ' '
            package_var += '--destination /tmp | cut -d " " -f 8)'
        lines.append('PACKAGE="%s"' % package_var)

        if self.azure_helm_token is not None:
            helm_push_command = 'curl --fail -X PUT --data-binary "@${PACKAGE}" ' + self.chart_repo_url + '_blobs/$(basename $PACKAGE)' + ' || curl --fail -X PATCH --data-binary "@${PACKAGE}" ' + self.chart_repo_url + '_blobs/$(basename $PACKAGE)'
        elif self.chart_repo_url.startswith('cm://'):
            helm_push_command = 'helm push $PACKAGE remote'
        elif self.chart_repo_url.startswith('s3://'):
            helm_push_command = 'helm s3 push $PACKAGE remote'
        elif self.chart_repo_url.startswith('gs://'):
            helm_push_command = 'helm gcs push $PACKAGE remote'
        else:
            raise Exception('Unsupported protocol in CHART_REPO_URL')

        if self.cmd_ps is not None:
            helm_push_command += ' ' + self.cmd_ps

        if self.dry_run:
            helm_push_command = 'echo ' + helm_push_command

        lines.append(helm_push_command)

        return lines

    def build(self):
        lines = ['#!/bin/bash -e']
        lines += self._build_export_commands()
        lines += self._build_kubectl_commands()
        lines += self._build_version_commands()
        lines += self._build_helm_commands()
        return '\n'.join(lines)
