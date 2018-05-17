# -*- coding: utf-8 -*-
import argparse
import os
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
    task.add_argument("--purge", action="store_true", help="Purge when doing the fetch")
    task.add_argument("--no-tags", action="store_true", help="Skip fetching tags")
    task.set_defaults(func=fetch)

    task = tasks.add_parser("add", help="Add an unmanaged (or partially managed) repo to the config")
    task.add_argument("path", help="The path to add")
    task.set_defaults(func=add)

    task = tasks.add_parser("ignore", help="Ignore an unmanaged path")
    task.add_argument("path", help="The path to ignore")
    task.set_defaults(func=ignore)

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
    status = sourcerer.config.compareConfigToFilesystem()
    for path, pathConfig in status["missing"].items():
        sourcerer.git.clone(path, pathConfig)
    for path, pathConfig in status["managed"].items():
        sourcerer.git.ensureRemotes(path, pathConfig)


def fetch(args):
    status = sourcerer.config.compareConfigToFilesystem()
    if len(status["managed"]):
        for path, pathConfig in status["managed"].items():
            print("{} ({})".format(path, ", ".join(pathConfig.keys())))
            sourcerer.git.fetch(path, pathConfig.keys(), args.purge, not args.no_tags)


def add(args):
    if args.path.startswith(os.sep):
        print("Must pass in relative path")
        return False
    path = args.path.rstrip(os.sep)
    repo = sourcerer.git.gatherStats(path)
    sourcerer.config.addToConfig(path, repo["remotes"])


def ignore(args):
    if args.path.startswith(os.sep):
        print("Must pass in relative path")
        return False
    path = args.path.rstrip(os.sep)
    sourcerer.config.ignoreInConfig(path)
