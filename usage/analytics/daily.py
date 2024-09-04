import requests
import logging
import json
import os
from datetime import datetime, timedelta
import traceback

# Configure logging to display information level logs with timestamps
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger()

class DailyUpdate:
    """
    A class to handle the daily retrieval and storage of GitHub repository statistics, 
    including download statistics and traffic data.

    This class provides methods to fetch download statistics from the releases of a GitHub 
    repository and to fetch traffic data such as clones. The retrieved data is then saved 
    to JSON files, where it can be aggregated with previous data for long-term tracking.
    """

    def __init__(self, repo_owner, repo_name, access_token):
        """
        Initialize the DailyUpdate class with repository details and GitHub access token.

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

    def get_github_downloads(self):
        """
        Fetch download statistics for all releases in the GitHub repository.

        :return: A list of dictionaries, each containing download statistics for an asset.
        :rtype: list
        :raises Exception: If the request to the GitHub API fails, an exception is raised with 
                           the status code and error message.
        """
        logger.info("Starting to fetch download statistics from GitHub.")
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases"
        headers = {"Authorization": f"token {self.access_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Failed to fetch data: {response.status_code} - {response.text}")
            raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

        releases = response.json()
        download_stats = []

        # Extract download statistics for each asset in every release
        for release in releases:
            for asset in release['assets']:
                download_stats.append({
                    "release_id": release['id'],
                    "release_name": release['name'],
                    "asset_id": asset['id'],
                    "asset_name": asset['name'],
                    "download_count": asset['download_count'],
                    "created_at": asset['created_at'],
                    "updated_at": asset['updated_at']
                })

        logger.info(f"Fetched download statistics for {len(releases)} releases.")
        return download_stats

    def get_repo_traffic(self):
        """
        Fetch repository traffic data, specifically clones, from the GitHub API.

        :return: A list of dictionaries, each containing the timestamp and clone data.
        :rtype: list
        :raises Exception: If the request to the GitHub API fails, an exception is raised with 
                           the status code and error message.
        """
        logger.info("Starting to fetch repository traffic data from GitHub.")
        url_clones = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/traffic/clones"
        headers = {"Authorization": f"token {self.access_token}"}

        response_clones = requests.get(url_clones, headers=headers)

        if response_clones.status_code != 200:
            logger.error(f"Failed to fetch clones data: {response_clones.status_code} - {response_clones.text}")
            raise Exception(f"Failed to fetch clones data: {response_clones.status_code} - {response_clones.text}")

        clones_data = response_clones.json().get('clones', [])
        logger.info(f"Fetched clones data: {clones_data}")
        return clones_data

    def save_to_json(self, data, filename, key=None):
        """
        Save the given data to a JSON file, merging it with existing data if the file already exists.

        :param data: The data to be saved, typically a list of dictionaries.
        :type data: list
        :param filename: The name of the JSON file where the data will be saved.
        :type filename: str
        :param key: The key used to identify unique entries in the data (e.g., 'asset_id' for downloads).
                    If provided, the data will be merged based on this key.
        :type key: str or None
        """
        # Ensure the 'data' directory exists
        if not os.path.exists('data'):
            os.makedirs('data')

        file_path = os.path.join('data', filename)

        # Load existing data if the file exists
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
                    logger.info(f"Existing data from {filename}: {existing_data[:2]}...")
            except (json.JSONDecodeError, ValueError):
                logger.error(f"Error reading {filename}, initializing as empty list.")
                existing_data = []
        else:
            existing_data = []

        # Merge new data with existing data
        if key:
            # Update existing records based on a unique key (e.g., for downloads)
            data_dict = {item[key]: item for item in data}
            existing_data_dict = {item[key]: item for item in existing_data}
            existing_data_dict.update(data_dict)
            merged_data = list(existing_data_dict.values())
        else:
            # Merge by updating entries with matching timestamps (e.g., for clones)
            existing_data_dict = {entry['timestamp']: entry for entry in existing_data}
            for entry in data:
                existing_data_dict[entry['timestamp']] = entry
            merged_data = list(existing_data_dict.values())

        logger.info(f"Saving data to {filename}: {merged_data[:2]}...")

        # Save the merged data back to the JSON file
        with open(file_path, 'w') as f:
            json.dump(merged_data, f, indent=4)

    def run(self):
        """
        Run the daily update process to fetch, aggregate, and save GitHub download statistics and traffic data.

        This method coordinates the entire process of retrieving, aggregating, and storing GitHub 
        download statistics and traffic data. It logs the progress and handles any exceptions that occur 
        during the process.

        Steps performed:
        1. Fetch download statistics and save them to a JSON file.
        2. Fetch repository traffic data and save it to a separate JSON file.
        3. Log the outcome of the script's execution.
        """
        try:
            # Fetch and save download statistics
            download_stats = self.get_github_downloads()
            self.save_to_json(download_stats, "downloads.json", key="asset_id")

            # Fetch and save repository traffic data
            clones_data = self.get_repo_traffic()
            self.save_to_json(clones_data, "clones.json")

            logger.info("Script ran successfully.")
        except Exception as e:
            # Log any errors and their traceback
            logger.error(f"Error occurred: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")

def main():
    """
    Main function to execute the daily update process.

    This function initializes the DailyUpdate class and runs the daily update process.
    """
    repo_owner = "sandialabs"
    repo_name = "snl-quest"
    access_token = os.getenv("QUEST_TOKEN")

    # Instantiate the DailyUpdate class and run the process
    du = DailyUpdate(repo_owner, repo_name, access_token)
    du.run()

# Entry point of the script
if __name__ == "__main__":
    main()
