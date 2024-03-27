import logging
import os
from datetime import datetime

import pandas as pd

from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty, BooleanProperty

from es_gui.resources.widgets.common import RecycleViewRow, WarningPopup


class DataImporterFileChooser(FileChooserListView):
    """FileChooserListView for selecting file to import.
    """
    def __init__(self, *args, **kwargs):
        super(DataImporterFileChooser, self).__init__(**kwargs)

        self.filters = ['*.csv',]
        self.multiselect = False

    def on_submit(self, selection, touch):
        self.host_view.file_selected()


class DataImporterFileChooserScreen(Screen):
    """DataImporter screen for selecting which file to import.
    """
    def __init__(self, *args, **kwargs):
        super(DataImporterFileChooserScreen, self).__init__(**kwargs)

        DataImporterFileChooser.host_view = self

    def file_selected(self):
        self._validate_file_selected()
    
    def _validate_file_selected(self):
        try:
            file_selected = self.filechooser.selection[0]
        except IndexError:
            pass
        else:
            file_selected_ext = file_selected.split('.')[-1]

            if file_selected_ext == 'csv':
                logging.info('DataImporter: {0} is a valid csv file.'.format(file_selected))
                self.manager.file_selected = file_selected

                self.manager.current = self.manager.next()
            else:
                logging.error('DataImporter: {0} is not a valid csv file.'.format(file_selected))


class DataImporterFormatAnalyzerScreen(Screen):
    """DataImporter screen for selecting which column to use and completing the import process.
    """
    datetime_column = StringProperty("")
    data_column = StringProperty("")
    has_selections = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(DataImporterFormatAnalyzerScreen, self).__init__(**kwargs)

        DataColumnRecycleViewRow.data_analyzer_screen = self

    def on_pre_enter(self):
        """Populates the recycle view with column names based on selected file.
        """
        file_selected = self.manager.file_selected
        self.file_selected_df = pd.read_csv(file_selected)

        column_options = [{'name': column} 
        for column in self.file_selected_df.columns
        ]

        self.data_col_rv.data = column_options
        self.data_col_rv.unfiltered_data = column_options
    
    def on_data_column(self, instance, value):
        """Checks if data column has been specified.
        """
        logging.info('DataImporter: Data column changed to {0}.'.format(self.data_column))

        self.has_selections = (self.data_column != "")

    def on_has_selections(self, instance, value):
        """Activates the import button if both columns have been specified.
        """
        if value:
            logging.info("DataImporter: All selections have been made.")
        
        self.import_button.disabled = not value
    
    def finalize_selections(self):
        """Validates the specified data based on the selected columns using a validation function.

        Returns
        -------
        Pandas DataFrame
            Dataframe with the data series
        
        str
            Name of the data column
        """
        try:
            import_df, data_column_name = self._validate_columns_selected()
        except ValueError as e:
            exception_popup = WarningPopup()
            exception_popup.popup_text.text = e.args[0]
            exception_popup.open()
        else:
            logging.info("DataImporter: Data format validation completed without issues.")

            completion_popup = self.manager.completion_popup
            completion_popup.open()

            return import_df, data_column_name
    
    def _validate_columns_selected(self):
        """Validates the data using a validation function.

        Raises
        ------
        ValueError
            If validation fails based on ``self.validation_function``
        """
        self.data_validation_function(self.file_selected_df, self.data_column)

        return self.file_selected_df, self.data_column
    
    def get_selections(self):
        """Returns the data import results.

        Returns
        -------
        Pandas DataFrame
            DataFrame containing a single Series for the data
        
        str
            Name of the data column
        """
        import_df, data_column_name = self._validate_columns_selected()

        return import_df, data_column_name


class DataColumnRecycleViewRow(RecycleViewRow):
    """The representation widget for column names in the data column selector RecycleView."""
    data_analyzer_screen = None

    def on_touch_down(self, touch):
        """Add selection on touch down."""
        if super(DataColumnRecycleViewRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected

        if is_selected:
            self.data_analyzer_screen.data_column = rv.data[self.index]['name']


class DataImporter(ModalView):
    """A ModalView with a series of prompts for importing time series data from a csv file.
    
    Parameters
    ----------
    write_directory : str
        Path of directory where the imported data will be written

    write_function : func
        Function describing how to write the imported data to a persistent file
    
    chooser_description : str
        Description displayed on the DataImporter file chooser screen
    
    format_description : str
        Description displayed on the DataImporter format analyzer screen
    
    data_validation_function : str
        Function used to validate the selected data

    Notes
    -----
    ``write_function`` should handle saving the persistent object (e.g., csv file) to disk.
    ``data_validation_function`` should raise a ValueError to indicate failing validation with a relevant reason why it failed.    
    """
    def __init__(self, write_directory=None, write_function=None, chooser_description=None, format_description=None, data_validation_function=None, **kwargs):
        super(DataImporter, self).__init__(**kwargs)

        if write_directory is None:
            self.write_directory = ""
        else:
            self.write_directory = write_directory
        
        if write_function is None:
            def _write_time_series_csv(fname, dataframe):
                """Writes a generic time series dataframe to a two-column csv. 
                
                The data is inferred to be at an hourly time resolution for one standard year.

                Parameters
                ----------
                fname : str
                    Name of the file to be saved without an extension
                dataframe : Pandas DataFrame
                    DataFrame containing a single Series of the data
                
                Returns
                -------
                str
                    The save destination of the resulting file.
                """
                save_destination = os.path.join(self.write_directory, fname + ".csv")

                data_column_name = dataframe.columns[0]

                datetime_start = datetime(2019, 1, 1, 0)
                hour_range = pd.date_range(start=datetime_start, periods=len(dataframe), freq="H")
                dataframe["DateTime"] = hour_range

                dataframe[["DateTime", data_column_name]].to_csv(save_destination, index=False)
                
                return save_destination
            
            self.write_function = _write_time_series_csv
        else:
            self.write_function = write_function

        if chooser_description is None:
            self.chooser_description = "Select a .csv file to import data from."
        else:
            self.chooser_description = chooser_description
        
        file_chooser_screen = self.screen_manager.get_screen("FileChooser")
        file_chooser_screen.file_chooser_body_text.text = self.chooser_description

        if format_description is None:
            self.format_description = "Specify the data column."
        else:
            self.format_description = format_description

        format_analyzer_screen = self.screen_manager.get_screen("FormatAnalyzer")
        format_analyzer_screen.format_analyzer_body_text.text = self.format_description
    
        if data_validation_function is None:
            def _default_data_validation_function(dataframe, data_column_name):
                if len(dataframe) != 8760:
                    raise ValueError("The length of the time series must be 8760 (got {0}).".format(len(dataframe)))
                
                data_column = dataframe[data_column_name]

                try:
                    data_column.astype("float")
                except ValueError:
                    raise ValueError("The selected data column could not be interpeted as numeric float values.")


            self.data_validation_function = _default_data_validation_function
        else:
            self.data_validation_function = data_validation_function

        # Bind DataImporter dismissal to successful data import.
        completion_popup = WarningPopup()
        completion_popup.title = "Success!"
        completion_popup.popup_text.text = "Data successfully imported."
        completion_popup.bind(on_dismiss=self.dismiss)

        self.screen_manager.completion_popup = completion_popup

    @property
    def write_directory(self):
        """The directory where the imported time series data will be saved."""
        return self._write_directory
    
    @write_directory.setter
    def write_directory(self, value):
        self._write_directory = value
    
    @property
    def write_function(self):
        """The function used to write the imported data to disk."""
        return self._write_function
    
    @write_function.setter
    def write_function(self, value):
        self._write_function = value
    
    @property
    def chooser_description(self):
        """Description displayed on the file chooser screen."""
        return self._chooser_description
    
    @chooser_description.setter
    def chooser_description(self, value):
        self._chooser_description = value
        file_chooser_screen = self.screen_manager.get_screen("FileChooser")
        file_chooser_screen.file_chooser_body_text.text = self.chooser_description
    
    @property
    def format_description(self):
        """Description displayed on the format analyzer screen."""
        return self._format_description
    
    @format_description.setter
    def format_description(self, value):
        self._format_description = value
        format_analyzer_screen = self.screen_manager.get_screen("FormatAnalyzer")
        format_analyzer_screen.format_analyzer_body_text.text = self.format_description
    
    @property
    def data_validation_function(self):
        """"The function used to validate the format of the selected data."""
        return self._data_validation_function
    
    @data_validation_function.setter
    def data_validation_function(self, value):
        self._data_validation_function = value
        format_analyzer_screen = self.screen_manager.get_screen("FormatAnalyzer")
        format_analyzer_screen.data_validation_function = self.data_validation_function
    
    def get_import_selections(self):
        """Returns the destination of the processed imported data.

        This method pulls the selections from the DataImporter prompts. 
        Using the selected data, it writes a formatted version of the data to disk according to specification.
        
        Returns
        -------
        str
            The save destination of the file with the imported data.
        """
        imported_filename = self.screen_manager.file_selected
        import_df, data_column_name = self.screen_manager.get_screen("FormatAnalyzer").get_selections()

        # Write imported time series data to write_directory.
        os.makedirs(self.write_directory, exist_ok=True)

        # Strip non-alphanumeric chars from data column name.
        delchars = ''.join(c for c in map(chr, range(256)) if not c.isalnum())

        generated_save_name = "_".join([os.path.split(imported_filename)[-1][:-4], data_column_name.translate({ord(i): None for i in delchars})])
        dataframe = import_df[[data_column_name]]

        save_destination = self.write_function(generated_save_name, dataframe)
        logging.info('DataImporter: Selected time series saved to {0}'.format(save_destination))

        return save_destination
        