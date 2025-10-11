# tests/test_repo_summarize.py

import os
import pandas as pd
import pytest
from datetime import datetime, timedelta
from src.repo_miner import fetch_commits, fetch_issues, merge_and_summarize
import src.repo_miner as rm

"""
    A set of tests for the repo_miner class that utilize monkeypath to mimic API calls/results
"""

# --- Helpers for dummy GitHub API objects ---

class DummyAuthor:
    def __init__(self, name, email, date):
        self.name = name
        self.email = email
        self.date = date

class DummyCommitCommit:
    def __init__(self, author, message):
        self.author = author
        self.message = message

class DummyCommit:
    def __init__(self, sha, author, email, date, message):
        self.sha = sha
        self.commit = DummyCommitCommit(DummyAuthor(author, email, date), message)

class DummyUser:
    def __init__(self, login):
        self.login = login

class DummyIssue:
    def __init__(self, id_, number, title, user, state, created_at, closed_at, comments, is_pr=False):
        self.id = id_
        self.number = number
        self.title = title
        self.user = DummyUser(user)
        self.state = state
        self.created_at = created_at
        self.closed_at = closed_at
        self.comments = comments

        # attribute only on pull requests
        self.pull_request = DummyUser("pr") if is_pr else None

class DummyRepo:
    def __init__(self, commits, issues):
        self._commits = commits
        self._issues = issues

    def get_commits(self):
        return self._commits

    def get_issues(self, state="all"):
        # filter by state
        if state == "all":
            return self._issues
        
        return [i for i in self._issues if i.state == state]

class DummyGithub:
    def __init__(self, token):
        assert token == "fake-token"

    def get_repo(self, repo_name):
        # ignore repo_name; return repo set in test fixture
        return self._repo

@pytest.fixture(autouse=True)
def patch_env_and_github(monkeypatch):
    # Set fake token
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")

    # Patch Github class
    monkeypatch.setattr("src.repo_miner.Github", lambda *args, **kwargs: gh_instance)
    yield

# Helper global placeholder
gh_instance = DummyGithub("fake-token")


# --- Tests for fetch_commits ---

# Basic test case for fetch_commits
def test_fetch_commits_basic(monkeypatch):
    # Setup dummy commits
    now = datetime.now()

    commits = [
        DummyCommit("sha1", "Alice", "a@example.com", now, "Initial commit\nDetails"),
        DummyCommit("sha2", "Bob", "b@example.com", now - timedelta(days=1), "Bug fix")
    ]

    gh_instance._repo = DummyRepo(commits, [])
    df = fetch_commits("any/repo")

    assert list(df.columns) == ["sha", "author", "email", "date", "message"]
    assert len(df) == 2
    assert df.iloc[0]["message"] == "Initial commit"

# Test that fetch_commits respects the max_commits limit.
def test_fetch_commits_limit(monkeypatch):
    # Setup dummy placeholders
    now = datetime.now()

    # Set up more commits than max_commits
    commits = [
        DummyCommit("sha1", "Alice", "a@example.com", now, "Initial commit\nDetails"),
        DummyCommit("sha2", "Bob", "b@example.com", now - timedelta(days=1), "Bug fix")
    ]

    gh_instance._repo = DummyRepo(commits, [])
    df = fetch_commits("any/repo", 1)

    assert list(df.columns) == ["sha", "author", "email", "date", "message"]
    assert len(df) == 1
    assert df.iloc[0]["message"] == "Initial commit"

# Test that fetch_commits returns empty DataFrame when no commits exist.
def test_fetch_commits_empty(monkeypatch):
    # Setup dummy placeholders
    gh_instance._repo = DummyRepo([], [])
    df = fetch_commits("any/repo")

    assert len(df) == 0


# --- Tests for fetch_issues ---

# Basic test case for fetch_issues
def test_fetch_issues_basic(monkeypatch):
    now = datetime.now()

    issues = [
        DummyIssue(1, 101, "Issue A", "alice", "open", now, None, 0),
        DummyIssue(2, 102, "Issue B", "bob", "closed", now - timedelta(days=2), now, 2)
    ]

    gh_instance._repo = DummyRepo([], issues)
    df = fetch_issues("any/repo", state="all")

    assert {"id", "number", "title", "user", "state", "created_at", "closed_at", "comments"}.issubset(df.columns)
    assert len(df) == 2

    # Check date normalization
    assert df.iloc[1]["closed_at"].endswith("Z") or isinstance(df.iloc[1]["closed_at"], str)

# Test that fetch_issues doesn't return any prs
def test_fetch_issues_excludes_prs(monkeypatch):
    now = datetime.now()

    issues = [
        DummyIssue(1, 101, "Issue", "alice", "open", now, None, 0),
        DummyIssue(3, 201, "PR", "bob", "closed", now, now, 1, is_pr=True)
    ]

    gh_instance._repo = DummyRepo([], issues)
    df = fetch_issues("any/repo")

    assert len(df) == 1
    assert df.iloc[0]["title"] == "Issue"

# Test that fetch_issues respects limit and state resitrictions
def test_fetch_issues_limit_and_state(monkeypatch):
    now = datetime.now()
    issues = [
        DummyIssue(i, 100+i, f"Issue {i}", "user", "open", now, None, 0) for i in range(10)
    ]
    gh_instance._repo = DummyRepo([], issues)
    df = fetch_issues("any/repo", state="open", max_issues=5)
    assert len(df) == 5


# --- Tests for merge_and_summarize_output ---

# Basic test case for merge_and_summarize_output
def test_merge_and_summarize_output(capsys):
    # Prepare test DataFrames
    df_commits = pd.DataFrame({
        "sha": ["a", "b", "c", "d"],
        "author": ["X", "Y", "X", "Z"],
        "email": ["x@e", "y@e", "x@e", "z@e"],
        "date": ["2025-01-01T00:00:00", "2025-01-01T01:00:00",
                 "2025-01-02T00:00:00", "2025-01-02T01:00:00"],
        "message": ["m1", "m2", "m3", "m4"]
    })

    df_issues = pd.DataFrame({
        "id": [1,2,3],
        "number": [101,102,103],
        "title": ["I1","I2","I3"],
        "user": ["u1","u2","u3"],
        "state": ["closed","open","closed"],
        "created_at": ["2025-01-01T00:00:00","2025-01-01T02:00:00","2025-01-02T00:00:00"],
        "closed_at": ["2025-01-01T12:00:00",None,"2025-01-02T12:00:00"],
        "comments": [0,1,2]
    })

    # Run summarize
    merge_and_summarize(df_commits, df_issues)
    captured = capsys.readouterr().out

    # Check top committer
    assert "Top 5 Committers" in captured
    assert "X: 2 commits" in captured

    # Check close rate
    assert "Issue Close Rate : 0.67" in captured

    # Check avg open duration
    assert "Average Open Duration for Closed Issues : " in captured

# Test that open_duration_days is calculated correctly
def test_merge_and_summarize_duration(capsys):
    # Prepare test DataFrames
    df_commits = pd.DataFrame({
        "sha": ["a", "b", "c", "d"],
        "author": ["X", "Y", "X", "Z"],
        "email": ["x@e", "y@e", "x@e", "z@e"],
        "date": ["2025-01-01T00:00:00", "2025-01-01T01:00:00",
                 "2025-01-02T00:00:00", "2025-01-02T01:00:00"],
        "message": ["m1", "m2", "m3", "m4"]
    })

    df_issues = pd.DataFrame({
        "id": [1,2,3],
        "number": [101,102,103],
        "title": ["I1","I2","I3"],
        "user": ["u1","u2","u3"],
        "state": ["closed","open","closed"],
        "created_at": ["2025-01-01T00:00:00","2025-01-01T02:00:00","2025-01-02T00:00:00"],
        "closed_at": ["2025-01-03T00:00:00", None, "2025-01-06T00:00:00"],
        "comments": [0,1,2]
    })

    # Run summarize
    merge_and_summarize(df_commits, df_issues)
    captured = capsys.readouterr().out

    # Check avg open duration (2 and 4 days -> average 3.0)
    assert "Average Open Duration for Closed Issues : 3.0" in captured

# Test that open_duration_days is calculated correctly
def test_merge_and_summarize_duration(capsys):
    # Prepare test DataFrames
    df_commits = pd.DataFrame({
        "sha": ["a", "b", "c", "d"],
        "author": ["X", "Y", "X", "Z"],
        "email": ["x@e", "y@e", "x@e", "z@e"],
        "date": ["2025-01-01T00:00:00", "2025-01-01T01:00:00",
                 "2025-01-02T00:00:00", "2025-01-02T01:00:00"],
        "message": ["m1", "m2", "m3", "m4"]
    })

    df_issues = pd.DataFrame({
        "id": [1,2,3],
        "number": [101,102,103],
        "title": ["I1","I2","I3"],
        "user": ["u1","u2","u3"],
        "state": ["closed","open","closed"],
        "created_at": ["2025-01-01T00:00:00","2025-01-01T02:00:00","2025-01-02T00:00:00"],
        "closed_at": ["2025-01-03T00:00:00", None, "2025-01-06T00:00:00"],
        "comments": [0,1,2]
    })

    # Run summarize
    merge_and_summarize(df_commits, df_issues)
    captured = capsys.readouterr().out

    # Count up the number of top committers
    lines = captured.split("\n")
    commits = []
    is_committer = False

    for line in lines :
        if "Top 5 Committers" in line :
            is_committer = True
        elif "Issue Close Rate" in line :
            is_committer = False
        elif is_committer :
            commits.append(line)

    # Check that number of committers is less than 5
    assert len(commits) == 4