#!/usr/bin/env bash
echo "package test"
VERSION=`cat ../pc-navtex-py/version.py | grep version | awk '{print $3}' | tr -d '"'`
python3 ../dist/pc-navtex-py-$VERSION-py3-none-any.whl/pc-navtex-py &
exit
