#!/bin/python3

import argparse
from pkg import *
import pkg
import sys

if __name__ != "__main__":
	print("This file is not meant to be imported!")
	sys.exit(1)

parser = argparse.ArgumentParser(description='dalixOS package manager')
parser.add_argument(
	'-r',
	'--root',
	help='Root directory of the system',
	default='/home/derek/Code/dalixOS/Tests/testroot'
)
parser.add_argument(
	'-i',
	'--install',
	help='Install a .deb package',
)
parser.add_argument(
	'-t',
	'--test',
	help='Run a random test script',
	action='store_true'
)
args = parser.parse_args()

pkg.root = args.root

if args.install:
	install_deb(args.install)
elif args.test:
	a = occurence_count(["test", "test", "test", "usr", "usr", "usr/bin", "usr/share", "usr/share"])
	for b in a:
		print(f"{b}: {a[b]}")