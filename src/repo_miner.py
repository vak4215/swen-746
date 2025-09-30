import os
import argparse
import pandas as pd
from github import Github, Auth

"""
repo_miner.py

A command-line tool to:
  1) Fetch and normalize commit data from GitHub
  2) Fetch and normalize issue data from GitHub

Sub-commands:
  - fetch-commits
  - fetch-issues
"""

def fetch_commits(repo_name: str, max_commits: int = None) -> pd.DataFrame:
  """
  Fetch up to `max_commits` from the specified GitHub repository.
  Returns a DataFrame with columns: sha, author, email, date, message.
  """

  # 1) Read GitHub token from environment
  gitHubToken = os.environ.get("GITHUB_TOKEN")

  # 2) Initialize GitHub client and get the repo
  gitHubClient = Github(auth=Auth.Token(gitHubToken))
  repo = gitHubClient.get_repo(repo_name)
  
  # 3) Fetch commit objects (paginated by PyGitHub)
  commits = repo.get_commits()

  # 4) Normalize each commit into a record dict
  data = []

  numberOfCommitsChecked = 0

  if max_commits == None or max_commits > 0 :
    for commit in commits :
      commit_dict = {}
      commit_dict["sha"] = commit.sha
      commit_dict["author"] = commit.commit.author.name
      commit_dict["email"] = commit.commit.author.email
      commit_dict["date"] = commit.commit.author.date
      commit_dict["message"] = (commit.commit.message) .split('\n') [0]

      data.append(commit_dict)

      numberOfCommitsChecked += 1

      if numberOfCommitsChecked == max_commits :
        break

  # 5) Build DataFrame from records
  dataFrame = pd.DataFrame(data)

  return dataFrame

def fetch_issues(repo_name: str, state: str = "all", max_issues: int = None) -> pd.DataFrame:
  """
    Fetch up to `max_issues` from the specified GitHub repository (issues only).
    Returns a DataFrame with columns: id, number, title, user, state, created_at, closed_at, comments, open_duration_days.
  """

  # 1) Read GitHub token from environment
  gitHubToken = os.environ.get("GITHUB_TOKEN")

  # 2) Initialize GitHub client and get the repo
  gitHubClient = Github(auth=Auth.Token(gitHubToken))
  repo = gitHubClient.get_repo(repo_name)

  # 3) Fetch issues, filtered by state ('all', 'open', 'closed')
  issues = repo.get_issues(state=state)

  # 4) Normalize each issue (skip PRs)
  records = []
  numberOfIssuesAdded = 0   # count only actual issues, not PRs, so that the --max limit applies to issues only

  for idx, issue in enumerate(issues):
    if max_issues and numberOfIssuesAdded >= max_issues:
      break
      
    # Skip pull requests
    if issue.pull_request :
      continue

    # Append records
    created = issue.created_at
    closed = issue.closed_at if issue.closed_at else None
    duration = (closed - created).days if closed else None

    created = created.isoformat()
    closed = closed.isoformat() if closed else None

    issue_dict = {}
    issue_dict["id"] = issue.id
    issue_dict["number"] = issue.number
    issue_dict["title"] = issue.title
    issue_dict["user"] = issue.user.login
    issue_dict["state"] = issue.state
    issue_dict["created_at"] = created
    issue_dict["closed_at"] = closed
    issue_dict["comments"] = issue.comments
    issue_dict["open_duration_days"] = duration

    records.append(issue_dict)
    numberOfIssuesAdded += 1

  # 5) Build DataFrame
  dataFrame = pd.DataFrame(records)

  return dataFrame


def main():
  """
    Parse command-line arguments and dispatch to sub-commands.
  """

  parser = argparse.ArgumentParser(
    prog="repo_miner",
    description="Fetch GitHub commits/issues and summarize them"
  )
  subparsers = parser.add_subparsers(dest="command", required=True)

  # Sub-command: fetch-commits
  c1 = subparsers.add_parser("fetch-commits", help="Fetch commits and save to CSV")
  c1.add_argument("--repo", required=True, help="Repository in owner/repo format")
  c1.add_argument("--max",  type=int, dest="max_commits",
                  help="Max number of commits to fetch")
  c1.add_argument("--out",  required=True, help="Path to output commits CSV")

  # Sub-command: fetch-issues
  c2 = subparsers.add_parser("fetch-issues", help="Fetch issues and save to CSV")
  c2.add_argument("--repo",  required=True, help="Repository in owner/repo format")
  c2.add_argument("--state", choices=["all","open","closed"], default="all",
                  help="Filter issues by state")
  c2.add_argument("--max",   type=int, dest="max_issues",
                  help="Max number of issues to fetch")
  c2.add_argument("--out",   required=True, help="Path to output issues CSV")

  args = parser.parse_args()

  # Dispatch based on selected command
  if args.command == "fetch-commits":
    df = fetch_commits(args.repo, args.max_commits)
    df.to_csv(args.out, index=False)

    print(f"Saved {len(df)} commits to {args.out}")

  elif args.command == "fetch-issues":
    df = fetch_issues(args.repo, args.state, args.max_issues)
    df.to_csv(args.out, index=False)

    print(f"Saved {len(df)} issues to {args.out}")

if __name__ == "__main__":
  main()
