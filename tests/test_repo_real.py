# tests/test_repo_miner.py

import os
import pandas as pd
import pytest
import vcr
from datetime import datetime, timedelta
from src.repo_miner import fetch_commits #, fetch_issues, merge_and_summarize

# --- Set Up the VCR --- 

test_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes",
    record_mode="new_episodes",
    match_on=["uri", "method"]
)

# --- Test against the well-known small repo octocat/Hello-World

def test_fetch_commits_hello_world_repo():
    # Test a basic test against the real repo
    
    with test_vcr.use_cassette("hello_world_commits.yaml"):
        df = fetch_commits("octocat/Hello-World", max_commits=20)

        assert not df.empty
        assert list(df.columns) == ["sha", "author", "email", "date", "message"]
        assert len(df) <= 20

def test_fetch_commits_hello_world_repo_small_limit():
    # Test that fetch_commits respects the max_commits limit.

    with test_vcr.use_cassette("hello_world_commits.yaml"):
        df = fetch_commits("octocat/Hello-World", max_commits=7)

        assert not df.empty
        assert list(df.columns) == ["sha", "author", "email", "date", "message"]
        assert len(df) <= 7

def test_fetch_commits_hello_world_repo_empty():
    # Test that fetch_commits returns empty DataFrame when limit is 0

    with test_vcr.use_cassette("hello_world_commits.yaml"):
        df = fetch_commits("octocat/Hello-World", max_commits=0)

        assert df.empty
        assert len(df) <= 0
