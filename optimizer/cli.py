#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from pprint import pprint
from aws import ECS, CloudWatch
from optimizer import MemoryOptimizer

@click.group()
def cli():
    pass

@cli.command()
@click.argument('cluster')
@click.option('--oversubscribe', default=0.1, help='Maximum allowed oversubscription of memory. Increasing this will increase costs.')
@click.option('--undersubscribe', default=0.1, help='Minimum allowed undersubscription of memory. Increasing this will decrease costs.')
def memory(cluster, oversubscribe, undersubscribe):
    ecs = ECS()
    cloudwatch = CloudWatch()
    optimizer = MemoryOptimizer(ecs, cloudwatch)

    for service in ecs.list_services(cluster):
        optimizer.optimize(cluster, service, oversubscribe, undersubscribe)

if __name__ == '__main__':
    cli()
