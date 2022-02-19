import pytest

from src.gh_stats import gh_stats  # type: ignore
from src.gh_stats import stats  # type: ignore


def test_get_username():
    """This will only work on my system. This test could be better"""
    assert gh_stats.get_username() == "ttibsi"


def test_get_current_year():
    """Is there a future proof way to test this?"""
    assert gh_stats.get_current_year() == 2022


def test_count_commits():
    res = 0
    with open("test_data.json") as f:
        for item in f:
            res += gh_stats.count_commits(f)

    assert res == 30


def test_count_monthly():
    res = 0
    with open("test_data.json") as f:
        for item in f:
            res += gh_stats.count_monthly(f)

    assert res == 30
