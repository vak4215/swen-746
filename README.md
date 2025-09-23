# Class Project : SWEN 746

## Project Setup (Tag rm0 on 09/17)
The project skeleton includes the following :
- a Python 3 virtual environment initialized on my local machine
- a requirements.txt file with the following entries : PyGithub; pandas; pytest
- a src/repo_miner.py file with an empty main() and an if __name__ == "__main__": main() stub
- a top‐level README.md stub
- a GitHub Actions CI workflow that runs pytest

## Commit Fetcher (Tag rm1 on 09/17)
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
