# -*- coding: utf-8 -*-

import os
import os.path
import yaml


def compareConfigToFilesystem():
    config = None
    try:
        with open(".sourcerer.yaml", "r") as configFile:
            config = yaml.load(configFile)
    except FileNotFoundError:
        pass

    if config is None:
        for root, dirs, files in os.walk("."):
            return dict(managed=dict(), unmanaged=list(dirs), missing=dict())

    managed = {}
    unmanaged = []
    missing = _flattenConfig(config)

    for root, dirs, files in os.walk("."):
        currentFolder = root[2:]
        for ignored in [".git"]:
            if ignored in dirs:
                dirs.remove(ignored)

        isUnmanagedDir = True
        for missingPath, missingConfig in missing.items():

            # We've found a config for this folder
            if missingPath == currentFolder:
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


def _flattenConfig(config):
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
            else:
                raise Exception("Unhandled config type: {}: {}<{}>".format(fullpath, value, type(value)))

    recurse(None, config)

    # Require an 'origin' remote
    for key, value in results.items():
        if "origin" not in value:
            raise ValueError("{} has no origin: {}".format(key, value))

    return results


def addToConfig(path, remotes):
    config = None
    try:
        with open(".sourcerer.yaml", "r") as configFile:
            config = yaml.load(configFile)
    except FileNotFoundError:
        pass
    if config is None:
        config = dict()

    pathParts = path.split(os.sep)
    configNode = config
    for part in pathParts[:-1]:
        if part not in configNode:
            configNode[part] = dict()
        configNode = configNode[part]

    if len(remotes) == 1 and "origin" in remotes:
        configNode[pathParts[-1]] = remotes["origin"]
    else:
        configNode[pathParts[-1]] = list()
        for key, value in remotes.items():
            configNode[pathParts[-1]].append([key, value])

    with open(".sourcerer.yaml", "w") as configFile:
        configFile.write(yaml.dump(config))
