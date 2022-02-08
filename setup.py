from setuptools import find_packages  # type: ignore
from setuptools import setup  # type: ignore


setup(
    name="gh_stats",
    version="0.1.0",
    description="Get statistics about your Github commit history",
    author="Ttibsi",
    author_email="ashisbitt@icloud.com",
    url="https://github.com/ttibsi/gh_stats",
    install_requires=[
        "requests",
    ],
    packages=find_packages(exclude="test*"),
    entry_points={
        "console_scripts": [
            "ghstat = src.gh_stats.gh_stats:main",
        ],
    },
)
