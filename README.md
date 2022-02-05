# Git Interface
[![Documentation Status](https://readthedocs.org/projects/python-git-interface/badge/?version=latest)](https://python-git-interface.readthedocs.io/en/latest/?badge=latest)
![PyPI](https://img.shields.io/pypi/v/git-interface)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/git-interface)
![PyPI - Downloads](https://img.shields.io/pypi/dm/git-interface)
![GitHub](https://img.shields.io/github/license/enchant97/python-git-interface)
![GitHub issues](https://img.shields.io/github/issues/enchant97/python-git-interface)
![Lines of code](https://img.shields.io/tokei/lines/github/enchant97/python-git-interface)
![GitHub last commit](https://img.shields.io/github/last-commit/enchant97/python-git-interface)

Use the git cli from Python.

> This project currently is not heavily tested and not fully feature complete

## Requirements
- Git (version 2.30)

## Example Of Use

```python
import asyncio
from git_interface.branch import get_branches

head, other_branches = asyncio.run(get_branches("my_git_repo.git"))

print("HEAD = ", head)
print("OTHER", other_branches)
```
