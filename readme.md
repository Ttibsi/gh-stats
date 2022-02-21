# gh-stats

Find out infromation about your git commit history with this one simple tool!

### Installation

```
$ git clone git@github.com:Ttibsi/gh-stats.git
$ cd gh_stats
$ pip install .
```

### Usage

Run `ghstat` to trigger the main script. This will tell you your current github contributions (the number of times you've done a `git commit ... git push` to github).

```console
usage: ghstat.py [-h] [-v] [-f] [-e] [-u USERNAME]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output of operations
  -f, --flags           Display status of all flags for debugging purposes
  -e, --extend          Show more statistics
  -u USERNAME, --username USERNAME
                        Check a specific github account
```

### Rationale

I found myself regularly checking my github account's contribution graph to see how much work I'd been doing throughout the day.

However, I found myself wanting more granular information that I could get at a glance without leaving the terminal.

Thus, `gh-stats` was born


### How to help

Feel free to make any PRs you see fit, or check out the [issues page](https://github.com/Ttibsi/gh-stats/issues) if you're unsure where to start.

Please make use of the [pre-commit](http://pre-commit.com) config file attached to automatically format and type check your PRs.

(This will eventually be replaced with automated CI)
