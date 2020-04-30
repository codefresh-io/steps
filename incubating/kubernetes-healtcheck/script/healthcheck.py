import datetime
import json
from kubernetes import client, config
from kubernetes.client import configuration
from prometheus_http_client import Prometheus
import os
import time
import sys

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

def kube_http_client(healthcheck_type, cluster, namespace, deployment):
    print('Making Kubernetes API call')
    config.load_kube_config(context=cluster)
    api = client.AppsV1Api()
    if healthcheck_type.strip() == 'kubernetes_deployment':
        print('Checking on Kubernetes Deployment')
        api_response = api.read_namespaced_deployment_status(deployment, namespace, _preload_content=False)
    elif healthcheck_type.strip() == 'kubernetes_statefulset':
        print('Checking on Kubernetes Statefulset')
        api_response = api.read_namespaced_stateful_set_status(deployment, namespace, _preload_content=False)
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
            print('No Unavailable Replicas Found')
            unavailable_replicas = 0
    elif healthcheck_type.strip() == 'kubernetes_statefulset':
        ready_replicas = response_dict['status']['readyReplicas']
        unavailable_replicas = replicas - ready_replicas
    d = dict();  
    d['name'] = name
    d['unavailable_replicas'] = unavailable_replicas
    return d

def get_metrics(metric):
    prometheus = Prometheus()
    query_results = prometheus.query(metric=f'{metric}')
    query_dict = json.loads(query_results)
    success_percent = query_dict['data']['result'][0]['value'][1]
    if success_percent.replace('.','',1).isdigit():
        return success_percent
    else:
        return False

def main():

    cluster = os.getenv('CLUSTER')
    deployment = os.getenv('DEPLOYMENT')
    deploy_time_wait = os.getenv('DEPLOY_WAIT', 5)
    deploy_timeout = os.getenv('DEPLOY_TIMEOUT', 120)
    metric_timeout = os.getenv('METRIC_TIMEOUT', 120)
    namespace = os.getenv('NAMESPACE')
    testing_time_total = os.getenv('TOTAL', 300)
    testing_time_wait = os.getenv('WAIT', 15)
    threshold = os.getenv('THRESHOLD', 1)
    types = os.getenv('TYPES')

    d_timeout = time.time() + int(deploy_timeout)

    healthcheck_types = types.lower().strip()

    healthcheck_list = healthcheck_types.split(';')

    for healthcheck_type in healthcheck_list:
        if 'kubernetes' in healthcheck_type:
            deployment_completed = False
            while not deployment_completed:
                print(f'Checking Deployment Status for: {deployment}')
                response_dict = kube_http_client(healthcheck_type, cluster, namespace, deployment)
                name = response_dict['name']
                unavailable_replicas = response_dict['unavailable_replicas']
                if unavailable_replicas == 0:
                    deployment_completed = True
                    print('Deployment Completed Successfully')
                    break
                else:
                    print(f'Deployment for {name} has not completed...')
                    print(f'Deployment has {unavailable_replicas} unavailable replicas.')
                    print(f'Issuing another check in {deploy_time_wait} seconds...')
                    time.sleep(int(deploy_time_wait))
                if time.time() > d_timeout:
                    print(f'Deployment Timeout ({deploy_timeout}) Exceeded!!!' )
                    print('Rollback Initiated')
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


if __name__ == "__main__":
    main()