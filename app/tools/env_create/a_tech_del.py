import os
import os.path
import sys
import shutil


def remove_tech_env(directory):
    """Remove the environment installed for tech selection."""

    try:

        shutil.rmtree(directory)
        print(f"Environment '{directory}' successfully deleted.")

    except FileNotFoundError:
        print(f"Environement '{directory}' not found.")
    except Exception as e:
        print(f"Error deleting environment '{directory}': {e}")
        
def main():
    app_env = "env_tech"

    # current_path = os.getcwd()
    
    # parent_path = os.path.abspath(os.path.join(current_path, '..', '..'))
    
    # app_env_path = os.path.join(parent_path, 'app_envs', app_env)
    module_dir = os.path.dirname(__file__)
    app_env_path = os.path.abspath(os.path.join(module_dir, '..', '..', '..', 'app_envs', app_env))

    remove_tech_env(app_env_path)
    
if __name__ == "__main__":
    main()



