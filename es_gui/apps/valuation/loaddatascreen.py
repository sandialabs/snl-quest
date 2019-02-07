from __future__ import absolute_import

from functools import partial
from threading import Thread
import os
import calendar

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.modalview import ModalView
from kivy.properties import DictProperty

from es_gui.apps.data_manager.data_manager import DataManagerException
from es_gui.tools.valuation.utilities import *
from es_gui.resources.widgets.common import MyPopup, InputError, RecycleViewRow


class LoadDataScreen(Screen):
    """The screen for loading data for the energy valuation application."""
    # loading = False
    # thread_list = []
    node = DictProperty()

    def __init__(self, **kwargs):
        super(LoadDataScreen, self).__init__(**kwargs)

        SingleRunNodeRecycleViewRow.host_screen = self
        NodeSelectMenu.host_screen = self
        self.node_select_menu = NodeSelectMenu()

    def on_enter(self):
        self.load_toolbar()

        # change the navigation bar title
        ab = self.manager.nav_bar
        ab.build_valuation_advanced_nav_bar()
        ab.set_title('Single Run: Select Data')
    
    def on_node(self, instance, value):
        try:
            logging.info('ValuationSingle: Pricing node changed to {0}.'.format(value['name']))
        except KeyError:
            logging.info('ValuationSingle: Pricing node selection reset.')
        else:
            self.node_select.text = value['name']
        finally:
            self.type_select.text = 'Select revenue streams'
            self.year_select.text = 'Select year'
            self.month_select.text = 'Select month'

    def _validate_inputs(self):
        iso_selected = self.iso_select.text

        data_manager = App.get_running_app().data_manager

        try:
            self.iso_select.values.index(iso_selected)
        except ValueError:
            raise InputError('Select a market area in "Select Data."')

        try:
            node_selected = self.node['nodeid']
            market_models_available = data_manager.get_valuation_revstreams(iso_selected, node_selected)
        except KeyError:
            raise InputError('Select a pricing node in "Select Data."')

        if node_selected not in data_manager.get_nodes(iso_selected).keys():
            raise InputError('Select a pricing node in "Select Data."')

        rev_streams = self.type_select.text

        if rev_streams not in market_models_available.keys():
            raise InputError('Select revenue streams in "Select Data."')

        try:
            year_selected = int(self.year_select.text)
        except ValueError:
            raise InputError('Select a year in "Select Data."')

        try:
            month_selected = list(calendar.month_name).index(self.month_select.text)
        except ValueError:
            raise InputError('Select a month in "Select Data."')

    def get_inputs(self):
        self._validate_inputs()

        iso_selected = self.iso_select.text

        data_manager = App.get_running_app().data_manager
        market_models_available = data_manager.get_valuation_revstreams(self.iso_select.text, self.node['nodeid'])
        market_formulation_selected = market_models_available[self.type_select.text]['market type']

        #node_selected = [self.node_select_menu.node_rv.data[selected_ix] for selected_ix in self.node_select_menu.node_rv.layout_manager.selected_nodes][0]

        node_selected = self.node['nodeid']

        year_selected = self.year_select.text
        month_selected = str(list(calendar.month_name).index(self.month_select.text))

        return iso_selected, market_formulation_selected, node_selected, year_selected, month_selected

    def load_toolbar(self, **kwargs):
        data_manager = App.get_running_app().data_manager
        iso_options = data_manager.get_markets()
        
        self.iso_select.values = iso_options
        self.type_select.values = []
        self.year_select.values = []
        self.month_select.values = []

    def reset_toolbar(self, **kwargs):
        self.type_select.text = 'Select revenue streams'
        self.year_select.text = 'Select year'
        self.month_select.text = 'Select month'
        self.node_select.text = 'Select node'

        if self.iso_select.text=='PJM':
            self.iso_img.source=os.path.join('es_gui', 'resources', 'images', 'IRCmap_pjm.png')
        elif self.iso_select.text=='MISO':
            self.iso_img.source=os.path.join('es_gui', 'resources', 'images', 'IRCmap_miso.png')
        elif self.iso_select.text=='ERCOT':
            self.iso_img.source=os.path.join('es_gui', 'resources', 'images', 'IRCmap_ercot.png')
        elif self.iso_select.text=='ISONE':
            self.iso_img.source=os.path.join('es_gui', 'resources', 'images', 'IRCmap_isone.png')
        elif self.iso_select.text=='NYISO':
            self.iso_img.source=os.path.join('es_gui', 'resources', 'images', 'IRCmap_nyiso.png')
        elif self.iso_select.text=='CAISO':
            self.iso_img.source=os.path.join('es_gui', 'resources', 'images', 'IRCmap_caiso.png')
        elif self.iso_select.text=='SPP':
            self.iso_img.source=os.path.join('es_gui', 'resources', 'images', 'IRCmap_spp.png')

        data_manager = App.get_running_app().data_manager
        node_data = [{'name': node[1],
                      'nodeid': node[0]} for node in data_manager.get_nodes(self.iso_select.text).items()]

        self.node_select_menu.node_rv.data = node_data
        self.node_select_menu.node_rv.unfiltered_data = node_data
        self.node_select_menu.node_rv.deselect_all_nodes()
        self.node = {}

    def load_year(self, iso):
        try:
            data_manager = App.get_running_app().data_manager
            year_options = data_manager.get_historical_data_options(self.iso_select.text, self.node['nodeid'], self.type_select.text).keys()
            self.year_select.values = year_options
        except (KeyError, DataManagerException):
            self.year_select.values = []

    def load_month(self, iso, year):
        try:
            data_manager = App.get_running_app().data_manager
            hist_data_options = data_manager.get_historical_data_options(self.iso_select.text, self.node['nodeid'], self.type_select.text)
            month_options = hist_data_options[str(year)]
            self.month_select.values = [calendar.month_name[int(month_index)] for month_index in month_options]
            
        except (KeyError, DataManagerException):
            self.month_select.values = []

    def load_nodeid(self, iso):
        try:
            self.node_select_menu.open()
        except KeyError:
            pass

    def load_dtype(self, iso):
        try:
            data_manager = App.get_running_app().data_manager
            market_models_available = data_manager.get_valuation_revstreams(self.iso_select.text, self.node['nodeid'])
            self.type_select.values = market_models_available.keys()
        except (KeyError, DataManagerException):
            self.type_select.values = []
    
    def enable_load(self):
        self.load_button.disabled=False

    # def load_data_function(self, iso, dttype, year, month, nodeid, op=None):
    #     mes_pop=MessagePopup()
    #     try:
    #         path = self.dpath[iso]
    #         flag = True
    #     except KeyError as e:
    #         flag = False
    #         mes_pop.title='Loading Data Error!'
    #         mes_pop.pop_label.text='Invalid ISO!'
    #         mes_pop.open()
    #         print(repr(e))
    #         raise(KeyError('Invalid ISO specified.'))

    #     try:
    #         yeari = int(year)
    #         monthi = int(month)
    #     except ValueError as e:
    #         flag = False
    #         mes_pop.title='Loading Data Error!'
    #         mes_pop.pop_label.text='Invalid year or month!'
    #         mes_pop.open()
    #         print(repr(e))
    #         raise(ValueError('Invalid year or month specified.'))


    #     if op is None:
    #         op_screen = self.manager.get_screen('valuation_advanced')
    #         op = op_screen.op

    #     dms = self.manager.get_screen('valuation_home').dms

    #     if flag and iso == 'PJM':
    #         node_name = dms.get_node_name(nodeid, iso)

    #         lmp_da, RUP, RDW, MR, RA, RD, RegCCP, RegPCP = dms.get_pjm_data(yeari, monthi, node_name)

    #         if dttype == 'Arbitrage and regulation':
    #             op.market_type = 'pjm_pfp'
    #             op.price_electricity = lmp_da
    #             op.mileage_ratio = MR
    #             op.mileage_slow = RA
    #             op.mileage_fast = RD
    #             op.price_reg_capacity = RegCCP
    #             op.price_reg_performance = RegPCP
    #             op.fraction_reg_up = RUP
    #             op.fraction_reg_down = RDW

    #         print('Finished loading data!')
    #     elif flag and iso == 'ERCOT':
    #         node_name = dms.get_node_name(nodeid, iso)

    #         lmp_da, rd, ru = dms.get_ercot_data(yeari, monthi, node_name)

    #         if dttype == 'Arbitrage and regulation':
    #             op.market_type = 'ercot_arbreg'
    #             op.price_electricity = lmp_da
    #             op.price_reg_up = ru
    #             op.price_reg_down = rd

    #         print('Finished loading data!')
    #     elif flag and iso == 'MISO':
    #         node_name = dms.get_node_name(nodeid, iso)

    #         lmp_da, RegMCP = dms.get_miso_data(yeari, monthi, node_name)
            
    #         if dttype == 'Arbitrage and regulation':
    #             op.market_type = 'miso_pfp'
    #             op.price_electricity = lmp_da
    #             op.price_reg_performance = RegMCP

    #         print('Finished loading data!')

    #     elif flag == True and iso == 'ISO-NE':
    #         node_name = dms.get_node_name(nodeid, iso)
    #         # nodeidi = int(nodeid)
    #         daLMP, RegCCP, RegPCP = dms.get_isone_data(year, month, nodeid)

    #         if dttype == 'Arbitrage and regulation':
    #             op.market_type = 'isone_pfp'
    #             op.price_electricity = daLMP
    #             op.price_reg_capacity = RegCCP
    #             op.price_reg_performance = RegPCP

    #         print('Finished loading data!')

    # def load_data(self, iso, dttype, year, month, nodeid):
    #     for th in self.thread_list:
    #         if th.isAlive():
    #             self.loading=True
    #         else:
    #             self.loading=False

    #     if not self.loading:
    #         t=Thread(target=self.load_data_function,args=(iso,dttype,year,month,nodeid))
    #         self.thread_list.append(t)
    #         t.start()
    #     else:
    #         mes_pop=MessagePopup()
    #         mes_pop.title='Loading Data Status'
    #         mes_pop.pop_label.text='Loading data is currently running!'
    #         mes_pop.open()
    #         print('Loading data is currently running')
    #         #print self.thread_list
    #         #print self.loading


class MessagePopup(MyPopup):
    pass


class NodeSelectMenu(ModalView):
    host_screen = None

    def on_dismiss(self):
        try:
            node_selected = [self.node_rv.data[selected_ix] for selected_ix in self.node_rv.layout_manager.selected_nodes][0]
            self.host_screen.node = node_selected
            #self.host_screen.node_select.text = node_selected['name']
        except IndexError:
            self.host_screen.node = {}
            #self.host_screen.node_select.text = 'Select node'


class SingleRunNodeRecycleViewRow(RecycleViewRow):
    """The representation widget for node in the node selector RecycleView."""
    host_screen = None

    def on_touch_down(self, touch):
        """Add selection on touch down."""
        if super(SingleRunNodeRecycleViewRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)
