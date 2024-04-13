import os
import os.path
import venv
import sys
import subprocess


def energy_env():
    """Install the environment for the equity app."""

#      Directory
    venv_name = "env_energy"
    module_dir = os.path.dirname(__file__)
    venv_dir = os.path.abspath(os.path.join(module_dir, '..', '..', '..', 'app_envs', venv_name))
    if not os.path.exists(venv_dir):
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            
if __name__ == "__main__":
    
    energy_env()
