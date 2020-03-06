import common


class CFStepHelm(common.CommandRunner):
    def run_with_env(self, env={}):
        self.run_command_with_env(['release_chart'], False, env)

    def source_with_env_and_check_for_var(self, env={}, var=''):
        self.run_command_with_env([
            '/bin/sh', '-xc', 'unset %s && . release_chart && ( env | grep -q %s ) && exit 255' % (var, var)
        ], False, env)
