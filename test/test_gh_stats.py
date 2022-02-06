import pytest
from src.gh_stats import gh_stats

def test_main():
    assert gh_stats.main() == 0
