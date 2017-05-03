from __future__ import division
import numpy as np
import re
from collections import OrderedDict
import os

class TileUtils:
    def search_dir(self, directory):
        for dp, dn, fn in os.walk(os.path.expanduser(directory)):
            for f in fn:
                yield os.path.join(dp, f)

    def get_tiles(self, filenames, template, separator):
        """
        Given a list of tar pathnames + templates, parse Z X Ys
        """
        validtile = re.compile(template)
        for f in filenames:
            if validtile.match(f):
                matchstring = r"\d+%s\d+%s\d+" % (separator, separator)
                yield [
                    int(i) for i in re.compile(matchstring).findall(f)[-1].split(separator)
                ]

    def select_tiles(self, tiles, zoom):
        """
        Get the list of tiles for a zoom and their min / max Xs / Ys
        """
        tileCount, depth = tiles.shape

        if tileCount <= 0 or depth != 3:
            raise ValueError("Tile array must have shape of n > 0, 3 (recieved %s, %s)" % (tileCount, depth))

        tiles = tiles[np.where(tiles[:, 0] == zoom)]

        tileCount, depth = tiles.shape

        if tileCount <= 0 or depth != 3:
            raise ValueError("Tile array must have shape of n > 0, 3 (recieved %s, %s)" % (tileCount, depth))

        return tiles, tiles[:, 1].min(), tiles[:, 2].min(), tiles[:, 1].max(), tiles[:, 2].max()

    def get_super_tiles(self, subTiles, zoom):
        """
        Given an array of [z, x, y] tiles, find all their parent tiles at a particular zoom
        """
        if np.any(subTiles[:, 0] < zoom):
            raise ValueError("Cannot get super tiles of tile array w/ smaller zoom")
        zoomdiffs = 2 ** (subTiles[:, 0] - zoom)
        superTiles = subTiles // np.vstack(zoomdiffs)
        superTiles[:,0] = zoom

        return superTiles

    def get_unique_tiles(self, data):
        """
        Given an array of [z, x, y] tiles, find all the unique tiles
        """
        ncols = data.shape[1]
        dtype = data.dtype.descr * ncols
        struct = data.view(dtype)

        uniq = np.unique(struct)
        uniq = uniq.view(data.dtype).reshape(-1, ncols)
        return uniq


    def get_zoom_tiles(self, subTiles, superTiles, tile, tilefloor=16):
        """
        Given:
        (1) an array of [z, x, y] sub tiles at multiple zooms;
        (2) as array of [z, x, y] super tiles at one zoom, one for each record in the subtile array;
        (3) a single [z, x, y] from the above super tile array,
        find the maximum zoom level of tiles within that tile, and
        the maximum zoom level of complete coverage for that tile.
        If the same, returns <array of zMax tiles>, False
        If different, returns <array of zMax tiles>, <array of zMaxCov tiles>
        """

        if subTiles.shape != superTiles.shape:
            raise ValueError("Input sub and super tiles must have the same shape")

        subTiles = subTiles[np.all(superTiles == tile, axis=1)]
        subTileMin, subTileMax = subTiles[:, 0].min(), subTiles[:, 0].max()



        if subTileMax < tilefloor:
            raise ValueError("No tiles found below that floor")

        for zMaxCov in range(subTileMax, max([subTileMin - 1, tilefloor - 1]), -1):
            if 4 ** (zMaxCov - tile[0]) == np.where(subTiles[:, 0] == zMaxCov)[0].shape[0]:
                break


        if subTileMax != zMaxCov:
            return subTiles[np.where(subTiles[:, 0] == subTileMax)], subTiles[np.where(subTiles[:, 0] == zMaxCov)]
        else:
            return subTiles[np.where(subTiles[:, 0] == subTileMax)], False

    def get_sub_tiles(self, subTiles, superTiles):
        for t in self.get_unique_tiles(superTiles):
            z, x, y = t
            zMaxTiles, maxCovTiles = self.get_zoom_tiles(subTiles, superTiles, t)
            
            if not np.any(maxCovTiles):
                zMaxCov = False
            else:
                zMaxCov = maxCovTiles[0][0]

            yield OrderedDict({
                'zMaxTiles': zMaxTiles,
                'maxCovTiles': maxCovTiles,
                'zMax': zMaxTiles[0][0],
                'zMaxCov': zMaxCov,
                'x': x,
                'y': y,
                'z': z
            })

    def filter_tiles(self, tiles, zoomfloor):
        return tiles[np.where(tiles[:, 0] <= zoomfloor)]

    def get_fill_super_tiles(self, superTiles, fillTiles, fillThresh):
        for ct in ((np.all(superTiles == a, axis=1).sum(), a) for a in fillTiles):
            if ct[0] != fillThresh or ct[0] == 0:
                yield ct[1]

    def get_sub_base_zoom(self, px, py, pz, z):
        if z < pz:
            raise ValueError("cannot get base zoom of %s, is less than %s" % (z, pz))
        mult = 2 ** (z - pz)
        return (px * mult, py * mult)


def parse_template(template):
    """
    Parse and verify a pathname template
    """
    pattern = re.compile(r".*{z}.*{x}.*{y}.*(png|jpg|tif)")
    match = pattern.match(template)
    if pattern.match(template):    
        valPattern = re.compile(r"{(z|x|y)}")
        filepath = re.compile(r"(jpg|png|tif)$")
        sepmatch = re.compile(r"(?:{z})(/|-)(?:{x})(/|-)(?:{y})")
        separator = sepmatch.findall(template)[0]

        if len(separator) != 2 or separator[0] != separator[1]:
            raise ValueError('Too many / not matching separators!')
    
        return valPattern.sub('\d+', template), valPattern.sub('%s', template), separator[0]
    else:
        raise ValueError('Invalid template "%s"' % (template))


if __name__ == "__main__":
    TileUtils()
    parse_template()
