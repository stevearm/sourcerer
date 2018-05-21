# -*- coding: utf-8 -*-

import os

import git

def gatherStats(path):
    repo = git.Repo(path)
    remotes = dict(map(lambda x: (x.name, next(x.urls)), repo.remotes))

    unpushed = list()
    localBranches = dict([(x.name, x) for x in repo.branches])
    for branchName, branch in localBranches.items():
        tracking = branch.tracking_branch()
        if tracking is None:
            # `branch` has no upstream
            unpushed.append(branchName)
        elif tracking.remote_name == ".":
            # `branch` has another local branch set as upstream
            localBranchName = tracking.remote_head
            if localBranchName not in localBranches or branch.object != localBranches[localBranchName].object:
                unpushed.append(branchName)
        else:
            # `branch` has a remote branch set as upstream
            if branch.object != tracking.object:
                unpushed.append(branchName)
    return dict(clean=(not repo.is_dirty()), unpushed=unpushed, remotes=remotes)


def fetch(path, remoteNames, purge, tags):
    repo = git.Git(path)
    for remoteName in remoteNames:
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
