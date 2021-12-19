Quick Start
-----------

Get Branches:
::

    from git_interface.branch import get_branches

    head, other_branches = get_branches("my_git_repo.git")

    print("HEAD = ", head)
    print("OTHER", other_branches)
