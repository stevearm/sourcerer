This is a tool for keeping your source folders up to date, tracking what hasn't been pushed, and replicating the whole tree on a new machine.

## Install

1. Clone this somewhere (`~/src/sourcerer`)
1. Install: `pip3 install -e .`
1. Tag a folder for control: `cd ~/src; touch .sourcerer.yaml`

## Getting started

1. Go to the root of all your git repos: `cd ~/src`
1. Initialize that folder as sourcerer managed: `srcr init`
  * This creates `.sourcerer.yaml` in the current folder
1. Show the current status: `srcr status`
  * See the status icon legend: `srcr --help status`
1. Add any repos you care about: `srcr add java/utils`
1. Ignore any folders you don't want managed: `srcr ignore scratchpad`

## Regular use

## srcr status
This will show any repos that have uncommitted changes (with \*) and any commits that have not been pushed to a remote (with ↑). This includes:

* A branch with no upstream branch set
* A branch where the upstream branch is missing
* A branch where it has commits ahead of it's upstream

## srcr clone
This will ensure you've got every working copy you should, and that they all have the right remotes. If you specify a directory, it will only do so for that directory.

## srcr fetch
This will fetch on all managed existing remote on all existing repos. Specify `--purge` if you want to remove local branches that were deleted on the remote.

## srcr cleanup
This removes code from your machine that are persisted elsewhere. For all managed folders, it deletes local branches that are already pushed and switches to `master`. If run with `--remove`, it will remove any working copies that just have `master` and it is synced with remote.

## To Do
* Update more commands to handle non-base-dir: add, ignore
