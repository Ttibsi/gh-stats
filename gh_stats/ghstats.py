#!/usr/bin/env python3
import argparse
import datetime
import subprocess
from collections import Counter
from collections.abc import Sequence
from typing import Any
from typing import NamedTuple

import requests

# https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types
GITHUB_EVENTS = frozenset(
    (
        "CommitCommentEvent",  # Commit via GH web ui
        "CreateEvent",  # Create branch or tag
        "DeleteEvent",  # Delete branch or tag
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


class Response(NamedTuple):
    json: Any
    links: dict[str, str]


def parse_header(lnk: str | None) -> dict[str, str]:
    if lnk is None:
        return {}

    ret = {}
    parts = lnk.split(",")
    for part in parts:
        link, rel = part.split(";")
        rel = rel.strip()[len('rel="') : -1]
        ret[rel] = link.strip()[1:-1]

    return ret


def make_request(url: str) -> Response:
    req = requests.get(url)
    lnk = req.headers.get("link")
    return Response(req.json(), parse_header(lnk))


def output_version() -> str:
    ver = subprocess.check_output(("git", "describe", "--abbrev=0"))
    return f"Current version: {ver.strip().decode('utf-8')}"


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


def count_today(item: dict[str, Any]) -> int:
    commit_date = item["created_at"]
    date_obj = datetime.datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ").date()

    if datetime.date.today() == date_obj:
        if item["type"] == "PushEvent":
            return int(item["payload"]["size"])
        elif item["type"] == "PullRequestEvent":
            return int(item["payload"]["pull_request"]["commits"])
        elif item["type"] in GITHUB_EVENTS:
            return 1

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
    statblock: dict[str, Any] = {
        "username": args.username,
        "daily": 0,
        "count": 0,
        "month_count": 0,
        "month": "",
        "month_name": "",
        "projects": Counter(),
        "new_repo_count": 0,
    }

    statblock["month_name"], statblock["month"] = get_current_month()
    starting_url = f"https://api.github.com/users/{statblock['username']}/events"
    resp = make_request(starting_url)

    while True:
        for item in resp.json:
            item_date = item["created_at"]
            date_obj = datetime.datetime.strptime(
                item_date, "%Y-%m-%dT%H:%M:%SZ"
            ).date()

            if datetime.date.today().year != date_obj.year:
                break

            # Checks through the year
            statblock["count"] += count_commits(item)
            statblock["projects"] += count_per_repo(item)
            statblock["new_repo_count"] += new_repos(item)

            # Checks through the month
            if datetime.date.today().month == date_obj.month:
                statblock["month_count"] += count_monthly(item, statblock["month"])

            # Checks through the current day
            if (
                datetime.date.today().month == date_obj.month
                and datetime.date.today().day == date_obj.day
            ):

                statblock["daily"] += count_today(item)

        try:
            resp = make_request(resp.links["next"])
        except KeyError:
            break

    return statblock


def print_output(statblock: dict[str, Any], extend: bool) -> None:
    print(f"====== {datetime.date.today()} ======")
    print(f"Daily interactions: {statblock['daily']}")
    print(f"Total interactions: {statblock['count']}")
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

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-u",
        "--username",
        help="Specify github username (required)",
    )

    group.add_argument(
        "--version",
        help="Output current version",
        action="store_true",
    )

    args: argparse.Namespace = parser.parse_args(argv)

    if args.version:
        print(output_version())
        return 0

    if args.flags:
        print(vars(args))

    statblock = parse_json(args)
    print_output(statblock, args.extend)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
