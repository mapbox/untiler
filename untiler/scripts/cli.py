#!/usr/bin/env python

import os, tarfile, re

import click, mercantile

import untiler

@click.group()
def cli():
    pass

@click.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=True))
@click.option('--compositezoom', '-c', default=13, type=int,
    help='Tile size to mosaic into [default=13]')
@click.option('--maxzoom', '-z', default=None, type=int,
    help='Force a maxzom [default=max in each compositezoom area]')
@click.option('--logdir', '-l', default=None, help="Location for log files [default=None]")
@click.option('--readtemplate', '-t', default="jpg/{z}/{x}/{y}.jpg", help="File path template [default='jpg/{z}/{x}/{y}.jpg']")
@click.option('--scenetemplate', '-s', default="{z}-{x}-{y}-tile.tif", help="Template for output scenetif filenames [default='{z}-{x}-{y}-tile.tif']")
@click.option('--workers', '-w', default=4, help="Number of workers in the processing pool [default=4]")
def streamdir(input_dir, output_dir, compositezoom, maxzoom, logdir, readtemplate, scenetemplate, workers):
    untiler.stream_dir(input_dir, output_dir, compositezoom, maxzoom, logdir, readtemplate, scenetemplate, workers)

cli.add_command(streamdir)

@click.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--zoom', '-z', default=None, type=int,
    help='Zoom to inspect [default = all]')
@click.option('--readtemplate', '-t', default="jpg/{z}/{x}/{y}.jpg",
    help="File path template [default='jpg/{z}/{x}/{y}.jpg']")
def inspectdir(input_dir, zoom, readtemplate):
    untiler.inspect_dir(input_dir, zoom, readtemplate)

cli.add_command(inspectdir)

if __name__ == "__main__":
    cli()
