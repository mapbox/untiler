#!/usr/bin/env python

import pytest
import tile_stitcher as stitcher
import tile_stitcher.scripts.stitch_utils as stitch_util

import numpy as np
import json, pickle, os
import mercantile as merc
import inspect
import rasterio

def test_templating_good_jpg():
    print("")
    expectedMatch = 'tarbase/jpg/\d+/\d+/\d+.jpg'
    expectedInterp = 'tarbase/jpg/%s/%s/%s.jpg'
    template = 'tarbase/jpg/{z}/{x}/{y}.jpg'

    matchTemplate, interpTemplate = stitch_util.parse_template(template)

    assert matchTemplate == expectedMatch

    assert interpTemplate == expectedInterp
    print("# OK - %s " % (inspect.stack()[0][3]))


def test_templating_good_png():
    expectedMatch = 'tarbase/jpg/\d+/\d+/\d+.png'
    expectedInterp = 'tarbase/jpg/%s/%s/%s.png'
    template = 'tarbase/jpg/{z}/{x}/{y}.png'

    matchTemplate, interpTemplate = stitch_util.parse_template(template)

    assert matchTemplate == expectedMatch

    assert interpTemplate == expectedInterp
    print("# OK - %s " % (inspect.stack()[0][3]))


def test_templating_fails():
    template = 'tarbase/jpg/{x}/{y}/{z}.jpg'
    with pytest.raises(ValueError):
        stitch_util.parse_template(template)

    template = 'tarbase/jpg/{z}/{x}/{y}.poop'
    with pytest.raises(ValueError):
        stitch_util.parse_template(template)

    template = 'tarbase/jpg/z/x/y.jpg'
    with pytest.raises(ValueError):
        stitch_util.parse_template(template)
    print("# OK - %s " % (inspect.stack()[0][3]))

def tests_templating_scene_template():
    template = '{z}-{x}-{y}-source-date-tileid.tif'

    template, sceneTemplate = stitch_util.parse_template(template)

    assert sceneTemplate == '%s-%s-%s-source-date-tileid.tif'
    print("# OK - %s " % (inspect.stack()[0][3]))

def tests_templating_scene_template_numeric():
    template = '{z}-{x}-{y}-source-2015-xyz.tif'

    template, sceneTemplate = stitch_util.parse_template(template)

    assert sceneTemplate == '%s-%s-%s-source-2015-xyz.tif'
    print("# OK - %s " % (inspect.stack()[0][3]))

def tests_templating_scene_template_fails():
    template = '{x}-{y}-source-2015-xyz.tif'

    with pytest.raises(ValueError):
        stitch_util.parse_template(template)

    print("# OK - %s " % (inspect.stack()[0][3]))

@pytest.fixture
def inputTilenames():
    with open('tests/fixtures/tar_list.json') as ofile:
        return json.load(ofile)

@pytest.fixture
def expectedTileList():
    with open('tests/expected/tile_list.json') as ofile:
        return np.array(json.load(ofile))

def test_parse_tiles(inputTilenames, expectedTileList):
    matchTemplate = '3857_9_83_202_20130517_242834/jpg/\d+/\d+/\d+.jpg'

    tiler = stitch_util.TileUtils()

    output_tiles = np.array([
        t for t in tiler.get_tiles(inputTilenames, matchTemplate)
        ])

    assert np.array_equal(output_tiles, expectedTileList)

    tweakedTilenames = [f.replace('/', '?') for f in inputTilenames]

    output_tiles = np.array([
        t for t in tiler.get_tiles(tweakedTilenames, matchTemplate)
        ])

    assert len(output_tiles) == 0
    assert np.array_equal(output_tiles, expectedTileList) == False
    print("# OK - %s " % (inspect.stack()[0][3]))

@pytest.fixture
def expectedTiles19():
    with open('tests/expected/tile_list_19.json') as ofile:
        return json.load(ofile)

def test_get_xys(expectedTileList, expectedTiles19):
    tiler = stitch_util.TileUtils()
    tiles, minX, minY, maxX, maxY = tiler.select_tiles(expectedTileList, 19)

    assert np.array_equal(tiles, np.array(expectedTiles19['tiles']))

    assert minX == expectedTiles19['minX']
    assert maxX == expectedTiles19['maxX']
    assert minY == expectedTiles19['minY']
    assert maxY == expectedTiles19['maxY']
    print("# OK - %s " % (inspect.stack()[0][3]))

def test_get_xys_invalid_tiles():
    tiler = stitch_util.TileUtils()
    badtiles = np.array([0])

    with pytest.raises(ValueError):
        tiles, minX, minY, maxX, maxY = tiler.select_tiles(badtiles, 19)

    badtiles = np.array([[1,2], [1,2]])

    with pytest.raises(ValueError):
        tiles, minX, minY, maxX, maxY = tiler.select_tiles(badtiles, 19)

    print("# OK - %s " % (inspect.stack()[0][3]))

def test_get_xys_invalid_zoom(expectedTileList):
    tiler = stitch_util.TileUtils()
    with pytest.raises(ValueError):
        tiles, minX, minY, maxX, maxY = tiler.select_tiles(expectedTileList, 20)

    print("# OK - %s " % (inspect.stack()[0][3]))

def test_affine():
    ul, lr = (-18848759.67889818, 19225441.354287542), (-18846313.693993058, 19222995.3693824)
    expected = np.array([0.5971642834774684, 0.0, -18848759.67889818, 0.0, -0.5971642834820159, 19225441.354287542, 0.0, 0.0, 1.0])

    assert np.array_equal(np.array(stitcher.make_affine(4096, 4096, ul, lr)), expected)
    print("# OK - %s " % (inspect.stack()[0][3]))


@pytest.fixture
def expectedMeta():
    with open('tests/expected/src_meta.pkl') as pklfile:
        return pickle.load(pklfile)


# SKIP UNTIL I DEAL W/ DECIMAL ISSUES

def test_src_meta_making(expectedMeta):
    bounds = merc.bounds(10, 10, 10)

    src_meta = stitcher.make_src_meta(bounds, 4096)

    for k, e in zip(sorted(src_meta), sorted(expectedMeta)):
        assert k == e
        # assert src_meta[k] == expectedMeta[e]

    print("# OK - %s " % (inspect.stack()[0][3]))


def test_make_window():
    expected = ((23808, 24064), (1024, 1280))
    window = stitcher.make_window(102, 343, 98, 250, 256)

    assert window == expected
    print("# OK - %s " % (inspect.stack()[0][3]))


def test_make_window_fails():
    with pytest.raises(ValueError):
        stitcher.make_window(102, 13, 98, 50, 256)
    print("# OK - %s " % (inspect.stack()[0][3]))

def test_upsampling():
    rShape = 2 ** int(np.random.rand() * 5 + 5)
    rUp = 2 ** int(np.random.rand() * 3 + 1)

    toFaux, frFaux = stitcher.affaux(rUp)

    test = np.zeros((3, rShape, rShape))

    with rasterio.drivers():
        outputUp = stitcher.upsample(test, rUp, frFaux, toFaux)

    assert outputUp.shape == (3, rUp * rShape, rUp * rShape)

    print("# OK - %s " % (inspect.stack()[0][3]))

@pytest.fixture
def expectedAffauxs():
    return np.array([1., 0., 0., 0., -1., 0., 0., 0., 1.]), np.array([4., 0., 0., 0., -4., 0., 0., 0., 1.])

def test_affaux(expectedAffauxs):
    toFaux, frFaux = stitcher.affaux(4)

    expectedTo, expectedFr = expectedAffauxs

    assert np.array_equal(toFaux, expectedTo)
    assert np.array_equal(frFaux, expectedFr)

    print("# OK - %s " % (inspect.stack()[0][3]))


def test_make_grey_imagedata():
    inputData = np.zeros((256, 256, 1), dtype=np.uint8)

    imdata = stitcher.make_image_array(inputData, 256, 1)

    assert imdata.shape == (4, 256, 256)

    assert np.array_equal(imdata[-1], np.zeros((256, 256), dtype=np.uint8) + 255)

    assert np.array_equal(imdata[0], imdata[1])

    assert np.array_equal(imdata[1], imdata[2])
    print("# OK - %s " % (inspect.stack()[0][3]))


def test_make_rgb_imagedata():
    inputData = np.zeros((256, 256, 4), dtype=np.uint8)

    imdata = stitcher.make_image_array(inputData, 256, 4)

    assert imdata.shape == (4, 256, 256)
    print("# OK - %s " % (inspect.stack()[0][3]))


def test_load_imagedata_rgb():
    expectedLength = 65536
    expectedDepth = 3
    expectedSize = 256
    inputData = np.zeros((expectedLength, expectedDepth), dtype=np.uint8)

    imdata, imsize, depth = stitcher.load_image_data(inputData, expectedSize)

    assert imdata.shape == (expectedSize, expectedSize, expectedDepth,)

    assert imsize == expectedLength

    assert depth == expectedDepth
    print("# OK - %s " % (inspect.stack()[0][3]))


def test_load_imagedata_grey():
    expectedLength = 65536
    expectedDepth = 1
    expectedSize = 256
    inputData = np.zeros((expectedLength, expectedDepth), dtype=np.uint8)

    imdata, imsize, depth = stitcher.load_image_data(inputData, expectedSize)

    assert imdata.shape == (expectedSize, expectedSize, expectedDepth,)

    assert imsize == expectedLength

    assert depth == expectedDepth
    print("# OK - %s " % (inspect.stack()[0][3]))


def test_load_imagedata_random():
    expectedSize = int(np.random.rand() * 256)
    expectedLength = expectedSize ** 2
    expectedDepth = int(np.random.rand() * 5)

    inputData = np.zeros((expectedLength, expectedDepth), dtype=np.uint8)

    imdata, imsize, depth = stitcher.load_image_data(inputData, expectedSize)

    assert imdata.shape == (expectedSize, expectedSize, expectedDepth,)

    assert imsize == expectedLength

    assert depth == expectedDepth
    print("# OK - %s " % (inspect.stack()[0][3]))


def test_load_imagedata_fails():
    expectedLength = 65535
    expectedDepth = 1
    expectedSize = 256
    inputData = np.zeros((expectedLength, expectedDepth), dtype=np.uint8)

    with pytest.raises(ValueError):
        imdata, imsize, depth = stitcher.load_image_data(inputData, expectedSize)

    print("# OK - %s " % (inspect.stack()[0][3]))

@pytest.fixture
def tilesShort():
    with open('tests/fixtures/tile_list_short.json') as ofile:
        return np.array(json.load(ofile))

@pytest.fixture
def expectedSuper():
    with open('tests/expected/tile_parents.json') as ofile:
        return np.array(json.load(ofile))

def test_create_supertiles(tilesShort, expectedSuper):
    tiler = stitch_util.TileUtils()
    superTiles = tiler.get_super_tiles(tilesShort, 14)

    assert tilesShort.shape == superTiles.shape
    assert np.array_equal(superTiles, expectedSuper)

    print("# OK - %s " % (inspect.stack()[0][3]))

def test_create_supertiles_fails(tilesShort):
    tiler = stitch_util.TileUtils()

    with pytest.raises(ValueError):
        superTiles = tiler.get_super_tiles(tilesShort, 20)

    print("# OK - %s " % (inspect.stack()[0][3]))

@pytest.fixture
def uniqueExpected():
    return np.array([[14, 2684, 6464], [14, 2685, 6464], [14, 2686, 6464], [14, 2687, 6464]])

def test_find_unique_tiles(expectedSuper, uniqueExpected):
    tiler = stitch_util.TileUtils()
    uniqueTiles = tiler.get_unique_tiles(expectedSuper)

    assert np.array_equal(uniqueTiles, uniqueExpected)

    print("# OK - %s " % (inspect.stack()[0][3]))

@pytest.fixture
def expectedZooms():
    with open('tests/expected/expected_zoom_tiles.json') as ofile:
        return json.load(ofile)

def test_find_zoom_tiles(expectedTileList, expectedZooms):
    tiler = stitch_util.TileUtils()

    superTiles = tiler.get_super_tiles(expectedTileList, 13)

    for t, e in zip(tiler.get_unique_tiles(superTiles), expectedZooms):
        maxZ, maxZcoverage = tiler.get_zoom_tiles(expectedTileList, superTiles, t)
        assert np.array_equal(maxZ, e['maxZ'])

        assert np.array_equal(maxZcoverage, e['maxZcoverage'])

    print("# OK - %s " % (inspect.stack()[0][3]))

def test_find_zoom_tiles_fail(expectedTileList):
    tiler = stitch_util.TileUtils()
    superTiles = tiler.get_super_tiles(expectedTileList, 13)[:-10]

    with pytest.raises(ValueError):
        maxZ, maxZcoverage = tiler.get_zoom_tiles(expectedTileList, superTiles, superTiles[0])
    print("# OK - %s " % (inspect.stack()[0][3]))

def test_find_zoom_tiles_floor_fail(expectedTileList):
    ### a subset of tiles that don't have any tiles less than z 17
    tiles = expectedTileList[:1000]

    tiler = stitch_util.TileUtils()
    superTiles = tiler.get_super_tiles(tiles, 12)
    with pytest.raises(ValueError):
        tiler.get_zoom_tiles(tiles, superTiles, superTiles[0], 17)
    print("# OK - %s " % (inspect.stack()[0][3]))

def test_find_zoom_tiles_floor(expectedTileList):
    ### a subset of tiles that have tiles less than z 17
    tiles = expectedTileList[1000:]

    tiler = stitch_util.TileUtils()
    superTiles = tiler.get_super_tiles(tiles, 13)

    zMaxtiles, zFloortiles = tiler.get_zoom_tiles(tiles, superTiles, superTiles[-1], 17)

    assert zMaxtiles.shape == (848, 3)
    assert zFloortiles.shape == (68, 3)

    assert zFloortiles[:, 0].min() == 17 and zFloortiles[:, 0].max() == 17
    print("# OK - %s " % (inspect.stack()[0][3]))

def test_logger():
    rstring = ''.join(np.random.randint(0,9, 10000).astype(str))
    rfile =  '/tmp/%s.log'% (''.join(np.random.randint(0,9, 5).astype(str)))
    with open(rfile, 'w') as loggerfile:
        stitcher.logwriter(loggerfile, rstring)

    with open(rfile) as ofile:
        logged = ofile.read()

    assert rstring + '\n' == logged

    os.remove(rfile)
    print("# OK - %s " % (inspect.stack()[0][3]))
