from BaseCommandBuilder import BaseCommandBuilder


class Helm3CommandBuilder(BaseCommandBuilder):

    def build_export_commands(self, google_application_credentials_json):
        lines = super().build_export_commands(google_application_credentials_json)
        return lines

    def build_helm_upgrade_command(self, release_name, chart_ref):
        return 'helm upgrade %s %s --install --reset-values ' % (release_name, chart_ref)

    def build_repo_commands(self):
        lines = []
        lines.append('helm repo add cf-stable https://kubernetes-charts.storage.googleapis.com/')
        return lines
