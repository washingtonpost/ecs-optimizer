#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from pprint import pprint
from aws import ECS, CloudWatch
from optimizer import ServiceOptimizer
import datetime
import sys

@click.group()
def cli():
    pass

@cli.command()
@click.argument('cluster')
@click.option('--verbose/--no-verbose', default=False, help='Verbose output.')
@click.option('--interval', default='7d', help='How many days or hours to look back at key metrics.')
@click.option('--mem-over-reserve', default=0.2, help='Maximum percentage of memory reserved above peak usage before recommending a decrease. \
              Increasing this will increase costs and reduce the chance your service is killed with an out of memory error.')
@click.option('--cpu-under-reserve', default=0.1, help='Minimum percentage of CPU reserved below the average usage before recommending an increase. \
              Increasing this will decrease costs and decrease the chance your service has the CPU it needs.')
@click.option('--cpu-over-reserve', default=0.1, help='Maximum percentage of CPU reserved above average usage before recommending a decrease. \
              Increasing this will increase costs and increase the chance your service has the CPU it needs.')
@click.option('--recommend-limit-decrease/--no-recommend-limit-decrease', default=False, help='Recommend decrease in service limits')
def services(cluster, verbose, interval, mem_over_reserve, cpu_under_reserve, cpu_over_reserve, recommend_limit_decrease):
    hours = _parse_interval(interval)
    if not hours:
        print 'Invalid --interval option: %s' % interval
        sys.exit(1)
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(hours=hours)
    print 'Analyzing metrics between %s and %s' % (start_date.strftime('%Y-%m-%d %H:%M'), end_date.strftime('%Y-%m-%d %H:%M'))
    ecs = ECS()
    cloudwatch = CloudWatch()
    optimizer = ServiceOptimizer(ecs, cloudwatch)

    for service in ecs.list_services(cluster):
        optimizer.optimize(verbose, cluster, service, start_date, end_date, cpu_over_reserve, cpu_under_reserve, mem_over_reserve,
                           recommend_limit_decrease)

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
