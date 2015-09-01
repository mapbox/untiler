from click.testing import CliRunner

from tile_stitcher.scripts.cli import cli
import os, shutil, mercantile
import numpy as np
import rasterio as rio

def setup_sample_1():
    zooms = np.arange(6) + 14

    obj = {
        zooms[0]: [mercantile.tile(-122.4, 37.5, 14)]
    }

    try:
        shutil.rmtree('/tmp/test-tile-stitcher')
    except:
        pass

    basepath = '/tmp/test-tile-stitcher/jpg'

    os.mkdir('/tmp/test-tile-stitcher')

    os.mkdir('/tmp/test-tile-stitcher/jpg')

    for i in xrange(1, len(zooms)):
        tiles = []
        os.mkdir("%s/%s" % (basepath, zooms[i])) 
        for t in obj[zooms[i - 1]]:
            for tt in mercantile.children(t):
                tiles.append(tt)
                if os.path.isdir("%s/%s/%s" % (basepath, zooms[i], tt.x)):
                    shutil.copy('tests/fixtures/fill_img.jpg',
                                "%s/%s/%s/%s.jpg" % (basepath, zooms[i], tt.x, tt.y))
                else:
                    os.mkdir("%s/%s/%s" % (basepath, zooms[i], tt.x))
                    shutil.copy('tests/fixtures/fill_img.jpg',
                                "%s/%s/%s/%s.jpg" % (basepath, zooms[i], tt.x, tt.y))
        obj[zooms[i]] = tiles

def test_cli_exit2():
    setup_sample_1()
    runner = CliRunner()

    result = runner.invoke(cli, ['streamdir', '/tmp/test-tile-stitcher', '/tmp/test-tile-stitcher', '-c', '14'])
    
    assert result.output.rstrip() == '/tmp/test-tile-stitcher/14-2621-6348-tile.tif'    

    with rio.open(result.output.rstrip()) as src:
        assert src.shape == (8192, 8192)
        assert src.count == 4

