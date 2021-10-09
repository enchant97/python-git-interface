"""
Constants
"""
EMPTY_REPO_RE = r"fatal: your current branch '\w+' does not have any commits yet"
UNKNOWN_REV_RE = r"fatal: ambiguous argument '\w+': unknown revision or path not in the working tree."
BRANCH_ALREADY_EXISTS_RE = r"fatal: A branch named '\w+' already exists."
BRANCH_NOT_FOUND_RE = r"error: branch '\w+' not found."
BRANCH_REFNAME_NOT_FOUND_RE = r"error: refname \w+ not found"
NOT_VALID_OBJECT_NAME_RE = r"fatal: Not a valid object name \w+"
# git ls-tree <tree-ish>
LS_TREE_RE = r"^(\d{6}) (\w+) (\w{40})\t(.+)$"
# git ls-tree <tree-ish> -l
LS_TREE_LONG_RE = r"^(\d{6}) (\w+) (\w{40}) +(\d+|\-)\t(.+)$"
