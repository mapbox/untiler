# tile-stitcher

[![Build Status](https://magnum.travis-ci.com/mapbox/tile-stitcher.svg?token=Dkq56qQtBntqTfE3yeVy&branch=master)](https://magnum.travis-ci.com/mapbox/tile-stitcher) [![Coverage Status](https://coveralls.io/repos/mapbox/tile-stitcher/badge.svg?branch=master&service=github&t=nhModO)](https://coveralls.io/github/mapbox/tile-stitcher?branch=master)

Utility to take a directory of {z}/{x}/{y}.(jpg|png) tiles, and stitch into a scenetiff. Future versions will support fast indexed reading directly from `tar` archives.

## Dev installation
```
git clone git@github.com:mapbox/tile-stitcher.git

cd tile-stitcher

pip install -e .
```

## Usage
```
tile-stitch streamdir <dir of tiles> <output dir> -z <max zoom> -c <composite zoom> -w <workers>
```
