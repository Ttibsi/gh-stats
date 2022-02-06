#!/usr/bin/env python3

def log(msg:str):
    with open('gh_stat.log', 'a') as file:
        file.write(msg + "\n")


def main() -> int:
    log("start")
    log("end")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
