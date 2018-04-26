# -*- coding: utf-8 -*-
import argparse
import sys

import sourcerer.config

def main():
    parser = argparse.ArgumentParser(description="Manage source folders")
    parser.add_argument("--verbose", action="store_true", help="More logs")
    tasks = parser.add_subparsers(title="Commands")

    task = tasks.add_parser("status")
    task.set_defaults(func=status)

    task = tasks.add_parser("fetch")
    task.set_defaults(func=fetch)

    args = parser.parse_args()
    if "func" in args:
        if not args.func(args):
            sys.exit(1)
    else:
        parser.print_usage()
        sys.exit(1)

def status(args):
    status = sourcerer.config.compareConfigToFilesystem()
    print("Managed: {}".format(len(status["managed"])))
    for path, pathConfig in status["managed"].items():
        print("  {} ({})".format(path, pathConfig))

    print("Missing: {}".format(len(status["missing"])))
    for path, pathConfig in status["missing"].items():
        print("  {} ({})".format(path, pathConfig))

    print("Unmanaged: {}".format(len(status["unmanaged"])))
    for path in status["unmanaged"]:
        print("  {}".format(path))
    return True

def fetch(args):
    raise Exception("Not yet implemented")
