#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('--cluster', help='ECS cluster to optimize.')
def service(cluster):
    print cluster

if __name__ == '__main__':
    cli()
