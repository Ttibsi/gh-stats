#!/usr/bin/env python3

import os
import requests
import pprint as p

def log(msg:str):
    with open('gh_stat.log', 'a') as file:
        file.write(msg + "\n")


def get_username() -> str:
    with open(os.path.expanduser("~/.gitconfig")) as git_file:
        git_lines = git_file.readlines()

    for line in git_lines:
        if line.startswith("name"):
            name_line = line.split(" = ")
            break

    return name_line[1].lower().strip()


def make_request(user: str):
    return requests.get(f"https://api.github.com/users/{user}/events?page=1&per_page=100").json()


def count_commits(resp) -> int:
    count = 0
    for item in resp:
        if item["type"] == "PushEvent":
            count += len(item["payload"]["commits"])

    return count


def main() -> int:
    log("start")

    username = get_username()
    log(f"{username=}")

    resp = make_request(username)
    print(count_commits(resp))

    log("end")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
