# untiler

[![Build Status](https://magnum.travis-ci.com/mapbox/untiler.svg?token=Dkq56qQtBntqTfE3yeVy&branch=master)](https://magnum.travis-ci.com/mapbox/untiler) [![Coverage Status](https://coveralls.io/repos/mapbox/untiler/badge.svg?branch=master&service=github&t=nhModO)](https://coveralls.io/github/mapbox/untiler?branch=master)

Utility to take a directory of {z}/{x}/{y}.(jpg|png) tiles, and stitch into a scenetiff. Future versions will support fast indexed reading directly from `tar` archives.

## Dev installation
```
git clone git@github.com:mapbox/untiler.git

cd untiler

pip install -e .
```

## Usage
```
untiler streamdir <dir of tiles> <output dir> -z <max zoom> -c <composite zoom> -w <workers>
```
