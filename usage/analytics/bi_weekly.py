import requests
import logging
import json
import os
from datetime import datetime, timedelta

# Configure logging to display information level logs
logging.basicConfig(level=logging.INFO)

class BiWeeklyUpdate:
    """
    A class to handle the bi-weekly retrieval, aggregation, and storage of GitHub repository traffic data.

    This class provides methods to fetch traffic data from a GitHub repository, such as popular referrers 
    and paths. The retrieved data is then aggregated with existing data and saved in JSON format for 
    long-term tracking.
    """

    def __init__(self, repo_owner, repo_name, access_token):
        """
        Initialize the BiWeeklyUpdate class with repository details and GitHub access token.

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

    def get_github_data(self, data_type):
        """
        Fetch GitHub traffic data for a specific repository.

        This method interacts with the GitHub REST API to retrieve traffic data related to
        a specific repository. The data can include information such as the most popular
        referrers or the most popular paths.

        :param data_type: The specific type of traffic data to retrieve (e.g., "popular/referrers", "popular/paths").
        :type data_type: str

        :return: A dictionary or list (depending on the API response) containing the requested
                traffic data in JSON format. The structure of the returned data depends on the
                specific `data_type` requested.
        :rtype: dict or list

        :raises Exception: Raises an exception if the API request fails, providing the HTTP
                        status code returned by the GitHub API for diagnostic purposes.
        """
        # Construct the URL to access the GitHub API endpoint for the specified traffic data type
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/traffic/{data_type}"

        # Set up the request headers including the authorization token
        headers = {"Authorization": f"token {self.access_token}"}

        # Send the GET request to the GitHub API
        response = requests.get(url, headers=headers)

        # Check if the request was successful (status code 200 indicates success)
        if response.status_code != 200:
            # If not, raise an exception with the status code
            raise Exception(f"Failed to fetch {data_type} data: {response.status_code}")

        # Return the response data as a JSON object
        return response.json()

    def load_json(self, filename):
        """
        Load data from a JSON file if it exists, returning an empty list otherwise.

        This utility function attempts to open a specified JSON file and load its contents
        into a Python list. The function is designed to handle cases where the file may not
        exist by returning an empty list if the file cannot be found.

        :param filename: The path to the JSON file that needs to be loaded.
        :type filename: str

        :return: The contents of the JSON file loaded into a Python list. If the file does not
                exist, an empty list is returned.
        :rtype: list
        """
        # Check if the specified file exists at the given path
        if os.path.exists(filename):
            # If the file exists, open it and load the JSON data
            with open(filename, 'r') as f:
                return json.load(f)

        # If the file does not exist, return an empty list
        return []

    def aggregate_data(self, new_data, existing_data, key_field, count_field, unique_field):
        """
        Aggregate new traffic data with previously stored data based on a key identifier.

        This method combines new traffic data with existing data by matching entries based on 
        a common key field. When a match is found between new and existing entries, their 
        respective counts are aggregated by summing them up.

        :param new_data: A list of dictionaries representing the newly retrieved traffic data.
                        Each dictionary contains fields that correspond to the traffic metrics
                        provided by GitHub.
        :type new_data: list

        :param existing_data: A list of dictionaries representing the previously aggregated
                            traffic data. This data is typically loaded from a JSON file.
        :type existing_data: list

        :param key_field: The field in each data dictionary that serves as the unique identifier
                        for matching entries (e.g., "referrer" for referrer data, "path" for
                        path data).
        :type key_field: str

        :param count_field: The field that tracks the total number of occurrences (e.g., the
                            number of visits or clicks).
        :type count_field: str

        :param unique_field: The field that tracks the number of unique occurrences (e.g., unique
                            visitors).
        :type unique_field: str

        :return: A list of dictionaries representing the aggregated traffic data, combining the
                new data with the previously existing data.
        :rtype: list
        """
        # Convert the existing data list into a dictionary for easy lookup by key_field
        existing_dict = {entry[key_field]: entry for entry in existing_data}

        # Iterate over each entry in the new data
        for entry in new_data:
            key = entry[key_field]  # Identify the key for the current entry

            # If the key already exists in the existing data dictionary
            if key in existing_dict:
                # Aggregate the counts and unique values by adding the new data to the existing data
                existing_dict[key][count_field] += entry[count_field]
                existing_dict[key][unique_field] += entry[unique_field]
            else:
                # If the key is not present in the existing data, add it as a new entry
                existing_dict[key] = {
                    key_field: key,
                    count_field: entry[count_field],
                    unique_field: entry[unique_field]
                }

        # Convert the dictionary back into a list for consistent output format
        return list(existing_dict.values())

    def save_aggregated_data(self, data, filename):
        """
        Save the aggregated data to a JSON file, creating directories as needed.

        This method writes the provided list of dictionaries (representing aggregated
        traffic data) to a specified JSON file. If the directories leading to the file
        do not exist, they are created automatically.

        :param data: The aggregated data that needs to be saved.
        :type data: list

        :param filename: The path to the JSON file where the aggregated data will be stored.
        :type filename: str
        """
        # Ensure that the directory structure exists by creating directories as necessary
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Open the file and write the aggregated data to it in JSON format with indentation
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def run(self):
        """
        Run the bi-weekly update process to fetch, aggregate, and save GitHub traffic data.

        This method coordinates the process of retrieving, aggregating, and storing
        GitHub traffic data. It retrieves popular referrer and path data from the GitHub API,
        aggregates this data with any existing data, and saves the updated data back to JSON files.

        :raises Exception: Logs an error if any part of the data retrieval, aggregation, or
                           saving process fails, providing details for debugging.
        """
        try:
            # Retrieve referrer data from the GitHub API
            referrers_response = self.get_github_data("popular/referrers")
            referrers_data = referrers_response if isinstance(referrers_response, list) else referrers_response.get('referrers', [])

            # Retrieve path data from the GitHub API
            paths_response = self.get_github_data("popular/paths")
            paths_data = paths_response if isinstance(paths_response, list) else paths_response.get('paths', [])

            # Load previously aggregated referrer data from a JSON file
            aggregated_referrers = self.load_json("data/aggregated_referrers.json")
            # Load previously aggregated path data from a JSON file
            aggregated_paths = self.load_json("data/aggregated_paths.json")

            # Aggregate the newly retrieved referrer data with existing data
            aggregated_referrers = self.aggregate_data(referrers_data, aggregated_referrers, "referrer", "count", "uniques")
            # Aggregate the newly retrieved path data with existing data
            aggregated_paths = self.aggregate_data(paths_data, aggregated_paths, "path", "count", "uniques")

            # Save the updated aggregated referrer data to a JSON file
            self.save_aggregated_data(aggregated_referrers, "data/aggregated_referrers.json")
            # Save the updated aggregated path data to a JSON file
            self.save_aggregated_data(aggregated_paths, "data/aggregated_paths.json")

            # Log a success message
            logging.info("Bi-weekly update script ran successfully.")
        except Exception as e:
            # Log any errors encountered during the process
            logging.error(f"Error occurred: {e}")

def main():
    """
    Main function to execute the bi-weekly update process.

    This function initializes the BiWeeklyUpdate class and runs the bi-weekly update process.
    """
    repo_owner = "sandialabs"
    repo_name = "snl-quest"
    access_token = os.getenv('GITHUB_TOKEN')

    # Instantiate the BiWeeklyUpdate class and run the process
    biweekly_update = BiWeeklyUpdate(repo_owner, repo_name, access_token)
    biweekly_update.run()

# Entry point of the script
if __name__ == "__main__":
    main()
