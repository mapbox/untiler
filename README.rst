tile-stitcher
=============

Utility to take a directory of {z}/{x}/{y}.(jpg\|png) tiles, and stitch
into a scenetiff. Future versions will support fast indexed reading
directly from ``tar`` archives.

Dev installation
----------------

::

    git clone git@github.com:mapbox/tile-stitcher.git

    cd tile-stitcher

    pip install -e .

Usage
-----

::

    tile-stitch streamdir <dir of tiles> <output dir> -z <max zoom> -c <composite zoom> -w <workers>
