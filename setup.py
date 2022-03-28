from setuptools import setup

# Only requirements are listed here for GitHub dependency graph
setup(
    name="git-interface",
    install_requires=[
        "aiofiles >= 0.8",
    ],
    extras_require={
        "quart": ["quart>=0.16.3", "async-timeout>=4.0.2"],
        "ssh": ["asyncssh>=2.9.0"],
    },
)
