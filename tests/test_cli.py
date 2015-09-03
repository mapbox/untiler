from click.testing import CliRunner

from untiler.scripts.cli import cli
import os, shutil, mercantile, pytest
import numpy as np
import rasterio as rio

from pprint import pprint


class TestTiler:
    def __init__(self, path):
        self.path = path
        self.cleanup()
        os.mkdir(self.path)

    def cleanup(self):
        try:
            shutil.rmtree(self.path)
        except:
            pass

    def add_tiles(self, zMin, zMax):
        zooms = np.arange(zMax - zMin + 2) + zMin - 1

        obj = {
            zMin - 1: [mercantile.tile(-122.4, 37.5, zMin - 1)]
        }

        basepath = '%s/jpg' % (self.path)
        if not os.path.isdir(basepath):
            os.mkdir(basepath)

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

def test_cli_streamdir_all_ok():
    testtiles = TestTiler('/tmp/test-untiler')
    testtiles.add_tiles(15, 19)
    runner = CliRunner()

    result = runner.invoke(cli, ['streamdir', '/tmp/test-untiler', '/tmp/test-untiler', '-c', '14'])
    
    assert result.output.rstrip() == '/tmp/test-untiler/14-2621-6348-tile.tif'    

    with rio.open(result.output.rstrip()) as src:
        assert src.shape == (8192, 8192)
        assert src.count == 4

    testtiles.cleanup()

def test_cli_streamdir_mixed_ok():
    testtiles = TestTiler('/tmp/test-untiler')
    testtiles.add_tiles(15, 16)
    testtiles.add_tiles(17, 19)
    runner = CliRunner()

    result = runner.invoke(cli, ['streamdir', '/tmp/test-untiler', '/tmp/test-untiler', '-c', '14'])
    
    assert result.output.rstrip() == '/tmp/test-untiler/14-2621-6348-tile.tif'    

    with rio.open(result.output.rstrip()) as src:
        assert src.shape == (8192, 8192)
        assert src.count == 4

    testtiles.cleanup()

def test_cli_streamdir_mixed_ok():
    testtiles = TestTiler('/tmp/test-untiler')
    testtiles.add_tiles(15, 16)
    runner = CliRunner()

    result = runner.invoke(cli, ['streamdir', '/tmp/test-untiler', '/tmp/test-untiler', '-c', '14', '-t', 'poo/{z}/{z}/{z}.jpg'])

    assert result.exit_code == -1

    testtiles.cleanup()

def test_cli_baddir_fails():
    rdir = '/tmp' + ''.join(np.random.randint(0,9,10).astype(str))
    runner = CliRunner()

    result = runner.invoke(cli, ['streamdir', rdir, rdir, '-c', '14'])

    assert result.exit_code == 2

def test_cli_badoutput_fails():
    pdir = '/tmp/' + ''.join(np.random.randint(0,9,10).astype(str))
    rdir = '/tmp/' + ''.join(np.random.randint(0,9,10).astype(str))
    os.mkdir(pdir)
    runner = CliRunner()

    result = runner.invoke(cli, ['streamdir', pdir, rdir, '-c', '14'])

    assert result.exit_code == 2

    shutil.rmtree(pdir)

def test_diff_zooms():
    testtiles = TestTiler('/tmp/test-untiler')
    testtiles.add_tiles(15, 16)
    testtiles.add_tiles(17, 18)
    runner = CliRunner()

    result = runner.invoke(cli, ['streamdir', '/tmp/test-untiler', '/tmp/test-untiler', '-c', '15'])

    expected_scenes = '/tmp/test-untiler/15-5242-12696-tile.tif\n/tmp/test-untiler/15-5243-12696-tile.tif\n/tmp/test-untiler/15-5243-12697-tile.tif\n/tmp/test-untiler/15-5242-12697-tile.tif\n'

    with rio.open('/tmp/test-untiler/15-5242-12697-tile.tif') as src:
        assert src.shape == (2048, 2048)
        assert src.count == 4

    with rio.open('/tmp/test-untiler/15-5242-12696-tile.tif') as src:
        assert src.shape == (512, 512)
        assert src.count == 4

    testtiles.cleanup()


