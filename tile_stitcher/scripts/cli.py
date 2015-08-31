#!/usr/bin/env python

import os, tarfile, re

import click, mercantile

import tile_stitch

@click.group()
def cli():
    pass

@click.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=True))
@click.option('--compositezoom', '-c', default=14, type=int,
    help='Tile size to mosaic into [default = 4]')
@click.option('--maxzoom', '-z', default=None, type=int,
    help='Force a maxzom [default = max in tar]')
@click.option('--logdir', '-l', default=None, help="Location for log files")
@click.option('--readtemplate', '-t', default="jpg/{z}/{x}/{y}.jpg", help="File path template within TAR")
@click.option('--scenetemplate', '-s', default="{z}-{x}-{y}-tile.tif", help="Template for output scenetif filenames")
@click.option('--workers', '-w', default=4)
def streamdir(input_dir, output_dir, compositezoom, maxzoom, logdir, readtemplate, scenetemplate, workers):
    tile_stitch.stream_dir(input_dir, output_dir, compositezoom, maxzoom, logdir, readtemplate, scenetemplate, workers)

cli.add_command(streamdir)

@click.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--zoom', '-z', default=None, type=int,
    help='Zoom to inspect [default = all]')
def inspectdir(input_dir, zoom):
    tile_stitch.inspect_dir(input_dir, zoom)

cli.add_command(inspectdir)

if __name__ == "__main__":
    cli()
