import os
from retrying import retry
import boto3
import botocore
from datetime import datetime
from pprint import pprint

def _is_retryable_exception(exception):
    return not isinstance(exception, botocore.exceptions.ClientError) or \
        (exception.response["Error"]["Code"] in ['RequestLimitExceeded'])


class ECS(object):
    def __init__(self, region='us-east-1'):
        self.ecs = boto3.client('ecs', region_name=region)

    def list_services(self, cluster):
        services = []
        next_token = None
        more_results = True
        while more_results:
            kwargs = {
                'cluster': cluster,
                'maxResults': 10,
            }
            if next_token:
                kwargs['nextToken'] = next_token
            response = self._ecs_list_services(**kwargs)
            for service_arn in response.get('serviceArns'):
                name = service_arn.split(':')[5].split('/')[1]
                services.append(name)

            next_token = response.get('nextToken')

            if not next_token:
                more_results = False

        return sorted(services)

    def service_reservations(self, cluster, service):
        response = self._ecs_describe_services(cluster=cluster, services=[service])
        for service in response.get('services', []):
            task_definition = service.get('taskDefinition')
            return self.task_reservations(task_definition)

    def task_reservations(self, task_definition):
        mem_hard_limit = 0
        mem_soft_limit = 0
        cpu_shares = 0
        response = self._ecs_describe_task_definition(taskDefinition=task_definition)
        for container in response.get('taskDefinition', {}).get('containerDefinitions', []):
            mem_soft_limit += container.get('memoryReservation', 0)
            mem_hard_limit += container.get('memory', 0)
            cpu_shares += container.get('cpu', 0)

        return cpu_shares, mem_hard_limit, mem_soft_limit

    def instance_capacity(self, cluster):
        cpu_capacity = None
        mem_capacity = None
        response = self._ecs_list_container_instances(cluster=cluster, maxResults=1, status='ACTIVE')
        instance_arns = response.get('containerInstanceArns', [])
        if len(instance_arns):
            response = self._ecs_describe_container_instances(cluster=cluster, containerInstances=instance_arns)
            for container_instance in response.get('containerInstances', []):
                resources = container_instance.get('registeredResources', [])
                for resource in resources:
                    if 'cpu' == resource.get('name').lower():
                        cpu_capacity = resource.get('integerValue')
                    elif 'memory' == resource.get('name').lower():
                        mem_capacity = resource.get('integerValue')

        return cpu_capacity, mem_capacity

    @retry(retry_on_exception=_is_retryable_exception, stop_max_delay=5000, wait_exponential_multiplier=500)
    def _ecs_describe_container_instances(self, **kwargs):
        return self.ecs.describe_container_instances(**kwargs)

    @retry(retry_on_exception=_is_retryable_exception, stop_max_delay=5000, wait_exponential_multiplier=500)
    def _ecs_list_container_instances(self, **kwargs):
        return self.ecs.list_container_instances(**kwargs)

    @retry(retry_on_exception=_is_retryable_exception, stop_max_delay=5000, wait_exponential_multiplier=500)
    def _ecs_describe_task_definition(self, **kwargs):
        return self.ecs.describe_task_definition(**kwargs)

    @retry(retry_on_exception=_is_retryable_exception, stop_max_delay=5000, wait_exponential_multiplier=500)
    def _ecs_describe_services(self, **kwargs):
        return self.ecs.describe_services(**kwargs)

    @retry(retry_on_exception=_is_retryable_exception, stop_max_delay=5000, wait_exponential_multiplier=500)
    def _ecs_list_services(self, **kwargs):
        return self.ecs.list_services(**kwargs)


class CloudWatch(object):
    def __init__(self, region='us-east-1'):
        self.ecs = boto3.client('ecs', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)

    def max_memory_utilization(self, cluster, service, start_date, end_date):
        response = self._cloudwatch_get_metric_statistics(Namespace='AWS/ECS',
                                                          MetricName='MemoryUtilization',
                                                          Dimensions=[{'Name': 'ClusterName', 'Value': cluster}, {'Name': 'ServiceName', 'Value': service}],
                                                          StartTime=start_date,
                                                          EndTime=end_date,
                                                          Period=3600,
                                                          Statistics=['Maximum'],
                                                          Unit='Percent')
        range_max = 0.0
        for metric in response.get('Datapoints', []):
            hourly_max = metric.get('Maximum')
            if hourly_max is not None:
                if hourly_max > range_max:
                    range_max = hourly_max

        return range_max

    def avg_cpu_utilization(self, cluster, service, start_date, end_date):
        response = self._cloudwatch_get_metric_statistics(Namespace='AWS/ECS',
                                                          MetricName='CPUUtilization',
                                                          Dimensions=[{'Name': 'ClusterName', 'Value': cluster}, {'Name': 'ServiceName', 'Value': service}],
                                                          StartTime=start_date,
                                                          EndTime=end_date,
                                                          Period=3600,
                                                          Statistics=['Average'],
                                                          Unit='Percent')
        range_sum = 0.0
        count = 0

        # geometrically link the hourly averages to get a range average
        for metric in response.get('Datapoints', []):
            hourly_avg = metric.get('Average')
            range_sum += hourly_avg
            count += 1

        if count == 0:
            return range_sum
        else:
            return range_sum / count

    @retry(retry_on_exception=_is_retryable_exception, stop_max_delay=30000, wait_exponential_multiplier=1000)
    def _cloudwatch_get_metric_statistics(self, **kwargs):
        return self.cloudwatch.get_metric_statistics(**kwargs)

