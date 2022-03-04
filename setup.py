from setuptools import find_packages
from setuptools import setup


setup(
    name="gh-stats",
    version="1.0.1",
    description="Get statistics about your Github commit history",
    author="Ttibsi",
    author_email="ashisbitt@icloud.com",
    url="https://github.com/ttibsi/gh-stats",
    python_requires=">=3.10",
    install_requires=[
        "PyInputPlus",
        "requests",
    ],
    packages=find_packages(
        exclude=["test*"],
    ),
    entry_points={
        "console_scripts": [
            "ghstats = gh_stats.ghstats:main",
        ],
    },
)
