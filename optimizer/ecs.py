import os
from retrying import retry
import boto3
import botocore

class ECS(object):
    def __init__(self, region='us-east-1'):
        self.ecs = boto3.client('ecs', region_name=region)

    def _is_retryable_exception(exception):
        return not isinstance(exception, botocore.exceptions.ClientError) or \
            (exception.response["Error"]["Code"] in ['RequestLimitExceeded'])

    def list_services(self, cluster):
        service_arns = []
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
            service_arns.extend(response.get('serviceArns'))
            next_token = response.get('nextToken')

            if not next_token:
                more_results = False
        return service_arns

    @retry(retry_on_exception=_is_retryable_exception, stop_max_delay=30000, wait_exponential_multiplier=1000)
    def _ecs_list_services(self, **kwargs):
        return self.ecs.list_services(**kwargs)
