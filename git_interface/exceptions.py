"""
Exceptions that could be raised during one of the git commands
"""


class BufferedProcessError(Exception):
    """
    Exception raised when non-zero return code is found
    """


class GitException(Exception):  # noqa: N818
    """
    Parent exception for all git exceptions,
    used when there is no other exception that fits error
    """


class NoCommitsException(GitException):
    """
    Raised when a repository has commits
    """


class NoBranchesException(GitException):
    """
    Raised when a repository has no branches
    or none that match a filter
    """


class AlreadyExistsException(GitException):
    """
    Raised when something already exists
    could be repository, branch, etc
    """


class DoesNotExistException(GitException):
    """
    Raised when something does not exist e.g. tag
    """


class NoLogsException(GitException):
    """
    Raised when a repository has no logs available
    """


class UnknownRevisionException(GitException):
    """
    Raised when a revision is not found
    """


class UnknownRefException(GitException):
    """
    Raised when a a reference is not found
    """


class PathDoesNotExistInRevException(GitException):
    """
    Raised when a path does not exist in a repository
    """
