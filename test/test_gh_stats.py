import pytest
from src.gh_stats import gh_stats

def test_main():
    assert gh_stats.main() == 0


def test_get_username():
    """This will only work on my system. This test could be better"""
    assert gh_stats.get_username() == 'ttibsi' 
