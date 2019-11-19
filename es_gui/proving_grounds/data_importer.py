import logging
import os

import pandas as pd

from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty, BooleanProperty

from es_gui.resources.widgets.common import RecycleViewRow, WarningPopup


class DataImporterFileChooser(FileChooserListView):
    def __init__(self, *args, **kwargs):
        super(DataImporterFileChooser, self).__init__(**kwargs)

        self.filters = ['*.csv',]
        self.multiselect = False

    def on_submit(self, selection, touch):
        self.host_view.file_selected()


class DataImporterFileChooserScreen(Screen):
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
    datetime_column = StringProperty("")
    data_column = StringProperty("")
    has_selections = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(DataImporterFormatAnalyzerScreen, self).__init__(**kwargs)

        DatetimeColumnRecycleViewRow.data_analyzer_screen = self
        DataColumnRecycleViewRow.data_analyzer_screen = self

    def on_pre_enter(self):
        file_selected = self.manager.file_selected
        self.file_selected_df = pd.read_csv(file_selected)

        column_options = [{'name': column} 
        for column in self.file_selected_df.columns
        ]
        self.datetime_col_rv.data = column_options
        self.datetime_col_rv.unfiltered_data = column_options
        self.data_col_rv.data = column_options
        self.data_col_rv.unfiltered_data = column_options
    
    def on_datetime_column(self, instance, value):
        logging.info('DataImporter: Datetime column changed to {0}.'.format(self.datetime_column))

        self.has_selections = (self.datetime_column != "") and (self.data_column != "")
    
    def on_data_column(self, instance, value):
        logging.info('DataImporter: Data column changed to {0}.'.format(self.data_column))

        self.has_selections = (self.datetime_column != "") and (self.data_column != "")

    def on_has_selections(self, instance, value):
        if value:
            logging.info('DataImporter: Both columns have been selected.')
        
        self.import_button.disabled = not value
    
    def finalize_selections(self):
        import_df, datetime_column_name, data_column_name = self._validate_columns_selected()

        popup = WarningPopup()
        popup.title = 'Success!'
        popup.popup_text.text = 'Data successfully imported.'
        popup.open()

        return import_df, datetime_column_name, data_column_name
    
    def _validate_columns_selected(self):
        # TODO: Pass validation rules from instance?
        datetime_column = self.file_selected_df[self.datetime_column]
        data_column = self.file_selected_df[self.data_column]
        
        # if validation passes, return dataframe, datetime column, data column
        return self.file_selected_df, self.datetime_column, self.data_column
    
    def get_selections(self):
        return self.file_selected_df, self.datetime_column, self.data_column


class DatetimeColumnRecycleViewRow(RecycleViewRow):
    """The representation widget for column names in the datetime column selector RecycleView."""
    data_analyzer_screen = None

    def on_touch_down(self, touch):
        """Add selection on touch down."""
        if super(DatetimeColumnRecycleViewRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected

        if is_selected:
            self.data_analyzer_screen.datetime_column = rv.data[self.index]['name']


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
    """A ModalView with a series of prompts for importing time series data from a csv file."""
    def __init__(self, write_directory=None, **kwargs):
        super(DataImporter, self).__init__(**kwargs)

        if write_directory is None:
            self._write_directory = ""
        else:
            self._write_directory = write_directory

    @property
    def write_directory(self):
        """The directory where the imported time series data will be saved."""
        return self._write_directory
    
    @write_directory.setter
    def write_directory(self, value):
        self._write_directory = value
    
    def get_import_selections(self):
        imported_filename = self.screen_manager.file_selected
        import_df, datetime_column_name, data_column_name = self.screen_manager.get_screen('FileAnalyzer').get_selections()

        # Write imported time series data to write_directory.
        os.makedirs(self.write_directory, exist_ok=True)
        generated_save_name = '_'.join([os.path.split(imported_filename)[-1][:-4], data_column_name]) + '.csv'
        
        save_destination = os.path.join(self.write_directory, generated_save_name)
        import_df[[datetime_column_name, data_column_name]].to_csv(save_destination, index=False)
        logging.info('DataImporter: Selected time series saved to {0}'.format(save_destination))

        return save_destination
        