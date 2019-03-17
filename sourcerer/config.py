# -*- coding: utf-8 -*-

import os
import os.path
import yaml

__yamlFileName = ".sourcerer.yaml"

def findBaseDir(wd=""):
    while True:
        if os.path.isfile(os.path.join(wd, __yamlFileName)):
            return wd
        if os.path.abspath(wd) == "/":
            return None
        if wd is "":
            wd = ".."
        else:
            wd = os.path.join(wd, "..")


def isBaseDir():
    return os.path.isfile(__yamlFileName)


def initBaseDir():
    with open(__yamlFileName, "w") as configFile:
        configFile.write(yaml.dump(dict(), default_flow_style=False))


def compareConfigToFilesystem(baseDir):
    with open(os.path.join(baseDir, __yamlFileName), "r") as configFile:
        config = yaml.safe_load(configFile)

    managed = {}
    unmanaged = []
    missing = _flattenConfig(config, baseDir)

    for root, dirs, files in os.walk("." if baseDir is "" else baseDir):
        if baseDir is "":
            currentFolder = root[2:]
        else:
            currentFolder = root
        for ignored in [".git"]:
            if ignored in dirs:
                dirs.remove(ignored)

        isUnmanagedDir = True
        for missingPath, missingConfig in missing.items():

            # We've found a config for this folder
            if missingPath == currentFolder:
                if missingConfig is False:
                    # This is an ignored path so drop it
                    pass
                else:
                    # Move the config from missing to managed
                    managed[missingPath] = missingConfig
                del missing[missingPath]

                # Stop walking this folder
                del dirs[:]
                isUnmanagedDir = False
                break

            if missingPath.startswith(currentFolder):
                # Found a config that is below this folder, so keep walking
                isUnmanagedDir = False
                break

        # Found no configs below this folder, so tag as unmanaged and stop walk
        if isUnmanagedDir:
            del dirs[:]
            unmanaged.append(currentFolder)

    return dict(managed=managed, unmanaged=unmanaged, missing=missing)


def _flattenConfig(config, baseDir):
    if config is None:
        config = dict()

    results = dict()

    def recurse(prefix, node):
        for key, value in node.items():
            fullpath = os.path.join(prefix, key) if prefix else key
            if isinstance(value, dict):
                recurse(fullpath, value)
            elif isinstance(value, list):
                results[fullpath] = dict()
                for remoteConfig in value:
                    if not isinstance(remoteConfig, list) or len(remoteConfig) != 2:
                        raise Exception("Incorrect remote config: {} - {}".format(key, remoteConfig))
                    if remoteConfig[0] in results[fullpath]:
                        raise Exception("Duplicate remote config: {} - {}".format(key, remoteConfig[0]))
                    results[fullpath][remoteConfig[0]] = remoteConfig[1]
            elif isinstance(value, str):
                results[fullpath] = dict(origin=value)
            elif isinstance(value, bool):
                results[fullpath] = value
            else:
                raise Exception("Unhandled config type: {}: {}<{}>".format(fullpath, value, type(value)))

    recurse(None if baseDir is "" else baseDir, config)

    return results


def addToConfig(path, remotes):
    if len(remotes) == 0:
        raise ValueError("Repos with no remotes not allowed")
    if len(remotes) == 1 and "origin" in remotes:
        node = remotes["origin"]
    else:
        node = list()
        for key, value in remotes.items():
            node.append([key, value])
    _addNodeToConfig(path, node)


def ignoreInConfig(path):
    _addNodeToConfig(path, False)


def _addNodeToConfig(path, node):
    with open(__yamlFileName, "r") as configFile:
        config = yaml.safe_load(configFile)

    pathParts = path.split(os.sep)
    configNode = config
    for part in pathParts[:-1]:
        if part not in configNode:
            configNode[part] = dict()
        configNode = configNode[part]

    configNode[pathParts[-1]] = node

    with open(__yamlFileName, "w") as configFile:
        configFile.write(yaml.dump(config, default_flow_style=False))
