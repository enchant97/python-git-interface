"""
Custom types that are used
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

__all__ = ["Log", "ArchiveTypes"]


class ArchiveTypes(Enum):
    """
    Possible archive types
    """
    TAR = "tar"
    TAR_GZ = "tar.gz"
    ZIP = "zip"


class TreeContentTypes(Enum):
    """
    Tree content types
    """
    TREE = "tree"
    BLOB = "blob"


@dataclass
class Log:
    """
    Represents a single git log
    """
    commit_hash: str
    parent_hash: str
    author_email: str
    author_name: str
    commit_date: datetime
    subject: str


@dataclass
class TreeContent:
    """
    Reperesents a single 'ls-tree' entry
    """
    mode: str
    type_: TreeContentTypes
    object_: str
    file: Path
    object_size: Optional[int] = None

    @classmethod
    def from_str_values(cls, **kwargs):
        if not isinstance(kwargs["type_"], TreeContentTypes):
            kwargs["type_"] = TreeContentTypes(kwargs["type_"])
        if kwargs.get("object_size"):
            if kwargs["object_size"] == "-":
                kwargs["object_size"] = None
            else:
                kwargs["object_size"] = int(kwargs["object_size"])
        kwargs["file"] = Path(kwargs["file"])
        return cls(**kwargs)
