#!/usr/bin/env python

import sys

import bunny


try:
    package_name = sys.argv[1]
except IndexError:
    package_name = "python"

try:
    version = sys.argv[2]
except IndexError:
    version = "2.8"

u = bunny.UpstreamReleaseMonitoring()
u.new_release(package_name, version)
