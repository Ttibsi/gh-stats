import json

import pytest

from gh_stats import ghstat  # type: ignore
from gh_stats import stats  # type: ignore


def test_get_username():
    """This will only work on my system. This test could be better"""
    assert ghstat.get_username() == "ttibsi"


def test_get_current_year():
    """Is there a future proof way to test this?"""
    assert ghstat.get_current_year() == 2022


def test_count_commits():
    res = 0
    with open("test_data.json") as f:
        obj = json.load(f)

    for item in obj:
        res += ghstat.count_commits(item)

    assert res == 72


def test_count_monthly():
    res = 0
    with open("test_data.json") as f:
        obj = json.load(f)

    for item in obj:
        res += ghstat.count_monthly(item, "02")

    assert res == 72


def test_count_per_repo():
    test = stats.Statblock()
    test_counter = {
        "Ttibsi/gh-stats": 54,
        "Ttibsi/AdventOfCode2021": 13,
        "Ttibsi/dotfiles": 3,
        "bashbunni/dotfiles": 1,
        "clarkdave/DSACancellationChecker": 1,
    }

    with open("test_data.json") as f:
        obj = json.load(f)

    for item in obj:
        test = ghstat.count_per_repo(item, test)

    assert test.projects == test_counter
