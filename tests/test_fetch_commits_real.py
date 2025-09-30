import vcr
from src.repo_miner import fetch_commits

"""
    tests/test_fetch_commits_real.py

    A set of tests for the repo_miner class that utilize vcrpy to hit real APIs
"""

# --- Set Up the VCR --- 

test_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes",
    record_mode="new_episodes",
    match_on=["uri", "method"],
    filter_headers=["authorization"]
)

# --- Test against the well-known small repo octocat/Hello-World

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