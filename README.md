This is a tool for keeping your source folders up to date, tracking what hasn't been pushed, and replicating the whole tree on a new machine.

## Install

1. Clone this somewhere (`~/src/sourcerer`)
1. Install: `pip3 install -e .`
1. Tag a folder for control: `cd ~/src; touch .sourcerer.yaml`

# Usage

1. Go to the folder with `.sourcerer.yaml`
1. Show the current status: `srcr status`
1. Find out more about the status command: `srcr --help status`
1. Add a git repo to the config: `srcr add utils`
1. Fetch all repos: `srcr clone`
1. Get any missing repos: `srcr clone`
1. Find out about more commands: `srcr --help`

## To Do
* Update more commands to handle non-base-dir: add, ignore
* Need a way to fast forward
  * When we run `srcr fetch` it pulls new remote commits, then master is behind and it looks like unpushed. Need a way to handle this better
