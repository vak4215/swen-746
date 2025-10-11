from datetime import datetime
import pandas as pd
import vcr
from src.repo_miner import fetch_commits, fetch_issues

"""
    A set of tests for the repo_miner class that utilize vcrpy to hit real APIs
"""

# --- Set Up the VCR --- 

test_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes",
    record_mode="new_episodes",
    match_on=["uri", "method"],
    filter_headers=["authorization"]
)

# --- Test fetch_commits against the well-known small repo octocat/Hello-World

# Test a basic test against the real repo
def test_fetch_commits_hello_world_repo():
    with test_vcr.use_cassette("hello_world_commits.yaml"):
        df = fetch_commits("octocat/Hello-World", max_commits=20)

        assert not df.empty
        assert list(df.columns) == ["sha", "author", "email", "date", "message"]
        assert len(df) <= 20

# Test that fetch_commits respects the max_commits limit.
def test_fetch_commits_hello_world_repo_small_limit():
    with test_vcr.use_cassette("hello_world_commits.yaml"):
        df = fetch_commits("octocat/Hello-World", max_commits=7)

        assert not df.empty
        assert list(df.columns) == ["sha", "author", "email", "date", "message"]
        assert len(df) <= 7

# Test that fetch_commits returns empty DataFrame when limit is 0
def test_fetch_commits_hello_world_repo_empty():
    with test_vcr.use_cassette("hello_world_commits.yaml"):
        df = fetch_commits("octocat/Hello-World", max_commits=0)

        assert df.empty


# --- Test fetch_issues against the well-known small repo octocat/Hello-World

# Test a basic test against the real repo
def test_fetch_issues_hello_world_repo():
    with test_vcr.use_cassette("hello_world_issues.yaml"):
        df = fetch_issues("octocat/Hello-World", max_issues=20)

        assert not df.empty
        assert {"id", "number", "title", "user", "state", "created_at", "closed_at", "comments"}.issubset(df.columns)
        assert len(df) == 20

# Test that pull requests are excluded
def test_fetch_issues_hello_world_no_prs():
    with test_vcr.use_cassette("hello_world_issues.yaml"):
        df = fetch_issues("octocat/Hello-World", max_issues=20)

        assert not df.empty
        
        for issue in df.itertuples():
            title = issue.title

            assert "PR" not in title and "Pull Request" not in title

# Test that dates are parsed and formatted correctly
def test_fetch_issues_hello_world_dates_parsed_correctly():
    with test_vcr.use_cassette("hello_world_issues.yaml"):
        df = fetch_issues("octocat/Hello-World", max_issues=20)

        assert not df.empty
        
        for issue in df.itertuples():
            dateCreated = issue.created_at
            dateClosed = issue.closed_at

            # Attempt to parse dates; python will raise an error if format is wrong
            if dateClosed:
                datetime.fromisoformat(dateClosed)
            date = datetime.fromisoformat(dateCreated)

            assert date # is a valid date

# Test that open_duration_days is calculated correctly
def test_fetch_issues_hello_world_open_duration_correct():
    with test_vcr.use_cassette("hello_world_issues.yaml"):
        df = fetch_issues("octocat/Hello-World", max_issues=20)

        assert not df.empty
        assert {"created_at", "closed_at", "open_duration_days"}.issubset(df.columns)
        
        for issue in df.itertuples():
            dateCreated = issue.created_at
            dateClosed = issue.closed_at
            duration = issue.open_duration_days

            if dateClosed:
                date1 = datetime.fromisoformat(dateClosed)
                date2 = datetime.fromisoformat(dateCreated)
                assert duration == (date1 - date2).days
            else :
                assert pd.isna(duration)