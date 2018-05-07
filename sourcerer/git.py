# -*- coding: utf-8 -*-

import os

import git

def gatherStats(path):
    repo = git.Repo(path)
    remotes = dict(map(lambda x: (x.name, next(x.urls)), repo.remotes))

    masterPushed = repo.remotes.origin.refs.master.object == repo.refs.master.object
    return dict(clean=(not repo.is_dirty()), masterPushed=masterPushed, remotes=remotes)


def fetch(path, remoteNames):
    repo = git.Repo(path)
    for remoteName in remoteNames:
        try:
            remote = repo.remote(remoteName)
            remote.fetch()
        except ValueError:
            raise Exception("{} has no remote {}".format(path, remoteName))


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
