import shutil, tempfile, os

import click

from mbutil import mbtiles_to_disk

import contextlib
import sys
import cStringIO

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = cStringIO.StringIO()
    yield
    sys.stdout = save_stdout

class MBTileExtractor:
    def __init__(self, path, subdir='tiles', scheme='xyz'):
        self.path = path
        self.tmpdir = tempfile.mkdtemp()
        self.subdir = subdir
        self.scheme = scheme
    def extract(self):
        with nostdout():
            mbtiles_to_disk(self.path, os.path.join(self.tmpdir, self.subdir), **{'scheme': self.scheme})
        return self.tmpdir
    def __enter__(self):
        return self
    def __exit__(self, ext_t, ext_v, trace):
        shutil.rmtree(self.tmpdir)
        if ext_t:
            click.echo("in __exit__")
