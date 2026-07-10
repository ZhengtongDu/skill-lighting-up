---
name: vault-sync
description: |
  Synchronize an Obsidian Vault between Git remotes using an explicit repository
  path. Use when the user asks to sync, back up, pull, or push their vault; do
  not use for unrelated repositories.
---

# Vault Sync

Use Git to align a configured Obsidian Vault across machines. The Vault path is
resolved from the user's explicit request, then `VAULT_PATH`; if neither is
available, ask before reading or changing any repository.

## Preconditions

- Confirm the target is an Obsidian Vault and a Git repository.
- Inspect `git status -sb`, the current branch, and configured remotes before
  staging anything.
- Never infer a remote URL, account name, home directory, or sync schedule.
- Pushing, committing unrelated changes, and resolving a rebase conflict all
  require the user's explicit authorization.

## Standard Flow

1. Resolve the Vault path and run `git status -sb`.
2. If the working tree has changes, show their scope. Stage only the files the
   user has approved, then commit with a concise message.
3. Fetch and pull with `git pull --rebase --autostash` only after the user has
   asked to synchronize with the remote.
4. If a conflict occurs, stop at the conflict, explain the affected files, and
   ask for a resolution choice. Do not guess or discard notes.
5. Push only after the user has asked for it or has explicitly requested a
   full sync.

## Optional Automation

Automation may call a local wrapper, but that wrapper is machine-specific and
is not part of this repository. Configure its Vault path, remote, schedule, and
log location locally. A model should inspect the wrapper before relying on it.

## Safety Notes

- Do not use cloud-sync migration commands unless the user asks.
- Do not expose `.obsidian` secrets, Git credentials, or private remote URLs in
  reports or commits.
- For a normal code repository, use its own Git workflow instead of this skill.
