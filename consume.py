#!/usr/bin/env python

import sys

import bunny


if "consume_and_ack" in sys.argv[0]:
    ack = True
else:
    ack = False


u = bunny.UpstreamReleaseMonitoring()

try:
    for m in u.fetch_releases(ack=ack):
        print m
except KeyboardInterrupt:
    pass
