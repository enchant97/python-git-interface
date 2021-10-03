# Git Interface
Use the git cli from Python.

> This project currently is not heavily tested and not fully feature complete

## Requirements
- Git (version 2.30)

## Example Of Use

```python
from git_interface.branch import get_branches

head, other_branches = get_branches("my_git_repo.git")

print("HEAD = ", head)
print("OTHER", other_branches)
```
