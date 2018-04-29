# -*- coding: utf-8 -*-
import argparse
import sys

import colorama

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
        colorama.init()
        if not args.func(args):
            sys.exit(1)
    else:
        parser.print_usage()
        sys.exit(1)

def status(args):
    status = sourcerer.config.compareConfigToFilesystem()
    if len(status["managed"]):
        print("Managed folders ({})".format(len(status["managed"])))
        print()
        for path, pathConfig in status["managed"].items():
            print(colorama.Style.DIM + "  {} ({})".format(path, pathConfig) + colorama.Style.RESET_ALL)
        print()

    if len(status["missing"]):
        print("Missing folder ({})".format(len(status["missing"])))
        print()
        for path, pathConfig in status["missing"].items():
            print(colorama.Fore.RED + "  {} ({})".format(path, pathConfig) + colorama.Style.RESET_ALL)
        print()

    if len(status["unmanaged"]):
        print("Unmanaged ({})".format(len(status["unmanaged"])))
        print()
        for path in status["unmanaged"]:
            print(colorama.Style.DIM + "  {}".format(path) + colorama.Style.RESET_ALL)
        print()

    return True

def fetch(args):
    raise Exception("Not yet implemented")
