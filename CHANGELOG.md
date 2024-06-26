# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.10.0] - 2024-05-01
### Added
-  "depth" support in clone command
### Changed
- Typing hint fixes
- Migrate to use hatch for project management tool
- Move docs to GitHub Pages
### Removed
- Dropped support for anything older than Python 3.10

## [0.9.3] - 2022-11-14
### Changed
- Update deps for docs
### Fixed
- Add missing doc stuff

## [0.9.2] - 2022-09-05
### Fixed
- When reading large repo objects, using the stream functions, the max buffer size would be hit. Now reads in chunks, the size of which will vary depending on the constant set by `io.DEFAULT_BUFFER_SIZE`

## [0.9.0] - 2022-09-04
### Added
- Ability to count branches in a repo
### Changed
- Move archive methods into separate module

## [0.8.2] - 2022-03-25
### Fixed
- SSH pack exchange hanging due to 'done' message not being received

## [0.8.1] - 2022-03-25 [YANKED]

## [0.8.0] - 2022-03-19
### Added
- Pack exchange and advertise
- Smart-HTTP helpers for quart

## [0.7.2] - 2022-02-28
### Fixed
- Fixed no tags being recognised as a tag

### Changed
- Updated sphinx pip requirement to 4.4.0

## [0.7.1] - 2022-02-06
### Fixed
- Fix clone repo function

## [0.7.0] - 2022-02-06
This version will break your projects written for previous versions as all functions are now asynchronous. I have changed them to increase speed for my  [basic-git-web-interface](https://github.com/enchant97/basic-git-web-interface) project.

To make your code compatible either switch to using async functions and await the function calls or wrap the functions in the asyncio.run() function.

### Added
- Add & Commit functionality

### Changed
- **Git commands are now asynchronous!**

## [0.6.0] - 2022-01-18
### Added
- Git tag functionality
- Buffered reading of files from repositories
- Documentation hosted at [readthedocs](https://python-git-interface.readthedocs.io/en/stable/)

### Changed
- Strings can be used instead of `pathlib.Path` objects for `git_repo` parameter
- Missing docstrings

### Removed
- Drop Python 3.8 support and below

## [0.5.2] - 2021-12-19
### Changed
- Docs hosted at: readthedocs
- Improve typing hints
- Missing doc strings
- Handle if git errors in `get_version()` method

### Fixed
- Generic GitException class being used instead of undetected ref error

## [0.5.1] - 2021-12-10
### Added
- Read file from a repo
- `cat-file` command
- `rev-list` command
- Access git version

### Changed
- Add parent hash and author name to log class

### Fixed
- #2 - cat file commands not running

## [0.5.0] - 2021-12-03
### Added
- Read file
- Get object size
- Get object type
- Read object pretty printed

## [0.4.1] - 2021-10-28
### Fixed
- Fix bug with getting branch names

## [0.4.0] - 2021-10-24
### Added
- Cloning support (without authentication)

## [0.3.1] - 2021-10-21
### Fixed
- Fixed #1 `get_branches()` not showing full branch names

## [0.3.0] - 2021-10-17
### Added
- Project changelog
- Branch creation
- Branch copy
- Branch rename
- Branch deletion
- Ls-tree functionality
- Symbolic-ref functionality

### Changed
- Add `NoBranchesException` to `get_branches()`

### Fixed
- Add missing `__all__` methods

## [0.2.0] - 2021-10-04
### Added
- Document Code
- Get/Set repo description
- Run maintenance
- Create archives

### Changed
- Use GitException for init_repo

## [0.1.0] - 2021-10-03
### Added
- Get branches
- Log viewing
- Init repo
