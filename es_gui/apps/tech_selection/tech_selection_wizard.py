from __future__ import absolute_import, print_function

import os
import json
import re

from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.properties import BooleanProperty
from kivy.app import App

from es_gui.resources.widgets.common import ValuationRunCompletePopup, RecycleViewRow, BASE_TRANSITION_DUR, ParameterRow2cols
from es_gui.apps.tech_selection.results_viewer import TechSelectionFeasible
from es_gui.apps.tech_selection.analysis import perform_tech_selection
from es_gui.apps.tech_selection.fAux import pdSeriesIdxWhereTrue


class TechSelectionWizard(Screen):
    """The main screen for the technology selection wizard. This hosts the nested screen manager for the actual wizard."""

    def on_enter(self):
        """Create navigation bar and screen title."""
        ab = self.manager.nav_bar
        ab.set_title('Energy Storage Technology Selection Application')

    def on_leave(self):
        """Reset wizard to initial state by removing all screens except the first."""
        self.sm.current = 'tech_selection_home'
        if len(self.sm.screens) > 1:
            self.sm.clear_widgets(screens=self.sm.screens[1:])


class TechSelectionWizardScreenManager(ScreenManager):
    """The screen manager for the technology selection wizard screens."""

    def __init__(self, **kwargs):
        super(TechSelectionWizardScreenManager, self).__init__(**kwargs)
        self.transition = SlideTransition()
        self.add_widget(TechSelectionWizardStart(name='tech_selection_home'))


class TechSelectionWizardStart(Screen):
    """The starting/welcome screen for the technology selection wizard."""

    def _next_screen(self):
        """Set actions for when the 'Next' button is pressed."""

        # Create, if necessary, the next screen
        if not self.manager.has_screen('tech_selection_inputs'):
            screen = TechSelectionUserInputs(name='tech_selection_inputs')
            self.manager.add_widget(screen)

        # Move to the next screen
        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'tech_selection_inputs'


class TechSelectionUserInputs(Screen):
    """The user inputs screen for the technology selection wizard."""

    has_selection = BooleanProperty(False) # Boolean variable indicating whether user selections have been made

    def __init__(self, **kwargs):
        super(TechSelectionUserInputs, self).__init__(**kwargs)
        self.selected_params = {} # Dictionary to collect/save user selections

        # 'Children screens' for each RecycleView
        GridLocationRVEntry.host_screen = self
        ApplicationRVEntry.host_screen = self
        SystemSizeRVEntry.host_screen = self
        DischargeDurationRVEntry.host_screen = self

        self.data_manager = App.get_running_app().data_manager

        self.target_cost_kW = 1500
        self.target_cost_kWh = 1000

        # Read input databases
        self.apps_db = self.data_manager.get_applications_db()
        self.all_user_options_names = self.data_manager.get_tech_selection_all_options()
        self.all_apps = self.apps_db.index.to_list()

        self.default_inputs = {
            'Transmission/central':
                [pdSeriesIdxWhereTrue(self.apps_db['Default at transmission'] == 'Yes')[0], 'Wholesale (100 MW)'],
            'Distribution':
                [pdSeriesIdxWhereTrue(self.apps_db['Default at distribution'] == 'Yes')[0], 'Distribution & microgrid (1 MW)'],
            'BTM: commercial/industrial':
                [pdSeriesIdxWhereTrue(self.apps_db['Default at industrial'] == 'Yes')[0], 'Commercial & industrial (100 kW)'],
            'BTM: residential':
                [pdSeriesIdxWhereTrue(self.apps_db['Default at residential'] == 'Yes')[0], 'Residential (10 kW)']}

        self.compatibility_apps = {
            'Transmission/central': pdSeriesIdxWhereTrue(self.apps_db['Compatible with transmission'] == 'Yes'),
            'Distribution': pdSeriesIdxWhereTrue(self.apps_db['Compatible with distribution'] == 'Yes'),
            'BTM: commercial/industrial': pdSeriesIdxWhereTrue(self.apps_db['Compatible with industrial'] == 'Yes'),
            'BTM: residential': pdSeriesIdxWhereTrue(self.apps_db['Compatible with residential'] == 'Yes')}

        # Populate lists for each category of user input
        self.ids.grid_location_rv.data = [{'name': value} for value in self.all_user_options_names['grid_location']]
        self.ids.app_names_rv.data = [{'name': value} for value in self.all_apps]
        self.ids.system_size_rv.data = [{'name': value} for value in self.all_user_options_names['system_size']]
        self.ids.discharge_duration_rv.data = [{'name': value} for value in self.all_user_options_names['discharge_duration']]

    def on_pre_enter(self):
        """Update list of available user selections according to previous selection."""

        # If a grid location has been selected previously, update the list of available applications accordingly
        try:
            self.set_compatible_apps()
        except:
            pass

    def on_has_selection(self, instance, value):
        """Enable the 'Next' button only if all user inputs have been selected."""
        self.next_button.disabled = not value

    def is_user_selection_complete(self):
        """Check if all user selections have been made and return True; otherwise, return False."""
        return all([hasattr(GridLocationRVEntry.host_screen, 'grid_location_selected'),
                    hasattr(ApplicationRVEntry.host_screen, 'application_selected'),
                    hasattr(SystemSizeRVEntry.host_screen, 'system_size_selected'),
                    hasattr(DischargeDurationRVEntry.host_screen, 'discharge_duration_selected')])

    def set_compatible_apps(self):
        """Update the list of available application names based on the selected grid location."""
        self.available_apps_at_location = sorted(self.compatibility_apps[
            GridLocationRVEntry.host_screen.grid_location_selected])
        self.ids.app_names_rv.data = [{'name': value} for value in self.available_apps_at_location]

    def set_default_inputs_app_and_size(self):
        """Set default values for application and system size based on the selected grid location."""
        selected_location = GridLocationRVEntry.host_screen.grid_location_selected
        default_application, default_size = self.default_inputs[selected_location]
        self.ids.app_names_rv_selectable.selected_nodes = [self.available_apps_at_location.index(default_application)]
        self.ids.system_size_rv_selectable.selected_nodes = [self.all_user_options_names['system_size'].index(default_size)]

    def set_default_inputs_duration(self):
        """Set default value for discharge duration based on the selected application."""
        selected_application = ApplicationRVEntry.host_screen.application_selected
        default_duration = ('4 hrs' if self.apps_db.loc[selected_application, 'Power vs. Energy'] == 'Energy'
                            else 'Up to 0.5 hr')
        self.ids.discharge_duration_rv_selectable.selected_nodes = [
            self.all_user_options_names['discharge_duration'].index(default_duration)]

    def _next_screen(self, *args):
        """Set actions for when the 'Next' button is pressed."""

        # Collect/save user selections in a .json file
        self.selected_params = [
            {'name': 'Grid location', 'attr name': 'location',
             'value': GridLocationRVEntry.host_screen.grid_location_selected},
            {'name': 'Application', 'attr name': 'application',
             'value': ApplicationRVEntry.host_screen.application_selected},
            {'name': 'System size', 'attr name': 'system_size',
             'value': re.search(r'\((.*?)\)', SystemSizeRVEntry.host_screen.system_size_selected).group(1)},
            {'name': 'Discharge duration', 'attr name': 'discharge_duration',
             'value': DischargeDurationRVEntry.host_screen.discharge_duration_selected},
            {'name': 'Type of application', 'attr name': 'app_type',
             'value': self.apps_db.loc[ApplicationRVEntry.host_screen.application_selected, 'Power vs. Energy']}]
        destination_file = os.path.join('es_gui', 'apps', 'data_manager', '_static', 'tech_selection_params.json')
        with open(destination_file, 'w') as outfile:
            json.dump(self.selected_params, outfile)

        # Create, if necessary, the next screen
        if not self.manager.has_screen('confirm_inputs'):
            screen = TechSelectionConfirmInputs(name='confirm_inputs')
            self.manager.add_widget(screen)

        # Move to the next screen
        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'confirm_inputs'


class TechSelectionConfirmInputs(Screen):
    """The user inputs confirmation screen for the technology selection wizard."""

    def __init__(self, **kwargs):
        super(TechSelectionConfirmInputs, self).__init__(**kwargs)

    def on_pre_enter(self):
        """Clear any widgets already present in the screen and create a new widget displaying the user selections."""
        self.data_manager = App.get_running_app().data_manager

        if self.param_widget.children:
            self.param_widget.clear_widgets()
        self.param_widget.build()

    def execute_run(self):
        """Run feasibility scores computation according to the user inputs."""

        # Collect user selections values from a .json file
        MODEL_PARAMS = self.data_manager.get_tech_selection_params()
        user_selections = {val['attr name']: val['value'] for val in MODEL_PARAMS}

        dfFeasible, dfRanking = perform_tech_selection(user_selections,
                                                       self.manager.get_screen('tech_selection_inputs').target_cost_kWh,
                                                       self.manager.get_screen('tech_selection_inputs').target_cost_kW)

        dfRanking.to_csv(os.path.join('results', 'tech_selection', 'table_ranking.csv'))

         # Popup window after analysis has been completed
        popup = ValuationRunCompletePopup(size_hint=(0.4, 0.37))
        popup.title = 'Success!'
        popup.popup_text.text = ('The analysis has been completed successfully. Click [i]Go back[/i] to return to the '
                                 'inputs selection screen or [i]Continue[/i] to see the results.')
        popup.view_results_button.text = 'Go back'
        popup.view_results_button.bind(on_release=popup.dismiss)
        popup.dismiss_button.text = 'Continue'
        popup.dismiss_button.bind(on_release=self._next_screen)
        popup.open()

    def _next_screen(self, *args):
        """Set actions for when the 'Next' button is pressed."""

        # Create, if necessary, the next screen
        if not self.manager.has_screen('feasible_techs'):
            screen = TechSelectionFeasible(name='feasible_techs')
            self.manager.add_widget(screen)

        # Move to the next screen
        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'feasible_techs'


class TechSelectionParameterWidget(GridLayout):
    """Grid layout containing rows of user selections widgets."""

    def build(self):
        """Build the widget by creating a row for each parameter."""

        # Collect user selections values from a .json file
        data_manager = App.get_running_app().data_manager
        MODEL_PARAMS = data_manager.get_tech_selection_params()

        # Create and add to the screen one widget for each type of user input
        for param in MODEL_PARAMS:
            if param['attr name'] != 'app_type':
                row = ParameterRow2cols(desc=param)
                self.add_widget(row)


class GridLocationRVEntry(RecycleViewRow):
    """The representation for data entries in the RecycleView for 'Grid Location'."""

    def apply_selection(self, rv, index, is_selected):
        super(GridLocationRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.grid_location_selected = rv.data[self.index]['name']
            self.host_screen.set_compatible_apps()
            self.host_screen.set_default_inputs_app_and_size()
            self.host_screen.ids.app_names_rv.refresh_from_data()
            self.host_screen.ids.system_size_rv.refresh_from_data()


class ApplicationRVEntry(RecycleViewRow):
    """The representation for data entries in the RecycleView for 'Application'."""

    def apply_selection(self, rv, index, is_selected):
        super(ApplicationRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.application_selected = rv.data[self.index]['name']
            self.host_screen.set_default_inputs_duration()
            self.host_screen.ids.discharge_duration_rv.refresh_from_data()


class SystemSizeRVEntry(RecycleViewRow):
    """The representation for data entries in the RecycleView for 'System Size'."""

    def apply_selection(self, rv, index, is_selected):
        super(SystemSizeRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.system_size_selected = rv.data[self.index]['name']


class DischargeDurationRVEntry(RecycleViewRow):
    """The representation for data entries in the RecycleView for 'Discharge Duration'."""

    def apply_selection(self, rv, index, is_selected):
        super(DischargeDurationRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.discharge_duration_selected = rv.data[self.index]['name']
            self.host_screen.has_selection = self.host_screen.is_user_selection_complete()