#!/usr/bin/env bash
echo "package test"
VERSION=`cat ../pc_navtex_py/version.py | grep version | awk '{print $3}' | tr -d '"'`
python3 ../dist/pc_navtex_py-$VERSION-py3-none-any.whl/pc_navtex_py &
exit
