#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from pprint import pprint
from ecs import ECS

@click.group()
def cli():
    pass

@cli.command()
@click.argument('cluster')
def service(cluster):
    ecs = ECS()
    for service in ecs.list_services(cluster):
        print service

if __name__ == '__main__':
    cli()
