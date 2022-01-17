"""
Constants
"""
EMPTY_REPO_RE = r"fatal: your current branch '.+' does not have any commits yet"
UNKNOWN_REV_RE = r"fatal: ambiguous argument '.+': unknown revision or path not in the working tree."
BRANCH_ALREADY_EXISTS_RE = r"fatal: A branch named '.+' already exists."
BRANCH_NOT_FOUND_RE = r"error: branch '.+' not found."
BRANCH_REFNAME_NOT_FOUND_RE = r"error: refname .+ not found"
NOT_VALID_OBJECT_NAME_RE = r"fatal: Not a valid object name .+"
INVALID_OBJECT_NAME = r"fatal: invalid object name '.+'"
PATH_DOES_NOT_EXIST = r"fatal: path '.+' does not exist in '.+'"
TAG_ALREADY_EXISTS_RE = r"fatal: tag '.+' already exists"
TAG_NOT_FOUND_RE = r"error: tag '.+' not found"
# git ls-tree <tree-ish>
LS_TREE_RE = r"^(\d{6}) (\w+) (\w{40})\t(.+)$"
# git ls-tree <tree-ish> -l
LS_TREE_LONG_RE = r"^(\d{6}) (\w+) (\w{40}) +(\d+|\-)\t(.+)$"
