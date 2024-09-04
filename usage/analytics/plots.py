import os
import json
import logging
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger()

class DataVisualizer:
    """
    A class to handle the loading, processing, and visualization of GitHub repository data.

    This class handles loading data from JSON files, generating plots and markdown tables,
    and saving the results to specified directories. It processes data related to clones, referrers,
    paths, and downloads, and generates a plot for clones over time.

    Attributes:
        root_dir (str): The directory of the current script.
        data_dir (str): The directory where the data JSON files are located.
        output_dir (str): The directory where output plots and markdown tables will be saved.
    """

    def __init__(self):
        """
        Initialize the DataVisualizer class.

        This constructor sets up the directory paths for loading data and saving outputs.
        It also ensures that the output directory exists.
        """
        # Set up directory paths
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.root_dir, 'data')
        self.output_dir = os.path.join(self.root_dir, 'plots')

        # Ensure the output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def load_json_data(self, filename):
        """
        Load data from a JSON file.

        This function loads data from a specified JSON file located in the data directory.
        If the file is not found or there's an error parsing the JSON, it logs an error
        and returns an empty list.

        :param filename: The name of the JSON file to load.
        :type filename: str
        :return: The data loaded from the JSON file, or an empty list if there's an error.
        :rtype: list
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                logger.info(f"Loaded data from {filename}: {data[:2]}...")  # Log the first two records for debugging
                return data
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            return []
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from file: {filename}")
            return []

    def save_clones_plot(self, clones):
        """
        Generate and save a plot of clones over time.

        This function generates a line plot of total and unique clones over time, based
        on data loaded from the clones.json file. The resulting plot is saved as a PNG file.

        :param clones: A list of dictionaries containing clone data.
        :type clones: list
        """
        if not clones:
            logger.warning("No clones data available to plot")
            return

        # Convert the list of dictionaries to a pandas DataFrame
        clones_df = pd.DataFrame(clones)

        # Convert timestamp to datetime and set it as the index
        clones_df['timestamp'] = pd.to_datetime(clones_df['timestamp'])
        clones_df.set_index('timestamp', inplace=True)

        # Remove duplicate entries by summing counts and uniques for each day
        clones_df = clones_df.resample('D').sum()

        # Generate the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(clones_df.index, clones_df['count'], marker='o', label='Total Clones')
        ax.plot(clones_df.index, clones_df['uniques'], marker='o', label='Unique Clones')
        ax.set_title('Clones Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Clones')
        ax.legend()
        ax.tick_params(axis='x', rotation=45)
        
        # Adjust margins to reduce white space
        fig.subplots_adjust(bottom=0.2, top=0.9)
        
        # Save the plot as a PNG file
        plt.savefig(os.path.join(self.output_dir, 'clones_plot.png'), bbox_inches='tight', pad_inches=0.01)
        plt.close()

    def add_totals_row(self, df, count_col, uniques_col=None):
        """
        Add a totals row to a DataFrame.

        This function appends a totals row to a pandas DataFrame by summing the values
        in the specified columns (e.g., count and uniques). If the DataFrame is empty,
        it logs a warning and returns the original DataFrame.

        :param df: The DataFrame to which the totals row will be added.
        :type df: pandas.DataFrame
        :param count_col: The column name containing the count values to sum.
        :type count_col: str
        :param uniques_col: The column name containing unique count values (optional).
        :type uniques_col: str, optional
        :return: The updated DataFrame with a totals row added.
        :rtype: pandas.DataFrame
        """
        if df.empty:
            logger.warning(f"DataFrame is empty, cannot add totals row for columns: {count_col}, {uniques_col}")
            return df

        total_count = df[count_col].sum()
        totals_data = {count_col: [total_count]}

        if uniques_col:
            total_uniques = df[uniques_col].sum()
            totals_data[uniques_col] = [total_uniques]

        # Identify the column for the label (e.g., 'Total' for the label column)
        label_col = df.columns[0]
        totals_data[label_col] = ["Total"]

        # Create a DataFrame for the totals row and append it to the original DataFrame
        totals_row = pd.DataFrame(totals_data)
        return pd.concat([df, totals_row], ignore_index=True)

    def dataframe_to_markdown(self, df):
        """
        Convert a pandas DataFrame to a markdown table format.

        This function converts a pandas DataFrame into a markdown table using the
        tabulate library's "pipe" table format.

        :param df: The DataFrame to convert.
        :type df: pandas.DataFrame
        :return: A markdown string representing the DataFrame as a table.
        :rtype: str
        """
        return df.to_markdown(index=False, tablefmt="pipe")

    def save_markdown_table(self, df, filename):
        """
        Save a DataFrame as a markdown table to a file.

        This function saves the markdown representation of a pandas DataFrame to a file
        in the output directory.

        :param df: The DataFrame to save as markdown.
        :type df: pandas.DataFrame
        :param filename: The name of the output markdown file.
        :type filename: str
        """
        markdown_data = self.dataframe_to_markdown(df)
        output_filepath = os.path.join(self.output_dir, filename)
        with open(output_filepath, 'w') as f:
            f.write(markdown_data)
        logger.info(f"Saved markdown table to {filename}")

    def run(self):
        """
        Load, process, and visualize data from JSON files.

        This method loads data from various JSON files, processes it into pandas DataFrames,
        generates plots and markdown tables, and saves the results to the output directory.
        It handles clones, referrers, paths, and downloads data.
        """
        # Load data from JSON files
        clones = self.load_json_data("clones.json")
        referrers = self.load_json_data("aggregated_referrers.json")
        paths = self.load_json_data("aggregated_paths.json")
        downloads = self.load_json_data("downloads.json")

        # Debug: Print the keys of the loaded data
        logger.info(f"Clones keys: {clones[0].keys() if clones else 'No data'}")
        logger.info(f"Referrers keys: {referrers[0].keys() if referrers else 'No data'}")
        logger.info(f"Paths keys: {paths[0].keys() if paths else 'No data'}")
        logger.info(f"Downloads keys: {downloads[0].keys() if downloads else 'No data'}")

        # Create DataFrames for referrers, paths, and downloads
        referrers_df = pd.DataFrame(referrers)
        if not referrers_df.empty and 'referrer' in referrers_df.columns:
            referrers_df = referrers_df[['referrer', 'count', 'uniques']]
            referrers_df.columns = ["Referrer", "Number of Referrals", "Unique Referrals"]
            referrers_df = self.add_totals_row(referrers_df, "Number of Referrals", "Unique Referrals")
        else:
            logger.warning("Referrers data is missing expected columns or is empty")

        paths_df = pd.DataFrame(paths)
        if not paths_df.empty and 'path' in paths_df.columns:
            paths_df = paths_df[['path', 'count', 'uniques']]
            paths_df.columns = ["Most Visited Path", "Times Visited", "Unique Visits"]
            paths_df = self.add_totals_row(paths_df, "Times Visited", "Unique Visits")
        else:
            logger.warning("Paths data is missing expected columns or is empty")

        downloads_df = pd.DataFrame(downloads)
        if not downloads_df.empty and 'asset_name' in downloads_df.columns:
            downloads_df = downloads_df[['asset_name', 'download_count']]
            downloads_df.columns = ["Asset Name", "Download Count"]
            downloads_df = self.add_totals_row(downloads_df, "Download Count")
        else:
            logger.warning("Downloads data is missing expected columns or is empty")

        # Generate and save the clones plot
        self.save_clones_plot(clones)

        # Save DataFrames as markdown tables
        self.save_markdown_table(referrers_df, 'referrers_table.md')
        self.save_markdown_table(paths_df, 'paths_table.md')
        self.save_markdown_table(downloads_df, 'downloads_table.md')

        logger.info("Tables and plot have been saved in the 'plots' directory.")

def main():
    """
    Main function to execute the data visualization process.

    This function initializes the DataVisualizer class and runs the data processing
    and visualization pipeline.
    """
    visualizer = DataVisualizer()
    visualizer.run()

# Entry point
if __name__ == "__main__":
    main()
