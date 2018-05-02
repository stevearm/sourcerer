# -*- coding: utf-8 -*-

import git

def gatherStats(path):
    repo = git.Repo(path)
    remotes = dict(map(lambda x: (x.name, next(x.urls)), repo.remotes))

    masterPushed = repo.remotes.origin.refs.master.object == repo.refs.master.object
    return dict(clean=(not repo.is_dirty()), masterPushed=masterPushed, remotes=remotes)


def fetch(path, remotes):
    repo = git.Repo(path)
    for remoteName in remotes:
        repo.remote(remoteName).fetch()
