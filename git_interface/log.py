"""
Methods for using the 'log' command
"""
import re
from collections.abc import Coroutine, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

from .constants import EMPTY_REPO_RE, UNKNOWN_REV_RE
from .datatypes import Log
from .exceptions import GitException, NoCommitsException, NoLogsException, UnknownRevisionException
from .helpers import subprocess_run

__all__ = ["get_logs"]

# formats: https://git-scm.com/docs/pretty-formats
LOG_FMT_STRING = "%H;;%P;;%ae;;%an;;%cI;;%s"
LOG_PARTS_COUNT = LOG_FMT_STRING.count("%")


def __process_log(stdout_line: str) -> Log:
    parts = stdout_line.split(";;")
    if len(parts) != LOG_PARTS_COUNT:
        msg = f"invalid log line: {stdout_line}"
        raise ValueError(msg)
    return Log(
        parts[0],
        parts[1],
        parts[2],
        parts[3],
        datetime.fromisoformat(parts[4]),
        parts[5],
    )


def __process_logs(stdout: str) -> Iterator[Log]:
    log_lines = stdout.strip().split("\n")
    return map(__process_log, log_lines)


async def get_logs(
    git_repo: Path,
    branch: str | None = None,
    max_number: int | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> Coroutine[Any, Any, Iterator[Log]]:
    """
    Generate git logs from a repo

        :param git_repo: Path to the repo
        :param branch: The branch name, defaults to None
        :param max_number: max number of logs to get, defaults to None
        :param since: Filter logs after given date, defaults to None
        :param until: Filter logs before given date defaults to None
        :raises NoCommitsException: Repo has no commits
        :raises UnknownRevisionException: Unknown revision/branch name
        :raises GitException: Error to do with git
        :raises NoLogsException: No logs have been generated
        :return: The generated logs
    """
    args = ["git", "-C", str(git_repo), "log"]

    if branch is not None:
        args.append(str(branch))
    if max_number is not None:
        args.append(f"--max-count={max_number}")
    if since is not None:
        args.append(f"--since={since.isoformat()}")
    if until is not None:
        args.append(f"--until={until.isoformat()}")
    args.append(f"--pretty={LOG_FMT_STRING}")

    process_status = await subprocess_run(args)
    if not process_status.stdout:
        stderr = process_status.stderr.decode()
        if re.match(EMPTY_REPO_RE, stderr):
            raise NoCommitsException
        if re.match(UNKNOWN_REV_RE, stderr):
            msg = f"unknown revision/branch {branch}"
            raise UnknownRevisionException(msg)
        if process_status.returncode != 0:
            raise GitException(stderr)
        msg = f"no logs found (using given filters) for '{git_repo.name}'"
        raise NoLogsException(msg)
    stdout = process_status.stdout.decode()
    return __process_logs(stdout)
