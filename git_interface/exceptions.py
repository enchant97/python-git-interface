"""
Exceptions that could be raised during one of the git commands
"""


class GitException(Exception):
    """
    Parent exception for all git exceptions,
    used when there is no other exception that fits error
    """
    pass


class NoCommitsException(GitException):
    """
    Raised when a repository has commits
    """
    pass


class NoBranchesException(GitException):
    """
    Raised when a repository has no branches
    or none that match a filter
    """
    pass


class AlreadyExistsException(GitException):
    """
    Raised when something already exists
    could be repository, branch, etc
    """
    pass


class DoesNotExistException(GitException):
    """
    Raised when something does not exist e.g. tag
    """
    pass


class NoLogsException(GitException):
    """
    Raised when a repository has no logs available
    """
    pass


class UnknownRevisionException(GitException):
    """
    Raised when a revision is not found
    """
    pass


class UnknownRefException(GitException):
    """
    Raised when a a reference is not found
    """
    pass


class PathDoesNotExistInRevException(GitException):
    """
    Raised when a path does not exist in a repository
    """
    pass
