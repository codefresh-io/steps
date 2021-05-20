#!/usr/bin/env python3

""" Purpose:
        Accepts a YAML file specifying a list of pipelines and options, and builds them concurrently. You can specify
        most `codefresh run` options on a per-build basis within the YAML file, including: branch, sha, no_cache,
        no_cf_cache, reset_volume, variables[], contexts[], skip[], and only[]. See example YAML file: 
        https://github.com/codefresh-io/steps/tree/master/incubating/codefresh-run-dynamic/example_run_list.yaml
    Required environment variables:
      - RUN_LIST_YAML_FILE - Path to the YAML file containing a list of pipelines to run 
    Optional environment variables:
      - DEBUG - Set to 'true' to enable debug logging. Default is 'false'.
      - WAIT - Wait for builds to finish and log the status of each build.
      - COLUMNS - When WAIT is specified, choose which columns to include when logging build statuses. Default is
            "id,pipeline-name,trigger,branch,status". Available columns are "id,pipeline-name,pipeline-id,status,
            created,started,finished,buildtime,totaltime,trigger,webhook,repository,branch,commit-id,
            pipeline-trigger-id".
      - TIMEOUT_MINS - When WAIT is specified, wait up to this amount of minutes for builds to finish. Default is 60.
      - CHECK_INTERVAL_MINS - When WAIT is specified, check the build status at this interval. Default is every 1 min.
      - LOG_INTERVAL_MINS - When WAIT is specified, log the build statuses at this interval. Default is every 15 min.
      - LOG_DIRECTORY - Write build logs to files in thie directory.
    Output files:
      - /tmp/cf_builds_started - a space-separated list of the build IDs that were started.
      - /tmp/success - contains 'true' or 'false' to indicate is all pipelines finished successfully.
"""

import os           # to read env vars
import time         # for sleep() and calculating wait timeout
import logging      # for debug logging
import subprocess   # to run the 'codefresh' process
import yaml


def run_cmd(cmd, cmd_args=[], input=None, fail_on_non_zero=True, no_echo_cmd=False, redact_cmd=False):
    """Run a command in the OS. Any command args that contain spaces should be 
       passed separately in the cmd_args list param (don't include quotes).
    """
    log_cmd = cmd
    for arg in cmd_args:
        if " " in arg:  # Display any implied quotes when echoing the command
            arg = "'{}'".format(arg)
        log_cmd += " " + arg
    if redact_cmd:
        log_cmd = "[REDACTED]"
    if not no_echo_cmd: 
        print(log_cmd)
    result = subprocess.run(cmd.split() + cmd_args, 
        input=input, 
        stdout=subprocess.PIPE,   # send stderr to stdout
        stderr=subprocess.STDOUT)
    output = result.stdout.decode('utf-8').rstrip()
    returncode = result.returncode
    summary = "\n  Command: {}".format(log_cmd) + \
                "\n  Return code: {}".format(returncode) + \
                "\n  Output:\n{}".format(output)
    if fail_on_non_zero: assert(returncode == 0), summary
    logging.debug(summary)
    return output, returncode


def verify_input_file_structure(pipelines_to_run):
    """ Verify the list/dict structure that was read in from the input YAML file.
    """
    logging.debug("Parsing input file to validate tree structure...")
    # Make sure the top level is a list
    assert (isinstance(pipelines_to_run, list)), "Input file must be structured as a list"
    # Make sure each list item is a dictionary
    for pipeline in pipelines_to_run:
        logging.debug(pipeline)
        # Make sure the dictionary contains the required property
        error_msg = "List item must be a dictionary with at least one property, 'pipeline_id': " + str(pipeline)
        assert (isinstance(pipeline, dict)), error_msg
        assert 'pipeline_id' in pipeline.keys(), error_msg
        # Make sure the 'variable' property is a dictionary with valid sub-properties
        if 'variables' in pipeline.keys():
            assert (isinstance(pipeline['variables'], dict)), "'variables' property must be a dictionary of key:value pairs"
            for var_name in pipeline['variables'].keys():
                var_value = pipeline['variables'][var_name]
                scalar_types = [str, int, float, complex, bool]
                assert (type(var_value) in scalar_types), \
                    "Bad variable encountered: '" + var_name + "'. Its value is not a string, number, or boolean."
        # Make sure the 'context' property is a list of strings
        if 'contexts' in pipeline.keys():
            assert (isinstance(pipeline['contexts'], list)), "'contexts' is not a list: " + str(pipeline)
            for item in pipeline['contexts']:
                assert (isinstance(item, str)), \
                    "Bad 'context' item encountered: '" + item + "'. It must be a string."
        # Make sure the 'only' property is a list of strings
        if 'only' in pipeline.keys():
            assert (isinstance(pipeline['only'], list)), "'only' is not a list: " + str(pipeline)
            for item in pipeline['only']:
                assert (isinstance(item, str)), \
                    "Bad 'only' item encountered: '" + item + "'. It must be a string."
        # Make sure the 'skip' property is a list of strings
        if 'skip' in pipeline.keys():
            assert (isinstance(pipeline['skip'], list)), "'skip' is not a list: " + str(pipeline)
            for item in pipeline['skip']:
                assert (isinstance(item, str)), \
                    "Bad 'skip' item encountered: '" + item + "'. It must be a string."
    logging.debug("Finished validating tree structure.")


def get_inputs_from_env_vars_and_defaults():
    """ Read environment variables. When optional env vars aren't provided, set default values.
    """
    ### Required env vars
    run_list_yaml_file = os.environ.get("RUN_LIST_YAML_FILE")
    if not run_list_yaml_file:
        raise ValueError("Missing required environment variable: RUN_LIST_YAML_FILE.")
    ### Optional env vars
    columns = os.environ.get('COLUMNS')
    if not columns: columns = "id,pipeline-name,trigger,branch,status"
    else: columns = columns.lower()  # 'codefresh run' requires lower case
    if str(os.environ.get('DEBUG')).upper() == "TRUE": debug = True
    else: debug = False
    if str(os.environ.get('WAIT')).upper() == "TRUE": wait = True
    else: wait = False
    timeout_mins = os.environ.get('TIMEOUT_MINS')
    if not timeout_mins: timeout_mins = 60
    else: timeout_mins = int(timeout_mins)
    check_interval_mins = os.environ.get('CHECK_INTERVAL_MINS')
    if not check_interval_mins: check_interval_mins = 1
    log_interval_mins = os.environ.get('LOG_INTERVAL_MINS')
    if not log_interval_mins: log_interval_mins = 15
    log_directory = os.environ.get('LOG_DIRECTORY')
    return run_list_yaml_file, columns, debug, wait, timeout_mins, check_interval_mins, log_interval_mins, log_directory


def run_pipeline(pipeline):
    """ Parse the 'pipeline' dictionary structure for 'codefresh run' params,
        and then execute the 'codefresh run...' command.
    """
    pipeline_id = pipeline['pipeline_id']
    logging.debug("Building command for pipeline " + pipeline_id)
    cmd = "codefresh run"
    cmd_args = [pipeline_id, "--detach"]
    if 'trigger_id' in pipeline.keys():
        cmd_args.append("--trigger=" + pipeline['trigger_id'])
    if 'branch' in pipeline.keys():
        cmd_args.append("--branch=" + pipeline['branch'])
    if 'sha' in pipeline.keys():
        cmd_args.append("--sha=" + pipeline['sha'])
    if 'no_cache' in pipeline.keys():
        if str(pipeline['no_cache']).upper() == "TRUE":
            cmd_args.append("--no-cache")
    if 'no_cf_cache' in pipeline.keys():
        if str(pipeline['no_cf_cache']).upper() == "TRUE":
            cmd_args.append("--no-cf-cache")
    if 'reset_volume' in pipeline.keys():
        if str(pipeline['reset_volume']).upper() == "TRUE":
            cmd_args.append("--reset-volume")
    if 'variables' in pipeline.keys():
        for var_name in pipeline['variables'].keys():
            var_value = pipeline['variables'][var_name]
            cmd_args.append("-v={}={}".format(var_name, var_value))
    if 'contexts' in pipeline.keys():
        for item in pipeline['contexts']:
            cmd_args.append("--context=" + item)
    if 'only' in pipeline.keys():
        for item in pipeline['only']:
            cmd_args.append("--only=" + item)
    if 'skip' in pipeline.keys():
        for item in pipeline['skip']:
            cmd_args.append("--skip=" + item)
    output, exit_code = run_cmd(cmd, cmd_args)
    if not output:
        raise RuntimeError("No output was returned from 'codefresh run' command - build number was expected")
    build_number = output
    return build_number


def get_build_info(build_number):
    """ Get a dictionary of info for the specified build.
    """
    logging.debug("Getting info for build " + build_number)
    cmd = "codefresh get build -o yaml " + build_number
    cmd_args = []
    output, exit_code = run_cmd(cmd, cmd_args, no_echo_cmd=True)
    if not output:
        raise RuntimeError("No output was returned from '" + cmd + "' command")
    build_info = yaml.load(output, Loader=yaml.SafeLoader)
    return build_info


def get_build_status(build_number):
    """ Get the current status of the specified build. For list of possible status
        values, see https://codefresh-io.github.io/cli/builds/get-build/.
    """
    build_info = get_build_info(build_number)
    return build_info['status']


def all_builds_finished(build_numbers_to_check):
    """ Looks at the status of each build. Returns False as soon as a non-finished build
        is encountered. Returns True if all builds have finished.
    """
    for build_number in build_numbers_to_check:
        if get_build_status(build_number) not in ['success', 'error', 'terminated', 'terminating']:
            return False
    return True


def print_build_statuses(build_numbers, columns):
    """ Print the specified info (columns) from each build. 'columns' should be
        a comma-separated list (no spaces). Accepable values are:
            id,pipeline-name,pipeline-id,status,created,started,finished,buildtime,totaltime,
            trigger,webhook,repository,branch,commit-id,pipeline-trigger-id
    """
    cmd = "codefresh get build --sc=" + columns
    output, exit_code = run_cmd(cmd, build_numbers, no_echo_cmd=True)
    if not output:
        raise RuntimeError("No output was returned from '" + cmd + "' command")
    print(output)


def get_build_log(build_number):
    """ Returns the logs from the specified build as a string.
    """
    cmd = "codefresh logs " + build_number
    cmd_args = []
    output, exit_code = run_cmd(cmd, cmd_args, no_echo_cmd=True)
    if not output:
        raise RuntimeError("No output was returned from '" + cmd + "' command")
    return output


def wait_for_builds(builds_started, timeout_mins, check_interval_mins, log_interval_mins, columns):
    """ Wait for the list of builds to all finish, up to the specified timeout. 
        Return True if all the builds finish before the timeout, otherwise False.
        Noteworthy args:
            check_interval_mins - how often to check the status of the builds to see if they're done
            log_interval_mins - how often to print the status of the builds
    """
    logging.info("Waiting for pipeline builds to finish...")
    timeout_secs = int(timeout_mins) * 60
    wait_start_time = time.time()
    wait_end_time = wait_start_time + timeout_secs
    check_interval_seconds = int(check_interval_mins) * 60
    log_interval_seconds = int(log_interval_mins) * 60  # Could be a string from the env var
    log_interval_tracker = []  # Keeps track of which logging interval we're in; only log once per logging interval
    while not all_builds_finished(builds_started) and time.time() < wait_end_time:
        ### Only log once per logging interval
        current_log_interval = int((time.time() - wait_start_time) // log_interval_seconds)
        logging.debug("Current logging interval is " + str(current_log_interval))
        if len(log_interval_tracker) - 1 < current_log_interval:
            print_build_statuses(builds_started, columns)
            log_interval_tracker.append(True)  # Flag the current interval as having been logged
        ### Sleep until the next check interval
        logging.debug("Sleeping for " + str(check_interval_seconds) + " seconds...")
        time.sleep(check_interval_seconds)
    if all_builds_finished(builds_started):
        success = True
    else:
        success = False
    return success


def verify_or_create_dir(dir_name):
    """ Create the specified directory if it doesn't already exist.
    """
    cmd = "mkdir -p " + dir_name
    cmd_args = []
    output, exit_code = run_cmd(cmd, cmd_args, no_echo_cmd=True)


def write_output_files(builds_started, success):
    """ Store outputs in temp files so that this script's parent step
        can read them into environment vars with export + cf_export.
    """
    space_separated_list = " ".join(builds_started)
    with open("/tmp/cf_builds_started", "w") as write_file:
        write_file.write(space_separated_list)
    with open("/tmp/success", "w") as write_file:
        write_file.write(str(success).lower())


def main():
    # Get script args
    run_list_yaml_file, columns, debug, wait, timeout_mins, check_interval_mins, \
        log_interval_mins, log_directory = get_inputs_from_env_vars_and_defaults()
    
    if debug: logging.basicConfig(level='DEBUG')

    # Read the list of pipelines to run from the input YAML file
    with open(run_list_yaml_file, "r") as read_file:
        pipelines_to_run = yaml.load(read_file, Loader=yaml.SafeLoader)
    verify_input_file_structure(pipelines_to_run)

    print("Running pipelines...\n")
    builds_started = []
    for pipeline in pipelines_to_run:
        build_number = run_pipeline(pipeline)
        builds_started.append(build_number)
        print("Started build https://g.codefresh.io/build/" + build_number + "\n")
   
    # Optionally wait for builds to finish
    if wait:
        print("\nWaiting for builds to finish...")
        success = wait_for_builds(builds_started, timeout_mins, check_interval_mins, log_interval_mins, columns)
        print_build_statuses(builds_started, columns)
        # Optionally write log files out to the specified directory
        if log_directory:
            verify_or_create_dir(log_directory)
            for build_number in builds_started:
                build_log = get_build_log(build_number)
                with open("{}/{}.log".format(log_directory,build_number), "w") as write_file:
                    write_file.write(build_log)
            print("Log files were written to " + log_directory)
    
    write_output_files(builds_started, success)


if __name__ == "__main__":
    main()