import subprocess
from pathlib import Path
from typing import Optional

from .exceptions import AlreadyExistsException


def init_repo(
        repo_dir: Path,
        repo_name: str,
        bare: bool = True,
        default_branch: Optional[str] = None):
    if bare:
        repo_name = repo_name + ".git"
    repo_path = repo_dir / repo_name

    if (repo_path.exists()):
        raise AlreadyExistsException(f"path already exists for '{repo_name}'")

    args = ["git", "init", str(repo_path), "--quiet"]
    if bare:
        args.append("--bare")
    if default_branch:
        args.append(f"--initial-branch={default_branch}")
    subprocess.run(args).check_returncode()
