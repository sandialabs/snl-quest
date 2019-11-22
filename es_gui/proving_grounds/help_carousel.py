import logging
import os

import pandas as pd

from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty, BooleanProperty

from es_gui.resources.widgets.common import RecycleViewRow, WarningPopup


class HelpCarouselModalView(ModalView):
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
    pass