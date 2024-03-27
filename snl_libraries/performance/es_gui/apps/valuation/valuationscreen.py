from __future__ import absolute_import

import threading
import logging
from time import sleep
from functools import partial

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.clock import mainthread
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.app import App

from es_gui.tools.valuation.valuation_optimizer import ValuationOptimizer
from es_gui.apps.valuation.loaddatascreen import InputError


class ValuationScreen(Screen):
    """The home screen for the 'Valuation - Advanced' section."""
    def __init__(self, **kwargs):
        super(ValuationScreen, self).__init__(**kwargs)

        self.op = ValuationOptimizer()

        self.pw = ProgressWindow()
        self.pw.run_button.bind(on_release=self.execute_valuation)

    def on_enter(self):
        ab = self.manager.nav_bar
        ab.build_valuation_advanced_nav_bar()
        ab.set_title('Valuation - Advanced')

    def _generate_requests(self):
        data_screen = self.manager.get_screen('load_data')
        params_screen = self.manager.get_screen('set_parameters')

        iso_selected, market_formulation_selected, node_selected, year_selected, month_selected = data_screen.get_inputs()

        param_settings = params_screen.get_inputs()

        requests = {'iso': iso_selected,
                    'market type': market_formulation_selected,
                    'months': [(month_selected, year_selected)],
                    'node id': node_selected,
                    }

        if param_settings:
            requests['param set'] = param_settings

        return requests

    def execute_valuation(self, *args):
        try:
            requests = self._generate_requests()
        except InputError as e:
            logging.error('ValuationExecute: ' + str(e))

            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.pw.title = 'Running optimization'
            self.pw.run_button.disabled = True

            solver_name = App.get_running_app().config.get('optimization', 'solver')
            handler = self.manager.get_screen('valuation_home').handler
            handler.solver_name = solver_name
            handler.process_requests(requests)

            self.pw.update_window('Finished!', 100, anim_duration=0)
            self.pw.title = 'Finished!'

            self.pw.view_results_button.bind(on_release=self.activate_view_results_button)
            self.pw.view_results_button.disabled = False

    def open_valuation_run_menu(self, *args):
        """
        Opens the popup/screen for executing a valuation optimization routine.
        """
        #if self.op.price_electricity is not None:
        if True:
            self.pw.open()
        else:
            # Optimizer LMP attribute is still its initialized None value.
            # TODO: Better way to check if data has been loaded?

            popup = WarningPopup()
            popup.popup_text.text = 'No data currently loaded. Please load data first!'
            popup.open()

    def save_run(self, name, iso, dtype, year, month, node, op=None):
        from datetime import datetime

        time_finished = datetime.now().strftime('%A, %B %d, %Y %H:%M:%S')

        results_dict = {}
        results_dict['name'] = name
        if op is None:
            results_dict['op'] = self.op
        else:
            results_dict['op'] = op
        results_dict['iso'] = iso
        results_dict['data_type'] = dtype
        results_dict['year'] = year
        results_dict['month'] = month
        results_dict['node'] = node
        results_dict['time'] = time_finished

        plot_screen = self.manager.get_screen('valuation_results_viewer')
        rv = plot_screen.run_selector.rv
        rv.data.append(results_dict)

    def execute_valuation_run(self, *args):
        """
        Executes the valuation run in a separate thread when possible.
        """
        self.pw.title = 'Running optimization'
        self.pw.run_button.disabled = True

        def _execute_valuation_run(*largs):
            self.pw.progress_label.text = ''

            # instantiate Pyomo model
            anim_duration = 0.3
            self.pw.update_window('Instantiating Pyomo model...\n', 10, anim_duration=anim_duration)
            self.op.instantiate_model()

            # populate Pyomo model
            anim_duration = 2.5  # this duration is empirically based
            self.pw.update_window('Populating Pyomo model...\n', 80, anim_duration=anim_duration)
            self.op.populate_model()

            # solve and process results
            anim_duration = 0.5
            self.pw.update_window('Solving model...\n', 90)
            sleep(0.5)  # hack to force pb to update before the solve clogs the main loop/thread

            @mainthread
            def solve_pyomo_model():
                # get the current optimization solver from settings
                solver_name = App.get_running_app().config.get('optimization', 'solver')
                self.op.solver = solver_name
                self.op.solve_model()

                # post-process solve results
                anim_duration = 0.5
                self.pw.update_window('Processing solve results...\n', 100, anim_duration=anim_duration)

                sleep(anim_duration)  # let the animation play out before "finish"?

                # finish
                anim_duration = 0
                self.pw.update_window('Finished!', 100, anim_duration=anim_duration)
                self.pw.title = 'Finished!'
                self.pw.view_results_button.bind(on_release=self.activate_view_results_button)
                self.pw.view_results_button.disabled = False

                # add to finished runs
                from random import sample
                from string import ascii_letters

                load_screen = self.manager.get_screen('load_data')
                iso = load_screen.iso_select.text
                year = load_screen.year_select.text
                month = load_screen.month_select.text
                dtype = load_screen.type_select.text
                node = load_screen.node_select.text

                # random string identifier for uniqueness
                name = '-'.join([node, year, month, ''.join(sample(ascii_letters, 5))])

                self.save_run(name, iso, dtype, year, month, node)

                # create new instance of Optimizer
                self.op = ValuationOptimizer()

            solve_pyomo_model()

        thread = threading.Thread(target=_execute_valuation_run, args=())
        thread.start()

    def activate_view_results_button(self, *args):
        """
        Enables the "View Results" button after the optimization routine is complete.
        """
        self.manager.nav_bar.go_to_screen('valuation_results_viewer')
        self.pw.dismiss()


class MyPopup(Popup):
    pass


class WarningPopup(MyPopup):
    pass


class ProgressWindow(MyPopup):
    def on_dismiss(self):
        if self.progress_bar.value == self.progress_bar.max:
            # Reset window if previous optimization has finished.
            self.reset_window()

    @mainthread
    def reset_window(self):
        """Resets the valuation run menu/screen to its initial state."""
        self.progress_label.text = 'Click "Run" to proceed.\n'
        self.progress_bar.value = 0
        self.title = 'Run optimization?'
        self.view_results_button.disabled = True
        self.run_button.disabled = False

    @mainthread
    def update_window(self, text, pb_val, anim_duration=0.5, *largs):
        """
        Updates the graphics of the valuation run menu/screen.

        :param text: The new text to be appended to the currently displayed text.
        :param pb_val: The value of the ProgressBar to be set.
        :param anim_duration: The duration of the ProgressBar animation.
        :param largs:
        :return:
        """
        pb_anim = Animation(value=pb_val, duration=anim_duration)
        Animation.cancel_all(self.progress_bar, 'value')

        self.progress_label.text += text
        pb_anim.start(self.progress_bar)
