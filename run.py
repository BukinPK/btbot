#!/usr/bin/env python3

import argparse
from btbot import *


parser = argparse.ArgumentParser(description='')
parser.add_argument('-n', '--no-report', action='store_false', dest='report',  help='without report')
parser.add_argument('-c', '--config', dest='path', help='path to the config file')
args = parser.parse_args()

if args.path:
    api = Api(args.path)
else:
    api = Api.fromconfig()
b = []
for a in api:
    b.append(BountyBase(a))
    b[-1].api.login()
    b[-1].make()
    b[-1].check()
    b[-1].start()
    if args.report:
        b[-1].report()
