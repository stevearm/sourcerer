# -*- coding: utf-8 -*-
import argparse
import sys

import colorama

import sourcerer.config
import sourcerer.git

def main():
    parser = argparse.ArgumentParser(description="Manage source folders")
    parser.add_argument("--verbose", action="store_true", help="More logs")
    tasks = parser.add_subparsers(title="Commands")

    task = tasks.add_parser("status")
    task.set_defaults(func=status)

    task = tasks.add_parser("clone")
    task.set_defaults(func=clone)

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
            stats = sourcerer.git.gatherStats(path)
            clean = " " if stats["clean"] else "*"
            masterPushed = " " if stats["masterPushed"] else "↑"
            color = colorama.Style.DIM if stats["clean"] and stats["masterPushed"] else ""
            print(color +
                  "  {clean}{masterPushed} {path}".format(clean=clean, masterPushed=masterPushed, path=path) +
                  colorama.Style.RESET_ALL)
        print()

    if len(status["missing"]):
        print("Missing folder ({})".format(len(status["missing"])))
        print()
        for path, pathConfig in status["missing"].items():
            print(colorama.Fore.RED + "     {}".format(path) + colorama.Style.RESET_ALL)
        print()

    if len(status["unmanaged"]):
        print("Unmanaged ({})".format(len(status["unmanaged"])))
        print()
        for path in status["unmanaged"]:
            print(colorama.Style.DIM + "     {}".format(path) + colorama.Style.RESET_ALL)
        print()

    return True

def clone(args):
    raise Exception("Should clone all missing folders")

def fetch(args):
    status = sourcerer.config.compareConfigToFilesystem()
    if len(status["managed"]):
        for path, pathConfig in status["managed"].items():
            sourcerer.git.fetch(path, map(lambda x: x[0], pathConfig))
