import yaml
import sys
import os


def main():

    applicationset_file = os.getenv('APPLICATIONSET_FILE')
    pipeline_id = os.getenv('PIPELINE')
    run_list_file = os.getenv('RUNLIST_FILE')
    sha = os.getenv('SHA')
    trigger_id = os.getenv('TRIGGER')

    # Open YAML file and import to dictionary
    try:
        with open(applicationset_file) as f:
            appsetDict = yaml.safe_load(f)
    except:
        print('File Not Found: {}'.format(applicationset_file))
        sys.exit(1)

    # Pipeline item example:
    #   - pipeline_id: my-project/my-pipeline3
    #     trigger_id: my-trigger-name
    #     sha: 941852163761eb98f21a339a9988cbb7f2cdd589
    #     variables:
    #       SOME_VAR: blah
    #       SOME_OTHER_VAR: blahblah

    # List example:
    #   generators:
    #     - list:
    #         elements:
    #           - cluster: dev
    #             url: https://2A343DA625C5CD98C0D8616D5394DD00.gr7.us-west-2.eks.amazonaws.com
    #             namespace: development
    #           - cluster: stage
    #             url: https://E4AE0FC20FE62919F26F73A002E7D18E.gr7.us-west-2.eks.amazonaws.com
    #             namespace: staging
    #           - cluster: prod
    #             url: https://4590144362D24F48EF6C165BF1D32B3C.gr7.us-west-2.eks.amazonaws.com
    #             namespace: production        

    # Create runlist dictionary

    runlistArr = []

    # Loop list and generate pipelines

    for item in appsetDict['spec']['generators'][0]['list']['elements']:

        itemDict = item

        pipelineDict = {
            'pipeline_id': pipeline_id,
            'trigger_id': trigger_id,
            'sha': sha
        }

        pipelineDict['variables'] = {}

        for key, value in itemDict.items():
            print(key, value)
            pipelineDict['variables'][key] = value
        runlistArr.append(pipelineDict)

    # Write YAML file
    with open(run_list_file, 'w') as f:
        yaml.dump(runlistArr, f)
    
    print('Created: {}'.format(run_list_file))


if __name__ == "__main__":
    main()