from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass
class Log:
    commit_hash: str
    author_email: str
    commit_date: datetime
    subject: str


class ArchiveTypes(Enum):
    TAR = "tar"
    TAR_GZ = "tar.gz"
    ZIP = "zip"
