from __future__ import absolute_import

import os
from functools import partial

from kivy.uix.screenmanager import Screen
from kivy.app import App

from es_gui.tools.valuation.valuation_dms import ValuationDMS
from es_gui.resources.widgets.common import WarningPopup, NavigationButton
from es_gui.proving_grounds.help_carousel import HelpCarouselModalView
from .op_handler import ValuationOptimizerHandler


class ValuationHomeScreen(Screen):
    """
    The home screen for doing energy storage valuation analysis.
    """
    def __init__(self, **kwargs):
        super(ValuationHomeScreen, self).__init__(**kwargs)

        # Initialize data management system.
        self.dms = ValuationDMS(max_memory=App.get_running_app().config.getint('valuation', 'valuation_dms_size')*1000,
                                save_data=bool(App.get_running_app().config.getint('valuation', 'valuation_dms_save')),
                                save_name='valuation_dms.p',
                                home_path='data')
        self.handler = ValuationOptimizerHandler(App.get_running_app().config.get('optimization', 'solver'))
        self.handler.dms = self.dms

    def on_enter(self):
        ab = self.manager.nav_bar
        ab.reset_nav_bar()
        ab.set_title('Valuation')

        help_button = NavigationButton(
            text='help',
            on_release=self.open_help_carousel,
        )

        ab.action_view.add_widget(help_button)

        # data_manager = App.get_running_app().data_manager
        
        # # Check if any data is available.
        # if not data_manager.data_bank:
        #     no_data_popup = WarningPopup()
        #     no_data_popup.popup_text.text = "Looks like you haven't downloaded any data yet. Try using QuESt Data Manager to get some data before returning here!"
        #     no_data_popup.dismiss_button.text = "Got it, take me back!"

        #     no_data_popup.bind(on_dismiss=partial(ab.go_to_screen, 'index'))
        #     no_data_popup.open()
    
    def open_help_carousel(self, *args):
        """
        """
        help_carousel_view = HelpCarouselModalView()
        help_carousel_view.title.text = "QuESt Valuation"

        slide_01_text = "QuESt Valuation is an application for estimating the revenue potential for an energy storage system providing ISO/RTO services. It takes a retrospective analysis approach using historical data.\n\nData is required to use the tools in QuESt Valuation. Options in the user interface such as market area selection are entirely based on the contents of your QuESt data bank."

        slide_02_text = "The Wizard mode under the Simulation tab walks you through a series of prompts to set up the analysis. This mode is streamlined for a simpler experience compared to the Batch Runs mode.\n\nYou will need the following data to use this tool:\n* Market data for each ISO/RTO that you want to look at"

        slide_03_text = "Upon completion of the wizard, you will be taken to the summary report screen. There a number of reports you can browse through that summarize different aspects of the simulation results. A brief synopsis of each component of the results including some key numbers.\n\nThe 'Generate report' button can be used to produce a document that summarizes the wizard run."

        slide_04_text = "This document includes your input selections, a primer on the mathematical model used, and all of the charts from the wizard summary reports.\n\nThe resulting HTML document and images are saved to the /results/*/report directory. You can view the report in a web browser."

        slide_05_text = "The Batch Runs mode is more advanced than the Wizard mode. The workflow for using this mode is identical but offers more flexibility and options.\n\nThere are two panels for your input: 'Data' and 'Parameters'. You can toggle between the two using the buttons at the bottom. Note that changing market area or pricing node selections will reset the other input widgets."

        slide_06_text = "The parameters available are more numerous than those in the Wizard mode and may also vary among the market areas. The default values indicated by the hint text for each parameter will be used if you do not enter in a new value.\n\nTry using the 'Tab' key to quickly navigate among the text input fields."

        slide_07_text = "The parameter sweep can be used for parameter sensitivity analysis. The sweep will be applied to each month of data selected.\n\nIn this example, a sweep over the power rating from 5 to 20 MW in ten evenly-spaced points will be performed for each month selected in the 'Data' tab. If four months were selected then a total of 40 models will be solved."

        slide_08_text = "When you are done with your selections, click the 'Go!' button to proceed. The models will be built and solved in the background. Upon completion, a popup will open to inform you of the results and provide any pertinent warnings.\n\nYou can proceed to the QuESt Valuation results viewer via the popup, navigation bar, or QuESt Valuation home screen to look at the results."

        slide_09_text = "You can view simulation results in more detail using the Results Viewer tool. You can plot time series data and export simulation results for external processing."

        slides = [
            (os.path.join("es_gui", "resources", "help_views", "valuation", "01.png"), slide_01_text),
            (os.path.join("es_gui", "resources", "help_views", "valuation", "02.png"), slide_02_text),
            (os.path.join("es_gui", "resources", "help_views", "common", "wizard_report", "01.png"), slide_03_text),
            (os.path.join("es_gui", "resources", "help_views", "common", "wizard_report", "02.png"), slide_04_text),
            (os.path.join("es_gui", "resources", "help_views", "valuation", "03.png"), slide_05_text),
            (os.path.join("es_gui", "resources", "help_views", "valuation", "04.png"), slide_06_text),
            (os.path.join("es_gui", "resources", "help_views", "valuation", "05.png"), slide_07_text),
            (os.path.join("es_gui", "resources", "help_views", "valuation", "06.png"), slide_08_text),
            (os.path.join("es_gui", "resources", "help_views", "common", "results_viewer", "00.png"), slide_09_text),
        ]

        help_carousel_view.add_slides(slides)
        help_carousel_view.open()
