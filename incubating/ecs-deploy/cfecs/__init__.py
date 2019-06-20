import logging, pprint, boto3, time, copy, pytz
from datetime import datetime

C_SUCCESS = 'SUCCESS'
C_FAIL = 'FAIL'
C_TIMEOUT = 'TIMEOUT'
C_SUBMITTED = 'SUBMITTED'

def now():
    return datetime.now().strftime('%d-%b-%Y %H:%M:%S.%f')[:-3]

LOGGER_NAME = 'cfecs_logger'
def init_log(level=logging.INFO, log_stdout=True):
    log = logging.getLogger(LOGGER_NAME)
    if not [sh for sh in log.handlers if sh.__class__.__name__ == 'StreamHandler'] and log_stdout:
        log.addHandler(logging.StreamHandler())

    log.setLevel(level)
    for h in log.handlers:
        h.setLevel(level)
    return log
log = init_log()

def get_ecs(**kwargs):
    return boto3.client('ecs', **kwargs)

def _ecs_arn_dsp(arn):
    """
    :param arn:
    :return: display name of ecs
    """
    try:
        return arn.split('/')[1]
    except Exception:
        return arn

def _ecs_service_dsp(service):
    """
    copies service dict for display
    :param service:
    :return:
    """
    _service = copy.deepcopy(service)
    if "events" in _service:
        del _service["events"]
    return _service


WAIT_SLEEP=10
DEPLOY_TIMEOUT=900
MAX_FAILED_TASKS=2

def wait_for_deployment(cluster_name, service_name, ecs=None, **kwargs):
    """
    Waiting for ecs deployment (update service) to complete
    :param cluster_name:
    :param service_name:
    :param ecs:
    :param kwargs:

    :return:
    """
    log.info("\n---------------------\nWaiting For Deployment: cluster = {} , service = {} ...".format(cluster_name, service_name))
    if not ecs:
        ecs = get_ecs(region_name = kwargs.get("region_name"))

    d_start = datetime.now()
    deploy_timeout = kwargs.get('deploy_timeout') or DEPLOY_TIMEOUT
    max_failed_tasks = kwargs.get('max_failed') or MAX_FAILED_TASKS
    failed_tasks = []
    log.info("Wait until runningCount will be equal to desiredCount for PRIMARY service task ... ")
    while True:
        time.sleep(WAIT_SLEEP)
        log.info("\n........... {}".format(now()))

        service = ecs.describe_services(cluster=cluster_name, services=[service_name])['services'][0]
        task_definition_arn = service["taskDefinition"]
        deployments = service["deployments"]
        deployment_created_at = None
        for d in deployments:
            log.info( "    {}  task {} - runningCount = {} , desiredCount = {},  pendingCount = {}".
                      format(d["status"], _ecs_arn_dsp(d["taskDefinition"]), d.get("runningCount"), d.get("desiredCount"), d.get("pendingCount")))

            if d['status'] == 'PRIMARY':
                deployment_created_at = d['createdAt']

            if d['status'] == 'PRIMARY' and d["desiredCount"] == d["runningCount"]:
                log.info("Deployment completed Successfully!!!")
                return {"status": C_SUCCESS, "service": _ecs_service_dsp(service)}

        # Check for failed tasks every 30s
        if (datetime.now() - d_start).total_seconds() > 30:
            failed_tasks = get_failed_tasks(cluster_name, service_name, task_definition_arn, ecs,
                                            max_results=max_failed_tasks, created_after=deployment_created_at)
            if failed_tasks and len(failed_tasks) >= max_failed_tasks:
                log.error("ERROR:  {} or more ecs tasks failed".format(max_failed_tasks))
                log.error(pprint.pformat(failed_tasks))
                return {"status": C_FAIL, "failed_tasks": failed_tasks}

        if (datetime.now() - d_start).total_seconds() > deploy_timeout:
            log.error("ERROR: Deploy Timeout {}s reached ".format(deploy_timeout))
            return {"status": C_TIMEOUT, "service": _ecs_service_dsp(service), "failed_tasks": failed_tasks}

def get_failed_tasks(cluster_name, service_name, task_definition_arn, ecs=None, **kwargs):
    """

    :param cluster_name:
    :param service_name:
    :param task_definition_arn:
    :param created_after:
    :param max_results:
    :param next_token:
    :return:
    """

    region_name = kwargs.get("region_name")
    created_after = (kwargs.get('created_after') or datetime.fromtimestamp(1)).replace(tzinfo=pytz.utc)
    max_results = kwargs.get('max_results')
    next_token = kwargs.get('next_token') or ""
    if not ecs:
        ecs = get_ecs(region_name = region_name)


    def is_task_failed(task):
        if task.get('lastStatus') != 'STOPPED':
            return False
        if task.get('stoppedReason') and 'Scaling activity initiated by' not in task.get('stoppedReason'):
            return True
        failed_containers = [t for t in task.get('containers') if t.get('reason') and 'error' in (t['reason']).lower or t.get('exitCode') > 0]
        if failed_containers:
            return True

    task_list_resp = ecs.list_tasks(cluster=cluster_name, serviceName=service_name, desiredStatus='STOPPED',
                                    maxResults=min((max_results or 100), 100), nextToken=next_token)
    next_token = task_list_resp.get('nextToken')
    task_arns_resp = task_list_resp.get("taskArns")
    if not task_arns_resp:
        return []

    tasks_all_resp = ecs.describe_tasks(cluster=cluster_name, tasks=task_arns_resp)
    tasks_all = tasks_all_resp.get('tasks')
    failed_tasks = [t for t in tasks_all if t.get('taskDefinitionArn') == task_definition_arn and t.get('createdAt').replace(tzinfo=pytz.utc) > created_after and is_task_failed(t)]
    if not next_token or max_results and len(failed_tasks) >= max_results:
        return failed_tasks
    else:
        return failed_tasks + get_failed_tasks(cluster_name, service_name, task_definition_arn, ecs, created_after=created_after, max_results=max_results, next_token=next_token)


def update_service(cluster_name, service_name, ecs=None, **kwargs):

    log.info("\n---------------------\nUpdating Service: cluster = {} , service = {}\n"
             "{}".format(cluster_name, service_name, pprint.pformat(kwargs, indent=4)))
    if not ecs:
        ecs = get_ecs(region_name = kwargs.get("region_name"))

    services = ecs.describe_services(cluster=cluster_name, services=[service_name])
    if not services or not services.get('services'):
        raise Exception("ERROR: Cannot find service {} in cluster {}".format(service_name, cluster_name))

    service = services['services'][0]
    current_task_def_arn = service["taskDefinition"]
    log.info('current task definition arn = {}'.format(current_task_def_arn))

    task_definition_desc = ecs.describe_task_definition(taskDefinition = current_task_def_arn)
    task_definition = task_definition_desc['taskDefinition']
    keys_to_remove = ["status", "taskDefinitionArn", "requiresAttributes", "revision", "compatibilities"]
    for k in keys_to_remove:
        task_definition.pop(k, None)

    image_name = kwargs.get('image_name')
    new_image_tag = kwargs.get('image_tag')
    new_image_name_tag = '{}:{}'.format(image_name, new_image_tag)
    if image_name and new_image_tag:
        _found = False
        for c in task_definition['containerDefinitions']:
            _image_name_split = c.get('image').split(':')
            if _image_name_split[0] == image_name:
                log.info("Set new image: {} ( was {} )".format(new_image_name_tag, c.get('image')))
                c['image'] = new_image_name_tag
                _found = True
                break
        if not _found:
            raise Exception("ERROR: Cannot find image {} in service {} of cluster {}".format(image_name, service_name, cluster_name))

    register_task_resp = ecs.register_task_definition(**task_definition)
    new_task_def_arn = register_task_resp['taskDefinition']['taskDefinitionArn']

    log.info("new task definition arn: {}".format(new_task_def_arn))

    update_service_params = {
        'cluster': cluster_name,
        'service': service_name,
        'desiredCount': service['desiredCount'],
        'taskDefinition': new_task_def_arn,
        'deploymentConfiguration': service['deploymentConfiguration']
    }
    log.info("Updating Service: {}".format(pprint.pformat(update_service_params)))
    response = ecs.update_service(**update_service_params)
    if not response or not response.get('service') or not response.get('ResponseMetadata') or response.get('ResponseMetadata').get('HTTPStatusCode') > 299:
        raise Exception("ERROR: Invalid response from aws: {}".format(response))

    wait = kwargs.get('wait')
    if wait:
        log.info("Waiting for deployment to complete ...")
        return wait_for_deployment(cluster_name, service_name, ecs, **kwargs)
    else:
        return {"status": C_SUBMITTED, "service": _ecs_service_dsp(response['service'])}

