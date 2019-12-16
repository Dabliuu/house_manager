#!/usr/bin/env bash

python setup.py sdist # this one generate a tar file so the module can be portable
python setup.py develop # this one generate the manifest file to link dependencies