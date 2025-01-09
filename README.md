# git-switch
A simple tool to manage and quickly swap between multiple SSH keys / personas when working with multiple repositories.

# Installation
To install, simply run `make` which will install to `~/.local/bin`. Alternatively, copy the single script somewhere in your `PATH`.

# Usage
See `git-switch --help`. You can:
- `git-switch add` to add a new persona
- `git-switch list` to list existing personas
- `git-switch become` to switch to an existing persona
- `git-switch remove` to remove a persona

# How does it work?
It's super simple. The script reads name, email, and key path from the config for the given persona, then uses `git config ...` to change the user, email, and sshCommand so that the given SSH private key is used during SSH.