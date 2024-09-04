import os

class READMEUpdater:
    """
    A class to handle the automated updating of sections within a README.md file, specifically
    inserting generated plots and markdown tables into designated placeholders.

    The process involves reading the current content of the README.md file, finding specific
    placeholders marked by start and end markers, and replacing the content between these markers
    with new content such as plot images or tables. This class ensures that the README is
    automatically kept up to date with the latest generated data.

    Attributes:
        readme_path (str): The file path to the README.md file that needs to be updated.
        plot_path (str): The file path to the image of the plot that should be inserted.
        downloads_md_path (str): The file path to the markdown file containing the downloads table.
        paths_md_path (str): The file path to the markdown file containing the paths table.
        referrers_md_path (str): The file path to the markdown file containing the referrers table.
    """

    def __init__(self, readme_path, plot_path, downloads_md_path, paths_md_path, referrers_md_path):
        """
        Initialize the READMEUpdater class with the paths to the necessary files.

        This constructor sets up the required file paths for the README, plot image, and
        markdown tables. These paths are stored as instance attributes, allowing other
        methods within the class to access them easily when performing file operations or
        content updates.

        :param readme_path: The path to the README.md file that will be updated.
        :type readme_path: str
        :param plot_path: The path to the plot image file that will be embedded in the README.md.
        :type plot_path: str
        :param downloads_md_path: The path to the markdown file containing the downloads data table.
        :type downloads_md_path: str
        :param paths_md_path: The path to the markdown file containing the paths data table.
        :type paths_md_path: str
        :param referrers_md_path: The path to the markdown file containing the referrers data table.
        :type referrers_md_path: str
        """
        self.readme_path = readme_path
        self.plot_path = plot_path
        self.downloads_md_path = downloads_md_path
        self.paths_md_path = paths_md_path
        self.referrers_md_path = referrers_md_path

    def read_file(self, filepath):
        """
        Read the content of a specified file.

        This method opens the file at the given filepath in read mode and returns its content as a string.
        It's used to retrieve the existing content of the README.md file, as well as the content of the
        markdown files containing the tables.

        :param filepath: The file path to the file that needs to be read.
        :type filepath: str
        :return: The entire content of the file as a string.
        :rtype: str

        The process involves:
        - Opening the file in read mode using a context manager to ensure proper file handling.
        - Reading the content of the file and returning it to the caller.
        """
        with open(filepath, 'r') as file:
            return file.read()

    def write_file(self, filepath, content):
        """
        Write content to a specified file.

        This method opens the file at the given filepath in write mode and writes the provided content to it.
        It's primarily used to save the updated README.md content after the necessary replacements have been made.

        :param filepath: The file path to the file where the content should be written.
        :type filepath: str
        :param content: The content to be written to the file.
        :type content: str

        The process involves:
        - Opening the file in write mode, which overwrites the existing content of the file.
        - Writing the provided content to the file.
        - Closing the file automatically through the context manager.
        """
        with open(filepath, 'w') as file:
            file.write(content)

    def replace_between_markers(self, content, start_marker, end_marker, replacement):
        """
        Replace the content between specified start and end markers within a string.

        This method searches for the specified start and end markers within the provided content string.
        Once the markers are located, the content between them is replaced with the new replacement text.
        If either marker is not found, the content is returned unchanged, and a message is printed to indicate
        the issue.

        :param content: The original content string where the replacement will occur.
        :type content: str
        :param start_marker: The marker indicating the beginning of the section to be replaced.
        :type start_marker: str
        :param end_marker: The marker indicating the end of the section to be replaced.
        :type end_marker: str
        :param replacement: The new content that will replace the old content between the markers.
        :type replacement: str
        :return: The updated content with the section between the markers replaced.
        :rtype: str

        The process involves:
        - Finding the start and end markers within the content string.
        - Calculating the positions of the markers to correctly identify the section to be replaced.
        - Replacing the content between the markers with the new replacement text.
        - Returning the updated content string.
        """
        start_index = content.find(start_marker)
        end_index = content.find(end_marker)
        if start_index == -1 or end_index == -1:
            print(f"Markers not found in the file: {start_marker} or {end_marker}")
            return content
        start_index += len(start_marker)
        return content[:start_index] + '\n' + replacement + '\n' + content[end_index:]

    def update_readme(self):
        """
        Update the README.md file by inserting the latest plot and markdown tables.

        This method reads the existing content of the README.md file and replaces the sections
        marked by specific placeholders (start and end markers) with the latest plot image and
        markdown tables. After performing the replacements, the updated content is written back
        to the README.md file.

        The process involves:
        - Reading the current content of the README.md file.
        - Reading the content of the plot image and markdown table files.
        - Replacing the placeholders in the README.md content with the new content from the files.
        - Writing the updated content back to the README.md file.
        """
        # Read the README.md file
        readme_content = self.read_file(self.readme_path)
        print("Original README Content:")
        print(readme_content[:500])  # Print the first 500 characters for brevity

        # Read the plot and markdown table files
        plot_url = f'![Clones Plot]({self.plot_path})'
        downloads_md = self.read_file(self.downloads_md_path)
        paths_md = self.read_file(self.paths_md_path)
        referrers_md = self.read_file(self.referrers_md_path)

        print("Downloads Table Content:")
        print(downloads_md)

        print("Paths Table Content:")
        print(paths_md)

        print("Referrers Table Content:")
        print(referrers_md)

        # Update plot section in README.md
        readme_content = self.replace_between_markers(
            readme_content,
            '<!-- PLOT_PLACEHOLDER_START -->',
            '<!-- PLOT_PLACEHOLDER_END -->',
            plot_url
        )

        # Update downloads table section in README.md
        readme_content = self.replace_between_markers(
            readme_content,
            '<!-- TABLE_DOWNLOADS_PLACEHOLDER_START -->',
            '<!-- TABLE_DOWNLOADS_PLACEHOLDER_END -->',
            downloads_md
        )

        # Update paths table section in README.md
        readme_content = self.replace_between_markers(
            readme_content,
            '<!-- TABLE_PATHS_PLACEHOLDER_START -->',
            '<!-- TABLE_PATHS_PLACEHOLDER_END -->',
            paths_md
        )

        # Update referrers table section in README.md
        readme_content = self.replace_between_markers(
            readme_content,
            '<!-- TABLE_REFERRERS_PLACEHOLDER_START -->',
            '<!-- TABLE_REFERRERS_PLACEHOLDER_END -->',
            referrers_md
        )

        print("Updated README Content:")
        print(readme_content[:500])  # Print the first 500 characters for brevity

        # Write the updated content back to the README.md file
        self.write_file(self.readme_path, readme_content)

    def run(self):
        """
        Execute the README update process.

        This method serves as the entry point for the README update process. It calls the
        `update_readme` method, which handles the detailed steps of reading, replacing,
        and writing the content of the README.md file.

        The process involves:
        - Invoking the `update_readme` method to perform the actual content update.
        """
        self.update_readme()

def main():
    """
    Main function to execute the README update process.

    This function initializes the READMEUpdater class with the necessary file paths and
    then calls the `run` method to update the README.md file with the latest content.

    The process involves:
    - Setting up the paths for the README, plot, and markdown files.
    - Creating an instance of the READMEUpdater class with these paths.
    - Calling the `run` method on the class instance to update the README.
    """
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Paths to the files
    readme_path = os.path.join(current_dir, 'README.md')
    plot_path = os.path.join(current_dir, 'plots/clones_plot.png')
    downloads_md_path = os.path.join(current_dir, 'plots/downloads_table.md')
    paths_md_path = os.path.join(current_dir, 'plots/paths_table.md')
    referrers_md_path = os.path.join(current_dir, 'plots/referrers_table.md')

    # Initialize and run the READMEUpdater
    updater = READMEUpdater(readme_path, plot_path, downloads_md_path, paths_md_path, referrers_md_path)
    updater.run()

# Entry point
if __name__ == "__main__":
    main()
