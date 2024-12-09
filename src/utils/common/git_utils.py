from pathlib import Path
import subprocess

def git_clone(repo: str, temp_dir: Path):
    ''' Clones a git repository into a temporary directory'''
    try:
        print(f"Cloning {repo} into {temp_dir}")
        subprocess.run(["git", "clone", repo], cwd=temp_dir, check=True)
        print(f"Successfully cloned {repo}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository {repo}: {e}")