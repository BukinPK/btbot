#!/usr/bin/env python3

import argparse
import sys
import signal
from btbot import *


def exit(sig, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, exit)

if len(sys.argv) < 2:
    print('starts with arguments: --report --social')
    sys.argv.append('-rs')

parser = argparse.ArgumentParser(description='without args start with -rs')

parser.add_argument('-r', '--report', action='store_true',  help='make report')
parser.add_argument('-s', '--social', action='store_true',  help='start social posting')
parser.add_argument('-c', '--config', dest='path', help='path to the config file')
parser.add_argument('-m', '--show-messages', action='store_true', dest='show_msgs',
                    help='show report messages')
parser.add_argument('-d', '--debug', action='store_true',  help='debug for args')

args = parser.parse_args()

if args.path:
    api = Api(args.path)
else:
    api = Api.fromconfig()
b = []
if args.debug:
    print(args)
for a in api:
    b.append(BountyBase(a))
    b[-1].api.login()
    b[-1].make()
    b[-1].check()
    if args.show_msgs:
        print(b[-1])
        for bounty in b[-1]:
            print(bounty.get_data())
        print('-------------------\n')
    if args.social:
        b[-1].start()
    if args.report:
        b[-1].report()
