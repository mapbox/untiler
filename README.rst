tile-stitcher
=============

|Build Status|\ |Coverage Status|

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

.. |Build Status| image:: https://magnum.travis-ci.com/mapbox/tile-stitcher.svg?token=Dkq56qQtBntqTfE3yeVy&branch=master
   :target: https://magnum.travis-ci.com/mapbox/tile-stitcher
.. |Coverage Status| image:: https://coveralls.io/repos/mapbox/tile-stitcher/badge.svg?branch=master&service=github&t=nhModO
   :target: https://coveralls.io/github/mapbox/tile-stitcher?branch=master
