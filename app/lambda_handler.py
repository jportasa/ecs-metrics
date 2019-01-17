import boto3
from functools import reduce
from os import environ

AWS_PAGE_SIZE = 10

ecs_client = boto3.client('ecs')
cloudwatch_client = boto3.client('cloudwatch')


def __paginate_call(client, method, output_key, params=None):
    """
    Paginate a Boto3 API call on a given method to return a flat list.
    """
    def is_response_success(response):
        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    params = dict() if params is None else params
    params['PaginationConfig'] = dict(PageSize=AWS_PAGE_SIZE)

    paginator = client.get_paginator(method)
    responses = list(paginator.paginate(**params))

    if not all([is_response_success(r) for r in responses]):
        raise Exception('Error during execution of method {method}'.format(method=method))

    responses = [r[output_key] for r in responses]
    return reduce(lambda x, y: x + y, responses)


def chunk(iterable, size=AWS_PAGE_SIZE):
    """
    Split an `iterable` into chunks of `size` items
    :param iterable: the iterable that is split
    :param size: the maximum number of items in each chunk
    """
    return (iterable[pos:pos + size] for pos in range(0, len(iterable), size))


def list_clusters(_filter=None):
    """
    Return available clusters in the AWS account.
    :param _filter: filters on any part of the name of the cluster
    """
    ecs_clusters = __paginate_call(ecs_client, 'list_clusters', 'clusterArns')
    if _filter:
        ecs_clusters = [cluster for cluster in ecs_clusters if _filter in cluster]
    return sorted(ecs_clusters)


def services_in_cluster(cluster):
    params = {'cluster': cluster}
    deployed_services = __paginate_call(ecs_client, 'list_services', 'serviceArns', params)
    return deployed_services


def getCurrentDesired(cluster, service):
    describeService = ecs_client.describe_services(
        cluster=cluster,
        services=[
            service,
        ]
    )

    currentDesired = describeService['services'][0]['desiredCount']
    return currentDesired


def putMetric(cluster, service, currentDesired):
    cloudwatch_client.put_metric_data(
        Namespace='ECS',
        MetricData=[
            {
                'MetricName': 'currentDesired',
                'Dimensions': [
                    {
                        'Name': 'ClusterName',
                        'Value': cluster.split('/')[1]
                    },
                    {
                        'Name': 'ServiceName',
                        'Value': service.split('/')[1]
                    }
                ],
                'StorageResolution': 1,
                'Value': float(currentDesired)
            }
        ]
    )


def lambda_handler(event, context):

    env = environ['env']

    clusters = list_clusters(env)
    for cluster in clusters:
        deployed_services = services_in_cluster(cluster)
        for service in deployed_services:
            currentDesired = getCurrentDesired(cluster, service)
            putMetric(cluster, service, currentDesired)

    return {
        'clusters': clusters,
        'deployed_services': deployed_services,
    }
