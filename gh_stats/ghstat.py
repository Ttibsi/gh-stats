#!/usr/bin/env python3
import argparse
import datetime
import pprint as p
from collections.abc import Sequence
from typing import Any

import requests

from gh_stats import stats

# https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types
GITHUB_EVENTS = frozenset(
    (
        "CommitCommentEvent",  # Commit via GH web ui
        "CreateEvent",
        "DeleteEvent",
        "ForkEvent",
        "IssueCommentEvent",
        "IssuesEvent",
        "PullRequestEvent",
        "PullRequestReviewEvent",
        "PullRequestReviewCommentEvent",
        "ReleaseEvent",  # Make a git release
        "WatchEvent",  # Star a repo
    )
)

response_length = 100  # max 100, default 30


def make_request(
    args: argparse.Namespace, user: str, page: int = 1
) -> list[dict[str, Any]]:
    return requests.get(
        f"https://api.github.com/users/{user}/events?page={page}&per_page={response_length}"
    ).json()


def get_current_year() -> int:
    return datetime.date.today().year


def get_current_month(statblk: stats.Statblock) -> None:
    statblk.month_name = datetime.date.today().strftime("%b")
    statblk.month = f"{datetime.datetime.now().month:02}"


def count_commits(item: dict[str, Any]) -> int:
    # Get year count
    if item["type"] == "PushEvent":
        return item["payload"]["size"]
    elif item["type"] == "PullRequestEvent":
        return item["payload"]["pull_request"]["commits"]
    elif item["type"] in GITHUB_EVENTS:
        return 1
    else:
        return 0


def count_monthly(item: dict[str, Any], month: str) -> int:
    if item["created_at"][5:7] == month:
        if item["type"] == "PushEvent":
            return int(item["payload"]["size"])
        elif item["type"] == "PullRequestEvent":
            return int(item["payload"]["pull_request"]["commits"])
        elif item["type"] in GITHUB_EVENTS:
            return 1

    return 0


def count_per_repo(item: dict[str, Any], statblk: stats.Statblock) -> stats.Statblock:
    # Count commits per repo
    if item["type"] == "PushEvent":
        statblk.projects[item["repo"]["name"]] += item["payload"]["size"]
    elif item["type"] == "PullRequestEvent":
        statblk.projects[item["repo"]["name"]] += item["payload"]["pull_request"][
            "commits"
        ]
    elif item["type"] in GITHUB_EVENTS:
        statblk.projects[item["repo"]["name"]] += 1

    return statblk


def new_repos(item: dict[str, Any]) -> int:
    if item["type"] == "CreateEvent" and item["payload"]["ref_type"] == "repository":
        return 1
    else:
        return 0


def parse_json(args: argparse.Namespace, statblk: stats.Statblock) -> stats.Statblock:
    page_count = 1

    current_year = get_current_year()

    get_current_month(statblk)

    resp = make_request(args, statblk.username)

    while (
        resp[0]["created_at"][:4] == str(current_year) and len(resp) == response_length
    ):

        for item in resp:
            if item["created_at"][:4] != str(current_year):
                break

            statblk.count += count_commits(item)
            statblk.month_count += count_monthly(item, statblk.month)
            statblk = count_per_repo(item, statblk)
            statblk.new_repo_count += new_repos(item)

        page_count += 1
        resp = make_request(args, statblk.username, page_count)

    return statblk


def print_output(statblk: stats.Statblock, extend: bool) -> None:
    print(f"Github interactions: {statblk.count}")

    if extend:
        print(f"Monthly interactions ({statblk.month_name}): {statblk.month_count}")

        mcr = statblk.get_most_common_repo()
        print(f"Most active repo ({mcr[0]}): {mcr[1]}")

        print(f"Repos created this year: {statblk.new_repo_count}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbose output of operations",
        action="store_true",
    )

    parser.add_argument(
        "-f",
        "--flags",
        help="Display status of all flags for debugging purposes",
        action="store_true",
    )

    parser.add_argument(
        "-e",
        "--extend",
        help="Show more statistics",
        action="store_true",
    )

    parser.add_argument(
        "-u",
        "--username",
        help="Check a specific github account",
        required=True,
    )

    args: argparse.Namespace = parser.parse_args(argv)
    statblk = stats.Statblock()

    if args.flags:
        p.pprint(args)

    statblk.username = args.username

    statblk = parse_json(args, statblk)
    print_output(statblk, args.extend)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
