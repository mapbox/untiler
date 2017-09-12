#!/usr/bin/env python

import os, re

import click, mercantile, json
from rasterio.rio.options import creation_options

import untiler
import numpy as np

from untiler import tarstream
import untiler.scripts.tile_utils as tile_utils
from untiler.scripts.mbtiles_extract import MBTileExtractor

@click.group()
def cli():
    pass

@click.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=True))
@creation_options
@click.option('--compositezoom', '-c', default=13, type=int,
    help='Tile size to mosaic into [default=13]')
@click.option('--maxzoom', '-z', default=None, type=int,
    help='Force a maxzom [default=max in each compositezoom area]')
@click.option('--logdir', '-l', default=None, help="Location for log files [default=None]")
@click.option('--readtemplate', '-t', default="jpg/{z}/{x}/{y}.jpg", help="File path template [default='jpg/{z}/{x}/{y}.jpg']")
@click.option('--scenetemplate', '-s', default="{z}-{x}-{y}-tile.tif", help="Template for output scenetif filenames [default='{z}-{x}-{y}-tile.tif']")
@click.option('--workers', '-w', default=4, help="Number of workers in the processing pool [default=4]")
@click.option('--no-fill', '-x', is_flag=True, help="Don't fill in with lower zooms")
def streamdir(input_dir, output_dir, compositezoom, maxzoom, logdir, readtemplate, scenetemplate, workers, creation_options, no_fill):
    # with MBTileExtractor(input_dir) as mbtmp:
    #     print mbtmp.extract()
    untiler.stream_dir(input_dir, output_dir, compositezoom, maxzoom, logdir, readtemplate, scenetemplate, workers, creation_options, no_fill)

cli.add_command(streamdir)

@click.command()
@click.argument('mbtiles', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=True))
@creation_options
@click.option('--compositezoom', '-c', default=13, type=int,
    help='Tile size to mosaic into [default=13]')
@click.option('--maxzoom', '-z', default=None, type=int,
    help='Force a maxzom [default=max in each compositezoom area]')
@click.option('--scenetemplate', '-s', default="{z}-{x}-{y}-tile.tif", help="Template for output scenetif filenames [default='{z}-{x}-{y}-tile.tif']")
@click.option('--workers', '-w', default=4, help="Number of workers in the processing pool [default=4]")
@click.option('--no-fill', '-x', is_flag=True, help="Don't fill in with lower zooms")
def streammbtiles(mbtiles, output_dir, compositezoom, maxzoom, creation_options, scenetemplate, workers, no_fill):
    with MBTileExtractor(mbtiles) as mbtmp:
        input_tile_dir = mbtmp.extract()
        with open(os.path.join(input_tile_dir, 'tiles', 'metadata.json')) as ofile:
            metadata = json.loads(ofile.read())
        readtemplate = "tiles/{z}/{x}/{y}.%s" % (metadata['format'])
        untiler.stream_dir(input_tile_dir, output_dir, compositezoom, maxzoom, None, readtemplate, scenetemplate, workers, creation_options, no_fill)

cli.add_command(streammbtiles)

@click.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--zoom', '-z', default=None, type=int,
    help='Zoom to inspect [default = all]')
@click.option('--readtemplate', '-t', default="jpg/{z}/{x}/{y}.jpg",
    help="File path template [default='jpg/{z}/{x}/{y}.jpg']")
def inspectdir(input_dir, zoom, readtemplate):
    untiler.inspect_dir(input_dir, zoom, readtemplate)

cli.add_command(inspectdir)


@click.command()
@click.argument('tar', type=click.Path(exists=True))
@click.option('--compositezoom', default=None, type=int,
    help='Print out parent tiles at the composite level')
def inspectar(tar, compositezoom):
    tiler = tile_utils.TileUtils()
    index = tarstream._index(tar)

    tiles = (tarstream._parse_path(p) for p in index.keys())

    tiles = np.array([t for t in tiles if t is not None])

    if compositezoom is not None:
        compositezoom = compositezoom
        tiles = tiler.get_unique_tiles(tiler.get_super_tiles(tiles, compositezoom))

    for t in tiles:
        if t is not None:
            tile = t.tolist()
            tile.append(tile.pop(0))
            click.echo(json.dumps(tile))

cli.add_command(inspectar)

if __name__ == "__main__":
    cli()
