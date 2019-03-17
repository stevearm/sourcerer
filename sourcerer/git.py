# -*- coding: utf-8 -*-

import logging
import os

import git

def gatherStats(path):
    logging.debug("gatherStats({})".format(path))
    repo = git.Repo(path)
    remotes = dict(map(lambda x: (x.name, next(x.urls)), repo.remotes))

    unpushed = list()
    localBranches = dict([(x.name, x) for x in repo.branches])
    for branchName, branch in localBranches.items():
        tracking = branch.tracking_branch()
        if tracking is None:
            # `branch` has no upstream
            logging.debug("{}'s has no upstream".format(branchName))
            unpushed.append(branchName)
        elif tracking.remote_name == ".":
            # `branch` has another local branch set as upstream
            localBranchName = tracking.remote_head
            if localBranchName not in localBranches:
                # The local upstream branch is missing, so treat as if there's no upstream
                logging.debug("{}'s upstream is local {} which is missing".format(branchName, localBranchName))
                unpushed.append(branchName)
            elif branch.object != localBranches[localBranchName].object:
                # We've now got two real branches that aren't the same. Check if branch is ahead or behind of upstream
                if not contains(localBranches[localBranchName].object, branch.object):
                    logging.debug("{} is ahead of it's local upstream {}".format(branchName, localBranchName))
                    unpushed.append(branchName)
        else:
            # `branch` has a remote branch, but the remote might not exist
            try:
                tracking.object # Dereference the remote branch to see it exists
            except ValueError as e:
                # `branch` is linked to upstream, but upstream is now missing
                # Treat as though it was never pushed
                logging.debug("{} has a remote upstream which is missing".format(branchName))
                unpushed.append(branchName)
                continue
            # `branch` has a remote branch set as upstream
            if branch.object != tracking.object:
                # We've now got two real branches that aren't the same. Check if branch is ahead or behind of upstream
                if not contains(tracking.object, branch.object):
                    logging.debug("{} is ahead of it's remote upstream {}".format(branchName, tracking))
                    unpushed.append(branchName)
    return dict(clean=(not repo.is_dirty()), unpushed=unpushed, remotes=remotes)


def fetch(path, remoteNames, purge, tags):
    repo = git.Git(path)
    remotes = repo.remote().split("\n") # Is this really the best way to get a list of remote names?
    for remoteName in remoteNames:
        if remoteName not in remotes:
            raise ValueError("'{}' not a remote for {}({})".format(remoteName, path, remotes))

        # This uses the command-line interface
        # https://github.com/gitpython-developers/GitPython/blob/05e3b0e58487c8515846d80b9fffe63bdcce62e8/git/cmd.py#L970
        response = repo.fetch(remoteName, p=purge, t=tags)
        if response != "":
            raise Exception("{} fetch {}: {}".format(path, remoteName, response))


""" Clones from origin to the given path and add any extra remotes
"""
def clone(path, remotes):
    if os.path.isdir(path):
        raise Exception("Cannot clone into existing location")
    repo = git.Repo.clone_from(remotes["origin"], path)
    ensureRemotes(path, remotes)


""" Ensures the repo at the given path has all specified remotes
"""
def ensureRemotes(path, remotes):
    repo = git.Repo(path)
    for remoteName, remoteUrl in remotes.items():
        try:
            remote = repo.remote(remoteName)
            if remoteUrl != next(remote.urls):
                raise Exception("{} already has {} pointing to {}".format(path, remoteName, remoteUrl))
        except ValueError:
            git.Remote.add(repo, remoteName, remoteUrl)


""" Is needle somewhere in haystack's history
"""
def contains(haystack, needle):
    needleSha = needle.hexsha
    activePaths = [haystack]
    seen = set()

    while len(activePaths) > 0:
        current = activePaths.pop(0)
        currentSha = current.hexsha
        if currentSha == needleSha:
            return True
        if currentSha in seen:
            continue
        seen.add(currentSha)
        for parent in current.parents:
            activePaths.append(parent)
    logging.debug("Never found {} in {}".format(needle, haystack))

    return False
