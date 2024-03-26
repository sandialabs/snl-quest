import os
import os.path
import venv
import sys
import subprocess


def micro_env():
    """Install the environment for microgrid app."""

#      Directory
    venv_name = "env_micro"
    sys.stderr.write("Total complete: 5%\n")
    venv_dir = os.path.abspath(os.path.join('..', '..', 'app_envs', venv_name))
    if not os.path.exists(venv_dir):
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    
    micro_env()
