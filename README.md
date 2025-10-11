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
- The src/repo_miner.py file now contains an implementation of the fetch_commits(repo_full_name, max_commits) -> pd.DataFrame function which :
    - Reads GITHUB_TOKEN from the environment.
    - Pages through repo.get_commits().
    - Stops after max_commits if provided.
    - Returns a DataFrame with columns: sha, author, email, date (ISO-8601), message (first line)
- The src/repo_miner.py file now contains an implementation of the main() function
- Pytest cases for the fetch_commits function using global dummy placeholders
- Pytest cases for the fetch_commits function using vcrpy to access the real repo octocat/Hello-World


The src/repo_miner.py file is accessible via CLI (in the following command, repo_miner is under src at the project root):

    python -m src.repo_miner fetch-commits --repo owner/repo [--max 100] --out src/data/commits.csv


Example command :

    python -m src.repo_miner fetch-commits --repo vak4215/swen-746 --out src/data/commits.csv

    python -m src.repo_miner fetch-commits --repo octocat/Hello-World --out src/data/hello_world_commits.csv



## Isuse Fetcher (Tag rm2 on 09/30)
The project now includes the following :
- The src/repo_miner.py file now contains an implementation of the fetch_issues(repo_name, state, max_issues) -> pd.DataFrame function which :
    - Reads GITHUB_TOKEN from the environment.
    - Pages through repo.get_issues().
    - Skips over pull requests.
    - Normalizes dates as ISO-8601 strings.
    - Adds a new column open_duration_days = days between created_at and closed_at (or None).
    - Stops after max_issues if provided.
    - Returns a DataFrame with columns: id, number, title, user, state, created_at, closed_at, comments, open_duration_days .
- Pytest cases for the fetch_issues function using vcrpy to access the real repo octocat/Hello-World


The new method in src/repo_miner.py file is accessible via CLI (in the following command, repo_miner is under src at the project root):

    python -m src.repo_miner fetch-issues --repo owner/repo [--state all|open|closed] [--max 50] --out issues.csv


Example command :

    python -m src.repo_miner fetch-issues --repo octocat/Hello-World --max 20 --out src/data/hello_world_issues.csv



## Data Integration & Summary (Tag rm3 on 10/10)
The project now includes the following :
- The src/repo_miner.py file now contains an implementation of the merge_and_summarize(commits_df, issues_df) -> None function which :
    - Joins commits and issues on date (e.g., by day or week).
    - Computes and prints:
        Top 5 committers by count.
        Issue close rate (closed / total).
        Average issue open duration.
- Pytest cases for the merge_and_summarize function using monkeypatch to mimic a real world repo


The new method in src/repo_miner.py file is accessible via CLI (in the following command, repo_miner is under src at the project root):

    python -m src.repo_miner summarize --commits commits.csv --issues issues.csv


Example command :

    python -m src.repo_miner summarize --commits src/data/hello_world_commits.csv --issues src/data/hello_world_issues.csv