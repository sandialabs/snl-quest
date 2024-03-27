from __future__ import absolute_import

import os
from functools import partial

from kivy.uix.screenmanager import Screen
from kivy.app import App

from es_gui.resources.widgets.common import WarningPopup, NavigationButton
from es_gui.proving_grounds.help_carousel import HelpCarouselModalView


class PerformanceHomeScreen(Screen):
    """
    The home screen for doing performance simulation energy storage analysis.
    """
    def __init__(self, **kwargs):
        super(PerformanceHomeScreen, self).__init__(**kwargs)

        # Initialize data management system.
#        self.dms = BtmDMS(
#            max_memory=App.get_running_app().config.getint('performance', 'performance_dms_size')*1000,
#            save_data=bool(App.get_running_app().config.getint('performance', 'performance_dms_save')),
#            save_name='performance_dms.p',
#            home_path='data',
#            )
#        self.handler.dms = self.dms
        
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.reset_nav_bar()
        ab.set_title('Performance Applications')

        help_button = NavigationButton(
            text='help',
            on_release=self.open_help_carousel,
        )

        ab.action_view.add_widget(help_button)

        data_manager = App.get_running_app().data_manager

    def open_help_carousel(self, *args):
        """
        """
        help_carousel_view = HelpCarouselModalView()
        help_carousel_view.title.text = "QuESt Performance"

        slide_01_text = "QuESt Performance is an application with tools for analyzing the effects of heating and cooling on energy storage use cases."

        slide_02_text = "The performance simulation estimates the effects of parasitic loads on energy storage performance.\n\nYou will need the following to use this tool:\n* EnergyPlus software\n\n* Input file\n\n* Weather file\n\n* Charge/discharge profile\n\n* Battery parameters."

        slide_03_text = "EnergyPlus is a building simulation software used to model energy consumption developed by the Department of Energy Building Technologies Office. To download EnergyPlus, simply navigate to www.energyplus.net/downloads and select the appropriate package." 
        
        slide_04_text = "Once downloaded, move the software to the Quest directory and rename to 'energyplus'."
        
        slide_05_text = "An EnergyPlus input file describing a battery energy storage device in an uninsulated shipping container is provided. If you have another input file you would like to use, place it in the quest -> data -> idf directory."
        
        slide_06_text = "Weather files may be obtained in either of two ways. There is a large repository of weather files formatted for EnergyPlus found at www.energyplus.net/weather, which may be downloaded and placed under quest -> data -> weather -> location. NSRDB data may also be downloaded with the Quest Data Manager for a specific location and year."

        slide_07_text = "The battery charge/discharge profile may be used from a behind-the-meter or valuation run. If you would like to use your own data, place the file in the data directory under profile. Ensure the data file is formatted as shown."
        
        slide_08_text = "Battery parameters can be found or determined from nameplate values and the 1C discharge curve. See  T. A. Nguyen, D. A. Copp, R. H. Byrne, and B. R. Chalamala, “Market evaluation of energy storage systems incorporating technology-specific nonlinear models,” IEEE Transactions on Power Systems, vol. 34, no. 5, pp. 3706–3715, 2019. The default values correspond to an LG 18650 lithium-ion cell."

        slides = [
            (os.path.join("es_gui", "resources", "help_views", "performance", "performance_home.png"), slide_01_text),
            (os.path.join("es_gui", "resources", "help_views", "performance", "performance_data_select.png"), slide_02_text),
            (os.path.join("es_gui", "resources", "help_views", "performance", "eplus_download.png"), slide_03_text),
            (os.path.join("es_gui", "resources", "help_views", "performance", "Inkedquest_directory_LI.jpg"), slide_04_text),
            (os.path.join("es_gui", "resources", "help_views", "performance", "idf_dir.png"), slide_05_text),
            (os.path.join("es_gui", "resources", "help_views", "performance", "eplus_weather.png"), slide_06_text),
#            (os.path.join("es_gui", "resources", "help_views", "performance", "nsrdb_data.png"), slide_06_text),
            (os.path.join("es_gui", "resources", "help_views", "performance", "test_data.png"), slide_07_text),
            (os.path.join("es_gui", "resources", "help_views", "performance", "performance_param_select.png"), slide_08_text)
        ]

        help_carousel_view.add_slides(slides)
        help_carousel_view.open()
