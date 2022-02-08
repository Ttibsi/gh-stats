from setuptools import find_packages  # type: ignore
from setuptools import setup  # type: ignore


setup(
    name="gh-stats",
    version="0.1.0",
    description="Get statistics about your Github commit history",
    author="Ttibsi",
    author_email="ashisbitt@icloud.com",
    url="https://github.com/ttibsi/gh-stats",
    install_requires=[
        "requests",
    ],
    packages=find_packages(
        where="src",
    ),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "ghstat = gh_stats.gh_stats:main",
        ],
    },
)
