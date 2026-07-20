#!/usr/bin/env bash

rm -rf ../build/*
rm -rf ../pc-navtex-py/__pycache__
CWD=`pwd`

echo "- PyPI ---"
python -m build --wheel
cd $CWD

echo "for testing only, package is build by GitHub actions and publish in PyPi automatically"

# EOF
