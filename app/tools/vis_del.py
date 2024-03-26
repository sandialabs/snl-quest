import os
import os.path
import sys
import shutil


def remove_viz_env(directory):
    """Remove the environment installed for behind the meter."""

    try:
        sys.stderr.write("Total complete: 40%\n")
        shutil.rmtree(directory)
        print(f"Environment '{directory}' successfully deleted.")
        sys.stderr.write("Total complete: 60%\n")
    except FileNotFoundError:
        print(f"Environement '{directory}' not found.")
    except Exception as e:
        print(f"Error deleting environment '{directory}': {e}")
        
def main():
    app_env = "env_viz"

    current_path = os.getcwd()
    
    parent_path = os.path.abspath(os.path.join(current_path, '..', '..'))
    
    app_env_path = os.path.join(parent_path, 'app_envs', app_env)

    sys.stderr.write("Total complete: 20%\n")
    remove_viz_env(app_env_path)
    
if __name__ == "__main__":
    main()
    sys.stderr.write("Total complete: 100%\n")


