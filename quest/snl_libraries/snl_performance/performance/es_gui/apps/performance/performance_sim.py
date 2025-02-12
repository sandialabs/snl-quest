from __future__ import absolute_import, print_function

import logging
from functools import partial
import os
import shutil
import pandas as pd
import requests
import platform
import tarfile
import zipfile

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

from performance.es_gui.resources.widgets.common import MyPopup, WarningPopup, InputError, fade_in_animation, RecycleViewRow, ValuationRunCompletePopup # PopupLabel


class PerformanceSimScreenManager(ScreenManager):
    """Screen Manager for Performance tool."""

    def __init__(self, **kwargs):
        super(PerformanceSimScreenManager, self).__init__(**kwargs)

        # Add new screens here.
        self.add_widget(PerformanceSimDataScreen(name='data'))
        self.add_widget(PerformanceSimParamScreen(name='params'))
        self.add_widget(PerformanceSimSelectionsScreen(name='selections'))


class PerformanceSimRunScreen(Screen):
    """Main screen for Performance simulations."""

    def on_enter(self):
        """Set navigation bar title, check for energyplus, and create popups for running simulations."""
        ab = self.manager.nav_bar
        ab.set_title('Performance Simulations')

        self.check_eplus()

        self.warning_popup = WarningPopup()
        self.run_popup = PerformanceRunPopup()
        self.completion_popup = PerformanceSimCompletePopup()

    def _generate_requests(self):
        """Get the requested data from each screen."""
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
        """Run the performance simulation."""
        try:
            requests = self._generate_requests()
        except ValueError as e:
            self.warning_popup.popup_text.text = str(e)
            self.warning_popup.open()
        except InputError as e:
            self.warning_popup.popup_text.text = str(e)
            self.warning_popup.open()
        else:
            try:
                self.run_popup.run_open()
                self.manager.handler.process_requests(requests)
            except ModuleNotFoundError as e:
                logging.warning('PerformanceSim : {0}'.format(e))
                self.run_popup.dismiss()
                self.warning_popup.popup_text.text = str(e)
                self.warning_popup.open()
            else:
                self.run_popup.run_dismiss()
                self.completion_popup.view_results_button.bind(on_release=self._go_to_view_results)
                self.completion_popup.title = 'Success!'
                self.completion_popup.complete_open()

    def _go_to_view_results(self, *args):
        """Send user to the results viewer."""
        self.manager.nav_bar.go_to_screen('performance_results_viewer')
        self.completion_popup.complete_dismiss()

    def get_valuation_ops(self):
        """Get the completed QuESt Valuation optimization results."""
        valuation_ops = [op for op in self.manager.get_screen('valuation_home').handler.get_solved_ops()]

        valuationF = pd.DataFrame()
        while valuation_ops:
            root = valuation_ops[0]
            root_ls = [op for op in valuation_ops
                       if (op['iso'] == root['iso'] and op['market type'] == root['market type']
                           and op['node'] == root['node'] and op['year'] == root['year'])]
            rootF = pd.DataFrame({root['time']: root_ls})
            for op in root_ls:
                valuation_ops.pop(valuation_ops.index(op))

            valuationF = pd.concat([valuationF, rootF], axis=1)
        else:
            print('Success!')

        valuationF.columns = ['Valuation ' + col for col in valuationF.columns]
        self.sm.get_screen('data').valuation_ops = valuationF

    def get_btm_ops(self):
        """Get the data from all Behind-the-meter optimizations."""
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
            rootF = pd.DataFrame({root['time']: root_ls})
            for op in root_ls:
                btm_ops.pop(btm_ops.index(op))

            btmF = pd.concat([btmF, rootF], axis=1)
        else:
            print('Success!')

        btmF.columns = ['BTM ' + col for col in btmF.columns]
        self.sm.get_screen('data').btm_ops = btmF

    def check_eplus(self):
        """Ensure EnergyPlus and necessary python modules are installed."""
        try:
            from performance.es_gui.apps.performance.performance_sim_handler import PerformanceSimHandler
            data_manager = App.get_running_app().data_manager
            self.manager.handler = PerformanceSimHandler(os.path.join(data_manager.data_bank_root, 'output'))
        except ModuleNotFoundError as e:
            logging.warning('Performance: {}'.format(e))
            logging.warning('Performance: {}'.format(os.getcwd()+'\\energyplus'))
            popup = EnergyPlusPopup()
            if str(e) == "No module named 'pyenergyplus'":
                popup.open()
            elif str(e) == 'eppy':
                popup.popup_text.text = "This tool requires the python module eppy. Please pip install eppy on your machine."
                popup.open()
            else:
                popup.popup_text.text = "There is a required python module missing." \
                    + " Please visit your console window to determine which module you need to install."
                popup.open()
        # else:
            # self.get_valuation_ops()
            # self.get_btm_ops()
#            self.get_rates()


class PerformanceSimDataScreen(Screen):
    """Data selection screen for Performance Tool."""

    hvac = StringProperty('')
    location = StringProperty('')
    profile = StringProperty('')
    valuation_ops = None
    btm_ops = None

    def __init__(self, **kwargs):
        super(PerformanceSimDataScreen, self).__init__(**kwargs)

        HVACEntry.host_screen = LocationEntry.host_screen = ProfileEntry.host_screen = self

    def on_enter(self):
        """Reset screen on enter."""
        self._reset_screen()

    def _get_hvac_options(self):
        """Get input files from data bank."""
        data_manager = App.get_running_app().data_manager

        try:   
            hvac_options = data_manager.data_bank['idf files'].keys()
        except AttributeError:
            pass
        except KeyError:
            if not os.path.exists(os.path.join(data_manager.data_bank_root, 'idf')):
                print(os.path.join(data_manager.data_bank_root, 'idf'))
                popup = WarningPopup()
                popup.popup_text.text = "Looks like there are no EnergyPlus input files! Please visit the help tab to learn more."
                popup.open()
            else:
                data_root = os.path.join(data_manager.data_bank_root, 'idf')
                ls = [os.path.join(data_root, item) for item in os.listdir(data_root)]
                bool_ls = [True if os.path.isfile(item) else False for item in ls]

                if any(bool_ls):
                    bad_dir_popup = WarningPopup()
                    bad_dir_popup.popup_text.text = "There was an error processing the HVAC files." \
                        + " Please place your HVAC files in their own folder in the IDF directory."
                    bad_dir_popup.open()
                else:
                    popup = WarningPopup()
                    popup.popup_text.text = "Looks like there are no EnergyPlus input files! Please visit the help tab to learn more."
                    popup.open()
        else:
            self.hvac_select.values = [hvac_option for hvac_option in hvac_options] + ["Custom"]

    def _get_location_options(self):
        """Get weather data from data bank."""
        data_manager = App.get_running_app().data_manager

        try:
            location_options = data_manager.data_bank['weather files'].keys()
        except AttributeError:
            pass
        except KeyError:
            if not os.path.exists(os.path.join(data_manager.data_bank_root, 'weather')):
                popup = WarningPopup()
                popup.popup_text.text = "Looks like there are no weather files downloaded!" \
                    + " Please visit the Data Manager to download data or the help tab to learn more."
                popup.open()
            else:
                data_root = os.path.join(data_manager.data_bank_root, 'weather')
                ls = [os.path.join(data_root, item) for item in os.listdir(data_root)]
                bool_ls = [True if os.path.isfile(item) else False for item in ls]

                if any(bool_ls):
                    bad_dir_popup = WarningPopup()
                    bad_dir_popup.popup_text.text = "There was an error processing the weather files." \
                        + " Please place your weather files in their own folder in the weather directory."
                    bad_dir_popup.open()
                else:
                    popup = WarningPopup()
                    popup.popup_text.text = "Looks like there are no weather files downloaded!" \
                        + " Please visit the Data Manager to download data or the help tab to learn more."
                    popup.open()
        else:
            self.location_select.values = [location_option for location_option in location_options] + ["Custom"]

    def _get_profile_options(self):
        """Get profile options from data bank and btm/valuation runs."""
        data_manager = App.get_running_app().data_manager

        try:
            profile_options = [key for key in data_manager.data_bank['profiles'].keys()]
        except Exception as e:
            logging.warning(f"Performance: {e}")
            self.profile_select.values = ["Custom"]
        # except AttributeError as e:
        #     logging.warning("Performance: {} A1".format(e))
        #     popup = WarningPopup()
        #     popup.popup_text.text = "Looks like there are no battery charge/discharge profiles! Please visit the help tab for more info."
        #     popup.open()
        # except KeyError as e:
        #     logging.warning("Performance: {} Key1".format(e))
        #     if not os.path.exists(os.path.join(data_manager.data_bank_root, 'profile')):
        #         try:
        #             profile_options = [col for col in self.valuation_ops.columns] + [col for col in self.btm_ops.columns]
        #         except AttributeError as e:
        #             logging.warning("Performance: {} A2".format(e))
        #             popup = WarningPopup()
        #             popup.popup_text.text = "Looks like there are no battery charge/discharge profiles! Please visit the help tab for more info."
        #             popup.open()
        #         else:
        #             if profile_options:
        #                 self.profile_select.values = profile_options
        #             else:
        #                 popup = WarningPopup()
        #                 popup.popup_text.text = "Looks like there are no battery charge/discharge profiles! Please visit the help tab for more info."
        #                 popup.open()
        #     else:
        #         data_root = os.path.join(data_manager.data_bank_root, 'profile')
        #         ls = [os.path.join(data_root, item) for item in os.listdir(data_root)]
        #         bool_ls = [True if os.path.isfile(item) else False for item in ls]

        #         if any(bool_ls):
        #             bad_dir_popup = WarningPopup()
        #             bad_dir_popup.popup_text.text = "There was an error processing the weather files." \
        #                 + " Please place your weather files in their own folder in the weather directory."
        #             bad_dir_popup.open()
        #         else:
        #             try:
        #                 profile_options = [col for col in self.valuation_ops.columns] + [col for col in self.btm_ops.columns]
        #             except AttributeError as e:
        #                 logging.warning("Performance: {} A2".format(e))
        #                 popup = WarningPopup()
        #                 popup.popup_text.text = "Looks like there are no battery charge/discharge profiles! Please visit the help tab for more info."
        #                 popup.open()
        #             else:
        #                 if profile_options:
        #                     self.profile_select.values = profile_options
        #                 else:
        #                     popup = WarningPopup()
        #                     popup.popup_text.text = "Looks like there are no battery charge/discharge profiles! Please visit the help tab for more info."
        #                     popup.open()
        else:
            if profile_options:
                self.profile_select.values = profile_options + ["Custom"]
            else:
                # popup = WarningPopup()
                # popup.popup_text.text = "Looks like there are no battery charge/discharge profiles! Please visit the help tab for more info."
                # popup.open()
                self.profile_select.values = ["Custom"]

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

    def _hvac_selected(self):
        """Show input files."""
        self.hvac = self.hvac_select.text
        data_manager = App.get_running_app().data_manager
        hvac_root = os.path.join(data_manager.data_bank_root, 'idf')

        if self.hvac == 'Custom':
            popup = ChooseFilePopup(save_dir = hvac_root)
            popup.open()
            popup.on_dismiss = self._show_hvac_options
        else:
            self._show_hvac_options()


    def _show_hvac_options(self):
        """Show available HVAC idf files"""
        data_manager = App.get_running_app().data_manager
        data_manager.scan_performance_data_bank()

        try:
            self.hvac_rv.data = [{'name': idf_files[0], 'path':idf_files[1]}
                                 for idf_files in data_manager.data_bank['idf files'][self.hvac]]
        except AttributeError:
            pass
        else:
            Clock.schedule_once(partial(fade_in_animation, self.hvac_select_bx), 0)

    def _location_selected(self):
        """Show weather files."""
        self.location = self.location_select.text
        data_manager = App.get_running_app().data_manager
        loc_root = os.path.join(data_manager.data_bank_root, 'weather')

        if self.location == 'Custom':
            popup = ChooseFilePopup(save_dir = loc_root)
            popup.open()
            popup.on_dismiss = self._show_loc_options
        else:
            self._show_loc_options()

    def _show_loc_options(self):
        """Show available weather files"""
        data_manager = App.get_running_app().data_manager
        data_manager.scan_performance_data_bank()

        try:
            self.location_rv.data = [{'name': location_files[0], 'path':location_files[1]}
                                     for location_files in data_manager.data_bank['weather files'][self.location] if '.epw' in location_files[0]]

        except AttributeError:
            pass
        else:
            Clock.schedule_once(partial(fade_in_animation, self.location_select_bx), 0)

    def _profile_selected(self):
        """Show selectable charge/discharge profiles."""
        self.profile = self.profile_select.text
        data_manager = App.get_running_app().data_manager
        profile_root = os.path.join(data_manager.data_bank_root, 'profile')
        if not os.path.exists(profile_root):
            os.mkdir(profile_root)

        if self.profile == 'Custom':
            popup = ChooseFilePopup(save_dir = profile_root)
            popup.open()
            popup.on_dismiss = self._show_profile_options
        else:
            self._show_profile_options()


    def _show_profile_options(self):
        """Show available profiles"""
        data_manager = App.get_running_app().data_manager
        data_manager.scan_performance_data_bank()
        print(data_manager.data_bank)

        try:
            self.profile_rv.data = [{'name': profile_files[0], 'path':profile_files[1], 'op':None}
                                        for profile_files in data_manager.data_bank['profiles'][self.profile]]
        except AttributeError:
            pass
        else:

            Clock.schedule_once(partial(fade_in_animation, self.profile_select_bx), 0)

    def _validate_inputs(self):
        """Ensure proper selections are made."""
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
        """Get data selections."""
        self._validate_inputs()

        hvac_selected = self.hvac_to_sim
        location_selected = self.location_to_sim
        profile_selected = self.profile_to_sim

        return hvac_selected, location_selected, profile_selected


class PerformanceSimParamScreen(Screen):
    """Screen to set parameters for performance simulations."""

    iso = StringProperty('')
    param_to_attr = dict()
    built = False

    def on_enter(self):
        """Build parameter widget."""
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
        """Ensure inputs are made."""
        if len(self.param_widget.children) == 0:
            popup = WarningPopup()
            popup.popup_text.text = 'Please specify the simulation parameters.'
            popup.open()

    def get_inputs(self):
        """Get parameters."""
        self._validate_inputs()

        param_settings = self.param_widget.get_inputs(use_hint_text=True)

        return param_settings


class PerformanceSimSelectionsScreen(Screen):
    """Show the performance simulation data and parameter selections."""

    MODEL_PARAMS = {
        'eCap': 'Energy Capacity (MWh)',
        'pRat': 'Power Rating (MW)',
        'n_s': 'Self-Discharge Efficiency',
        'n_p': 'Power Electronics Efficiency',
        'q_rate': 'Battery Cell Ah Rating',
        'v_rate': 'Battery Cell Voltage Rating',
        'r': 'Battery Cell Internal Resistance',
        'k': 'Battery Cell k Parameter',
        'tau': 'Time Step (hr)',
        'h_setpoint': 'Heating Setpoint (C)',
        'c_setpoint': 'Cooling Setpoint (C)',
        'insulation': 'Insulation (m\u00b2 K/W)'
    }

    def __init__(self, **kwargs):
        super(PerformanceSimSelectionsScreen, self).__init__(**kwargs)

    def on_enter(self):
        """Show all of the selections."""
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
        param_settings = [self.MODEL_PARAMS[param] + ': {}'.format(param_inputs[param]) for param in param_inputs]

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
    """Popup for completed simulation."""

    def __init__(self, **kwargs):
        super(PerformanceSimCompletePopup, self).__init__(**kwargs)

        self.popup_text.text = 'Your performance simulation is completed.'

    def complete_open(self):
        """Open popup from main thread."""
        Clock.schedule_once(self.open)

    def complete_dismiss(self):
        """Close popup from main thread."""
        Clock.schedule_once(self.dismiss)


class PerformanceRunPopup(MyPopup):
    """Popup to ensure the user that the tool is running."""

    def __init__(self, **kwargs):
        super(PerformanceRunPopup, self).__init__(**kwargs)

        self.popup_text.text = 'Performance simulation is running. This may take a few minutes.'

    def run_open(self):
        """Open popup from main thread."""
        Clock.schedule_once(self.open)

    def run_dismiss(self):
        """Close popup from main thread."""
        Clock.schedule_once(self.dismiss)


class EnergyPlusPopup(MyPopup):
    """Warning popup if EnergyPlus is missing."""

    def __init__(self, **kwargs):
        super(EnergyPlusPopup, self).__init__(**kwargs)
        self.eplus_url = "http://api.github.com/repos/NREL/Energyplus/releases/latest"
        self.sys = platform.system()
        self.machine = platform.machine()
        self.platform = platform.platform().split("-")
        self.download = None
        self.target_path = None
        self.popup_text.text = 'EnergyPlus not found. Please visit the help tab to configure Energyplus on your machine.'

    def download_energyplus(self):
        eplus_url = "http://api.github.com/repos/NREL/Energyplus/releases/latest"

        try:
            response = requests.get(eplus_url, stream=True)
            assets_ls = response.json()['assets']
        except Exception as e:
            logging.warning(f"Performance: Energyplus request failed - {e}")
        else:
            self._asset_loop(assets_ls)
            self._download()

    def _asset_loop(self, assets_ls):
        potential_download_url = []
        osys = None
        if self.sys == 'Darwin':
            # osys = self.platform[0] + self.platform[1]
            machine = self.platform[2] + '.tar.gz'
        elif self.sys == 'Windows':
            if self.machine in ['x86', 'x64']:
                machine = 'x86_64.zip'
            else:
                machine = self.machine + '.zip'

        for asset in assets_ls:
            name_ls = asset['name'].split('-')
            if (self.sys in name_ls) and (machine in name_ls):
                self.download = (asset['browser_download_url'], asset['name'])
            elif (self.sys in name_ls) and (machine in name_ls):
                potential_download_url.append((asset['browser_download_url'], asset['name']))

        if (self.download == None) and (potential_download_url):
            self.download = potential_download_url[-1]

    def _download(self):
        if self.sys == 'Darwin':
            target_path = 'energyplus.tar'
        elif self.sys == 'Windows':
            target_path = 'energyplus.zip'

        

        try:
            download_response = requests.get(self.download[0], stream=True)
            if self.sys == 'Darwin':
                target_path = 'energyplus.tar'
                with open(target_path, 'wb') as f:
                    f.write(download_response.raw.read())
                with tarfile.open(target_path) as tar:
                    tar.extractall()
            elif self.sys == 'Windows':
                target_path = 'energyplus.zip'
                with open(target_path, 'wb') as f:
                    f.write(download_response.raw.read())
                with zipfile.open(target_path) as zip:
                    zip.extractall()

            os.rename('-'.join([x if (('tar' not in x) and ('zip' not in x)) else x.split('.')[0] for x in self.download[1].split('-')]), 'energyplus')
            os.remove(target_path)
        except Exception as e:
            logging.warning(f"Performance: Download failed - {e}")

class ChooseFilePopup(MyPopup):
    def __init__(self, save_dir, **kwargs):
        super(ChooseFilePopup, self).__init__(**kwargs)
        # file_load= FileChooserListView()
        # self.content = file_load
        self.selection = None
        self.save_dir = save_dir
        self.file_name_popup = FileNamePopup()

    def run_open(self):
        """Open popup from main thread."""
        Clock.schedule_once(self.open)

    def run_dismiss(self):
        """Close popup from main thread."""
        Clock.schedule_once(self.dismiss)

    def enter_name(self):
        """Ask user for entry name"""
        self.selection = self.file_chooser.selection[0]
        self.file_name_popup.open()
        self.file_name_popup.button.on_press = lambda: self.file_name_popup.move_selection(self.selection, self.save_dir)

class FileNamePopup(MyPopup):
    def __init__(self, **kwargs):
        super(FileNamePopup, self).__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")
        self.name = TextInput()
        self.button = Button(text="Enter")
        layout.add_widget(self.name)
        layout.add_widget(self.button)

        self.title = "Enter source name"
        self.content = layout

    def run_open(self):
        """Open popup from main thread."""
        Clock.schedule_once(self.open)

    def run_dismiss(self):
        """Close popup from main thread."""
        Clock.schedule_once(self.dismiss)

    def move_selection(self, selection, data_dir):
        """Return entered name"""
        src_file = selection
        file_name = os.path.basename(src_file)
        data_dir_base = os.path.basename(data_dir)

        if data_dir_base == "profiles":
            dst_file = os.path.join(data_dir, file_name)
        else:
            dst_dir = os.path.join(data_dir, self.name.text)
            dst_file = os.path.join(dst_dir, file_name)

            if not os.path.exists(dst_dir):
                os.mkdir(dst_dir)

        shutil.copyfile(src_file, dst_file)
        self.run_dismiss()

class HVACEntry(RecycleViewRow):
    """HVAC entry for recycle view."""

    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(HVACEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.hvac_to_sim = rv.data[self.index]
        # else:
        #     self.host_screen.node = ''


class LocationEntry(RecycleViewRow):
    """Location entry for recycle view."""

    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(LocationEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.location_to_sim = rv.data[self.index]
        # else:
        #     self.host_screen.node = ''


class ProfileEntry(RecycleViewRow):
    """Profile Entry for recycle view."""

    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(ProfileEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            if not rv.data[self.index] in self.host_screen.profile_to_sim:
                self.host_screen.profile_to_sim += [rv.data[self.index]]
        # else:
        #     self.host_screen.node = ''