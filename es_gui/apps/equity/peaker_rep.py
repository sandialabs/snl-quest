from __future__ import absolute_import, print_function

import logging
from functools import partial
import webbrowser
import calendar
import os
import numpy as np
import threading
import json

from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition, ScreenManagerException
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, ListProperty, DictProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox

# from es_gui.apps.valuation.reporting import Report
from .reporting import PeakerRepReport
from es_gui.resources.widgets.common import BodyTextBase, MyPopup, WarningPopup, TileButton, RecycleViewRow, InputError, BASE_TRANSITION_DUR, BUTTON_FLASH_DUR, ANIM_STAGGER, FADEIN_DUR, SLIDER_DUR, PALETTE, rgba_to_fraction, fade_in_animation, slow_blinking_animation, WizardCompletePopup, ParameterRow, ParameterGridWidget
from es_gui.apps.data_manager.data_manager import DATA_HOME


from es_gui.tools.equity.readdata import get_pv_profile_string
from es_gui.tools.equity.readdata import get_power_plant_string


class PeakerRepWizard(Screen):
    """The main screen for the cost savings wizard. This hosts the nested screen manager for the actual wizard."""
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.set_title('ES+PV Peaker Replacement')

        # self.sm.generate_start()

    def on_leave(self):
        # Reset wizard to initial state by removing all screens except the first.
        self.sm.current = 'start_peaker'

        if len(self.sm.screens) > 1:
            self.sm.clear_widgets(screens=self.sm.screens[1:])


class PeakerRepWizardScreenManager(ScreenManager):
    """The screen manager for the peaker plant replacement wizard screens."""
    def __init__(self, **kwargs):
        super(PeakerRepWizardScreenManager, self).__init__(**kwargs)

        self.transition = SlideTransition()
        self.add_widget(PeakerRepWizardStart(name='start_peaker'))


class PeakerRepWizardStart(Screen):
    """The starting/welcome screen for the peaker replacement wizard."""
    def _next_screen(self):
        if not self.manager.has_screen('plant_select_peaker'):
            screen = PeakerRepWizardPlantSelect(name='plant_select_peaker')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'plant_select_peaker'

class PeakerRepWizardPlantSelect(Screen):
    """The power plant selection screen for the peaker replacement wizard."""
    power_plant_selected = DictProperty()
    has_selection = BooleanProperty(False)
    imported_data_selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(PeakerRepWizardPlantSelect, self).__init__(**kwargs) 

        PeakerRepPowerPlantRecycleViewRow.power_plnat_screen = self

    def on_enter(self):
        try:
            data_manager = App.get_running_app().data_manager
            #print([x[1] for x in data_manager.get_plants().items()])
            plant_options = [
                {
                'name': x[0], 'path': x[1], 'descriptors': get_power_plant_string(x[1])
                }  
                for x in data_manager.get_plants().items()
                ]
            self.power_plant_rv.data = plant_options
            self.power_plant_rv.unfiltered_data = plant_options
        except Exception as e:
            print(e)
        
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)

    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0
    
    def on_plant_selected(self, instance, value):
        try:
            logging.info('PeakerRep: power plant selection changed to {0}.'.format(value['Name']))
        except KeyError:
            logging.info('PeakerRep: power plant selection reset.')
            self.has_selection = False
        else:
            self.has_selection = True
            self.imported_data_selected = False
    
    def on_imported_data_selected(self, instance, value):
        if value:
            self.open_data_importer_button.text = 'Data imported'
            self.open_data_importer_button.background_color = rgba_to_fraction(PALETTE[3])
            Clock.schedule_once(partial(slow_blinking_animation, self.open_data_importer_button), 0)

            self.power_plant_rv.deselect_all_nodes()
        else:
            self.open_data_importer_button.text = 'Open data importer'
            self.open_data_importer_button.background_color = rgba_to_fraction(PALETTE[0])
            self.open_data_importer_button.opacity = 1
            Animation.cancel_all(self.open_data_importer_button, 'opacity')

    def _validate_inputs(self):
        return self.power_plant_selected
    
    def get_selections(self):
        """Retrieves screen's selections."""
        try:
            power_plant_selected = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            return power_plant_selected
    
    def _next_screen(self):
        if not self.manager.has_screen('system_parameters_peaker'):
            screen = PeakerRepWizardSystemParameters(name='system_parameters_peaker')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'system_parameters_peaker'          
        

class PeakerRepPowerPlantRecycleViewRow(RecycleViewRow):
    """The representation widget for node in the Power Plant selector RecycleView."""
    power_plnat_screen = None

    def on_touch_down(self, touch):
        """Add selection on touch down."""
        if super(PeakerRepPowerPlantRecycleViewRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected

        if is_selected:
            self.power_plnat_screen.power_plant_selected = rv.data[self.index]
    
    def deselect_node(self):
        super(PeakerRepPowerPlantRecycleViewRow, self).deselect_node(self)



class PeakerRepWizardSystemParameters(Screen):
    """"""

    def on_pre_enter(self):
        if not self.param_widget.children:
            self.param_widget.build()
    
    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)
    
    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0
    
    def _validate_inputs(self):
        replacement_fractions = []
        if self.rf_10_button.state == 'down':
            replacement_fractions.append(0.1)
        if self.rf_20_button.state == 'down':
            replacement_fractions.append(0.2)
        if self.rf_30_button.state == 'down':
            replacement_fractions.append(0.3)
        if self.rf_40_button.state == 'down':
            replacement_fractions.append(0.4)
        if self.rf_50_button.state == 'down':
            replacement_fractions.append(0.5)
        if self.rf_60_button.state == 'down':
            replacement_fractions.append(0.6)
        if self.rf_70_button.state == 'down':
            replacement_fractions.append(0.7)
        if self.rf_80_button.state == 'down':
            replacement_fractions.append(0.8)
        if self.rf_90_button.state == 'down':
            replacement_fractions.append(0.9)
        if self.rf_100_button.state == 'down':
            replacement_fractions.append(1.0)

        params = self.param_widget.get_inputs()
        params[0]['replacement_fractions'] = replacement_fractions
        params_desc = self.param_widget.get_input_strings()
        replacement_fractions_desc = 'powerplant replacement fractions: '
        for i in range(len(replacement_fractions)):
            replacement_fractions_desc += str(replacement_fractions[i]) + ', '
        params_desc.append(replacement_fractions_desc)

        return params, params_desc

    def get_selections(self):
        """Retrieves screen's selections."""
        try:
            params, params_desc = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            return params, params_desc
    
    def _next_screen(self):
        if not self.manager.has_screen('peaker_summary'):
            screen = PeakerRepWizardSummary(name='peaker_summary')
            self.manager.add_widget(screen)
        
        try:
            self.get_selections()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            self.manager.transition.duration = BASE_TRANSITION_DUR
            self.manager.transition.direction = 'left'
            self.manager.current = 'peaker_summary'



class PeakerRepParameterWidget(ParameterGridWidget):
    """Grid layout containing rows of parameter adjustment widgets."""
    def build(self):
        # Build the widget by creating a row for each parameter.
        data_manager = App.get_running_app().data_manager
        MODEL_PARAMS = data_manager.get_equity_analysis_params()

        for param in MODEL_PARAMS:
            row = ParameterRow(desc=param)
            self.add_widget(row)
            setattr(self, param['attr name'], row)


class PeakerRepWizardSummary(Screen):
    """"""
    def get_selections(self):
        sm = self.manager

        op_handler_requests = {}

        op_handler_requests['plant_data'] = sm.get_screen('plant_select_peaker').get_selections()
        op_handler_requests['params'], op_handler_requests['param desc'] = sm.get_screen('system_parameters_peaker').get_selections()

        return op_handler_requests

    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)

        op_handler_requests = self.get_selections()
        plant_data = op_handler_requests['plant_data']
        #pv_profile = op_handler_requests['pv_profile']
        system_params = op_handler_requests['param desc']

        # Power plant data label.
        plant_data_text = '[b]Power Plant Data:[/b]\n'
        plant_data_text += '\n'.join(plant_data.get('descriptors', ['None selected']))
        self.plant_data_label.text = plant_data_text

        # System parameters label.
        system_parameters_text = '[b]System Parameters:[/b]\n'
        system_parameters_text += '\n'.join(system_params)
        self.system_parameters_label.text = system_parameters_text
    
    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0

    def _next_screen(self):
        if not self.manager.has_screen('execute_peaker'):
            screen = PeakerRepWizardExecute(name='execute_peaker')
            self.manager.add_widget(screen)
        
        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'execute_peaker'


class PeakerRepWizardExecute(Screen):
    """The screen for executing the prescribed optimizations for the cost savings wizard."""
    solved_ops = []
    report_attributes = {}

    def on_enter(self):
        self.execute_run()

    # def on_leave(self):
    #     self.progress_label.text = 'This may take a while. Please wait patiently!'

    def execute_run(self):
        equity_home = self.manager.parent.parent.manager.get_screen('equity_home')
        ss = self.manager.get_screen('peaker_summary')

        op_handler_requests = ss.get_selections()

        # Send requests to handler.
        handler = equity_home.handler
        handler.solver_name = App.get_running_app().config.get('optimization', 'solver')



        self.solved_ops, handler_status = handler.process_requests(op_handler_requests)

        popup = WizardCompletePopup()

        # Check PeakerOp handler status.
        if len(handler_status) > 0:
            if self.solved_ops:
                # At least one model solved successfully.
                popup.title = "Success!*"
                popup.popup_text.text = '\n'.join([
                    'All finished, but we found these issues:',
                ]
                + list(handler_status)
                )
            else:
                # No models solved successfully.
                popup.title = "Hmm..."
                popup.popup_text.text = '\n'.join([
                    'Unfortunately, none of the models were able to be solved. We found these issues:',
                ]
                + list(handler_status)
                )

                popup.results_button.text = "Take me back"
                popup.bind(on_dismiss=lambda x: self.manager.parent.parent.manager.nav_bar.go_up_screen())  # Go back to Equity Home
                popup.open()
                return
        
        self.report_attributes = op_handler_requests

        popup = WizardCompletePopup()

        # if not handler_status:
        #     popup.title = "Success!*"
        #     popup.popup_text.text = "All calculations finished. Press 'OK' to proceed to the results.\n\n*At least one model (month) had issues being built and/or solved. Any such model will be omitted from the results."

        popup.bind(on_dismiss=self._next_screen)
        popup.open()

    def _next_screen(self, *args):
        """Adds the report screen if it does not exist and changes screens to it."""
        report = PeakerRepReport(name='report', chart_data=self.solved_ops, report_attributes=self.report_attributes)
        self.manager.switch_to(report, direction='left', duration=BASE_TRANSITION_DUR)
