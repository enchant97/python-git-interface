import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from .constants import EMPTY_REPO_RE, UNKNOWN_REV_RE
from .datatypes import Log
from .exceptions import (GitException, NoCommitsException, NoLogsException,
                         UnknownRevisionException)


def __process_log(stdout_line: str):
    parts = stdout_line.split(";;")
    if len(parts) != 4:
        raise ValueError("invalid log line: {stdout_line}")
    return Log(
        parts[0],
        parts[1],
        datetime.fromisoformat(parts[2]),
        parts[3]
    )


def __process_logs(stdout: str):
    log_lines = stdout.strip().split("\n")
    return map(__process_log, log_lines)


def get_logs(
        git_repo: Path,
        branch: Optional[str] = None,
        max_number: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None):

    args = ["git", "-C", str(git_repo), "log"]

    if branch is not None:
        args.append(str(branch))
    if max_number is not None:
        args.append(f"--max-count={max_number}")
    if since is not None:
        args.append(f"--since={since.isoformat()}")
    if until is not None:
        args.append(f"--until={until.isoformat()}")
    args.append("--pretty=%H;;%ae;;%cI;;%s")

    process_status = subprocess.run(
        args,
        capture_output=True)
    if not process_status.stdout:
        stderr = process_status.stderr.decode()
        if re.match(EMPTY_REPO_RE, stderr):
            raise NoCommitsException()
        if re.match(UNKNOWN_REV_RE, stderr):
            raise UnknownRevisionException(f"unknown revision/branch {branch}")
        if process_status.returncode != 0:
            raise GitException(stderr)
        raise NoLogsException(f"no logs found (using given filters) for '{git_repo.name}'")
    stdout = process_status.stdout.decode()
    return __process_logs(stdout)
