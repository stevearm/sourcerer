# -*- coding: utf-8 -*-
import argparse
import functools
import sys

import colorama

import sourcerer.config
import sourcerer.git


def main():
    parser = argparse.ArgumentParser(description="Manage source folders")
    parser.add_argument("--verbose", action="store_true", help="More logs")
    tasks = parser.add_subparsers(title="Commands")

    task = tasks.add_parser("status", help="Show the status of all folders")
    task.set_defaults(func=status)

    task = tasks.add_parser("clone", help="Clone any missing repos and add any missing remotes")
    task.set_defaults(func=clone)

    task = tasks.add_parser("fetch", help="Fetch all remotes in config")
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

            branchesMatch = pathConfig == stats["remotes"]

            flags = [[stats["clean"], "*"],
                     [stats["masterPushed"], "↑"],
                     [branchesMatch, "☇"]]
            flagString = "".join(map(lambda x: " " if x[0] else x[1], flags))

            # Dim unless one of the flags is false
            color = colorama.Style.DIM if functools.reduce(lambda x, y: x and y[0], flags, True) else ""

            print(color +
                  "  {flags} {path}".format(flags=flagString, path=path) +
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
            print("{} ({})".format(path, ", ".join(pathConfig.keys())))
            sourcerer.git.fetch(path, pathConfig.keys())
