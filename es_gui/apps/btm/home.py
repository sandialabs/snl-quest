from __future__ import absolute_import

import os
from functools import partial

from kivy.uix.screenmanager import Screen
from kivy.app import App

# from es_gui.tools.valuation.valuation_dms import ValuationDMS
from es_gui.resources.widgets.common import WarningPopup
from es_gui.tools.btm.btm_dms import BtmDMS
from .op_handler import BtmOptimizerHandler


class BehindTheMeterHomeScreen(Screen):
    """
    The home screen for doing behind-the-meter energy storage analysis.
    """
    def __init__(self, **kwargs):
        super(BehindTheMeterHomeScreen, self).__init__(**kwargs)

        # Initialize data management system.
        self.dms = BtmDMS(
            max_memory=App.get_running_app().config.getint('btm', 'btm_dms_size')*1000,
            save_data=bool(App.get_running_app().config.getint('btm', 'btm_dms_save')),
            save_name='btm_dms.p',
            home_path='data',
            )
        self.handler = BtmOptimizerHandler(App.get_running_app().config.get('optimization', 'solver'))
        self.handler.dms = self.dms

    def on_enter(self):
        ab = self.manager.nav_bar
        ab.reset_nav_bar()
        ab.set_title('Behind-the-Meter Applications')

        # data_manager = App.get_running_app().data_manager
        
        # # Check if any data is available.
        # if not data_manager.data_bank:
        #     no_data_popup = WarningPopup()
        #     no_data_popup.popup_text.text = "Looks like you haven't downloaded any data yet. Try using QuESt Data Manager to get some data before returning here!"
        #     no_data_popup.dismiss_button.text = "Got it, take me back!"

        #     no_data_popup.bind(on_dismiss=partial(ab.go_to_screen, 'index'))
        #     no_data_popup.open()
