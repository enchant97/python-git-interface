Quick Start
-----------

Get Branches:
::

    import asyncio
    from git_interface.branch import get_branches

    head, other_branches = asyncio.run(get_branches("my_git_repo.git"))

    print("HEAD = ", head)
    print("OTHER", other_branches)
