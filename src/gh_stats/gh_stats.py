#!/usr/bin/env python3
import argparse
import datetime
import os
import pprint as p
from collections import Counter
from typing import Any
from typing import Sequence

import argparser
import requests
import stats

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


def get_current_month(statblk: stats.Statblock) -> None:
    statblk.month_name = datetime.date.today().strftime("%b")
    statblk.month = str(datetime.datetime.now().month).zfill(2)


def count_commits(args: dict[Any, Any], statblk: stats.Statblock) -> stats.Statblock:
    """This function needs unit tests"""
    page_count = 1

    current_year = get_current_year()
    log(f"Checking year: {current_year}", args["verbose"])

    get_current_month(statblk)

    if args["extend"]:
        log(f"Checking month: {statblk.month}", args["verbose"])

    resp = make_request(args, statblk.username)

    while (
        resp[0]["created_at"][:4] == str(current_year)  # type: ignore
        and len(resp) == response_length  # type: ignore
    ):

        log(f"Page {page_count} is length {len(resp)}", args["verbose"])

        for item in resp:  # type: ignore
            if item["created_at"][:4] != str(current_year):
                break

            # Get year count
            if item["type"] == "PushEvent":
                statblk.count += item["payload"]["size"]
            elif item["type"] == "PullRequestEvent":
                statblk.count += item["payload"]["pull_request"]["commits"]
            elif item["type"] in GITHUB_EVENTS:
                statblk.count += 1

            # Get month count
            if item["created_at"][5:7] == statblk.month:
                if item["type"] == "PushEvent":
                    statblk.month_count += item["payload"]["size"]
                elif item["type"] == "PullRequestEvent":
                    statblk.month_count += item["payload"]["pull_request"]["commits"]
                elif item["type"] in GITHUB_EVENTS:
                    statblk.month_count += 1

            # Count commits per repo
            if item["type"] == "PushEvent":
                statblk.projects[item["repo"]["name"]] += item["payload"]["size"]
            elif item["type"] == "PullRequestEvent":
                statblk.projects[item["repo"]["name"]] += item["payload"][
                    "pull_request"
                ]["commits"]
            elif item["type"] in GITHUB_EVENTS:
                statblk.projects[item["repo"]["name"]] += 1

        log(f"In-progress commit count is at: {statblk.count}", args["verbose"])

        if args["extend"]:
            log(
                f"In-progress month count is at: {statblk.month_count}", args["verbose"]
            )
            log(f"Commits per repo: \n{statblk.projects}", args["verbose"])

        page_count += 1
        resp = make_request(args, statblk.username, page_count)

    return statblk


def print_output(statblk: stats.Statblock, extend: bool) -> None:
    print(f"Github interactions: {statblk.count}")

    if extend:
        print(f"Monthly interactions ({statblk.month_name}): {statblk.month_count}")

        (most_common_repo,) = statblk.projects.most_common(1)
        print(f"Most active repo: {most_common_repo}")


def main(argv: Sequence[str] | None = None) -> int:
    args = argparser.parser(argv)
    statblk = stats.Statblock()

    if args["flags"]:
        p.pprint(args)

    log("Starting gh_stats", args["verbose"])
    log(f"Accepted arguments: {args}", args["verbose"])

    log("Fetching github username", args["verbose"])
    statblk.username = get_username()
    log(f"username = {statblk.username}\n", args["verbose"])

    if args["extend"]:
        log("Count extended commits", args["verbose"])
    else:
        log("Count commits in year", args["verbose"])

    statblk = count_commits(args, statblk)
    log(f"commit_count={statblk.count}\n", args["verbose"])

    print_output(statblk, args["extend"])

    log("Closing gh_stats", args["verbose"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
