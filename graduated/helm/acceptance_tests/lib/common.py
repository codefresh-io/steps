import os
import subprocess


class CommandRunner(object):
    def __init__(self):
        self.rc = 0
        self.pid = 0
        self.stdout = ''
        self.rootdir = os.path.realpath(os.path.join(__file__, '../../../'))

    def return_code_should_be(self, expected_rc):
        if int(expected_rc) != self.rc:
            raise AssertionError('Expected return code to be "%s" but was "%s".'
                                 % (expected_rc, self.rc))

    def return_code_should_not_be(self, expected_rc):
        if int(expected_rc) == self.rc:
            raise AssertionError('Expected return code not to be "%s".' % expected_rc)

    def output_contains(self, s):
        if s not in self.stdout:
            raise AssertionError('Output does not contain "%s".' % s)

    def output_does_not_contain(self, s):
        if s in self.stdout:
            raise AssertionError('Output contains "%s".' % s)

    def run_command_with_env(self, command, detach=False, env={}):
        execution_env = os.environ.copy()
        for key, val in env.items():
            execution_env[str(key)] = str(val)
        process = subprocess.Popen(command,
                                   env=execution_env,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        if not detach:
            stdout = str(process.communicate()[0].strip())
            self.rc = process.returncode
            # Remove debug lines that start with "+ "
            lines = stdout.split('\\n')
            for line in lines:
                print(line)
            self.stdout = '\n'.join(filter(lambda x: not x.startswith('+ '), lines))


    def should_have_failed(self):
        return self.return_code_should_not_be(0)

    def should_have_succeeded(self):
        return self.return_code_should_be(0)
