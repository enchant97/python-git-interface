"""
Custom types that are used
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

__all__ = ["Log", "ArchiveTypes"]


@dataclass
class Log:
    """
    Represents a single git log
    """
    commit_hash: str
    author_email: str
    commit_date: datetime
    subject: str


class ArchiveTypes(Enum):
    """
    Possible archive types
    """
    TAR = "tar"
    TAR_GZ = "tar.gz"
    ZIP = "zip"
