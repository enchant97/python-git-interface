import subprocess
from pathlib import Path
from typing import List, Tuple

from .exceptions import GitException, NoBranchesException


def get_branches(git_repo: Path) -> Tuple[str, List[str]]:
    head = ""
    other_branches = []

    args = ["git", "-C", str(git_repo), "branch", "--no-color"]

    process_status = subprocess.run(args, capture_output=True)
    if not process_status.stdout:
        stderr = process_status.stderr.decode()
        if process_status.returncode != 0:
            raise GitException(stderr)
        if not stderr:
            raise NoBranchesException(f"no branches found for '{git_repo.name}'")

    split = process_status.stdout.decode().strip().split("\n")

    for line in split:
        if line[0] == "*":
            head = line[2:]
        else:
            other_branches.append(line[2:])

    return head, other_branches
