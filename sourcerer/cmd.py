# -*- coding: utf-8 -*-
import argparse
import os
import functools
import logging
import sys

import colorama

import sourcerer.config
import sourcerer.diffutils
import sourcerer.git


FLAGS=dict(dirty="*", unpushed="↑", unmanagedRemote="⇞")

def main():
    parser = argparse.ArgumentParser(description="Manage source folders")
    parser.add_argument("--verbose", action="store_true", help="More logs")
    tasks = parser.add_subparsers(title="Commands")

    task = tasks.add_parser("status", help="Show the status of all folders",
                            description="Flags: {}".format(", ".join(["{}: {}".format(key, value) for key, value in sorted(FLAGS.items())])))
    task.add_argument("path", nargs="?", help="The path to show details for")
    task.add_argument("--show-all", action="store_true", help="Show all folders")
    task.set_defaults(func=status)

    task = tasks.add_parser("clone", help="Clone any missing repos and add any missing remotes")
    task.add_argument("path", nargs="?", help="Limit task to just one path")
    task.set_defaults(func=clone)

    task = tasks.add_parser("fetch", help="Fetch all remotes in config")
    task.add_argument("--purge", "-p", action="store_true", help="Purge when doing the fetch")
    task.add_argument("--no-tags", action="store_true", help="Skip fetching tags")
    task.set_defaults(func=fetch)

    task = tasks.add_parser("init", help="Initialize the current folder as a sourcerer root")
    task.set_defaults(func=init)

    task = tasks.add_parser("add", help="Add an unmanaged (or partially managed) repo to the config")
    task.add_argument("path", help="The path to add")
    task.set_defaults(func=add)

    task = tasks.add_parser("ignore", help="Ignore an unmanaged path")
    task.add_argument("path", help="The path to ignore")
    task.set_defaults(func=ignore)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("git.cmd").setLevel(logging.INFO)

    if "func" in args:
        colorama.init()
        if not args.func(args):
            sys.exit(1)
    else:
        parser.print_usage()
        sys.exit(1)


def status(args):
    if args.path:
        return singleDirStatus(args)

    baseDir = sourcerer.config.findBaseDir()
    if baseDir is None:
        print("Could not find config")
        return False
    status = sourcerer.config.compareConfigToFilesystem(baseDir)
    if len(status["managed"]):
        print("Managed folders ({})".format(len(status["managed"])))
        print()
        for path, pathConfig in status["managed"].items():
            stats = sourcerer.git.gatherStats(path)

            remotesMatch = pathConfig == stats["remotes"]

            flags = [[stats["clean"],              FLAGS["dirty"]],
                     [len(stats["unpushed"]) == 0, FLAGS["unpushed"]],
                     [remotesMatch,                FLAGS["unmanagedRemote"]]]
            flagString = "".join(map(lambda x: " " if x[0] else x[1], flags))

            if not args.show_all and flagString.strip() == "":
                continue

            # Dim unless one of the flags is false
            color = colorama.Style.DIM if functools.reduce(lambda x, y: x and y[0], flags, True) else ""

            print(color +
                  "  {flags} {path}".format(flags=flagString, path=path) +
                  colorama.Style.RESET_ALL)
        print()

    # Drop missing folders where the config says they're ignored
    missingFolders = [x for x in status["missing"] if status["missing"][x] is not False]
    if len(missingFolders):
        print("Missing folder ({})".format(len(missingFolders)))
        print()
        for path in missingFolders:
            print(colorama.Fore.RED + "     {}".format(path) + colorama.Style.RESET_ALL)
        print()

    if len(status["unmanaged"]):
        print("Unmanaged ({})".format(len(status["unmanaged"])))
        print()
        for path in status["unmanaged"]:
            print(colorama.Style.DIM + "     {}".format(path) + colorama.Style.RESET_ALL)
        print()

    return True


def singleDirStatus(args):
    baseDir = sourcerer.config.findBaseDir()
    if baseDir is None:
        print("Could not find config")
        return False
    status = sourcerer.config.compareConfigToFilesystem(baseDir)
    path = args.path.rstrip("/")

    if path in status["managed"]:
        pathConfig = status["managed"][path]
        stats = sourcerer.git.gatherStats(path)

        if pathConfig != stats["remotes"]:
            print("Remotes are unmanaged or urls don't match config")
            for name, urls in sourcerer.diffutils.dictDiff(pathConfig, stats["remotes"]).items():
                if urls[0] != urls[1]:
                    print(" {}  {}".format(FLAGS["unmanagedRemote"], name))
            print()

        if len(stats["unpushed"]):
            print("Branches with no upstream or that are ahead of upstream")
            for branch in stats["unpushed"]:
                print(" {}  {}".format(FLAGS["unpushed"], branch))
            print()

        return True


    if path in status["missing"]:
        print("This folder is missing: `srcr clone`")
        return True

    if path in status["unmanaged"]:
        print("Unmanaged folder")
        return True

    print("Couldn't understand that folder")
    return False


def clone(args):
    baseDir = sourcerer.config.findBaseDir()
    if baseDir is None:
        print("Could not find config")
        return False
    status = sourcerer.config.compareConfigToFilesystem(baseDir)
    for path, pathConfig in status["missing"].items():
        if pathConfig is False:
            continue
        if args.path and args.path != path:
            continue
        sourcerer.git.clone(path, pathConfig)
    for path, pathConfig in status["managed"].items():
        if args.path and args.path != path:
            continue
        sourcerer.git.ensureRemotes(path, pathConfig)


def fetch(args):
    baseDir = sourcerer.config.findBaseDir()
    if baseDir is None:
        print("Could not find config")
        return False
    status = sourcerer.config.compareConfigToFilesystem(baseDir)
    if len(status["managed"]):
        for path, pathConfig in status["managed"].items():
            print("{} ({})".format(path, ", ".join(pathConfig.keys())))
            try:
                sourcerer.git.fetch(path, pathConfig.keys(), args.purge, not args.no_tags)
            except ValueError as e:
                print("Fetch failed: {}".format(e))


def init(args):
    if sourcerer.config.findBaseDir() is not None:
        print("Already inside a root")
        return False
    sourcerer.config.initBaseDir()


def add(args):
    if args.path.startswith(os.sep):
        print("Must pass in relative path")
        return False
    if not sourcerer.config.isBaseDir():
        print("Only supported when at base dir")
        return False
    path = args.path.rstrip(os.sep)
    repo = sourcerer.git.gatherStats(path)
    sourcerer.config.addToConfig(path, repo["remotes"])


def ignore(args):
    if args.path.startswith(os.sep):
        print("Must pass in relative path")
        return False
    if not sourcerer.config.isBaseDir():
        print("Only supported when at base dir")
        return False
    path = args.path.rstrip(os.sep)
    sourcerer.config.ignoreInConfig(path)
