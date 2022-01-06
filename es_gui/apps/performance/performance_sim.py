from __future__ import absolute_import, print_function

import logging
from functools import partial
import webbrowser
import calendar
import os
import numpy as np
import threading
import json
import pandas as pd

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

# from es_gui.apps.valuation.reporting import Report
#from .reporting import BtmCostSavingsReport
from es_gui.resources.widgets.common import MyPopup, WarningPopup, InputError, fade_in_animation, RecycleViewRow, PerformanceParameterRow, ParameterGridWidget, ValuationRunCompletePopup


class PerformanceSimScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(PerformanceSimScreenManager, self).__init__(**kwargs)

        # Add new screens here.
        self.add_widget(PerformanceSimDataScreen(name='data'))
        self.add_widget(PerformanceSimParamScreen(name='params'))
        self.add_widget(PerformanceSimSelectionsScreen(name='selections'))
        
        
class PerformanceSimRunScreen(Screen):
    def on_enter(self):
        # Change the navigation bar title.
        ab = self.manager.nav_bar
        ab.set_title('Performance Simulations')
        
        self.check_eplus()

    def _generate_requests(self):
        data_screen = self.sm.get_screen('data')
        params_screen = self.sm.get_screen('params')

        hvac, location, profile = data_screen.get_inputs()
        param_settings = params_screen.get_inputs()

        requests = {'hvac': hvac,
                    'location': location,
                    'profile': profile,
                    'params': param_settings
                    }

        return requests

    def run_batch(self):
        
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
        else:
            try:
                run_popup = PerformanceRunPopup()
                run_popup.open()
                results = self.manager.handler.process_requests(requests)
            except BadRunException as e:
                run_popup.dismiss()
                popup = WarningPopup()
                popup.popup_text.text = str(e)
                popup.open()
            else:
                run_popup.dismiss()
                self.completion_popup = PerformanceSimCompletePopup()
                self.completion_popup.view_results_button.bind(on_release=self._go_to_view_results)

                self.completion_popup.title = 'Success!'
                self.completion_popup.open()            

    def _go_to_view_results(self, *args):
        self.manager.nav_bar.go_to_screen('performance_results_viewer')
        self.completion_popup.dismiss()
        
    def get_valuation_ops(self):
        valuation_ops = [op for op in self.manager.get_screen('valuation_home').handler.get_solved_ops()]
         
        valuationF = pd.DataFrame()
        while valuation_ops:
            root = valuation_ops[0]
            root_ls = [op for op in valuation_ops 
                      if (op['iso'] == root['iso'] and op['market type'] == root['market type']
                      and op['node'] == root['node'] and op['year'] == root['year'])]
            for op in root_ls:
                valuation_ops.pop(valuation_ops.index(op))
            valuationF[root['time']] = root_ls
        else:
            print('Success!')
            
        valuationF.columns = ['Valuation ' + col for col in valuationF.columns]
        self.sm.get_screen('data').valuation_ops = valuationF
        
    def get_btm_ops(self):
        btm_ops = [op for op in self.manager.get_screen('btm_home').handler.get_solved_ops()]
        
        for op in btm_ops:
            string = op['name']
            spl_str = string.split(' | ')
            op['rate'] = spl_str[2]
            op['pv'] = spl_str[3]
            op['load'] = spl_str[4]
        
        btmF = pd.DataFrame()
        while btm_ops:
            root = btm_ops[0]
            root_ls = [op for op in btm_ops 
                      if (op['params'] == root['params'] and op['rate'] == root['rate']
                      and op['pv'] == root['pv'] and op['load'] == root['load'])]

            for op in root_ls:
                btm_ops.pop(btm_ops.index(op))
            btmF[root['time']] = root_ls
        else:
            print('Success!')
           
        btmF.columns = ['BTM ' + col for col in btmF.columns]
        self.sm.get_screen('data').btm_ops = btmF
        
#    def get_rates(self):
#        try:
#            data_manager = App.get_running_app().data_manager
#            data_manager._scan_rate_structure_data_bank()
#            rate_structure_options = [rs[1] for rs in data_manager.get_rate_structures().items()]
#            self.sm.get_screen('data').rates = rate_structure_options
#        except KeyError as e:
#            logging.warning('CostSavings: No rate structures available to select.')
#            # TODO: Warning popup
#        
##        Clock.schedule_once(partial(fade_in_animation, self.content), 0)
        
    def check_eplus(self):
        
        try:
            from es_gui.apps.performance.performance_sim_handler import BadRunException, PerformanceSimHandler
            data_manager = App.get_running_app().data_manager
            self.manager.handler = PerformanceSimHandler(os.path.join(data_manager.data_bank_root,'output'))
        except ModuleNotFoundError:
            popup = EnergyPlusPopup()
            popup.open()
        else:
            self.get_valuation_ops()
            self.get_btm_ops()
#            self.get_rates()
        
class PerformanceSimDataScreen(Screen):
    hvac = StringProperty('')
    location = StringProperty('')
    profile = StringProperty('')
    valuation_ops = None
    btm_ops = None
#    rates = None

    def __init__(self, **kwargs):
        super(PerformanceSimDataScreen, self).__init__(**kwargs)
        
        HVACEntry.host_screen = LocationEntry.host_screen = ProfileEntry.host_screen = self
        
    def on_enter(self):
        self._reset_screen()
    
    def _get_hvac_options(self):
        try:
            data_manager = App.get_running_app().data_manager
        except AttributeError:
            pass
        else:
            hvac_options = data_manager.data_bank['idf files'].keys()
            self.hvac_select.values = [hvac_option for hvac_option in hvac_options]
            
    def _get_location_options(self):
        try:
            data_manager = App.get_running_app().data_manager
        except AttributeError:
            pass
        else:
            location_options = data_manager.data_bank['weather files'].keys()
            self.location_select.values = [location_option for location_option in location_options]
            
    def _get_profile_options(self):
        try:
            data_manager = App.get_running_app().data_manager
        except AttributeError:
            pass
        else:
            profile_options = [key for key in data_manager.data_bank['profiles'].keys()] + [col for col in self.valuation_ops.columns] + [col for col in self.btm_ops.columns]
            self.profile_select.values = profile_options
            
#    def _get_rate_options(self):
#        self.rate_select.values = [key['name'] for key in self.rates]

    def _reset_screen(self):

        # Deselects all RV selections.
        self.hvac_rv.deselect_all_nodes()
        self.location_rv.deselect_all_nodes()
        self.profile_rv.deselect_all_nodes()

        # Resets properties.
        self.hvac = ''
        self.location = ''
        self.profile = ''
        self.hvac_to_sim = None
        self.location_to_sim = None
        self.profile_to_sim = []
#        self.rate_to_sim = None

    def _hvac_selected(self):
        self.hvac = self.hvac_select.text
        
        try:
            data_manager = App.get_running_app().data_manager
#            print(data_manager.data_bank['idf files'])
#            print(self.hvac)
            self.hvac_rv.data = [{'name':idf_files[0],'path':idf_files[1]} 
            for idf_files in data_manager.data_bank['idf files'][self.hvac]] 
#            print(self.hvac_rv.data)
            
        except AttributeError:
            pass
        else:
            Clock.schedule_once(partial(fade_in_animation, self.hvac_select_bx), 0)
        
    def _location_selected(self):
        self.location = self.location_select.text
        
        try:
            data_manager = App.get_running_app().data_manager
            
            self.location_rv.data = [{'name':location_files[0],'path':location_files[1]}
            for location_files in data_manager.data_bank['weather files'][self.location] if '.epw' in location_files[0]] 
            
        except AttributeError:
            pass
        else:
            Clock.schedule_once(partial(fade_in_animation, self.location_select_bx), 0)
        
        
    def _profile_selected(self):
        self.profile = self.profile_select.text
        
        try:
            data_manager = App.get_running_app().data_manager
            profiles = data_manager.data_bank['profiles']
            if self.profile in profiles:
                self.profile_rv.data = [{'name':profile_files[0],'path':profile_files[1],'op':None}
                for profile_files in data_manager.data_bank['profiles'][self.profile]]
            elif self.profile in self.btm_ops.columns:
                self.profile_rv.data = [{'name':op['month'],'path':None,'op':op} for op in self.btm_ops[self.profile]]
            elif self.profile in self.valuation_ops.columns:
                self.profile_rv.data = [{'name':op['month'],'path':None,'op':op} for op in self.valuation_ops[self.profile]]
            else:
                print('The selected profile does not exist')
            
        except AttributeError:
            pass
        else:
            Clock.schedule_once(partial(fade_in_animation, self.profile_select_bx), 0)
            
#    def _rate_selected(self):
#        self.rate = self.rate_select.text
#        self.rate_rv = self.rates
#        Clock.schedule_once(partial(fade_in_animation,self.rate_select_bx),0)
            

    def _validate_inputs(self):
        if self.hvac_select.text == 'Select HVAC':
            popup = WarningPopup()
            popup.popup_text.text = 'Please select an HVAC.'
            popup.open()

        if self.location_select.text == 'Select location':
            popup = WarningPopup()
            popup.popup_text.text = 'Please select a location.'
            popup.open()

        if self.profile_select.text == 'Select profile':
            popup = WarningPopup()
            popup.popup_text.text = 'Please select a charge/discharge profile.'
            popup.open()

    def get_inputs(self):
        self._validate_inputs()
        
        hvac_selected = self.hvac_to_sim
        location_selected = self.location_to_sim
        profile_selected = self.profile_to_sim
#        rate_selected = self.rate_to_sim

        return hvac_selected,location_selected,profile_selected#,rate_selected

class PerformanceSimParamScreen(Screen):
    iso = StringProperty('')
    param_to_attr = dict()
    built = False
    
    def on_enter(self):
        
        if not self.built:
            self.built = self.param_widget.build()

    def _disable_text_input(self, text):
        # Disables the text input field of the parameter selected for a parameter sweep.
        for row_widget in self.param_widget.children:
            row_widget.text_input.disabled = False

        attr_name = self.param_to_attr.get(text, '')

        if attr_name:
            param_widget_row = getattr(self.param_widget, attr_name, None)
            param_widget_row.text_input.disabled = True

    def _validate_inputs(self):
        if len(self.param_widget.children) == 0:
            popup = WarningPopup()
            popup.popup_text.text = 'Please specify the simulation parameters.'
            popup.open()

    def get_inputs(self):
        self._validate_inputs()

        param_settings = self.param_widget.get_inputs(use_hint_text=True)

        return param_settings
    
class PerformanceSimSelectionsScreen(Screen):
    """"""
    
    def __init__(self,**kwargs):
        super(PerformanceSimSelectionsScreen,self).__init__(**kwargs)
        
    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)
        
        data_screen = self.manager.get_screen('data')
        params_screen = self.manager.get_screen('params')
        
        hvac = data_screen.hvac
        location = data_screen.location
        profile = data_screen.profile
        hvac_to_sim = data_screen.hvac_to_sim['name']
        location_to_sim = data_screen.location_to_sim['name']
        profile_to_sim = data_screen.profile_to_sim
        param_inputs = params_screen.get_inputs()
        param_settings = [param + ': {}'.format(param_inputs[param]) for param in param_inputs]
        
        hvac_text = '\n    '.join(['[b]HVAC:[/b]',
                               hvac,
                               hvac_to_sim])
        self.hvac_label.text = hvac_text
                    
        location_text = '\n    '.join(['[b]Location:[/b]',
                                   location,
                                   location_to_sim])
        self.location_label.text = location_text
                    
        profile_text = '\n    '.join(['[b]Profile:[/b]',
                                 profile,
                                 ]+[profile['name'] for profile in profile_to_sim])
        self.profile_label.text = profile_text
                    
        params_text = '[b]System Parameters:[/b]\n    '
        params_text += '\n    '.join(param_settings)
        self.params_label.text = params_text

    
class PerformanceSimCompletePopup(ValuationRunCompletePopup):
    def __init__(self, **kwargs):
        super(PerformanceSimCompletePopup, self).__init__(**kwargs)

        self.popup_text.text = 'Your performance simulation is completed.'
        
class PerformanceRunPopup(MyPopup):
    def __init__(self, **kwargs):
        super(PerformanceRunPopup, self).__init__(**kwargs)
        
        self.popup_text.text = 'Performance simulation is running. This may take a few minutes.'
        
class EnergyPlusPopup(WarningPopup):
    def __init__(self,**kwargs):
        super(EnergyPlusPopup,self).__init__(**kwargs)
        
        self.popup_text.text = 'EnergyPlus not found. Please visit the help tab to configure Energyplus on your machine.'
        
class HVACEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """
        Respond to the selection of items in the view.
        """
        super(HVACEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.hvac_to_sim = rv.data[self.index]
        # else:
        #     self.host_screen.node = ''
        
class LocationEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """
        Respond to the selection of items in the view.
        """
        super(LocationEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.location_to_sim = rv.data[self.index]
        # else:
        #     self.host_screen.node = ''
        
class ProfileEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """
        Respond to the selection of items in the view.
        """
        super(ProfileEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.profile_to_sim += [rv.data[self.index]]
        # else:
        #     self.host_screen.node = ''
        
#class RateEntry(RecycleViewRow):
#    host_screen = None
#
#    def apply_selection(self, rv, index, is_selected):
#        """
#        Respond to the selection of items in the view.
#        """
#        super(RateEntry, self).apply_selection(rv, index, is_selected)
#
#        if is_selected:
#            self.host_screen.profile_to_sim = [rv.data[self.index]]
#        # else:
#        #     self.host_screen.node = ''