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

# from es_gui.apps.valuation.reporting import Report
from .reporting import BtmCostSavingsReport
from es_gui.resources.widgets.common import BodyTextBase, MyPopup, WarningPopup, TileButton, RecycleViewRow, InputError, BASE_TRANSITION_DUR, BUTTON_FLASH_DUR, ANIM_STAGGER, FADEIN_DUR, SLIDER_DUR, PALETTE, rgba_to_fraction, fade_in_animation, slow_blinking_animation, WizardCompletePopup, ParameterRow, ParameterGridWidget
from es_gui.proving_grounds.data_importer import DataImporter
from es_gui.apps.data_manager.data_manager import DATA_HOME
from es_gui.tools.btm.readutdata import get_pv_profile_string


class CostSavingsWizard(Screen):
    """The main screen for the cost savings wizard. This hosts the nested screen manager for the actual wizard."""
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.set_title('Time-of-Use Cost Savings')

        # self.sm.generate_start()

    def on_leave(self):
        # Reset wizard to initial state by removing all screens except the first.
        self.sm.current = 'start'

        if len(self.sm.screens) > 1:
            self.sm.clear_widgets(screens=self.sm.screens[1:])


class CostSavingsWizardScreenManager(ScreenManager):
    """The screen manager for the cost savings wizard screens."""
    def __init__(self, **kwargs):
        super(CostSavingsWizardScreenManager, self).__init__(**kwargs)

        self.transition = SlideTransition()
        self.add_widget(CostSavingsWizardStart(name='start'))


class CostSavingsWizardStart(Screen):
    """The starting/welcome screen for the cost savings wizard."""
    def _next_screen(self):
        if not self.manager.has_screen('rate_select'):
            screen = CostSavingsWizardRateSelect(name='rate_select')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'rate_select'


class CostSavingsWizardRateSelect(Screen):
    """The starting/welcome screen for the cost savings wizard."""
    rate_structure_selected = DictProperty()
    has_selection = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CostSavingsWizardRateSelect, self).__init__(**kwargs)

        CostSavingsRateStructureRVEntry.host_screen = self
    
    def on_enter(self):
        try:
            data_manager = App.get_running_app().data_manager
            rate_structure_options = [rs[1] for rs in data_manager.get_rate_structures().items()]
            self.rate_structure_rv.data = rate_structure_options
            self.rate_structure_rv.unfiltered_data = rate_structure_options
        except KeyError as e:
            logging.warning('CostSavings: No rate structures available to select.')
            # TODO: Warning popup
        
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)
    
    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0
    
    def on_rate_structure_selected(self, instance, value):
        try:
            logging.info('CostSavings: Rate structure selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('CostSavings: Rate structure selection reset.')
            self.rate_structure_desc.text = ''
            self.has_selection = False
        else:
            Animation.stop_all(self.preview_box, 'opacity')
            self.preview_box.opacity = 0

            def _generate_preview():
                self.generate_schedule_charts()
                self.generate_flat_demand_rate_table()
                self.generate_misc_table()

                Clock.schedule_once(partial(fade_in_animation, self.preview_box), 0)
                self.has_selection = True
            
            thread_preview = threading.Thread(target=_generate_preview)
            thread_preview.start()

    def on_has_selection(self, instance, value):
        self.next_button.disabled = not value            

    def generate_flat_demand_rate_table(self):
        """Generates the preview table for the flat demand rate structure."""
        flat_demand_rates = self.rate_structure_selected['demand rate structure'].get('flat rates', {})

        table_data = [str(flat_demand_rates.get(month, '')) for month in calendar.month_abbr[1:]]
        self.flat_demand_rates_table.populate_table(table_data)
        
    def generate_misc_table(self):
        """Generates the preview table for the miscellaneous information."""
        self.misc_data_table.populate_table(self.rate_structure_selected)

    def generate_schedule_charts(self, *args):
        """Generates the preview for the weekday and weekend rate schedule charts."""
        weekday_schedule_data = self.rate_structure_selected['energy rate structure'].get('weekday schedule', [])
        weekend_schedule_data = self.rate_structure_selected['energy rate structure'].get('weekend schedule', [])

        legend_labels = ['${0}/kWh'.format(v) for _,v in self.rate_structure_selected['energy rate structure'].get('energy rates').items()]

        if weekday_schedule_data and weekend_schedule_data:
            n_tiers = len(np.unique(weekday_schedule_data))

            palette = [rgba_to_fraction(color) for color in PALETTE][:n_tiers]
            labels = calendar.month_abbr[1:]

            self.energy_weekday_chart.draw_chart(np.array(weekday_schedule_data), palette, labels, legend_labels=legend_labels)
            self.energy_weekend_chart.draw_chart(np.array(weekend_schedule_data), palette, labels, legend_labels=legend_labels)
        
        weekday_schedule_data = self.rate_structure_selected['demand rate structure'].get('weekday schedule', [])
        weekend_schedule_data = self.rate_structure_selected['demand rate structure'].get('weekend schedule', [])

        legend_labels = ['${0}/kW'.format(v) for _,v in self.rate_structure_selected['demand rate structure'].get('time of use rates').items()]

        if weekday_schedule_data and weekend_schedule_data:
            n_tiers = len(np.unique(weekday_schedule_data))

            # Select chart colors.
            palette = [rgba_to_fraction(color) for color in PALETTE][:n_tiers]
            labels = calendar.month_abbr[1:]

            # Draw charts.
            self.demand_weekday_chart.draw_chart(np.array(weekday_schedule_data), palette, labels, legend_labels=legend_labels)
            self.demand_weekend_chart.draw_chart(np.array(weekend_schedule_data), palette, labels, legend_labels=legend_labels)
    
    def _validate_inputs(self):
        # TODO: Progress already impeded until a structure is selected so...
        return self.rate_structure_selected
    
    def get_selections(self):
        """Retrieves screen's selections."""
        try:
            rate_structure_selected = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            return rate_structure_selected

    def _next_screen(self):
        if not self.manager.has_screen('load_profile_select'):
            screen = CostSavingsWizardLoadSelect(name='load_profile_select')
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
            self.manager.current = 'load_profile_select'


class CostSavingsRateStructureRVEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(CostSavingsRateStructureRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.rate_structure_selected = rv.data[self.index]


class FlatDemandRateTable(GridLayout):
    """A preview table to show the monthly flat demand rate structure."""
    def reset_table(self):
        """Builds the table column headers if necessary and removes all data entries."""
        if not self.col_headers.children:
            for month in calendar.month_abbr[1:]:
                col_header = BodyTextBase(text=month, color=rgba_to_fraction(PALETTE[1]), font_size=20)
                self.col_headers.add_widget(col_header)
        
        while len(self.data_grid.children) > 0:
            for widget in self.data_grid.children:
                self.data_grid.remove_widget(widget)
    
    def populate_table(self, data):
        """Populates the data entries."""
        self.reset_table()

        for datum in data:
            rate_label = BodyTextBase(text=datum, font_size=20)
            self.data_grid.add_widget(rate_label)


class MiscRateStructureDataTable(GridLayout):
    """A preview table for miscellaneous rate structure information."""
    def reset_table(self):
        """Removes all data entries."""
        while len(self.peak_min_box.children) > 0:
            for widget in self.peak_min_box.children:
                self.peak_min_box.remove_widget(widget)

        while len(self.peak_max_box.children) > 0:
            for widget in self.peak_max_box.children:
                self.peak_max_box.remove_widget(widget)
                
        while len(self.net_metering_type_box.children) > 0:
            for widget in self.net_metering_type_box.children:
                self.net_metering_type_box.remove_widget(widget)
        
        while len(self.energy_sell_price_box.children) > 0:
            for widget in self.energy_sell_price_box.children:
                self.energy_sell_price_box.remove_widget(widget)
    
    def populate_table(self, rate_structure_dict):
        """Populates the table with data from the rate structure dictionary."""
        self.reset_table()

        net_metering_dict = rate_structure_dict['net metering']
        demand_structure_dict = rate_structure_dict['demand rate structure']

        peak_kw_min = str(demand_structure_dict.get('minimum peak demand', '0'))
        peak_kw_min_label = TextInput(text=peak_kw_min, font_size=20, readonly=True)
        self.peak_min_box.add_widget(peak_kw_min_label)

        peak_kw_max = str(demand_structure_dict.get('maximum peak demand', 'None'))
        peak_kw_max_label = TextInput(text=peak_kw_max, font_size=20, readonly=True)
        self.peak_max_box.add_widget(peak_kw_max_label)

        net_metering_type = '2.0' if net_metering_dict['type'] else '1.0'
        net_metering_type_label = TextInput(text=net_metering_type, font_size=20, readonly=True)
        self.net_metering_type_box.add_widget(net_metering_type_label)

        energy_sell_price = 'N/A' if not net_metering_dict.get('energy sell price', False) else str(net_metering_dict.get('energy sell price', ''))
        energy_sell_price_label = TextInput(text=energy_sell_price, font_size=20, readonly=True)
        self.energy_sell_price_box.add_widget(energy_sell_price_label)
        

class CostSavingsWizardLoadSelect(Screen):
    """The load profile selection screen for the cost savings wizard."""
    load_profile_selected = DictProperty()
    has_selection = BooleanProperty(False)
    imported_data_selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CostSavingsWizardLoadSelect, self).__init__(**kwargs)

        LoadProfileRecycleViewRow.load_profile_screen = self

    def on_enter(self):
        try:
            data_manager = App.get_running_app().data_manager

            load_profile_options = [{'name': x[0], 'path': x[1]} for x in data_manager.get_load_profiles().items()]
            self.load_profile_rv.data = load_profile_options
            self.load_profile_rv.unfiltered_data = load_profile_options
        except KeyError as e:
            logging.warning('CostSavings: No load profiles available to select.')
        
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)
    
    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0
    
    def on_load_profile_selected(self, instance, value):
        try:
            logging.info('CostSavings: Load profile selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('CostSavings: Load profile selection reset.')
            self.has_selection = False
        else:
            self.has_selection = True
            self.imported_data_selected = False

    def on_has_selection(self, instance, value):
        self.next_button.disabled = not value
    
    def on_imported_data_selected(self, instance, value):
        if value:
            self.open_data_importer_button.text = 'Data imported'
            self.open_data_importer_button.background_color = rgba_to_fraction(PALETTE[3])
            Clock.schedule_once(partial(slow_blinking_animation, self.open_data_importer_button), 0)

            self.load_profile_rv.deselect_all_nodes()
        else:
            self.open_data_importer_button.text = 'Open data importer'
            self.open_data_importer_button.background_color = rgba_to_fraction(PALETTE[0])
            self.open_data_importer_button.opacity = 1
            Animation.cancel_all(self.open_data_importer_button, 'opacity')
    
    def open_data_importer(self):
        write_directory = os.path.join(DATA_HOME, 'load', 'imported')
        self.data_importer = DataImporter(
            write_directory=write_directory, 
            format_description="The data units should be in kilowatts and there should be 8,760 samples (hourly for one standard year). The time series is assumed to run January through December at an hourly resolution."
        )
        self.data_importer.title.text = "Import a load time series"

        def _check_data_importer_on_dismissal():
            try:
                import_filename = self.data_importer.get_import_selections()
            except (ValueError, AttributeError):
                logging.warning('DataImporter: Nothing was imported.')
            except KeyError:
                logging.warning('DataImporter: Import process was terminated early.')
            else:
                logging.info('DataImporter: Data import complete.')
                self.load_profile_selected = {'name': 'Custom', 'path': import_filename}
                self.imported_data_selected = True
        
        self.data_importer.bind(on_dismiss=lambda t: _check_data_importer_on_dismissal())
        self.data_importer.open()
    
    def _validate_inputs(self):
        # TODO: Progress already impeded until a profile is selected so...
        return self.load_profile_selected
    
    def get_selections(self):
        """Retrieves screen's selections."""
        try:
            load_profile_selected = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            return load_profile_selected
    
    def _next_screen(self):
        if not self.manager.has_screen('pv_profile_select'):
            screen = CostSavingsWizardPVSelect(name='pv_profile_select')
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
            self.manager.current = 'pv_profile_select'


class LoadProfileRecycleViewRow(RecycleViewRow):
    """The representation widget for node in the load profile selector RecycleView."""
    load_profile_screen = None

    def on_touch_down(self, touch):
        """Add selection on touch down."""
        if super(LoadProfileRecycleViewRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected

        if is_selected:
            self.load_profile_screen.load_profile_selected = rv.data[self.index]


class CostSavingsWizardPVSelect(Screen):
    """The optional PV profile selection screen for the cost savings wizard."""
    pv_profile_selected = DictProperty()
    has_selection = BooleanProperty(False)
    imported_data_selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CostSavingsWizardPVSelect, self).__init__(**kwargs)

        PVProfileRecycleViewRow.pv_profile_screen = self

    def on_enter(self):
        try:
            data_manager = App.get_running_app().data_manager

            pv_profile_options = [
                {
                'name': x[0], 'path': x[1], 'descriptors': get_pv_profile_string(x[1])
                } 
                for x in data_manager.get_pv_profiles().items()
                ]
            self.pv_profile_rv.data = pv_profile_options
            self.pv_profile_rv.unfiltered_data = pv_profile_options
        except Exception as e:
            print(e)
        
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)
        
    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0
    
    def on_pv_profile_selected(self, instance, value):
        try:
            logging.info('CostSavings: PV profile selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('CostSavings: PV profile selection reset.')
            self.has_selection = False
        else:
            self.has_selection = True
            self.imported_data_selected = False
    
    def on_imported_data_selected(self, instance, value):
        if value:
            self.open_data_importer_button.text = 'Data imported'
            self.open_data_importer_button.background_color = rgba_to_fraction(PALETTE[3])
            Clock.schedule_once(partial(slow_blinking_animation, self.open_data_importer_button), 0)

            self.pv_profile_rv.deselect_all_nodes()
        else:
            self.open_data_importer_button.text = 'Open data importer'
            self.open_data_importer_button.background_color = rgba_to_fraction(PALETTE[0])
            self.open_data_importer_button.opacity = 1
            Animation.cancel_all(self.open_data_importer_button, 'opacity')
    
    def open_data_importer(self):
        write_directory = os.path.join(DATA_HOME, 'pv')

        def _write_pv_profile_json(fname, dataframe):
            """Writes a generic time series dataframe to a PV profile json.

            Parameters
            ----------
            fname : str
                Name of the file to be saved without an extension
            dataframe : Pandas DataFrame
                DataFrame with one Series which is the PV power profile in watts
            
            Returns
            -------
            str
                The save destination of the resulting file.
            """
            pv_profile_template_file = os.path.join('es_gui', 'resources', 'import_templates', 'pv_profile.json')

            with open(pv_profile_template_file, 'r') as f:
                pv_profile_template = json.load(f)
            
            ac_output_w = dataframe.iloc[:, 0].tolist()
            pv_profile_template['outputs']['ac'] = ac_output_w

            save_destination = os.path.join(write_directory, fname + '.json')
            
            with open(save_destination, 'w') as f:
                json.dump(pv_profile_template, f)
            
            return save_destination

        self.data_importer = DataImporter(
            write_directory=write_directory, 
            write_function=_write_pv_profile_json, 
            format_description="The data units should be in watts and there should be 8,760 samples (hourly for one standard year). The time series is assumed to run January through December at an hourly resolution."
            )
        self.data_importer.title.text = "Import a PV power time series"

        def _check_data_importer_on_dismissal():
            try:
                import_filename = self.data_importer.get_import_selections()
            except (ValueError, AttributeError):
                logging.warning('DataImporter: Nothing was imported.')
            except KeyError:
                logging.warning('DataImporter: Import process was terminated early.')
            else:
                logging.info('DataImporter: Data import complete.')
                self.pv_profile_selected = {'name': 'Custom', 'path': import_filename, 'descriptors': get_pv_profile_string(import_filename)}
                self.imported_data_selected = True
        
        self.data_importer.bind(on_dismiss=lambda t: _check_data_importer_on_dismissal())
        self.data_importer.open()
    
    def _validate_inputs(self):
        return self.pv_profile_selected
    
    def get_selections(self):
        """Retrieves screen's selections."""
        try:
            pv_profile_selected = self._validate_inputs()
        except InputError as e:
            popup = WarningPopup()
            popup.popup_text.text = str(e)
            popup.open()
        else:
            return pv_profile_selected
    
    def _next_screen(self):
        if not self.manager.has_screen('system_parameters'):
            screen = CostSavingsWizardSystemParameters(name='system_parameters')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'system_parameters'


class PVProfileRecycleViewRow(RecycleViewRow):
    """The representation widget for node in the PV profile selector RecycleView."""
    pv_profile_screen = None

    def on_touch_down(self, touch):
        """Add selection on touch down."""
        if super(PVProfileRecycleViewRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected

        if is_selected:
            self.pv_profile_screen.pv_profile_selected = rv.data[self.index]
    
    def deselect_node(self):
        super(PVProfileRecycleViewRow, self).deselect_node(self)


class CostSavingsWizardSystemParameters(Screen):
    """"""
    def on_pre_enter(self):
        if not self.param_widget.children:
            self.param_widget.build()
        # while len(self.param_widget.children) > 0:
        #     for widget in self.param_widget.children:
        #         if isinstance(widget, CostSavingsParameterRow):
        #             self.param_widget.remove_widget(widget)
    
    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)
    
    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0
    
    def _validate_inputs(self):
        params = self.param_widget.get_inputs()
        params_desc = self.param_widget.get_input_strings()

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
        if not self.manager.has_screen('summary'):
            screen = CostSavingsWizardSummary(name='summary')
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
            self.manager.current = 'summary'


class CostSavingsParameterWidget(ParameterGridWidget):
    """Grid layout containing rows of parameter adjustment widgets."""
    def build(self):
        # Build the widget by creating a row for each parameter.
        data_manager = App.get_running_app().data_manager
        MODEL_PARAMS = data_manager.get_btm_cost_savings_model_params()

        for param in MODEL_PARAMS:
            row = ParameterRow(desc=param)
            self.add_widget(row)
            setattr(self, param['attr name'], row)


class CostSavingsWizardSummary(Screen):
    """"""
    def get_selections(self):
        sm = self.manager

        op_handler_requests = {}

        op_handler_requests['rate_structure'] = sm.get_screen('rate_select').get_selections()
        op_handler_requests['load_profile'] = sm.get_screen('load_profile_select').get_selections()
        op_handler_requests['pv_profile'] = sm.get_screen('pv_profile_select').get_selections()
        op_handler_requests['params'], op_handler_requests['param desc'] = sm.get_screen('system_parameters').get_selections()

        return op_handler_requests

    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)

        op_handler_requests = self.get_selections()

        load_profile = op_handler_requests['load_profile']
        pv_profile = op_handler_requests['pv_profile']
        system_params = op_handler_requests['param desc']
        rate_structure = op_handler_requests['rate_structure']

        # Rate structure label.
        rate_structure_text = '\n'.join([
            '[b]Rate Structure:[/b]',
            rate_structure['name'],
            rate_structure['utility']['utility name'],
            rate_structure['utility']['rate structure name'],
            ])
        self.rate_structure_label.text = rate_structure_text

        # Load profile label.
        load_profile_text = '\n'.join([
            '[b]Load Profile:[/b]',
            load_profile['name']
            ])
        self.load_profile_label.text = load_profile_text

        # PV profile label.
        pv_profile_text = '[b]PV Profile:[/b]\n'
        pv_profile_text += '\n'.join(pv_profile.get('descriptors', ['None selected']))
        self.pv_profile_label.text = pv_profile_text

        # System parameters label.
        system_parameters_text = '[b]System Parameters:[/b]\n'
        system_parameters_text += '\n'.join(system_params)
        self.system_parameters_label.text = system_parameters_text
    
    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0

    def _next_screen(self):
        if not self.manager.has_screen('execute'):
            screen = CostSavingsWizardExecute(name='execute')
            self.manager.add_widget(screen)
        
        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'execute'


class CostSavingsWizardExecute(Screen):
    """The screen for executing the prescribed optimizations for the cost savings wizard."""
    solved_ops = []
    report_attributes = {}

    def on_enter(self):
        self.execute_run()

    # def on_leave(self):
    #     self.progress_label.text = 'This may take a while. Please wait patiently!'

    def execute_run(self):
        btm_home = self.manager.parent.parent.manager.get_screen('btm_home')
        ss = self.manager.get_screen('summary')

        op_handler_requests = ss.get_selections()

        # Send requests to handler.
        handler = btm_home.handler
        handler.solver_name = App.get_running_app().config.get('optimization', 'solver')
        self.solved_ops, handler_status = handler.process_requests(op_handler_requests)

        popup = WizardCompletePopup()

        # Check BtmOp handler status.
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
                popup.bind(on_dismiss=lambda x: self.manager.parent.parent.manager.nav_bar.go_up_screen())  # Go back to BTM Home
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
        report = BtmCostSavingsReport(name='report', chart_data=self.solved_ops, report_attributes=self.report_attributes)
        self.manager.switch_to(report, direction='left', duration=BASE_TRANSITION_DUR)
