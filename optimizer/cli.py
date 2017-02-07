#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from pprint import pprint
from aws import ECS, CloudWatch
from optimizer import MemoryOptimizer
import datetime

@click.group()
def cli():
    pass

@cli.command()
@click.argument('cluster')
@click.option('--hours', default=24, help='How many hours to look back at key metrics.')
@click.option('--oversubscribe', default=0.1, help='Maximum allowed oversubscription of memory. Increasing this will increase costs.')
@click.option('--undersubscribe', default=0.1, help='Minimum allowed undersubscription of memory. Increasing this will decrease costs.')
def memory(cluster, hours, oversubscribe, undersubscribe):
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(hours=hours)
    print 'Analyzing metrics between %s %s' % (start_date, end_date)
    ecs = ECS()
    cloudwatch = CloudWatch()
    optimizer = MemoryOptimizer(ecs, cloudwatch)

    for service in ecs.list_services(cluster):
        optimizer.optimize(cluster, service, start_date, end_date, oversubscribe, undersubscribe)

if __name__ == '__main__':
    cli()
