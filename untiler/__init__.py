#!/usr/bin/env python
from __future__ import with_statement
from __future__ import print_function
import os
from multiprocessing import Pool

import click
import mercantile as merc
import numpy as np
import rasterio
from rasterio import Affine
from rasterio.warp import reproject
try:
    from rasterio.warp import RESAMPLING as Resampling  # pre-1.0
except ImportError:
    from rasterio.warp import Resampling

import untiler.scripts.tile_utils as tile_utils


def make_affine(height, width, ul, lr):
    """
    Create an affine for a tile of a given size
    """
    xCell = (ul[0] - lr[0]) / width
    yCell = (ul[1] - lr[1]) / height
    return Affine(-xCell, 0.0, ul[0],
        0.0, -yCell, ul[1])


def affaux(up):
    return Affine(1, 0, 0, 0, -1, 0), Affine(up, 0, 0, 0, -up, 0)


def upsample(rgb, up, fr, to):
    up_rgb = np.empty((rgb.shape[0], rgb.shape[1] * up, rgb.shape[2] * up), dtype=rgb.dtype)

    reproject(
        rgb, up_rgb,
        src_transform=fr,
        dst_transform=to,
        src_crs="EPSG:3857",
        dst_crs="EPSG:3857",
        resampling=Resampling.bilinear)

    return up_rgb


def make_src_meta(bounds, size, creation_opts={}):
    """
    Create metadata for output tiles
    """

    ul = merc.xy(bounds.west, bounds.north)
    lr = merc.xy(bounds.east, bounds.south)

    aff = make_affine(size, size, ul, lr)

    ## default values
    src_meta = {
        'driver': 'GTiff',
        'height': size,
        'width': size,
        'count': 4,
        'dtype': np.uint8,
        'affine': aff,
        "crs": 'EPSG:3857',
        'compress': 'JPEG',
        'tiled': True,
        'blockxsize': 256,
        'blockysize': 256
    }

    for c in creation_opts.keys():
        src_meta[c] = creation_opts[c]

    return src_meta


def make_window(x, y, xmin, ymin, windowsize):
    """
    Create a window for writing a child tile to a parent output tif
    """
    if x < xmin or y < ymin:
        raise ValueError("Indices can't be smaller than origin")
    row = (y - ymin) * windowsize
    col = (x - xmin) * windowsize

    return (
            (row, row + windowsize),
            (col, col + windowsize)
        )


globalArgs = None


def make_image_array(imdata, outputSize):
    try:
        depth, width, height = imdata.shape

        if depth == 4:
            alpha = imdata[3]
        else:
            alpha = np.zeros((outputSize, outputSize), dtype=np.uint8) + 255

        return np.array([
            imdata[0 % depth, :, :],
            imdata[1 % depth, :, :],
            imdata[2 % depth, :, :],
            alpha
        ])
    except Exception as e:
        raise e


def load_image_data(imdata, outputSize):
    imsize, depth = imdata.shape

    if int(np.sqrt(imsize)) != outputSize:
        raise ValueError("Output size of %s ** 2 does not equal %s" % (outputSize, imsize))

    return imdata.reshape(outputSize, outputSize, depth).astype(np.uint8), imsize, depth


def global_setup(inputDir, args):
    global globalArgs
    globalArgs = args


def logwriter(openLogFile, writeObj):
    if openLogFile:
        print(writeObj, file=openLogFile)
        return


def streaming_tile_worker(data):
    size = 2 ** (data['zMax'] - globalArgs['compositezoom']) * globalArgs['tileResolution']
    out_meta = make_src_meta(merc.bounds(data['x'], data['y'], data['z']), size, globalArgs['creation_opts'])
    filename = globalArgs['sceneTemplate'] % (data['z'], data['x'], data['y'])
    subtiler = tile_utils.TileUtils()
    log = 'FILE: %s\n' % filename
    try:
        with rasterio.open(filename, 'w', **out_meta) as dst:
            if data['zMaxCov']:
                superTiles = subtiler.get_super_tiles(data['zMaxTiles'], data['zMaxCov'])

                fillbaseX, fillbaseY = subtiler.get_sub_base_zoom(data['x'], data['y'], data['z'], data['zMaxCov'])

                ## fill thresh == the number of sub tiles that would need to occur in a fill tile to not fill (eg completely covered)
                fThresh = 4 ** (data['zMax'] - data['zMaxCov'])

                fDiff = 2 ** (data['zMax'] - data['zMaxCov'])

                toFaux, frFaux = affaux(fDiff)

                if not globalArgs['no_fill']:
                    print('filling')
                    ## Read and write the fill tiles first
                    for t in subtiler.get_fill_super_tiles(superTiles, data['maxCovTiles'], fThresh):
                        z, x, y = t
                        path = globalArgs['readTemplate'] % (z, x, y)
                        log += '%s %s %s\n' % (z, x, y)

                        with rasterio.open(path) as src:
                            imdata = src.read()

                        imdata = make_image_array(imdata, globalArgs['tileResolution'])

                        imdata = upsample(imdata, fDiff, frFaux, toFaux)

                        window = make_window(x, y, fillbaseX, fillbaseY, globalArgs['tileResolution'] * fDiff)
                        dst.write(imdata, window=window)


            baseX, baseY = subtiler.get_sub_base_zoom(data['x'], data['y'], data['z'], data['zMax'])

            for t in data['zMaxTiles']:
                z, x, y = t
                path = globalArgs['readTemplate'] % (z, x, y)
                log += '%s %s %s\n' % (z, x, y)

                with rasterio.open(path) as src:
                    imdata = src.read()

                imdata = make_image_array(imdata, globalArgs['tileResolution'])

                window = make_window(x, y, baseX, baseY, globalArgs['tileResolution'])

                dst.write(imdata, window=window)
        if globalArgs['logdir']:
            with open(os.path.join(globalArgs['logdir'], '%s.log' % os.path.basename(filename)), 'w') as logger:
                logwriter(logger, log)

        return filename

    except Exception as e:
        click.echo("%s errored" % (path), err=True)
        raise e


def inspect_dir(inputDir, zoom, read_template):
    tiler = tile_utils.TileUtils()

    allFiles = tiler.search_dir(inputDir)

    template, readTemplate, separator = tile_utils.parse_template("%s/%s" % (inputDir, read_template))

    allTiles = np.array([i for i in tiler.get_tiles(allFiles, template, separator)])

    allTiles, _, _, _, _ = tiler.select_tiles(allTiles, zoom)

    for t in allTiles:
        z, x, y = t
        click.echo([x, y, z])


def stream_dir(inputDir, outputDir, compositezoom, maxzoom, logdir, read_template, scene_template, workers, creation_opts, no_fill):
    tiler = tile_utils.TileUtils()

    allFiles = tiler.search_dir(inputDir)

    template, readTemplate, separator = tile_utils.parse_template("%s/%s" % (inputDir, read_template))

    allTiles = np.array([i for i in tiler.get_tiles(allFiles, template, separator)])

    if allTiles.shape[0] == 0 or allTiles.shape[1] != 3:
        raise ValueError("No tiles were found for that template")

    if maxzoom:
        allTiles = tiler.filter_tiles(allTiles, maxzoom)

    if allTiles.shape[0] == 0:
        raise ValueError("No tiles were found below that maxzoom")

    _, sceneTemplate, _ = tile_utils.parse_template("%s/%s" % (outputDir, scene_template))

    pool = Pool(workers, global_setup, (inputDir, {
        'maxzoom': maxzoom,
        'readTemplate': readTemplate,
        'outputDir': outputDir,
        'tileResolution': 256,
        'compositezoom': compositezoom,
        'fileTemplate': '%s/%s_%s_%s_%s.tif',
        'sceneTemplate': sceneTemplate,
        'logdir': logdir,
        'creation_opts': creation_opts,
        'no_fill': no_fill
        }))

    superTiles = tiler.get_super_tiles(allTiles, compositezoom)

    for p in pool.imap_unordered(streaming_tile_worker, tiler.get_sub_tiles(allTiles, superTiles)):
        click.echo(p)

    pool.close()
    pool.join()


if __name__ == "__main__":
    stream_dir()
    inspect_dir()
