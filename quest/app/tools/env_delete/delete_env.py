import sys
import shutil
import os

def remove_env(directory):
    """Remove the environment installed for behind the meter."""

    try:
        shutil.rmtree(directory)
        print(f"Environment '{directory}' successfully deleted.")
    except FileNotFoundError:
        print(f"Environment '{directory}' not found.")
    except Exception as e:
        print(f"Error deleting environment '{directory}': {e}")
        # Attempt a platform-independent fallback
        try:
            if os.name == 'nt':  # Windows
                os.system(f"rmdir /s /q {directory}")
            else:  # macOS and Linux
                os.system(f"rm -rf {directory}")
            print(f"Environment '{directory}' successfully deleted with os.")
        except Exception as e:
            print(f"Error deleting environment '{directory}' with os: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: script.py <directory_to_remove>")

    directory = sys.argv[1]
    remove_env(directory)
