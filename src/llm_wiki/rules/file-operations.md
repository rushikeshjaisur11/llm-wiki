---
description: Rules for file copy, move, and git file operations
---

# File & Git Move/Copy Operations

## File System Operations

- **Never use the Write tool to copy or move files.** Always use shell commands via the Bash tool.
- Use `cp <src> <dst>` to copy files.
- Use `mv <src> <dst>` to move or rename files.
- On Windows, `robocopy` or `xcopy` are also acceptable alternatives.
- Reading a file's content and writing it to a new path is **forbidden** for copy/move operations.

## Git File Operations

- Use `git mv <src> <dst>` to move or rename tracked files — never use `mv` followed by `git add/rm`.
- Use `git cp` patterns where applicable (copy via `cp` then `git add` the new file if a true copy is needed).
- Preserve git history by always preferring `git mv` over deleting and recreating files.
