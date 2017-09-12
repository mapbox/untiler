import tarfile
import re

def _parse_path(p):
    found = re.findall(r'([0-9]+)\/([0-9]+)\/([0-9]+)\.', p)
    if found:
        tile = [int(i) for i in found[0]]
        # tile.append(tile.pop(0))

        return tile

def _index(tarpath):
    offsets = {}
    with tarfile.open(tarpath, 'r|') as db:
        for i, item in enumerate(db):
            offsets[item.name] = [item.offset_data, item.size]
            if i % 1024 == 0:
                db.members = []

        return offsets
