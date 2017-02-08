#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from pprint import pprint
from aws import ECS, CloudWatch
from optimizer import MemoryOptimizer
import datetime
import sys

@click.group()
def cli():
    pass

@cli.command()
@click.argument('cluster')
@click.option('--interval', default='7d', help='How many days or hours to look back at key metrics.')
@click.option('--over-reserve', default=0.1, help='Maximum over reservation of memory. Increasing this will increase costs.')
@click.option('--under-reserve', default=0.1, help='Maximum under reservation of memory. Increasing this will decrease costs.')
def services(cluster, interval, over_reserve, under_reserve):
    hours = _parse_interval(interval)
    if not hours:
        print 'Invalid --interval option: %s' % interval
        sys.exit(1)
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(hours=hours)
    print 'Analyzing metrics between %s and %s' % (start_date.strftime('%Y-%m-%d %H:%M'), end_date.strftime('%Y-%m-%d %H:%M'))
    ecs = ECS()
    cloudwatch = CloudWatch()
    optimizer = MemoryOptimizer()

    for service in ecs.list_services(cluster):
        optimizer.optimize(ecs, cloudwatch, cluster, service, start_date, end_date, over_reserve, under_reserve)

def _parse_interval(interval):
    number = int(interval[:-1])
    unit = interval[-1].lower()
    if unit == 'h':
        return number
    elif unit == 'd':
        return 24 * number
    return None

if __name__ == '__main__':
    cli()
