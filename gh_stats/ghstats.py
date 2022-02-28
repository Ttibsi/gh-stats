#!/usr/bin/env python3
import argparse
import datetime
from collections import Counter
from collections.abc import Sequence
from typing import Any

import requests

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


def make_request(
    args: argparse.Namespace, user: str, page: int = 1
) -> list[dict[str, Any]]:
    return requests.get(
        f"https://api.github.com/users/{user}/events?page={page}&per_page=100"
    ).json()


def get_current_month() -> tuple[str, str]:
    today = datetime.date.today()
    return (today.strftime("%b"), f"{today.month:02}")


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
    commit_date = item["created_at"]
    month_obj = datetime.datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ").month

    if datetime.datetime.today().month == month_obj:
        if item["type"] == "PushEvent":
            return int(item["payload"]["size"])
        elif item["type"] == "PullRequestEvent":
            return int(item["payload"]["pull_request"]["commits"])
        elif item["type"] in GITHUB_EVENTS:
            return 1

    return 0


def count_per_repo(item: dict[str, Any]) -> Counter[str]:
    # Count commits per repo
    repo_counter: Counter[str] = Counter()

    if item["type"] == "PushEvent":
        repo_counter[item["repo"]["name"]] += item["payload"]["size"]
    elif item["type"] == "PullRequestEvent":
        repo_counter[item["repo"]["name"]] += item["payload"]["pull_request"]["commits"]
    elif item["type"] in GITHUB_EVENTS:
        repo_counter[item["repo"]["name"]] += 1

    return repo_counter


def new_repos(item: dict[str, Any]) -> int:
    if item["type"] == "CreateEvent" and item["payload"]["ref_type"] == "repository":
        return 1
    else:
        return 0


def parse_json(args: argparse.Namespace) -> dict[str, Any]:
    page_count = 1
    statblock: dict[str, Any] = {
        "username": args.username,
        "count": 0,
        "month_count": 0,
        "month": "",
        "month_name": "",
        "projects": Counter(),
        "new_repo_count": 0,
    }

    current_year = datetime.date.today().year

    statblock["month"], statblock["month_name"] = get_current_month()

    resp = make_request(args, statblock["username"])

    while resp[0]["created_at"][:4] == str(current_year) and len(resp) == 100:

        for item in resp:
            if item["created_at"][:4] != str(current_year):
                break

            statblock["count"] += count_commits(item)
            statblock["month_count"] += count_monthly(item, statblock["month"])
            statblock["projects"] += count_per_repo(item)
            statblock["new_repo_count"] += new_repos(item)

        page_count += 1
        resp = make_request(args, statblock["username"], page_count)

    return statblock


def print_output(statblock: dict[str, Any], extend: bool) -> None:
    print(f"====== {datetime.date.today()} ======")
    print(f"Total interactions: {statblock['count']}")
    # Interactions today:
    # Interactions per repo today

    if extend:
        print(
            f"Monthly interactions ({statblock['month_name']}): {statblock['month_count']}"
        )

        (mcr,) = statblock["projects"].most_common(1)
        print(f"Most active repo ({mcr[0]}): {mcr[1]}")

        print(f"Repos created this year: {statblock['new_repo_count']}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()

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
        help="Specify github username (required)",
        required=True,
    )

    args: argparse.Namespace = parser.parse_args(argv)

    if args.flags:
        print(vars(args))

    statblock = parse_json(args)
    print_output(statblock, args.extend)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
