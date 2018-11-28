from __future__ import absolute_import, print_function

import logging
from functools import partial
import webbrowser
import calendar
import os
import numpy as np

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
from es_gui.resources.widgets.common import BodyTextBase, MyPopup, WarningPopup, TileButton, RecycleViewRow, BASE_TRANSITION_DUR, BUTTON_FLASH_DUR, ANIM_STAGGER,FADEIN_DUR, SLIDER_DUR, PALETTE, rgba_to_fraction


class CostSavingsWizard(Screen):
    """The main screen for the cost savings wizard. This hosts the nested screen manager for the actual wizard."""
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.reset_nav_bar()
        ab.set_title('TOU/NEM Cost Savings')

        self.sm.generate_start()

    def on_leave(self):
        # Reset wizard to initial state by removing all screens except the first.
        self.sm.current = 'start'

        if len(self.sm.screens) > 1:
            self.sm.clear_widgets(screens=self.sm.screens[1:])


class CostSavingsWizardScreenManager(ScreenManager):
    """The screen manager for the valuation wizard screens."""
    def __init__(self, **kwargs):
        super(CostSavingsWizardScreenManager, self).__init__(**kwargs)

        self.transition = SlideTransition()
        self.add_widget(CostSavingsWizardStart(name='start'))
    
    def generate_start(self):
        """"""
        try:
            data_manager = App.get_running_app().data_manager
            rate_structure_options = [rs[1] for rs in data_manager.get_rate_structures().items()]
            self.get_screen('start').rate_structure_rv.data = rate_structure_options
            self.get_screen('start').rate_structure_rv.unfiltered_data = rate_structure_options
        except Exception as e:
            print(e)


class CostSavingsWizardStart(Screen):
    """The starting/welcome screen for the valuation wizard."""
    rate_structure_selected = DictProperty()

    def __init__(self, **kwargs):
        super(CostSavingsWizardStart, self).__init__(**kwargs)

        CostSavingsRateStructureRVEntry.host_screen = self
    
    def on_rate_structure_selected(self, instance, value):
        try:
            logging.info('CostSavings: Rate structure selection changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('CostSavings: Rate structure selection reset.')
            self.rate_structure_desc.text = ''
        else:
            self.generate_schedule_charts()
            self.generate_flat_demand_rate_table()
            # self.flat_demand_rates.text = repr(value['demand rate structure'].get('flat rates', ''))
            # self.net_metering.text = repr(value['net metering'])
    
    def generate_flat_demand_rate_table(self):
        """"""
        flat_demand_rates = self.rate_structure_selected['demand rate structure'].get('flat rates', {})

        table_data = [str(flat_demand_rates.get(month, '')) for month in calendar.month_abbr[1:]]
        self.flat_demand_rates_table.populate_table(table_data)
        self.net_metering_table.populate_table(self.rate_structure_selected['net metering'])

    def generate_schedule_charts(self, *args):
        """Draws the weekday and weekend rate schedule charts."""
        weekday_schedule_data = self.rate_structure_selected['energy rate structure'].get('weekday schedule', [])
        weekend_schedule_data = self.rate_structure_selected['energy rate structure'].get('weekend schedule', [])

        legend_labels = ['${0}/kWh'.format(v) for k,v in self.rate_structure_selected['energy rate structure'].get('energy rates').items()]

        if weekday_schedule_data and weekend_schedule_data:
            n_tiers = len(np.unique(weekday_schedule_data))

            palette = [rgba_to_fraction(color) for color in PALETTE][:n_tiers]
            labels = calendar.month_abbr[1:]

            self.energy_weekday_chart.draw_chart(np.array(weekday_schedule_data), palette, labels, legend_labels=legend_labels)
            self.energy_weekend_chart.draw_chart(np.array(weekend_schedule_data), palette, labels, legend_labels=legend_labels)
        
        weekday_schedule_data = self.rate_structure_selected['demand rate structure'].get('weekday schedule', [])
        weekend_schedule_data = self.rate_structure_selected['demand rate structure'].get('weekend schedule', [])

        legend_labels = ['${0}/kW'.format(v) for k,v in self.rate_structure_selected['demand rate structure'].get('time of use rates').items()]

        if weekday_schedule_data and weekend_schedule_data:
            n_tiers = len(np.unique(weekday_schedule_data))

            # Select chart colors.
            palette = [rgba_to_fraction(color) for color in PALETTE][:n_tiers]
            labels = calendar.month_abbr[1:]

            # Draw charts.
            self.demand_weekday_chart.draw_chart(np.array(weekday_schedule_data), palette, labels, legend_labels=legend_labels)
            self.demand_weekend_chart.draw_chart(np.array(weekend_schedule_data), palette, labels, legend_labels=legend_labels)

    # def _next_screen(self):
    #     if not self.manager.has_screen('iso_select'):
    #         screen = ValuationWizardISOSelect(name='iso_select')
    #         self.manager.add_widget(screen)

    #     self.manager.transition.duration = BASE_TRANSITION_DUR
    #     self.manager.transition.direction = 'left'
    #     self.manager.current = 'iso_select'

    # def on_enter(self):
    #     try:
    #         data_manager = App.get_running_app().data_manager
    #         rate_structure_options = [rs[1] for rs in data_manager.get_rate_structures().items()]
    #         self.rate_structure_rv.data = rate_structure_options
    #         self.rate_structure_rv.unfiltered_data = rate_structure_options
    #     except Exception as e:
    #         print(e)


class CostSavingsRateStructureRVEntry(RecycleViewRow):
    host_screen = None

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        super(CostSavingsRateStructureRVEntry, self).apply_selection(rv, index, is_selected)

        if is_selected:
            self.host_screen.rate_structure_selected = rv.data[self.index]


class FlatDemandRateTable(GridLayout):
    """"""
    def reset_table(self):
        if not self.col_headers.children:
            for month in calendar.month_abbr[1:]:
                col_header = BodyTextBase(text=month, color=rgba_to_fraction(PALETTE[1]), font_size=20)
                self.col_headers.add_widget(col_header)
        
        if not self.row_label_box.children:
            row_label = BodyTextBase(text='Flat Demand Rate [$/kW]', color=rgba_to_fraction(PALETTE[1]), font_size=20)
            self.row_label_box.add_widget(row_label)
        
        while len(self.data_grid.children) > 0:
            for widget in self.data_grid.children:
                self.data_grid.remove_widget(widget)
    
    def populate_table(self, data):
        """"""
        self.reset_table()

        for datum in data:
            rate_label = BodyTextBase(text=datum, font_size=20)
            self.data_grid.add_widget(rate_label)


class NetMeteringTable(GridLayout):
    """"""
    def reset_table(self):
        if not self.net_metering_type_label_box.children:
            net_metering_label = BodyTextBase(text='Net Metering Type', color=rgba_to_fraction(PALETTE[1]), font_size=20)
            self.net_metering_type_label_box.add_widget(net_metering_label)
        
        if not self.energy_sell_price_label_box.children:
            energy_sell_price_label = BodyTextBase(text='Energy Sell Price [$/kWh]', color=rgba_to_fraction(PALETTE[1]), font_size=20)
            self.energy_sell_price_label_box.add_widget(energy_sell_price_label)
        
        while len(self.net_metering_type_box.children) > 0:
            for widget in self.net_metering_type_box.children:
                self.net_metering_type_box.remove_widget(widget)
        
        while len(self.energy_sell_price_box.children) > 0:
            for widget in self.energy_sell_price_box.children:
                self.energy_sell_price_box.remove_widget(widget)
    
    def populate_table(self, net_metering_dict):
        """"""
        self.reset_table()

        net_metering_type = '2.0' if net_metering_dict['type'] else '1.0'

        net_metering_type_label = TextInput(text=net_metering_type, font_size=20, readonly=True)
        self.net_metering_type_box.add_widget(net_metering_type_label)

        energy_sell_price = 'N/A' if not net_metering_dict.get('energy sell price', False) else str(net_metering_dict.get('energy sell price', ''))
        energy_sell_price_label = TextInput(text=energy_sell_price, font_size=20, readonly=True)
        self.energy_sell_price_box.add_widget(energy_sell_price_label)
        