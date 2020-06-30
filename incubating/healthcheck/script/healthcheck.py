import datetime
import json
from kubernetes import client, config
from kubernetes.client import configuration
from prometheus_http_client import Prometheus
from datadog import initialize, api
import os
import time
import sys
import operator

class Error(Exception):
   """Base class for other exceptions"""
   pass
class MetricThreshold(Error):
   """Raised when metrics are below threshold given"""
   pass
class PrometheusMetricsNotAvailable(Error):
   """Raised when metrics are not returned from Prometheus"""
   pass
class ThresholdCheckFailed(Error):
   """Raised when metrics tests have failed"""
   pass
class DatadogNoSLOHistory(Error):
   """Raised when SLO in Datadog returns no history"""
   pass
class DatadogSLOFailing(Error):
   """Raised when SLO in Datadog returns failing status"""
   pass
class NoJobStatus(Error):
   """Raised when Job API does not return a status"""
   pass

def kube_http_client(healthcheck_type, cluster, namespace, resource):
    config.load_kube_config(context=cluster)
    api = client.AppsV1Api()
    batch_api = client.BatchV1Api()
    core_api = client.CoreV1Api()
    if healthcheck_type.strip() == 'kubernetes_deployment':
        print('Checking on Kubernetes Deployment')
        api_response = api.read_namespaced_deployment_status(resource, namespace, _preload_content=False)
    elif healthcheck_type.strip() == 'kubernetes_statefulset':
        print('Checking on Kubernetes Statefulset')
        api_response = api.read_namespaced_stateful_set_status(resource, namespace, _preload_content=False)
    elif healthcheck_type.strip() == 'kubernetes_job':
        print('Checking on Kubernetes Job')
        while True:
            try:
                api_response = batch_api.read_namespaced_job_status(resource, namespace, _preload_content=False)
                json_data = api_response.read()
                response_dict = json.loads(json_data.decode('utf-8'))
                name = response_dict['metadata']['name']
                status = response_dict['status']['conditions'][0]['type'] or response_dict['status']['active']
                print('Job: {} Status: {}'.format(name, status))
                if status == '1':
                    print('Still Active, Sleeping 5 seconds.')
                    time.sleep(5)
                    continue
                else:
                    break
            except NoJobStatus:
                continue
            break
        if status == 'Complete':
            print('Job Succeeded')
            return True
        elif status == 'Failed':
            print('Job Failed')
            label = response_dict['spec']['selector']['matchLabels']['controller-uid']
            print(f'Getting Pod for Controller UI: {label}')
            api_response = core_api.list_namespaced_pod(namespace=namespace, label_selector='controller-uid={}'.format(label), _preload_content=False)
            json_data = api_response.read()
            pods = json.loads(json_data.decode('utf-8'))
            pods_list = pods['items']
            sorted_pods = sorted(pods_list, key=lambda k: k['metadata']['creationTimestamp'],  reverse=True)
            last_pod = sorted_pods[0]
            pod_name = last_pod['metadata']['name']
            print(f'Last pod running for job: {pod_name}')
            print('Last run: {}'.format(last_pod['metadata']['creationTimestamp']))
            for container in last_pod['spec']['containers']:
                print('Container: {}'.format(container['name']))
                print('Fetching Logs')
                api_response = core_api.read_namespaced_pod_log(name=pod_name, namespace=namespace, container=container['name'], _preload_content=False)
                logs = api_response.read()
                print(logs.decode())
                log_directory = '/codefresh/volume/healthcheck/{}'.format(name)
                if not os.path.exists(log_directory):
                    os.makedirs(log_directory)
                log_file = '{}/{}-{}.log'.format(log_directory, container['name'], datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
                f = open(log_file, 'wb')
                f.write(logs)
                f.close()
                print(f'Logs written to: {log_file}')
            return False
        else:
            return False
    else:
        print('Incorrect Kubernetes Health Check Type {}'.format(healthcheck_type))
        sys.exit(1)
    json_data = api_response.read()
    response_dict = json.loads(json_data.decode('utf-8'))
    name = response_dict['metadata']['name']
    replicas = response_dict['status']['replicas']
    if healthcheck_type.strip() == 'kubernetes_deployment':
        try:
            current_replicas = response_dict['status']['unavailableReplicas']
        except:
            print('All Replicas are reporting Healthy.')
            unavailable_replicas = 0
    elif healthcheck_type.strip() == 'kubernetes_statefulset':
        ready_replicas = response_dict['status']['readyReplicas']
        unavailable_replicas = replicas - ready_replicas
    d = dict();  
    d['name'] = name
    d['unavailable_replicas'] = unavailable_replicas
    if unavailable_replicas == 0:
        return True
    else:
        return False

def get_metrics(metric):
    prometheus = Prometheus()
    query_results = prometheus.query(metric=f'{metric}')
    query_dict = json.loads(query_results)
    success_percent = query_dict['data']['result'][0]['value'][1]
    if success_percent.replace('.','',1).isdigit():
        return success_percent
    else:
        return False

def get_slo_id(name):
    query = name
    get_slo = api.ServiceLevelObjective.get_all(query=query)
    json_formatted_str_slo = json.dumps(get_slo, indent=2)
    query_slo_dict = json.loads(json_formatted_str_slo)
    slo_id = query_slo_dict['data'][0]['id']
    return slo_id

def get_slo_history(slo_id, from_ts, **kwargs):
    timeframe = kwargs.get('timeframe', None)
    formatted_from_ts = datetime.datetime.fromtimestamp(float(from_ts)).strftime('%c')
    while True:
        try:
            time.sleep(1)
            to_ts = int(time.time())
            formatted_to_ts = datetime.datetime.fromtimestamp(float(to_ts)).strftime('%c')
            print(f'Checking SLO History between {formatted_from_ts} to {formatted_to_ts}')
            slo_history = api.ServiceLevelObjective.history(slo_id, from_ts, to_ts)
            json_formatted_str_slo_history = json.dumps(slo_history, indent=2)
            print(json_formatted_str_slo_history)
            query_history_dict = json.loads(json_formatted_str_slo_history)
            if query_history_dict['data']['type'] == 'metric':
                print('Evaluating SLO Metrics')
                sli_value = query_history_dict['data']['overall']['sli_value']
                print(sli_value)
                target_value = query_history_dict['data']['thresholds'][timeframe]['target']
                print(target_value)
                if float(sli_value) >= float(target_value):
                    status = 0
                else:
                    status = 1
                history = [to_ts,status]
            else:
                history = query_history_dict['data']['overall']['history'][-1]
        except DatadogNoSLOHistory:
            print('Waiting 10 seconds for history')
            time.sleep(10)
            continue
        break
    print(history)
    return history

def main():

    cluster = os.getenv('CLUSTER')
    deployment = os.getenv('DEPLOYMENT')
    job = os.getenv('JOB')
    deploy_time_wait = os.getenv('DEPLOY_WAIT', 5)
    deploy_timeout = os.getenv('TESTING_TIMEOUT', 120)
    metric_timeout = os.getenv('METRIC_TIMEOUT', 120)
    namespace = os.getenv('NAMESPACE')
    testing_time_total = os.getenv('TOTAL', 300)
    testing_time_wait = os.getenv('WAIT', 15)
    threshold = os.getenv('THRESHOLD', 1)
    types = os.getenv('TYPES')
    datadog_api_key = os.getenv('DATADOG_API_KEY')
    datadog_app_key = os.getenv('DATADOG_APP_KEY')
    datadog_slo_list = os.getenv('DATADOG_SLO_LIST')
    datadog_slo_timewindow = os.getenv('DATADOG_SLO_TIMEWINDOW')

    d_timeout = time.time() + int(deploy_timeout)

    healthcheck_types = types.lower().strip()

    healthcheck_list = healthcheck_types.split(';')

    resource = deployment or job

    for healthcheck_type in healthcheck_list:
        if 'kubernetes' in healthcheck_type:
            testing_completed = False
            while not testing_completed:
                print(f'Checking Status of: {resource}')
                results = kube_http_client(healthcheck_type, cluster, namespace, resource)
                if results:
                    testing_completed = True
                    print('Testing Completed Successfully')
                    break
                else:
                    print(f'Testing for {resource} has not completed...')
                    print(f'Issuing another check in {deploy_time_wait} seconds...')
                    time.sleep(int(deploy_time_wait))
                if time.time() > d_timeout:
                    print(f'Deployment Timeout ({deploy_timeout}) Exceeded!!!' )
                    sys.exit(1)

        # Prometheus Tests

        if healthcheck_type == 'linkerd':

            app_info = f'namespace="{namespace}", deployment="{deployment}"'

            metric = 'sum(irate(response_total{classification="success", %s, direction="inbound"}[30s])) / sum(irate(response_total{%s, direction="inbound"}[30s]))' % (app_info, app_info)

            m_timeout = time.time() + int(metric_timeout)

            testing_started = False
            print('Checking for Prometheus for Metrics')
            while not testing_started:
                try:
                    check_for_metrics = get_metrics(metric)
                    if not check_for_metrics:
                        raise PrometheusMetricsNotAvailable
                    else:
                        print('Metrics Returned, Starting Timed Health Check')
                        testing_started = True
                        t_end = time.time() + int(testing_time_total)
                        while time.time() < t_end:
                            try:
                                success_percent = get_metrics(metric)
                                if not success_percent:
                                    print('Metrics Not Available At This Time.')
                                    time.sleep(int(testing_time_wait))
                                    threshold_check_failed = False
                                else:
                                    if float(success_percent) >= float(threshold):
                                        threshold_check_failed = False
                                        print('Health Check Passed, Success Rate at: {:.1%}'.format(1))
                                        time.sleep(int(testing_time_wait))
                                    else:
                                        threshold_check_failed = True
                                        testing_completed = True
                                        raise MetricThreshold
                            except (MetricThreshold):
                                print(f'Success Rate {success_percent} lower than threshold')
                                print('Metric Below Success Threshold!')
                                break                    
                            except:
                                print('Success Metrics Not Available...')
                                time.sleep(int(testing_time_wait))
                                pass
                        if threshold_check_failed:
                            raise ThresholdCheckFailed
                except (PrometheusMetricsNotAvailable):
                    print('Metrics Not Yet Available At This Time.')
                    print('Retrying Metric Test...')
                    if time.time() > m_timeout:
                        print(f'Metrics Timeout ({deploy_timeout}) Exceeded!!!' )
                        print('Rollback Initiated')
                        sys.exit(1)
                    time.sleep(int(testing_time_wait))
                    pass
                except (ThresholdCheckFailed):
                    print('Threshold Check Failed!!!')
                    print('Rollback Initiated')
                    sys.exit(1)
    
            print('Testing Completed Successfully')

        # Datadog Tests

        if healthcheck_type == 'datadog-slo':
            from_ts = int(time.time())
            options = {
                'api_key': datadog_api_key,
                'app_key': datadog_app_key
            }
            initialize(**options)
            t_end = time.time() + int(testing_time_total)
            while time.time() < t_end:
                try:
                    datadog_slos = datadog_slo_list.split(';')
                    for name in datadog_slos:
                        print(f'Testing SLO: {name}')
                        slo_id = get_slo_id(name)
                        history = get_slo_history(slo_id, from_ts, timeframe=datadog_slo_timewindow)
                        date, status = history
                        formatted_date = datetime.datetime.fromtimestamp(float(date)).strftime('%c')
                        if status == 1:
                            print(f'!!!!!Service Level Objective {name} started FAILING at {formatted_date}!!!!!')
                            raise DatadogSLOFailing
                        else:
                            print(f'Service Level Objective {name} is passing at {formatted_date}')
                    print(f'Waiting {testing_time_wait} Seconds before retesting')
                    time.sleep(int(testing_time_wait))
                except:
                    print(f'No Results Found for: {name}')
                    sys.exit(1)
            print('Testing Completed Successfully')


if __name__ == "__main__":
    main()