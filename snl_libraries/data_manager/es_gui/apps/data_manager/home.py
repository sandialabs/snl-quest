from __future__ import absolute_import

from functools import partial
import os

from kivy.uix.screenmanager import Screen

from es_gui.resources.widgets.common import NavigationButton
from es_gui.proving_grounds.help_carousel import HelpCarouselModalView


class DataManagerHomeScreen(Screen):
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.build_data_manager_nav_bar()
        ab.set_title('Data Manager')

        help_button = NavigationButton(
            text='help',
            on_release=self.open_help_carousel,
        )

        ab.action_view.add_widget(help_button)
    
    def open_help_carousel(self, *args):
        """
        """
        help_carousel_view = HelpCarouselModalView()
        help_carousel_view.title.text = "QuESt Data Manager"

        slide_01_text = "QuESt Data Manager is a collection of tools for acquiring data for use in other QuESt applications. Data acquired here is stored in a data bank accessible throughout the rest of the QuESt suite.\n\nClick on one of the data tools to get started."

        slide_02_text = "Some data sources require registration and credentials. Look out for [font=Modern Pictograms][color=00ADD0]?[/color][/font] symbols for additional information.\n\nThe 'settings' button will open the global settings menu from the navigation bar. Make sure your connection settings are appropriately configured when using QuESt Data Manager as internet access is required to download data."

        slide_03_text = "You can save some of your login information or API keys by entering in the 'QuESt Data Manager' tab in the global settings menu. These values will auto-populate the appropriate fields the next time you launch QuESt. These values are also stored in the quest.ini file in the QuESt installation folder.\n\nNote that QuESt does not store passwords."

        slide_04_text = "Rate structure tables can be modified before saving. You can change the rate for each period. Click on the [font=Modern Pictograms]D[/font] button to copy the value to the next row."

        slide_05_text = "The tables on the right describe the rate schedule for weekdays and weekends. Each row corresponds to a month and each column an hour. The value in each cell matches to a rate in the rates table; you can change each of these as needed. Try using the 'Tab' and arrow keys to navigate each table more quickly.\n\nNote that you cannot change the number of periods."
        
        slide_06_text = "National Solar Radiation Database (NSRDB) weather data is available to download for performance applications. With the longitude and latitude of your desired location, a year of data may be obtained."
        
        slide_07_text = "Once a file name has been entered and the save button is clicked, the EnergyPlus weather converter will run (must have EnergyPlus installed and in the QuESt directory; see Performance Tool for more information). Simply select the location data csv file, ensure the selected output format is EnergyPlus weather format (EPW), and enter the file name to save."

        slides = [
            (os.path.join("es_gui", "resources", "help_views", "data_manager", "updated_home.png"), slide_01_text),
            (os.path.join("es_gui", "resources", "help_views", "data_manager", "02.png"), slide_02_text),
            (os.path.join("es_gui", "resources", "help_views", "data_manager", "03.png"), slide_03_text),
            (os.path.join("es_gui", "resources", "help_views", "data_manager", "04.png"), slide_04_text),
            (os.path.join("es_gui", "resources", "help_views", "data_manager", "05.png"), slide_05_text),
            (os.path.join("es_gui", "resources", "help_views", "data_manager", "weather.png"), slide_06_text),
            (os.path.join("es_gui", "resources", "help_views", "data_manager", "eplus_converter.png"), slide_07_text)
        ]

        help_carousel_view.add_slides(slides)
        help_carousel_view.open()
