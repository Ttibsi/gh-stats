#!/usr/bin/env python3
import os
import pprint as p
from datetime import date

import requests


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


def make_request(user: str) -> object:
    return requests.get(
        f"https://api.github.com/users/{user}/events?page=1&per_page=100"
    ).json()


def count_commits(user: str, current_year: int) -> int:
    count = 0
    resp = make_request(user)
    for item in resp:
        if not item['created_at'].startswith(str(current_year)):
            break

        if item["type"] == "PushEvent":
            count += len(item["payload"]["commits"])

    return count


def main() -> int:
    log("start")

    username = get_username()
    log(f"{username=}")

    current_year = get_current_year()
    commit_count = (count_commits(username, current_year))
    log(f"{commit_count=}")
    print(f"Commits this year: {commit_count}")

    log("end")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
