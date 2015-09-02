untiler
=======

|Build Status| |Coverage Status|

Utility to take a directory of ``{z}/{x}/{y}.(jpg|png)`` tiles, and
stitch into a scenetiff (``tif`` w/ exact merc tile bounds). Future
versions will support fast indexed reading directly from ``tar``
archives.

Install
-------

make a virtual env + activate, then:

::

    pip install untiler

Dev installation
----------------

::

    git clone git@github.com:mapbox/untiler.git

    cd untiler

    pip install -e .

Usage - streamdir
-----------------

::

    untiler streamdir [OPTIONS] INPUT_DIR OUTPUT_DIR

    -c, --compositezoom INTEGER  Tile size to mosaic into [default=13]
    -z, --maxzoom INTEGER        Force a maxzom [default=max in each
                               compositezoom area]
    -l, --logdir TEXT            Location for log files [default=None]
    -t, --readtemplate TEXT      File path template
                               [default='jpg/{z}/{x}/{y}.jpg']
    -s, --scenetemplate TEXT     Template for output scenetif filenames
                               [default='{z}-{x}-{y}-tile.tif']
    -w, --workers INTEGER        Number of workers in the processing pool
                               [default=4]
    --help                       Show this message and exit.

Usage - inspectdir
------------------

::

    untiler inspectdir [OPTIONS] INPUT_DIR

    Options:
    -z, --zoom INTEGER  Zoom to inspect [default = all]
    --help              Show this message and exit.

Outputs a line-delimited stream of tile ``[x, y, z]``\ s; useful to pipe
into ``mercantile shapes`` to visualize geometry:

::

    untiler inspectdir <dir> -z 19 | mercantile shapes | fio collect | geojsonio

.. |Build Status| image:: https://magnum.travis-ci.com/mapbox/untiler.svg?token=Dkq56qQtBntqTfE3yeVy&branch=master
   :target: https://magnum.travis-ci.com/mapbox/untiler
.. |Coverage Status| image:: https://coveralls.io/repos/mapbox/untiler/badge.svg?branch=master&service=github&t=nhModO
   :target: https://coveralls.io/github/mapbox/untiler?branch=master
