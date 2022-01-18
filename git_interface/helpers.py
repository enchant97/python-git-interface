"""
Methods not related to git commands,
but to help the program function
"""
from pathlib import Path
from typing import Union


def ensure_path(path_or_str: Union[Path, str]) -> Path:
    """
    Ensures that given value is a pathlib.Path object.

        :param path_or_str: Either a path string or pathlib.Path obj
        :return: The value as a pathlib.Path obj
    """
    return path_or_str if isinstance(path_or_str, Path) else Path(path_or_str)
