import tarfile
import re
from io import BytesIO

from rasterio.io import MemoryFile

def _parse_path(p):
    '''
    Given a pathlike-string,
    parse out `z/x/y` as `[z, x, y]`
    '''
    found = re.findall(r'([0-9]+)\/([0-9]+)\/([0-9]+)\.', p)
    if found:
        tile = [int(i) for i in found[0]]

        return tile

def _get_template(info, checks=100):
    '''
    Given an info object with internal tar
    paths as strings, check N paths to find formatting
    and output result.
    '''
    match = None

    patt = re.compile(r'([a-zA-Z0-9\-\_\/]+\/)[0-9]+\/[0-9]+\/[0-9]+(\.jpg|png)')

    for i, k in enumerate(info.keys()):
        if patt.match(k):
            tpattern = patt.sub(r'\1%s/%s/%s\2', k)
            if match is not None and tpattern != match:
                raise ValueError('Inconsistent paths')

            match = tpattern
            if i >= checks:
                break

    return match


class TarStream:
    '''
    Class to stream image ndarrays from tars.
    - TarStream(<tar>).index() creates index for tar
    - TarStream..read(<[keys]|key>) returns image data for keys
    '''
    def __init__(self, tarpath):
        self.tarpath = tarpath
        self.offsets = None

    def index(self):
        '''
        Index tar and return offsets as dict
        mapped to internal paths
        '''
        self.offsets = {}
        with tarfile.open(self.tarpath, 'r|') as db:
            for i, item in enumerate(db):
                self.offsets[item.name] = [item.offset_data, item.size]
                # clear members for memory
                if i % 1024 == 0:
                    db.members = []

            return self.offsets

    def _read_yield(self, seekers):
        '''
        Util to handle reading
        '''
        with open(self.tarpath, 'rb') as tar:
            for a, b in seekers:
                tar.seek(a)
                with BytesIO(tar.read(b)) as data:
                    with MemoryFile(data) as memfile:
                        with memfile.open() as src:
                            yield src.read()


    def read(self, keys):
        '''
        Given a single (str) or list of (str) keys,
        return each key as a (d, r, c) ndarray
        '''
        if self.offsets == None:
            raise ValueError('TarStream must first be indexed via <object>.index()')

        return_single = False

        if not isinstance(keys, list):
            keys = [keys]
            return_single = True

        # Sort on seek keys for read cursor
        seekers = (
            (a, b) for a, b in sorted(
                [self.offsets[key] for key in keys],
                key=lambda pair: pair[0])
            )

        if return_single:
            return list(self._read_yield(seekers))[0]
        else:
            return list(self._read_yield(seekers))
