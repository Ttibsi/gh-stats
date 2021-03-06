# gh-stats

Find out information about your github commit history with this one simple tool!

![Example output](https://raw.githubusercontent.com/Ttibsi/gh-stats/master/screenshots/ExampleOutput.png)

### Installation

```console
$ git clone git@github.com:Ttibsi/gh-stats.git
$ cd gh_stats
$ python3 -m virtualenv venv
$ . venv/bin/activate
$ pip install .
```

Note that lines 3 and 4 above will only install to a virtual environment.

### Usage

Run `ghstats -u <username>` to trigger the main script. This will tell you your
current github contributions (the number of times you've done a
`git commit ... git push` to github). The username need to be specified each time - we
recommend you set up a shell alias if you plan to use this regularly

For more accurate reading, you'll want to add a github access token. To do this,
run `ghstats --add-token` and follow the instructions. This token is written to
`~/.config/gh_stats/GITHUB_TOKEN`, and gh_stats does not use this token for any
purpose other than reading.

See `ghstats --help` for more

### Rationale

I found myself regularly checking my github account's contribution graph
to see how much work I'd been doing throughout the day.  However, I found
myself wanting more granular information that I could get at a glance without
leaving the terminal.

Thus, `gh-stats` was born


### How to help

Feel free to make any PRs you see fit, or check out the
[issues page](https://github.com/Ttibsi/gh-stats/issues) if you're unsure where
to start.

Please make use of the [pre-commit](https://pre-commit.com) config file
attached to automatically format and type check your PRs.
