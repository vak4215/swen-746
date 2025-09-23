#!/usr/bin/env python3
"""
repo_miner.py

A command-line tool to:
  1) Fetch and normalize commit data from GitHub

Sub-commands:
  - fetch-commits
"""

import os
import argparse
import pandas as pd
from github import Github, Auth

def fetch_commits(repo_name: str, max_commits: int = None) -> pd.DataFrame:
  """
  Fetch up to `max_commits` from the specified GitHub repository.
  Returns a DataFrame with columns: sha, author, email, date, message.
  """

  # 1) Read GitHub token from environment
  gitHubToken = os.environ.get("GITHUB_TOKEN")

  # temp. debugging only
  print("GITHUB_TOKEN is set:", bool(os.environ.get("GITHUB_TOKEN")))

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

  args = parser.parse_args()

  # Dispatch based on selected command
  if args.command == "fetch-commits":
    df = fetch_commits(args.repo, args.max_commits)
    df.to_csv(args.out, index=False)
    print(f"Saved {len(df)} commits to {args.out}")

if __name__ == "__main__":
  main()
