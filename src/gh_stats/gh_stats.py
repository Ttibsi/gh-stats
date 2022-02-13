#!/usr/bin/env python3
import argparse
import datetime
import os
import pprint as p
from typing import Any
from typing import Sequence

import argparser  # type: ignore
import requests

# https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types
GITHUB_EVENTS = [
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
]

response_length = 100  # max 100, default 30


def log(msg: str, verbose: bool) -> None:
    """Not the fanciest logging, but it works"""
    with open("gh_stat.log", "a") as file:
        file.write(msg + "\n")

    if verbose:
        print(msg)


def get_username() -> str:
    with open(os.path.expanduser("~/.gitconfig")) as git_file:
        git_lines = git_file.readlines()

    for line in git_lines:
        name_line = line.split(" = ") if line.startswith("name") else ""

        if name_line != "":
            break

    return name_line[1].lower().strip()


def make_request(args: dict[Any, Any], user: str, page: int = 1):
    log(f"Request call to page {page}", args["verbose"])
    return requests.get(
        f"https://api.github.com/users/{user}/events?page={page}&per_page={response_length}"
    ).json()


def get_current_year() -> int:
    return int(datetime.date.today().strftime("%Y"))


def get_current_month(name: bool = False) -> str:
    if name:
        return datetime.date.today().strftime("%b")
    else:
        return str(datetime.datetime.now().month).zfill(2)


def count_commits(args: dict[Any, Any], user: str) -> tuple[int, int]:
    """This function needs unit tests"""
    count = 0
    page_count = 1

    current_year = get_current_year()
    log(f"Checking year: {current_year}", args["verbose"])

    current_month = get_current_month()
    month_count = 0
    if args["extend"]:
        log(f"Checking month: {current_month}", args["verbose"])

    resp = make_request(args, user)

    while resp[0]["created_at"][:4] == str(current_year) and len(resp) == response_length:  # type: ignore
        log(f"Page {page_count} is length {len(resp)}", args["verbose"])
        for item in resp:  # type: ignore
            if item["created_at"][:4] != str(current_year):
                break

            if item["type"] == "PushEvent":
                count += item["payload"]["size"]
            elif item["type"] in GITHUB_EVENTS:
                count += 1

            if item["created_at"][5:7] == current_month:
                if item["type"] == "PushEvent":
                    month_count += item["payload"]["size"]
                elif item["type"] in GITHUB_EVENTS:
                    month_count += 1

        page_count += 1
        log(f"In-progress commit count is at: {count}", args["verbose"])

        if args["extend"]:
            log(f"In-progress month count is at: {month_count}", args["verbose"])
        resp = make_request(args, user, page_count)

    return count, month_count if args["extend"] else 0


def main(argv: Sequence[str] | None = None) -> int:
    args = argparser.parser(argv)

    if args["flags"]:
        p.pprint(args)

    log("Starting gh_stats", args["verbose"])
    log(f"Accepted arguments: {args}", args["verbose"])

    log("Fetching github username", args["verbose"])
    username = get_username()
    log(f"{username=}\n", args["verbose"])

    if args["extend"]:
        log("Count extended commits", args["verbose"])
    else:
        log("Count commits in year", args["verbose"])

    output = count_commits(args, username)
    log(f"commit_count={output}", args["verbose"])

    commit_count, month_count = output

    print(f"\nGithub interactions: {commit_count}")

    if args["extend"]:
        month = get_current_month(True)
        print(f"Monthly interactions {month}: {month_count}")

    log("Closing gh_stats", args["verbose"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
