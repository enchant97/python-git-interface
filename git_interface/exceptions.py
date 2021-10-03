class GitException(Exception):
    pass


class NoCommitsException(GitException):
    pass


class NoBranchesException(GitException):
    pass


class AlreadyExistsException(GitException):
    pass


class NoLogsException(GitException):
    pass


class UnknownRevisionException(GitException):
    pass
