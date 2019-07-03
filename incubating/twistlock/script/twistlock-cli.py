import json
import os
import re
import requests
import sys
import subprocess
import tarfile


def create_annotation_list(name, json_data):
    annotations = []
    annotation_list = ''
    for key, value in json_data.items():
        if key != 'total' and value != 0:
            annotations.append("-l {}{}={}".format(key.upper(), name, value))
            annotation_list = ' '.join(annotations)
    return annotation_list


def annotate_image(codefresh_cli_key, docker_image_id, annotation_list):
    annotate_image_exec = ("codefresh auth create-context --api-key {} && codefresh annotate image {} {}"
                           .format(codefresh_cli_key,
                                   docker_image_id,
                                   annotation_list
                                   )
                           )

    print(annotate_image_exec)

    proc = subprocess.Popen(annotate_image_exec, shell=True)
    proc.wait()


def main(docker_command):
    codefresh_cli_key = os.getenv('CODEFRESH_CLI_KEY')
    console_hostname = os.getenv('CONSOLE_HOSTNAME')
    console_port = os.getenv('CONSOLE_PORT')
    console_username = os.getenv('CONSOLE_USERNAME')
    console_password = os.getenv('CONSOLE_PASSWORD')
    tlscacert = os.getenv('TLSCACERT')
    hash = os.getenv('HASH', 'sha1')
    include_package_files = os.getenv('INCLUDE_PACKAGE_FILES')
    details = os.getenv('DETAILS')
    only_fixed = os.getenv('ONLY_FIXED')
    compliance_threshold = os.getenv('COMPLIANCE_THRESHOLD')
    vulnerability_threshold = os.getenv('VULNERABILITY_THRESHOLD')

    proc = subprocess.Popen(docker_command, shell=True, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    docker_image_id = out.decode("utf-8").strip('\n')

    # Determine Protocol
    console_protocol = 'https' if tlscacert else 'http'

    # Base twistcli commnad to scan images
    twistcli_base_command = 'twistcli images scan'

    # Required twistcli options to successfully scan image
    twistcli_required_options = ("--address '{}://{}:{}' --user '{}' --password '{}' --hash '{}'"
                                 .format(console_protocol,
                                         console_hostname,
                                         console_port,
                                         console_username,
                                         console_password,
                                         hash)
                                 )

    # Optional twistcli options
    options = []
    if include_package_files:
        options.append("--include-package-files")
    if details:
        options.append("--details")
    if only_fixed:
        options.append("--only-fixed")
    if tlscacert:
        # Download and store Twistlock Console site cert
        cacertfile = 'console.cer'
        stripbegin = tlscacert.replace('-----BEGIN CERTIFICATE----- ', '')
        base64 = stripbegin.replace(' -----END CERTIFICATE-----', '')
        with open(cacertfile, 'a') as f:
            f.write('-----BEGIN CERTIFICATE-----\n')
            f.write(base64.replace(' ', '\n'))
            f.write('\n-----END CERTIFICATE-----')
            f.close()
        with open(cacertfile, 'r') as fin:
            print(fin.read())
        options.append("--tlscacert {}".format(cacertfile))
    if compliance_threshold:
        options.append("--compliance-threshold '{}'".format(compliance_threshold))
    if vulnerability_threshold:
        options.append("--vulnerability-threshold '{}'".format(vulnerability_threshold))
    twistcli_optional_options = ' '.join(options)

    # Concatenate required options with upload option and the docker image id to
    twistlock_exec_upload = ' '\
        .join([twistcli_base_command, twistcli_required_options, '--upload', docker_image_id])

    proc = subprocess.Popen(twistlock_exec_upload, shell=True, stdout=subprocess.PIPE)
    stdout = proc.communicate()[0].decode('utf-8').strip('\n')

    # Execute command pipe stdout to variable and parse for Twistlock Report URL
    report_url = ''.join(
        re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', stdout))
    print('Twistlock Report: ' + report_url)

    # Download Report
    resp = requests.get(report_url, auth=(console_username, console_password), verify=False)
    with open('twistlock_report.tar.gz', 'wb') as f:
        f.write(resp.content)
        f.close()

    # Extract JSON
    tar = tarfile.open('twistlock_report.tar.gz', 'r:gz')
    tar.extractall()
    tar.close()

    # Read JSON
    data = json.load(open('analysis.json'))
    compliance_counts = data['images'][0]['info']['complianceDistribution']
    vulnerability_counts = data['images'][0]['info']['cveVulnerabilityDistribution']

    # Annotate Docker image
    report_annotation = "-l TWISTLOCK_REPORT_URL={}".format(report_url)
    compliance_annotations = create_annotation_list('_CP_VIO_CNT', compliance_counts)
    vulnerability_annotations = create_annotation_list('_VUL_VIO_CNT', vulnerability_counts)
    complete_annotations = ' '.join([report_annotation, compliance_annotations, vulnerability_annotations])
    annotate_image(codefresh_cli_key, docker_image_id, complete_annotations)

    # Concatenate twistcli executable with options from pipeline variables
    twistcli_exec = ' '\
        .join([twistcli_base_command, twistcli_required_options, twistcli_optional_options, docker_image_id])

    # Execute command pipe stdout to variable and pipe to stdout and use for final exit code for threshold support
    proc = subprocess.Popen(twistcli_exec, shell=True)
    proc.communicate()

    if proc.returncode != 0:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
