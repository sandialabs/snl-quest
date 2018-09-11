from __future__ import absolute_import

from functools import partial

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

from es_gui.resources.widgets.common import WarningPopup, InputError, ValuationRunCompletePopup
from es_gui.tools.valuation.valuation_optimizer import BadParameterException


class SetParametersScreen(Screen):
    """
    The screen for setting parameters for the energy storage model.
    """
    iso = StringProperty('')
    param_to_attr = dict()

    def on_pre_enter(self):
        self.iso = self.manager.get_screen('load_data').iso_select.text

    def on_iso(self, instance, value):
        while len(self.param_widget.children) > 0:
            for widget in self.param_widget.children:
                if isinstance(widget, SetParameterRow):
                    self.param_widget.remove_widget(widget)

        if self.iso:
            try:
                self.param_widget.build(self.iso)

                data_manager = App.get_running_app().data_manager
                MODEL_PARAMS = data_manager.get_valuation_model_params(value)

                self.param_to_attr = {param['name']: param['attr name']
                                      for param in MODEL_PARAMS}
                self.title.text = 'Set simulation parameters for the {market_area} market area.'.format(market_area=self.iso)
            except KeyError:
                pass

    def on_enter(self):
        # change the navigation bar title
        ab = self.manager.nav_bar
        ab.build_valuation_advanced_nav_bar()
        ab.set_title('Single Run: Set Parameters')

        data_manager = App.get_running_app().data_manager
        MODEL_PARAMS = data_manager.get_valuation_model_params(self.iso)

        if not MODEL_PARAMS:
            popup = WarningPopup()
            popup.bind(on_dismiss=partial(ab.go_to_screen, 'load_data'))
            popup.dismiss_button.text = 'Go back'
            popup.popup_text.text = 'We need a market area in the "Select Data" screen selected first to populate this area.'
            popup.open()
        # else:
        #     self.go_button.bind(on_release=self.manager.get_screen('valuation_advanced').open_valuation_run_menu)

    def _validate_inputs(self):
        pass

    def get_inputs(self):
        self._validate_inputs()

        base_param_dict = {}

        # Check for any input into the parameter rows.
        for param_row in self.param_widget.children:
            param_name = param_row.name.text

            if param_row.text_input.text:
                param_value = float(param_row.text_input.text)
                base_param_dict[self.param_to_attr[param_name]] = param_value

        param_settings = [base_param_dict,]

        return param_settings
    
    def _generate_requests(self):
        data_screen = self.manager.get_screen('load_data')
        params_screen = self

        iso_selected, market_formulation_selected, node_selected, year_selected, month_selected = data_screen.get_inputs()
        param_settings = params_screen.get_inputs()

        requests = {'iso': iso_selected,
                    'market type': market_formulation_selected,
                    'months': [(month_selected, year_selected)],
                    'node id': node_selected,
                    'param set': param_settings
                    }

        return requests
    
    def execute_single_run(self, *args):
        try:
            requests = self._generate_requests()
        except ValueError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        except BadParameterException as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            solver_name = App.get_running_app().config.get('optimization', 'solver')

            handler = self.manager.get_screen('valuation_home').handler
            handler.solver_name = solver_name

            try:
                _, handler_status = handler.process_requests(requests)
            except BadParameterException as e:
                popup = WarningPopup()
                popup.popup_text.text = str(e)
                popup.open()
            else:
                self.completion_popup = ValuationSingleRunCompletePopup()
                self.completion_popup.view_results_button.bind(on_release=self._go_to_view_results)

                if not handler_status:
                    self.completion_popup.title = "Oops!"
                    self.completion_popup.popup_text.text = "The optimization model had issues being built and/or solved. This is most likely due to bad data. No results have been recorded."

                self.completion_popup.open()            
    
    def _go_to_view_results(self, *args):
        self.manager.nav_bar.go_to_screen('plot')
        self.completion_popup.dismiss()


class SetParameterRow(GridLayout):
    """Grid layout containing parameter descriptor label and text input field."""

    def __init__(self, desc, **kwargs):
        super(SetParameterRow, self).__init__(**kwargs)

        self._desc = desc
        self.name.text = self.desc['name']
        self.text_input.hint_text = str(self.desc['default'])

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value


class SetParameterWidget(GridLayout):
    """Grid layout containing rows of parameter adjustment widgets."""
    def __init__(self, **kwargs):
        super(SetParameterWidget, self).__init__(**kwargs)

    def build(self, iso):
        # Build the widget by creating a row for each parameter.
        data_manager = App.get_running_app().data_manager
        MODEL_PARAMS = data_manager.get_valuation_model_params(iso)

        for param in MODEL_PARAMS:
            row = SetParameterRow(desc=param)
            self.add_widget(row)
            setattr(self, param['attr name'], row)


class SetParamTextInput(TextInput):
    """
    A TextInput field for entering parameter value sweep range descriptors. Limited to float values.
    """
    def insert_text(self, substring, from_undo=False):
        # limit to 8 chars
        substring = substring[:8 - len(self.text)]
        return super(SetParamTextInput, self).insert_text(substring, from_undo=from_undo)


class ValuationSingleRunCompletePopup(ValuationRunCompletePopup):
    def __init__(self, **kwargs):
        super(ValuationSingleRunCompletePopup, self).__init__(**kwargs)

        self.popup_text.text = 'Your specified valuation job has been completed.'
