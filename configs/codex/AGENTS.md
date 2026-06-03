# Personal defaults

## Local environment

- For general local Python work, default to the Conda environment `dzt`.
- In non-interactive shell commands, prefer `conda run -n dzt <command>` over `conda activate dzt && <command>`.
- If a repository documents a different environment, follow the repository-specific instruction instead of `dzt`.

## Working preferences

- Prefer concise Chinese explanations unless the project or user request calls for English.
- Use `rg` for text search when available.
- Ask before installing or removing packages, changing Conda environments, pushing remote Git changes, deleting files, killing processes, or using `sudo`.
- Never print or summarize API tokens, authentication files, `.env` files, or shell startup secrets.
