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
@click.option('--over-reserve', default=0.1, help='Maximum over reservation of memory. Increasing this will increase costs.')
@click.option('--under-reserve', default=0.1, help='Maximum under reservation of memory. Increasing this will decrease costs.')
def memory(cluster, hours, over_reserve, under_reserve):
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(hours=hours)
    print 'Analyzing metrics between %s %s' % (start_date, end_date)
    ecs = ECS()
    cloudwatch = CloudWatch()
    optimizer = MemoryOptimizer()

    for service in ecs.list_services(cluster):
        optimizer.optimize(ecs, cloudwatch, cluster, service, start_date, end_date, over_reserve, under_reserve)

if __name__ == '__main__':
    cli()
