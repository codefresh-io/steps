import os.path
import json
import sys

def get_cvss_threshold(threshold):
    if threshold == 'LOW':
        cvss_threshold = 3.9
    elif threshold == 'MEDIUM':
        cvss_threshold = 6.9
    elif threshold == 'HIGH':
        cvss_threshold = 8.9
    elif threshold == 'CRITICAL':
        cvss_threshold = 10
    return cvss_threshold


def get_max_cvss(results_dict):
    max_cvss_score = 0
    for dic in results_dict:
        for key in dic:
            if key == 'vulnerability':
                if 'cvssScore' in dic['vulnerability']:
                    current_score = dic['vulnerability']['cvssScore']
                    if type(current_score) == int or type(current_score) == float:
                        if dic[key]['cvssScore'] > max_cvss_score:
                            max_cvss_score = dic['vulnerability']['cvssScore']
    return max_cvss_score


def main():

# Get Vars

    working_directory = os.getenv('WORKING_DIRECTORY')
    threshold = os.getenv('CVSS_SCORE') or os.getenv('THRESHOLD')

# Get CVSS

    if type(threshold) == int or type(threshold) == float:
        cvss_threshold = threshold
        print('CVSS Score for Threshold is: {}'.format(str(cvss_threshold)))
    else:
        cvss_threshold = get_cvss_threshold(threshold)
        print('CVSS Score for Threshold is: {}'.format(str(cvss_threshold)))

# Read YAML file

    results_json_path = (os.path.join(working_directory, 'results.json'))

    with open(results_json_path, 'r') as json_data:
        results_dict = json.load(json_data)

# Get Max CVSS for YAML file
    max_cvss_score = 0
    max_cvss_score = get_max_cvss(results_dict)

    print('Max CVSS Score Found in Results: {}'.format(str(max_cvss_score)))

# # Check Max CVSS against Threshold

    if max_cvss_score < float(cvss_threshold):
        print('All CVSS Scores are below Threshold')
    else:
        print('CVSS Scores Violated Threshold!')
        sys.exit(1)

# TODO Create Annotations to image

# TODO Create Violations file

if __name__ == '__main__':
    main()