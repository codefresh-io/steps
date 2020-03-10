class BaseCommandBuilder:

    def build_export_commands(self, google_application_credentials_json):
        lines = []
        lines.append('export HELM_REPO_ACCESS_TOKEN=$CF_API_KEY')
        lines.append('export HELM_REPO_AUTH_HEADER=Authorization')
        if google_application_credentials_json is not None:
            lines.append('echo -E $GOOGLE_APPLICATION_CREDENTIALS_JSON > /tmp/google-creds.json')
            lines.append('export GOOGLE_APPLICATION_CREDENTIALS=/tmp/google-creds.json')
        return lines
