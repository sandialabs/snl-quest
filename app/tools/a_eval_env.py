import os
import os.path
import venv
import sys
import subprocess


def eval_env():
    """Install the environment for behind the meter."""

#      Directory
    venv_name = "env_eval"
    sys.stderr.write("Total complete: 5%\n")
    venv_dir = os.path.abspath(os.path.join('..', '..', 'app_envs', venv_name))
    if not os.path.exists(venv_dir):
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
if __name__ == "__main__":
    
    eval_env()
