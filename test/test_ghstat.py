import json
from collections import Counter

import freezegun

import gh_stats.ghstats as ghstat


@freezegun.freeze_time("2022-02-12")
def test_get_current_month():
    expected = ("Feb", "02")
    assert ghstat.get_current_month() == expected


def test_count_commits():
    ret = 0
    with open("test_data.json") as f:
        obj = json.load(f)

    for item in obj:
        ret += ghstat.count_commits(item)

    assert ret == 72


@freezegun.freeze_time("2022-02-28")
def test_count_monthly():
    ret = 0
    with open("test_data.json") as f:
        obj = json.load(f)

    for item in obj:
        ret += ghstat.count_monthly(item)

    assert ret == 72


def test_count_per_repo():
    test_stats: dict[str, Counter[str]] = {"projects": Counter()}
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
        test_stats["projects"] += ghstat.count_per_repo(item)

    assert test_stats["projects"] == test_counter


def test_new_repos():
    ret = 0

    with open("test_data.json") as f:
        obj = json.load(f)

    for item in obj:
        ret += ghstat.new_repos(item)

    assert ret == 0
