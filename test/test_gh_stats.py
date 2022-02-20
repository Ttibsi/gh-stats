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
        for item in f:
            res += ghstat.count_commits(f)

    assert res == 30


def test_count_monthly():
    res = 0
    with open("test_data.json") as f:
        for item in f:
            res += ghstat.count_monthly(f)

    assert res == 30
