from __future__ import absolute_import

import os
from functools import partial

from kivy.uix.screenmanager import Screen
from kivy.app import App

# from es_gui.tools.valuation.valuation_dms import ValuationDMS
from es_gui.resources.widgets.common import WarningPopup, NavigationButton
from es_gui.tools.equity.equity_dms import EquityDMS
from es_gui.proving_grounds.help_carousel import HelpCarouselModalView
from .op_handler import EquityOptimizerHandler

class EquityHomeScreen(Screen):
    """
    The home screen for doing energy storage equitt analysis.
    """
    def __init__(self, **kwargs):
        super(EquityHomeScreen, self).__init__(**kwargs)

        # Initialize data management system.
        self.dms = EquityDMS(
            #max_memory=App.get_running_app().config.getint('equity', 'equity_dms_size')*1000,
            #save_data=bool(App.get_running_app().config.getint('equity', 'equity_dms_save')),
            save_name='equity_dms.p',
            home_path='data',
            )
        self.handler = EquityOptimizerHandler(App.get_running_app().config.get('optimization', 'solver')) 
        self.handler.dms = self.dms

    def on_enter(self):
        ab = self.manager.nav_bar
        ab.reset_nav_bar()
        ab.set_title('Energy Storage Equity Applications')

        help_button = NavigationButton(
            text='help',
            on_release=self.open_help_carousel,
        )

        ab.action_view.add_widget(help_button)

    def open_help_carousel(self, *args):
        """
        """
        help_carousel_view = HelpCarouselModalView()
        help_carousel_view.title.text = "QuESt Equity"

        slide_01_text = "QuESt Equity has tools for analyzing energy equity applications for energy storage including powerplant replacement"

        slide_02_text = "The list of powerplants is populated with the powerplant data downloaded using the QuESt Data Manger, Powerplant Dispatch and Pollution Data tool."

        slide_03_text = "Select a set of analysis parameters. The replacement fractions set how much of the powerplant's yearly energy production will be replaced with ES+PV and are plotted together. The plots can hold up to three result sets. Selecting more than three produces results that can be read in an output report or file."

        slide_04_text = "Select a dispatch offset assumption. The flexible dispatch assumption is appropriate for powerplants that have a low minimum dispatch or are comprised of many smaller generators that can be turned on/off independently. The fixed dispatch assumption is appropreate for powerplants with a high minimum dispatch."

        slide_05_text = "Upon completion of the wizard, you will be taken to the summary report screen. There a number of reports you can browse through that summarize different aspects of the simulation results. A brief synopsis of each component of the results including some key numbers.\n\nThe 'Generate report' button can be used to produce a document that summarizes the wizard run."

        slide_06_text = "This document includes your input selections, a primer on the mathematical model used, and all of the charts from the wizard summary reports.\n\nThe resulting HTML document and images are saved to the /results/*/report directory. You can view the report in a web browser."

        slide_07_text = "You can view simulation results in more detail using the Results Viewer tool. You can plot time series data and export simulation results for external processing."


        slides = [
            (os.path.join("es_gui", "resources", "help_views", "equity", "home.png"), slide_01_text),
            (os.path.join("es_gui", "resources", "help_views", "equity", "select_a_powerplant.png"), slide_02_text),
            (os.path.join("es_gui", "resources", "help_views", "equity", "analysis_param.png"), slide_03_text),
            (os.path.join("es_gui", "resources", "help_views", "equity", "dispatch_offset.png"), slide_04_text),
            (os.path.join("es_gui", "resources", "help_views", "equity", "results.png"), slide_05_text),
            (os.path.join("es_gui", "resources", "help_views", "equity", "report.png"), slide_06_text),
            (os.path.join("es_gui", "resources", "help_views", "equity", "analysis_results_viewer.png"), slide_07_text)
        ]

        help_carousel_view.add_slides(slides)
        help_carousel_view.open()