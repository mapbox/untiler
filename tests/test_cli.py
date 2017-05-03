import os
import shutil
import uuid

from click.testing import CliRunner
import mercantile
import numpy as np
import pytest
import rasterio as rio

from untiler.scripts.cli import cli


class TestTiler:
    def __init__(self):
        self.path = '/tmp/test-untiler-' + str(uuid.uuid4())
        os.mkdir(self.path)
        self.imgs = ['tests/fixtures/fill_img.jpg', 'tests/fixtures/fill_img_grey.jpg']

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self.cleanup()
        except:
            pass

    def cleanup(self):
        shutil.rmtree(self.path)

    def add_tiles(self, zMin, zMax):
        zooms = np.arange(zMax - zMin + 2) + zMin - 1

        obj = {
            zMin - 1: [mercantile.tile(-122.4, 37.5, zMin - 1)]
        }

        basepath = '%s/jpg' % (self.path)
        if not os.path.isdir(basepath):
            os.mkdir(basepath)

        for i in range(1, len(zooms)):
            tiles = []
            os.mkdir("%s/%s" % (basepath, zooms[i]))
            for t in obj[zooms[i - 1]]:
                for tt in mercantile.children(t):
                    tiles.append(tt)
                    if os.path.isdir("%s/%s/%s" % (basepath, zooms[i], tt.x)):
                        shutil.copy(self.imgs[int(np.random.rand() + 0.1)],
                                    "%s/%s/%s/%s.jpg" % (basepath, zooms[i], tt.x, tt.y))
                    else:
                        os.mkdir("%s/%s/%s" % (basepath, zooms[i], tt.x))
                        shutil.copy(self.imgs[int(np.random.rand() + 0.1)],
                                    "%s/%s/%s/%s.jpg" % (basepath, zooms[i], tt.x, tt.y))
            obj[zooms[i]] = tiles


def test_cli_streamdir_all_ok():
    with TestTiler() as testtiles:
        testtiles.add_tiles(15, 18)
        tmp = testtiles.path
        runner = CliRunner()
        result = runner.invoke(cli, ['streamdir', tmp, tmp, '-c', '14'])
        assert result.output.rstrip() == os.path.join(tmp, '14-2621-6348-tile.tif')
        with rio.open(result.output.rstrip()) as src:
            assert src.shape == (4096, 4096)  # matches z18
            assert src.count == 4


def test_cli_streamdir_mixed_ok():
    with TestTiler() as testtiles:
        testtiles.add_tiles(15, 16)
        testtiles.add_tiles(17, 18)
        tmp = testtiles.path
        runner = CliRunner()
        result = runner.invoke(cli, ['streamdir', tmp, tmp, '-c', '14'])
        assert result.output.rstrip() == os.path.join(tmp, '14-2621-6348-tile.tif')

        with rio.open(result.output.rstrip()) as src:
            assert src.shape == (4096, 4096)  # matches z18
            assert src.count == 4


def test_cli_streamdir_mixed_ok_poo():
    with TestTiler() as testtiles:
        testtiles.add_tiles(15, 16)
        tmp = testtiles.path
        runner = CliRunner()
        result = runner.invoke(cli, ['streamdir', tmp, tmp, '-c', '14', '-t', 'poo/{z}/{z}/{z}.jpg'])
        assert result.exit_code == -1


def test_cli_baddir_fails():
    rdir = '/tmp/this/does/not.exist'
    runner = CliRunner()
    result = runner.invoke(cli, ['streamdir', rdir, rdir, '-c', '14'])
    assert result.exit_code == 2


def test_cli_badoutput_fails():
    pdir = '/tmp/test-untiler-' + str(uuid.uuid4())
    rdir = '/tmp/test-untiler-' + str(uuid.uuid4())
    os.mkdir(pdir)
    runner = CliRunner()
    result = runner.invoke(cli, ['streamdir', pdir, rdir, '-c', '14'])
    assert result.exit_code == 2
    try:
        shutil.rmtree(pdir)
        shutil.rmtree(rdir)
    except:
        pass


def test_diff_zooms():
    with TestTiler() as testtiles:
        testtiles.add_tiles(15, 16)
        testtiles.add_tiles(17, 18)
        tmp = testtiles.path
        runner = CliRunner()

        runner.invoke(cli, ['streamdir', tmp, tmp, '-c', '15'])

        with rio.open(os.path.join(tmp, '15-5242-12697-tile.tif')) as src:
            assert src.shape == (2048, 2048)
            assert src.count == 4

        with rio.open(os.path.join(tmp, '15-5242-12696-tile.tif')) as src:
            assert src.shape == (512, 512)
            assert src.count == 4


def test_extract_mbtiles():
    with TestTiler() as tt:
        testpath = tt.path
        testmbtiles = os.path.join(os.path.dirname(__file__), 'fixtures/testtiles.mbtiles')
        runner = CliRunner()
        result = runner.invoke(cli, [
            'streammbtiles', testmbtiles, testpath, '-z', '16', '-x', '-s',
            '{z}-{x}-{y}-mbtiles.tif', '--co', 'compress=lzw'])
        assert result.exit_code == 0
        expected_checksums = [[13858, 8288, 51489, 31223], [17927, 52775, 411, 9217]]
        for o, c in zip(result.output.rstrip().split('\n'), expected_checksums):
            with rio.open(o) as src:
                checksums = [src.checksum(i) for i in src.indexes]
                assert checksums == c


def test_extract_mbtiles_fails():
    with TestTiler() as tt:
        testpath = tt.path
        testmbtiles = os.path.join(os.path.dirname(__file__), 'fixtures/bad.mbtiles')
        runner = CliRunner()
        result = runner.invoke(cli, [
            'streammbtiles', testmbtiles, testpath, '-z', '16', '-x', '-s',
            '{z}-{x}-{y}-mbtiles.tif', '--co', 'compress=lzw'])
        assert result.exit_code == -1
