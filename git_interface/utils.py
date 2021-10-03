import subprocess
from pathlib import Path
from typing import Optional

from .datatypes import ArchiveTypes
from .exceptions import AlreadyExistsException, GitException


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
    process = subprocess.run(args)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


def get_description(git_repo: Path) -> str:
    with open(git_repo / "description", "r") as fo:
        return fo.read()


def set_description(git_repo: Path, description: str):
    with open(git_repo / "description", "w") as fo:
        fo.write(description)


def run_maintenance(git_repo: Path):
    args = ["git", "-C", str(git_repo), "maintenance", "run"]
    process = subprocess.run(args, capture_output=True)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())


def get_archive(git_repo: Path, archive_type: ArchiveTypes, tree_ish: str = "HEAD") -> bytes:
    # this allows for strings to be passed
    if isinstance(archive_type, ArchiveTypes):
        archive_type = archive_type.value
    process = subprocess.run(
        ["git", "-C", str(git_repo), "archive", f"--format={archive_type}", tree_ish],
        capture_output=True)
    if process.returncode != 0:
        raise GitException(process.stderr.decode())
    return process.stdout
