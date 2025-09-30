# Class Project : SWEN 746

## Project Setup (Tag rm0 on 09/17)
The project skeleton includes the following :
- a Python 3 virtual environment initialized on my local machine
- a requirements.txt file with the following entries : PyGithub; pandas; pytest
- a src/repo_miner.py file with an empty main() and an if __name__ == "__main__": main() stub
- a top‐level README.md stub
- a GitHub Actions CI workflow that runs pytest

## Commit Fetcher (Tag rm1 on 09/22)
The project now includes the following :
- The src/repo_miner.py file now contains an implementation of the fetch_commits(repo_full_name: str, max_commits: int=None) -> pd.DataFrame function which :
    - Reads GITHUB_TOKEN from the environment.
    - Pages through repo.get_commits().
    - Stops after max_commits if provided.
    - Returns a DataFrame with columns: sha, author, email, date (ISO-8601), message (first line)
- The src/repo_miner.py file now contains an implementation of the main() function
- Pytest cases for the fetch_commits function using global dummy placeholders
- Pytest cases for the fetch_commits function using vcrpy to access the real repo octocat/Hello-World

The src/repo_miner.py file is accessible via CLI (in the following command, repo_miner is under src at the project root):
    python -m src.repo_miner fetch-commits --repo owner/repo [--max 100] --out src/output/commits.csv

Example command :
    python -m src.repo_miner fetch-commits --repo vak4215/swen-746 --out src/output/commits.csv
    python -m src.repo_miner fetch-commits --repo octocat/Hello-World --out src/output/hello_world_commits.csv

## Isuse Fetcher (Tag rm2 on 09/30)
The project now includes the following :
- The src/repo_miner.py file now contains an implementation of the etch_issues(repo_name: str, state: str = "all", max_issues: int = None) -> pd.DataFrame function which :
    - Reads GITHUB_TOKEN from the environment.
    - Pages through repo.get_issues().
    - Skips over pull requests.
    - Normalizes dates as ISO-8601 strings.
    - Adds a new column open_duration_days = days between created_at and closed_at (or None).
    - Stops after max_issues if provided.
    - Returns a DataFrame with columns: id, number, title, user, state, created_at, closed_at, comments, open_duration_days
- Pytest cases for the fetch_issues function using vcrpy to access the real repo octocat/Hello-World

The src/repo_miner.py file is accessible via CLI (in the following command, repo_miner is under src at the project root):
    python -m src.repo_miner fetch-issues --repo owner/repo [--state all|open|closed] [--max 50] --out issues.csv

Example command :
    python -m src.repo_miner fetch-issues --repo octocat/Hello-World --max 20 --out src/output/hello_world_issues.csv
