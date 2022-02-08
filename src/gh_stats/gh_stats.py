#!/usr/bin/env python3
import os
import pprint as p
from datetime import date

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

response_length = 100  # max 100


def log(msg: str):
    with open("gh_stat.log", "a") as file:
        file.write(msg + "\n")


def get_username() -> str:
    with open(os.path.expanduser("~/.gitconfig")) as git_file:
        git_lines = git_file.readlines()

    for line in git_lines:
        if line.startswith("name"):
            name_line = line.split(" = ")
            break

    return name_line[1].lower().strip()


def get_current_year() -> int:
    return int(date.today().strftime("%Y"))


def make_request(user: str, page: int = 1):
    log(f"Request call to page {page}")
    return requests.get(
        f"https://api.github.com/users/{user}/events?page={page}&per_page={response_length}"
    ).json()


def count_commits(user: str, current_year: int) -> int:
    count = 0
    page_count = 1
    resp = make_request(user)

    while resp[0]["created_at"][:4] == str(current_year) and len(resp) == response_length:  # type: ignore
        log(f"Page {page_count} is length {len(resp)}")
        for item in resp:  # type: ignore
            if item["created_at"][:4] != str(current_year):
                break

            if item["type"] == "PushEvent":
                count += item["payload"]["size"]
            elif item["type"] in GITHUB_EVENTS:
                count += 1

        page_count += 1
        resp = make_request(user, page_count)

    return count


def main() -> int:
    log("start")

    username = get_username()
    username = "asottile"
    log(f"{username=}")

    current_year = get_current_year()
    commit_count = count_commits(username, current_year)
    log(f"{commit_count=}")
    print(f"Github interactions: {commit_count}")

    log("end")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
