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

Usage
-----

::

    Usage: untiler [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      inspectdir
      streamdir
      streammbtiles

``streamdir``
~~~~~~~~~~~~~

Given a directory of tiles + a read template, mosaic into tifs at a
lower parent "composite" zoom extent

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
    -x, --no-fill                Don't fill in with lower zooms
    --help                       Show this message and exit.

``streammbtiles``
~~~~~~~~~~~~~~~~~

Mosaic an mbtiles into tifs of "composite" zoom extent

::

    untiler streammbtiles [OPTIONS] MBTILES OUTPUT_DIR

    Options:
      --co NAME=VALUE              Driver specific creation options.See the
                                   documentation for the selected output driver
                                   for more information.
      -c, --compositezoom INTEGER  Tile size to mosaic into [default=13]
      -z, --maxzoom INTEGER        Force a maxzom [default=max in each
                                   compositezoom area]
      -s, --scenetemplate TEXT     Template for output scenetif filenames
                                   [default='{z}-{x}-{y}-tile.tif']
      -w, --workers INTEGER        Number of workers in the processing pool
                                   [default=4]
      -x, --no-fill                Don't fill in with lower zooms
      --help                       Show this message and exit.

``inspectdir``
~~~~~~~~~~~~~~

Stream ``[x, y, z]``\ s of a directory

::

    untiler inspectdir [OPTIONS] INPUT_DIR

    Options:
    -z, --zoom INTEGER  Zoom to inspect [default = all]
    --help              Show this message and exit.

Outputs a line-delimited stream of tile ``[x, y, z]``\ s; useful to pipe
into ``mercantile shapes`` to visualize geometry:

::

    untiler inspectdir <dir> -z 19 | mercantile shapes | fio collect | geojsonio

.. |Build Status| image:: https://travis-ci.org/mapbox/untiler.svg?branch=master
   :target: https://travis-ci.org/mapbox/untiler
.. |Coverage Status| image:: https://coveralls.io/repos/mapbox/untiler/badge.svg?branch=master&service=github&t=nhModO
   :target: https://coveralls.io/github/mapbox/untiler?branch=master
