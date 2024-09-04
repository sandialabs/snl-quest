import json
import os
import requests

class BadgeDataUpdater:
    """
    A class to handle the updating of badge data for GitHub repository clones and downloads.

    This class is responsible for reading data from JSON files containing clone and download
    statistics, fetching the latest release information from a GitHub repository, and writing
    updated badge data to JSON files. These JSON files are typically used with shields.io badges
    to display the latest statistics on a repository's README or documentation.

    Attributes:
        repo_owner (str): The owner of the GitHub repository (username or organization name).
        repo_name (str): The name of the GitHub repository.
        access_token (str): GitHub personal access token with appropriate permissions.
        data_folder (str): Path to the folder where the clone and download data files are stored.
        shield_folder (str): Path to the folder where the output badge data files will be stored.
        clones_file_path (str): Path to the clones.json file containing clone statistics.
        downloads_file_path (str): Path to the downloads.json file containing download statistics.
        output_file_path (str): Path to the badge_data.json file for combined downloads and clones.
        release_output_file_path (str): Path to the release_badge_data.json file for the latest release.
        total_clones (int): Counter for the total number of clones.
        total_downloads (int): Counter for the total number of downloads.
        latest_release_tag (str): The tag name of the latest release in the GitHub repository.
    """

    def __init__(self, repo_owner, repo_name, access_token):
        """
        Initialize the BadgeDataUpdater class with repository details and GitHub access token.

        This method sets up the necessary file paths for reading and writing JSON data,
        ensures the required directories exist, and initializes counters for clone and download statistics.

        :param repo_owner: The owner of the GitHub repository (username or organization name).
        :type repo_owner: str
        :param repo_name: The name of the GitHub repository.
        :type repo_name: str
        :param access_token: GitHub personal access token with appropriate permissions.
        :type access_token: str
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.access_token = access_token

        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Define the paths to the JSON files relative to the script's directory
        self.data_folder = os.path.join(script_dir, 'data')
        self.shield_folder = os.path.join(script_dir, 'shields')
        self.clones_file_path = os.path.join(self.data_folder, 'clones.json')
        self.downloads_file_path = os.path.join(self.data_folder, 'downloads.json')
        self.output_file_path = os.path.join(self.shield_folder, 'badge_data.json')
        self.release_output_file_path = os.path.join(self.shield_folder, 'release_badge_data.json')

        # Ensure the data and shields folders exist
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.shield_folder, exist_ok=True)

        # Initialize counters
        self.total_clones = 0
        self.total_downloads = 0
        self.latest_release_tag = "unknown"

    def read_clones_data(self):
        """
        Read and sum the 'count' values from clones.json.

        This method reads clone data from the clones.json file and calculates the total
        number of clones by summing the 'count' values from each entry in the JSON file.
        If the file does not exist or an error occurs while reading, the total_clones
        counter remains zero, and the error is printed.
        """
        if os.path.exists(self.clones_file_path):
            try:
                with open(self.clones_file_path, 'r') as clones_file:
                    clones_data = json.load(clones_file)
                    self.total_clones = sum(item.get('count', 0) for item in clones_data)
            except Exception as e:
                print(f"Error reading {self.clones_file_path}: {e}")

    def read_downloads_data(self):
        """
        Read and sum the 'download_count' values from downloads.json.

        This method reads download data from the downloads.json file and calculates the
        total number of downloads by summing the 'download_count' values from each entry.
        It ensures that each asset is counted only once by keeping track of unique asset IDs.
        If the file does not exist, it creates an initial empty downloads.json file.
        """
        if not os.path.exists(self.downloads_file_path):
            initial_downloads_data = []
            try:
                with open(self.downloads_file_path, 'w') as downloads_file:
                    json.dump(initial_downloads_data, downloads_file)
                    print(f"Created initial {self.downloads_file_path}")
            except Exception as e:
                print(f"Error creating {self.downloads_file_path}: {e}")
        else:
            try:
                with open(self.downloads_file_path, 'r') as downloads_file:
                    downloads_data = json.load(downloads_file)

                    # Use a set to keep track of unique asset IDs to avoid double counting
                    seen_asset_ids = set()
                    for item in downloads_data:
                        asset_id = item.get('asset_id')
                        if asset_id not in seen_asset_ids:
                            seen_asset_ids.add(asset_id)
                            download_count = item.get('download_count', 0)
                            self.total_downloads += download_count
            except Exception as e:
                print(f"Error reading {self.downloads_file_path}: {e}")

    def fetch_latest_release(self):
        """
        Fetch the latest release information from the GitHub repository.

        This method makes an authenticated request to the GitHub API to fetch the latest
        release information for the specified repository. It updates the latest_release_tag
        attribute with the tag name of the latest release. If the request fails or if the
        response data is invalid, the latest_release_tag is set to "unknown".
        """
        GITHUB_API_URL = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        headers = {
            "Authorization": f"token {self.access_token}"
        }

        try:
            response = requests.get(GITHUB_API_URL, headers=headers)
            response.raise_for_status()
            latest_release = response.json()
            self.latest_release_tag = latest_release["tag_name"]
        except requests.exceptions.RequestException as e:
            self.latest_release_tag = "unknown"
            print(f"Error fetching latest release: {e}")
        except KeyError as e:
            self.latest_release_tag = "unknown"
            print(f"Key error in the response data: {e}")

    def write_badge_data(self):
        """
        Write the combined clones and downloads data to badge_data.json.

        This method writes the combined total of clones and downloads to the badge_data.json file
        in a format compatible with shields.io badges. It also writes the release-specific badge
        data to release_badge_data.json. If an error occurs during writing, it is printed.
        """
        combined_total = self.total_clones + self.total_downloads

        # Prepare the output data for the summed downloads and clones
        output_data = {
            "schemaVersion": 1,
            "label": "Downloads",
            "message": str(combined_total),
            "color": "blue"
        }

        # Prepare the output data for the latest release clones
        release_output_data = {
            "schemaVersion": 1,
            "label": f"{self.latest_release_tag} clones",
            "message": str(self.total_clones),
            "color": "purple"
        }

        # Write the output data to badge_data.json
        try:
            with open(self.output_file_path, 'w') as output_file:
                json.dump(output_data, output_file)
                print(f"Successfully wrote to {self.output_file_path}")
        except Exception as e:
            print(f"Error writing to {self.output_file_path}: {e}")

        # Write the release clones data to release_badge_data.json
        try:
            with open(self.release_output_file_path, 'w') as output_file:
                json.dump(release_output_data, output_file)
                print(f"Successfully wrote to {self.release_output_file_path}")
        except Exception as e:
            print(f"Error writing to {self.release_output_file_path}: {e}")

    def run(self):
        """
        Execute the full process of updating badge data.

        This method coordinates the entire process of reading clone and download data,
        fetching the latest release information, and writing the updated badge data to JSON files.
        """
        self.read_clones_data()
        self.read_downloads_data()
        self.fetch_latest_release()
        self.write_badge_data()

def main():
    """
    Main function to execute the badge data update process.

    This function initializes the BadgeDataUpdater class with repository details and access token,
    and then runs the badge update process.
    """
    repo_owner = "sandialabs"
    repo_name = "snl-quest"
    access_token = os.getenv('QUEST_TOKEN')

    # Instantiate the BadgeDataUpdater class and run the process
    updater = BadgeDataUpdater(repo_owner, repo_name, access_token)
    updater.run()

# Entry point of the script
if __name__ == "__main__":
    main()
