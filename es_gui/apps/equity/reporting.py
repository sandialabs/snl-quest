from random import sample, choice
from functools import partial
from collections import OrderedDict
import calendar
import os
import datetime
import webbrowser
import base64
from time import sleep
import json
import numpy_financial as npf
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from math import sin

from jinja2 import Environment, FileSystemLoader, select_autoescape
from kivy.uix.screenmanager import Screen, ScreenManager, WipeTransition, NoTransition
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
#from kivy.garden.graph import Graph, MeshLinePlot

from es_gui.proving_grounds.charts import BarChart, StackedBarChart, MultisetBarChart, PieChart, DonutChart, format_dollar_string
from es_gui.resources.widgets.common import TWO_ABC_WIDTH, THREE_ABC_WIDTH, MyPopup, TileButton, PALETTE, rgba_to_fraction, ReportScreen, WizardReportInterface, ReportChartToggle

STATIC_HOME = 'es_gui/apps/data_manager/_static'
GEOJSON = "geojson-counties-fips.json"

def format_long_dollar_string(value):
    """Formats a float representing USD with comma separators, dollar sign, $M/$B where appropreate, and proper negative sign placement."""

    if abs(value) > 1000000:
        # $M
        if value >= 0:
            return_str = "${0:,.1f}M".format(value/1000000)
        else:
            return_str = "-${0:,.1f}M".format(-value/1000000)
        if abs(value) > 1000000000:
            # $B
            if value >= 0:
                return_str = "${0:,.2f}B".format(value/1000000000)
            else:
                return_str = "-${0:,.2f}B".format(-value/1000000000)
    else:
        if value >= 0:
            return_str = "${0:,.0f}".format(value)
        else:
            return_str = "-${0:,.0f}".format(-value)
    
    return return_str

class PeakerRepReport(WizardReportInterface):
    chart_types = OrderedDict({
        'Capital Cost': 'cost_bar',
        'Power and Energy': 'power_and_energy',
        'Pollution Reduction Benefits': 'pollution_reduction_benefits',
        'Sotial Net Present Value (sNPV)': 'generate_NPV_bar_chart',
        'Disadvantaged benefits fraction': 'disadvantaged_stackedbar_normalized',
        'Disadvantaged sNPV': 'generate_disadvantaged_NPV_bar_chart',
        'Low-Income benefits fraction': 'low_income_stackedbar_normalized',
        'Low-Income sNPV': 'generate_low_income_NPV_bar_chart',
                   })
    
    # Sometimes the charges/bills/savings can be negative so we can't use stacked bar or donut charts.

    def __init__(self, chart_data, report_attributes, **kwargs):
        super(PeakerRepReport, self).__init__(**kwargs)

        self.chart_type = type
        self.chart_data = chart_data
        self.report_attributes = report_attributes

        sm = self.report_sm
        # self.generate_report_button.disabled = True

        # Build chart type selection buttons and corresponding report screens.
        for opt in self.chart_types.items():
            button = ReportChartToggle(text=opt[0])
            button.bind(state=partial(self.add_report, opt[1]))
            self.chart_type_toggle.add_widget(button)

            screen = PeakerRepReportScreen(type=opt[1], chart_data=self.chart_data, name=opt[1])
            sm.add_widget(screen)
    
    def has_chart(self, name):
        """Returns True if chart_data will generate a chart."""
        has_chart_status = True
        
        return has_chart_status

    def add_report(self, chart_type, *args):
        # Adds a ReportScreen of type chart_type to the screen manager.
        sm = self.report_sm
        sm.transition = WipeTransition(duration=0.8, clearcolor=[1, 1, 1, 1])

        if not sm.has_screen(chart_type):
            screen = PeakerRepReportScreen(type=chart_type, chart_data=self.chart_data, name=chart_type)
            sm.add_widget(screen)

        sm.current = chart_type
    
    def open_generate_report_menu(self):
        PeakerRepGenerateReportMenu.host_report = self
        gen_report_menu = PeakerRepGenerateReportMenu()
        gen_report_menu.open()


class ReportScreenManager(ScreenManager):
    transition = WipeTransition(duration=0.8, clearcolor=[1, 1, 1, 1])


class PeakerRepReportScreen(ReportScreen):
    """A report screen for the BTM Cost Savings Wizard."""

    def __init__(self, type, chart_data, do_animation=True, **kwargs):
        super(PeakerRepReportScreen, self).__init__(**kwargs)

        self.chart_type = type
        self.chart_data = chart_data
        self.do_animation = do_animation

        if self.chart_type == 'cost_bar':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = BarChart(bar_spacing=25, y_axis_format='${0:,.1f}', size_hint_x=1, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_cost_bar_chart)
        elif self.chart_type == 'power_and_energy':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = BarChart(bar_spacing=25, y_axis_format='{0:,.0f}', size_hint_x=1, do_animation=self.do_animation)            
            self.bind(on_enter=self.generate_power_energy_bar_chart)

        elif self.chart_type == 'pollution_reduction_benefits':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = BarChart(bar_spacing=25, y_axis_format='${0:,.1f}', size_hint_x=1, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_pollution_bar_chart)

        elif self.chart_type == 'generate_NPV_bar_chart':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = BarChart(bar_spacing=25, y_axis_format='${0:,.1f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_NPV_bar_chart)

        elif self.chart_type == 'disadvantaged_stackedbar_normalized':
            # set up vertical orientation for stackedbar chart
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            # generate stackedbar chart
            self.chart = StackedBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='{0:n}%', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=partial(self.generate_disadvantaged_stackedbar_chart))
        
        elif self.chart_type == 'generate_disadvantaged_NPV_bar_chart':
            # set up vertical orientation for stackedbar chart
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            # generate stackedbar chart
            self.chart = BarChart(bar_spacing=25, y_axis_format='${0:,.1f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_disadvantaged_NPV_bar_chart)

        elif self.chart_type == 'low_income_stackedbar_normalized':
            # set up vertical orientation for stackedbar chart
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            # generate stackedbar chart
            self.chart = StackedBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='{0:n}%', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=partial(self.generate_low_income_stackedbar_chart))

        elif self.chart_type == 'generate_low_income_NPV_bar_chart':
            # set up vertical orientation for stackedbar chart
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            # generate stackedbar chart
            self.chart = BarChart(bar_spacing=25, y_axis_format='${0:,.1f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_low_income_NPV_bar_chart)

        else:
            raise(ValueError('An improper chart type was specified. (got {0})'.format(self.chart_type)))

        self.chart_bx.add_widget(self.chart)

    def on_leave(self):
        # reset the chart
        self.chart.clear_widgets()

    def generate_cost_bar_chart(self, *args):
        """Generates bar chart showing the total bill with energy storage each month."""
        bar_data = []

        '''if len(self.chart_data) > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, len(self.chart_data))'''
        colors = PALETTE

        self.title.text = "Estemated costs for replacing the selected power plant."
        self.desc.text = "The selected power plant can be replaced, in part or in full, by a combenation of energy storage and PV. The total costs in order are: \n"
        report_templates = ''
        for ix, op in enumerate(self.chart_data, start=0):
            label = op[0]
            peaker_name = label.split(' | ')[1]
            eo = op[1]
            pv_cost =  eo.cost_per_MW_PV_system * eo.pv_capacity + eo.fixed_cost_of_PV_system
            ess_cost = eo.cost_per_MWh_BESS * eo.energy_capacity + eo.cost_per_MW_BESS * eo.power_capacity + eo.fixed_cost_of_the_BESS
            total_cost = pv_cost + ess_cost
            bar_color = colors[divmod(0, len(colors))[1]]
            bar_data.append(['pv :'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), pv_cost])
            
            bar_color = colors[divmod(1, len(colors))[1]]
            bar_data.append(['ess :'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), ess_cost])

            bar_color = colors[divmod(2, len(colors))[1]]
            bar_data.append(['total :'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), ess_cost+pv_cost])

            text = ('Rep. Frac.: {0:,.0f}%'.format(eo.replacement_fraction*100)
                   +', total cost: {0}'.format(format_long_dollar_string(total_cost))+'\n')
            report_templates += text

        self.chart.draw_chart(bar_data)

        self.desc.text += ' '.join(report_templates)
        self.is_drawn = True

    def generate_power_energy_bar_chart(self, *args):
        """Generates bar chart showing the energy storage and pv needed to replace the powerplant."""
        bar_data = []

        '''if len(self.chart_data) > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, len(self.chart_data))'''
        colors = PALETTE

        self.title.text = "Estemated pv and battery sizes needed to replace the selected power plant."
        self.desc.text = "\n "
        report_templates = ''
        for ix, op in enumerate(self.chart_data, start=0):
            label = op[0]
            peaker_name = label.split(' | ')[1]
            eo = op[1]
            pv_cost =  eo.cost_per_MW_PV_system * eo.pv_capacity + eo.fixed_cost_of_PV_system
            ess_cost = eo.cost_per_MWh_BESS * eo.energy_capacity + eo.cost_per_MW_BESS * eo.power_capacity + eo.fixed_cost_of_the_BESS
            total_cost = pv_cost + ess_cost
            bar_color = colors[divmod(0, len(colors))[1]]
            
            bar_data.append(['pv:'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), eo.pv_capacity])
            
            bar_color = colors[divmod(3, len(colors))[1]]
            bar_data.append(['ess-p:'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), eo.power_capacity])

            bar_color = colors[divmod(4, len(colors))[1]]
            bar_data.append(['ess-e:'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), eo.energy_capacity])
            text = ('R.F.: {0:.0f}%'.format(eo.replacement_fraction*100)
                   +', pv: {0:,.0f}MW'.format(eo.pv_capacity)
                   +', ess-p: {0:,.0f}MW'.format(eo.power_capacity)
                   +', ess-e: {0:,.0f}MWh'.format(eo.energy_capacity)+'\n')
            report_templates += text

        self.chart.draw_chart(bar_data)

        self.desc.text += ' '.join(report_templates)
        self.is_drawn = True

    def generate_pollution_bar_chart(self, *args):
        """Generates bar chart the health benefits of offsetting the powerplant's polution."""
        bar_data = []

        colors = PALETTE

        self.title.text = "Estemated health benefits of from reduced pollution."
        self.desc.text = "The EPA's COBRA tool estimates the value of the health benefits from cessation of powerplant pollution. Data from Justice40 are then used to calculate how much of those health benefits go to disadvantaged communities and people with low incomes. \n"
        report_templates = ''
        for ix, op in enumerate(self.chart_data, start=0):
            label = op[0]
            peaker_name = label.split(' | ')[1]
            eo = op[1]
    
            bar_color = colors[divmod(5, len(colors))[1]]
            bar_data.append(['Total Low', rgba_to_fraction(bar_color), eo.Pollution_Low_Value])
            bar_data.append(['Total High', rgba_to_fraction(bar_color), eo.Pollution_High_Value])
            bar_color = colors[divmod(4, len(colors))[1]]
            bar_data.append(['Disad. Low', rgba_to_fraction(bar_color), eo.total_impact_on_disadvantaged_population_low])
            bar_data.append(['Disad. High', rgba_to_fraction(bar_color), eo.total_impact_on_disadvantaged_population_high])
            bar_color = colors[divmod(3, len(colors))[1]]
            bar_data.append(['Low-Inc. Low', rgba_to_fraction(bar_color), eo.total_impact_on_low_income_population_low])
            bar_data.append(['Low-Inc. High', rgba_to_fraction(bar_color), eo.total_impact_on_low_income_population_high])

            break
            
        text = ('Total Health benefits : Low Estemate {0}, High Estemate {1}'.format(format_long_dollar_string(eo.Pollution_Low_Value),format_long_dollar_string(eo.Pollution_High_Value))+'\n'
                +'Disadvantaged Communities: Low {0}, High {1}'.format(format_long_dollar_string(eo.total_impact_on_disadvantaged_population_low),format_long_dollar_string(eo.total_impact_on_disadvantaged_population_high))+'\n'
                +'Low-Income (<200% poverty): Low {0}, High {1}'.format(format_long_dollar_string(eo.total_impact_on_low_income_population_low),format_long_dollar_string(eo.total_impact_on_low_income_population_high)) )

        report_templates += text

        self.chart.draw_chart(bar_data)

        self.desc.text += ' '.join(report_templates)
        self.is_drawn = True

    def generate_NPV_bar_chart(self, *args):
        """Generates bar chart showing the total Net Present Value"""
        bar_data = []

        '''if len(self.chart_data) > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, len(self.chart_data))'''
        colors = PALETTE


        self.title.text = "Total sNPV"
        self.desc.text = "Over a 20 year horizon the sotial Net Present Value (sNPV) can be calculated for the health and climate benifits. \n"
        report_templates = ''
        for ix, op in enumerate(self.chart_data, start=0):
            label = op[0]
            eo = op[1]

            NPV_multiplier = float(-npf.pv(eo.discount_rate,20,1,0))

            bar_color = colors[divmod(1, len(colors))[1]]
            Helth_Ave = (eo.Pollution_Low_Value+eo.Pollution_High_Value)*eo.replacement_fraction/2
            bar_data.append(['Health:'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), Helth_Ave*NPV_multiplier])

            bar_color = colors[divmod(4, len(colors))[1]]
            SCC = eo.CO2_emissions*eo.replacement_fraction*eo.cost_per_ton_of_CO2
            bar_data.append(['SCC:'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), SCC*NPV_multiplier])

            bar_color = colors[divmod(2, len(colors))[1]]
            total_sNPV = (Helth_Ave+SCC)*NPV_multiplier
            bar_data.append(['sNPV:'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), total_sNPV])
            
            text = ('Rep. Frac.: {0:.0f}%'.format(eo.replacement_fraction*100)
                    +', Health High: {0}'.format(format_long_dollar_string(Helth_Ave*NPV_multiplier))
                    +', Carbon: {0}'.format(format_long_dollar_string(SCC*NPV_multiplier))
                   +', Total sNPV: {0}'.format(format_long_dollar_string(total_sNPV))+'\n')
            report_templates += text

        self.chart.draw_chart(bar_data)

        self.desc.text += ' '.join(report_templates)
        self.is_drawn = True

    def generate_disadvantaged_stackedbar_chart(self, *args):
        """
        Creates a stacked bar chart counting the number of times each decision variable was nonzero. The number and labels of bar components are determined by the population and benifit fractions.
        :return:
        """

        stackedbar_data = OrderedDict()
        colors = PALETTE
        self.desc.text = 'The results from the COBRA tool are crossreferanced with justice40 data to calculate how much of the health benefits from replacing this powerplant would go to people in diadvantaged comunities. \n'   
        report_templates = ''
        # compute activity counts
        for ix, op in enumerate(self.chart_data, start=0):
            name = op[0]

            solved_op = op[1]
            results = solved_op.results

            population_bar_stack = []

            label = op[0]
            peaker_name = label.split(' | ')[1]
            eo = op[1]
    
            bar_color = colors[divmod(7, len(colors))[1]]
            population_bar_stack.append(['Disad', rgba_to_fraction(bar_color), eo.disadvantaged_population_fraction*100])
            bar_color = colors[divmod(2, len(colors))[1]]
            population_bar_stack.append(['Non-Disad', rgba_to_fraction(bar_color), 100-eo.disadvantaged_population_fraction*100])

            stackedbar_data['population'] = population_bar_stack

            benefits_bar_stack = []
    
            bar_color = colors[divmod(7, len(colors))[1]]
            benefits_bar_stack.append(['to Disad', rgba_to_fraction(bar_color), eo.impact_on_disadvantaged_population_fraction*100])
            bar_color = colors[divmod(2, len(colors))[1]]
            benefits_bar_stack.append(['to Non-Disad', rgba_to_fraction(bar_color), 100-eo.impact_on_disadvantaged_population_fraction*100])

            stackedbar_data['benefits'] = benefits_bar_stack

            text = ('% disadvantaged communities: {0:.1f}%'.format(eo.disadvantaged_population_fraction*100)+'\n'
                   +'% benefits to disadvantaged communities: {0:.1f}%'.format(eo.impact_on_disadvantaged_population_fraction*100)+'\n')
            report_templates += text
            break

        # generate chart
        self.chart.draw_chart(stackedbar_data)


        # generate report text
        self.title.text = "Estemated fraction of health benefits that would go to disadvantaged communities."
        self.desc.text += ' '.join(report_templates)

    def generate_low_income_stackedbar_chart(self, *args):
        """
        Creates a stacked bar chart counting the number of times each decision variable was nonzero. The number and labels of bar components are determined by the population and benifit fractions.
        :return:
        """

        stackedbar_data = OrderedDict()
        colors = PALETTE
        self.desc.text = 'The results from the COBRA tool are crossreferanced with justice40 data to calculate how much of the health benefits from replacing this plant would go to people with low incomes \n'
        report_templates = ''
        # compute activity counts
        for ix, op in enumerate(self.chart_data, start=0):
            name = op[0]
            solved_op = op[1]
            results = solved_op.results

            population_bar_stack = []

            label = op[0]
            peaker_name = label.split(' | ')[1]
            eo = op[1]
    
            bar_color = colors[divmod(3, len(colors))[1]]
            population_bar_stack.append(['Low', rgba_to_fraction(bar_color), eo.low_income_population_fraction*100])
            bar_color = colors[divmod(4, len(colors))[1]]
            population_bar_stack.append(['Non-Low', rgba_to_fraction(bar_color), 100-eo.low_income_population_fraction*100])

            stackedbar_data['population'] = population_bar_stack

            benefits_bar_stack = []
    
            bar_color = colors[divmod(3, len(colors))[1]]
            benefits_bar_stack.append(['to Low', rgba_to_fraction(bar_color), eo.impact_on_low_income_population_fraction*100])
            bar_color = colors[divmod(4, len(colors))[1]]
            benefits_bar_stack.append(['to Non-Low', rgba_to_fraction(bar_color), 100-eo.impact_on_low_income_population_fraction*100])

            stackedbar_data['benefits'] = benefits_bar_stack
            text = ('% low-income people: {0:.1f}%'.format(eo.low_income_population_fraction*100)+'\n'
                   +'% benefits to low-income people: {0:.1f}%'.format(eo.impact_on_low_income_population_fraction*100)+'\n')
            report_templates += text
            break

        # generate chart
        self.chart.draw_chart(stackedbar_data)

        # generate report text
        self.title.text = "Estemated fraction of health benefits that would go to people with low incomes."
        self.desc.text += ' '.join(report_templates)

    def generate_disadvantaged_NPV_bar_chart(self, *args):
        """Generates bar chart showing the total Net Present Value"""
        bar_data = []

        '''if len(self.chart_data) > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, len(self.chart_data))'''
        colors = PALETTE


        self.title.text = "Disadvantaged sNPV."
        self.desc.text = "Over a 20 year horizon the sotial Net Present Value (sNPV) in health benifits accrued to pepole in disadvantaged communities is calculated below. \n"
        report_templates = ''
        for ix, op in enumerate(self.chart_data, start=0):
            label = op[0]
            peaker_name = label.split(' | ')[1]
            eo = op[1]

            NPV_multiplier = float(-npf.pv(eo.discount_rate,20,1,0))
            bar_color = colors[divmod(7, len(colors))[1]]
            low_sNPV = eo.Pollution_Low_Value*eo.replacement_fraction*eo.impact_on_disadvantaged_population_fraction*NPV_multiplier
            bar_data.append(['sNPV Low '+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), low_sNPV])
            bar_color = colors[divmod(2, len(colors))[1]]
            high_sNPV = eo.Pollution_High_Value*eo.replacement_fraction*eo.impact_on_disadvantaged_population_fraction*NPV_multiplier
            bar_data.append(['sNPV High '+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), high_sNPV])

            text = ('Rep. Frac.: {0:.0f}%'.format(eo.replacement_fraction*100)
                    +', sNPV Low: {0}'.format(format_long_dollar_string(low_sNPV))
                    +', sNPV High {0}'.format(format_long_dollar_string(high_sNPV))+'\n') 
            report_templates += text

        self.chart.draw_chart(bar_data)

        self.desc.text += ' '.join(report_templates)
        self.is_drawn = True


    def generate_low_income_NPV_bar_chart(self, *args):
        """Generates bar chart showing the total Net Present Value"""
        bar_data = []

        '''if len(self.chart_data) > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, len(self.chart_data))'''
        colors = PALETTE

        self.title.text = "Low-Income sNPV"
        self.desc.text = "Over a 20 year horizon the sotial Net Present Value (sNPV) in health benifits accrued to low-income people is calculated below. \n"
        report_templates = ''
        for ix, op in enumerate(self.chart_data, start=0):
            label = op[0]
            peaker_name = label.split(' | ')[1]
            eo = op[1]

            NPV_multiplier = float(-npf.pv(eo.discount_rate,20,1,0))
            bar_color = colors[divmod(3, len(colors))[1]]
            bar_data.append(['sNPV Low '+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), eo.Pollution_Low_Value*eo.replacement_fraction*eo.impact_on_low_income_population_fraction*NPV_multiplier])
            bar_color = colors[divmod(4, len(colors))[1]]
            bar_data.append(['sNPV High '+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), eo.Pollution_High_Value*eo.replacement_fraction*eo.impact_on_low_income_population_fraction*NPV_multiplier])

            text = ('Rep. Frac.: {0:,.0f}%'.format(eo.replacement_fraction*100)
                    +', sNPV Low: {0}'.format(format_long_dollar_string(eo.Pollution_Low_Value*eo.replacement_fraction*eo.impact_on_low_income_population_fraction*NPV_multiplier))
                    +', sNPV High {0}'.format(format_long_dollar_string(eo.Pollution_High_Value*eo.replacement_fraction*eo.impact_on_low_income_population_fraction*NPV_multiplier))+'\n')
            report_templates += text

        self.chart.draw_chart(bar_data)

        self.desc.text += ' '.join(report_templates)
        self.is_drawn = True

class PeakerRepGenerateReportMenu(ModalView):
    host_report = None
    graphics_locations = {}
    report_id = None

    def __init__(self, **kwargs):
        super(PeakerRepGenerateReportMenu, self).__init__(**kwargs)

        self.sm.transition = NoTransition()

        self.report_id = datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')

    def save_figure(self, screen, *args):
        if not self.sm.has_screen(screen.name):
            self.sm.add_widget(screen)

        self.sm.current = screen.name

        chart_images_dir = os.path.join('results', 'equity', 'report', self.report_id, 'images')
        os.makedirs(chart_images_dir, exist_ok=True)

        chart_save_location = os.path.join(chart_images_dir, 'chart_{n}.png'.format(n=screen.name))

        Clock.schedule_once(partial(screen.chart.export_to_png, chart_save_location), 1.0)

        # Save image name/path for report generator.
        self.graphics_locations[screen.name] = os.path.join('images', 'chart_{n}.png'.format(n=screen.name))

    def generate_report_screens(self):
        screen_flip_interval = 1.2
        n_charts = len(self.host_report.chart_types.items())

        # Draw figures for saving to .png.
        for ix, opt in enumerate(self.host_report.chart_types.items(), start=0):
            chart_name = opt[1]
            has_chart_status = self.host_report.has_chart(chart_name)
            
            if has_chart_status:
                screen = PeakerRepReportScreen(type=chart_name, chart_data=self.host_report.chart_data, name=chart_name, do_animation=False)
                Clock.schedule_once(partial(self.save_figure, screen), ix * screen_flip_interval)

        self.generate_report_button.disabled = True

        # Generate report.
        Clock.schedule_once(lambda dt: self.generate_report_from_template(), (n_charts+1)*screen_flip_interval)
    
    def generate_executive_summary(self,eo,name):
        """Generates an executive summary similar to the report screen using chart data."""
        #eo = self.host_report.chart_data

        total_cost = eo.cost_per_MWh_BESS * eo.energy_capacity + eo.cost_per_MW_BESS * eo.power_capacity + eo.fixed_cost_of_the_BESS + eo.cost_per_MW_PV_system * eo.pv_capacity + eo.fixed_cost_of_PV_system

        executive_summary_strings = []

        header_text = 'The following summarizes the results of the analysis to replace {replacement_fraction:,.0f}% of the energy of the {name} powerplant with a combenation of energy storage and PV. '.format(replacement_fraction=eo.replacement_fraction*100,name=name)
        
        executive_summary_strings.append(header_text)

        sizing_text = ('The replacement system would need {0:,.0f} MW of PV, and a {1:,.0f} MW / {2:,.0f} MWh energy storage system. '.format(eo.pv_capacity,eo.power_capacity,eo.energy_capacity))
 
        executive_summary_strings.append(sizing_text)

        cost_text = ('The PV would cost roughly {0} and the es would cost roughly {1}, making the total capital cost estemate {2}.'.format(
            format_long_dollar_string(eo.cost_per_MW_PV_system * eo.pv_capacity + eo.fixed_cost_of_PV_system),
            format_long_dollar_string(eo.cost_per_MWh_BESS * eo.energy_capacity + eo.cost_per_MW_BESS * eo.power_capacity + eo.fixed_cost_of_the_BESS),
            format_long_dollar_string(total_cost)
        ))

        executive_summary_strings.append(cost_text)

        health_text = ('This system would provide between {0} and {1} in health benefits to people living in the U.S. per year.'.format(
            format_long_dollar_string(eo.Pollution_Low_Value),
            format_long_dollar_string(eo.Pollution_High_Value),
        ))

        executive_summary_strings.append(health_text)

        NPV_multiplier = float(-npf.pv(eo.discount_rate,20,1,0))
        Helth_Ave = eo.replacement_fraction*(eo.Pollution_Low_Value+eo.Pollution_High_Value)/2
        SCC = eo.CO2_emissions*eo.replacement_fraction*eo.cost_per_ton_of_CO2
        scc_text = ('The system would prevent {0:,.0f} tons of carbon emmisions each year. Assuming a Sotial Cost of Carbon (SCC) of {1}, this would provide roughly {2} in climate benifits per year.'.format(
            (eo.CO2_emissions*eo.replacement_fraction),
            format_long_dollar_string(eo.cost_per_ton_of_CO2),
            format_long_dollar_string(SCC),
        ))

        executive_summary_strings.append(scc_text)
        
        total_sNPV = (Helth_Ave+SCC)*NPV_multiplier
        
        sNPV_text = ('Assuming a 20 year time horizon, with a {0}% discount rate, this system would provide a sotial Net Present Value (sNPV) of {1} for the health benifits and {2} for the climate benifits adding up to a toal sNPV of {3}.'.format(
        eo.discount_rate*100,
        format_long_dollar_string(Helth_Ave*NPV_multiplier), 
        format_long_dollar_string(SCC*NPV_multiplier), 
        format_long_dollar_string(total_sNPV) 
        ) )

        executive_summary_strings.append(sNPV_text)

        low_sNPV = eo.replacement_fraction*eo.Pollution_Low_Value*eo.impact_on_disadvantaged_population_fraction*NPV_multiplier
        high_sNPV = eo.replacement_fraction*eo.Pollution_High_Value*eo.impact_on_disadvantaged_population_fraction*NPV_multiplier
        disad_text = ('Where {0:.1f}% of the U.S. population live in disadvantaged communities, {1:.1f}% of the health benifits would be accrued to people living in disadvantaged communities. This means an estemated sNPV between {2} and {3} would go to disadvantaged communities.'.format(
                    eo.disadvantaged_population_fraction*100,
                    eo.impact_on_disadvantaged_population_fraction*100,
                    format_long_dollar_string(low_sNPV),
                    format_long_dollar_string(high_sNPV)
        ))

        executive_summary_strings.append(disad_text)

        low_sNPV = eo.replacement_fraction*eo.Pollution_Low_Value*eo.impact_on_low_income_population_fraction*NPV_multiplier
        high_sNPV = eo.replacement_fraction*eo.Pollution_High_Value*eo.impact_on_low_income_population_fraction*NPV_multiplier
        low_income_text = ('Where {0:.1f}% of the U.S. population have incomes below 200% of the poverty line, {1:.1f}% of the health benifits would be accrued to people with incomes below 200% of the poverty line. This means an estemated sNPV between {2} and {3} would go to people with low incomes.'.format(
                    eo.low_income_population_fraction*100,
                    eo.impact_on_low_income_population_fraction*100,
                    format_long_dollar_string(low_sNPV),
                    format_long_dollar_string(high_sNPV)
        ))

        executive_summary_strings.append(low_income_text)

        return executive_summary_strings

    def generate_report_from_template(self):
        # Get current date.
        now = datetime.datetime.now()
        today = now.strftime("%B %d, %Y")

        op_handler_requests = self.host_report.report_attributes
        path = op_handler_requests['plant_data']['path']
        with open(path) as f:
            plant_dispatch_json = json.load(f)
        plant_name = plant_dispatch_json['Name']
        plant_state = plant_dispatch_json['State']
        plant_county = plant_dispatch_json['County']

        # Get report-specific data.
        chart_types = self.host_report.chart_types
        chart_list = []
        chart_ix = 1

        for chart_caption, chart_type in chart_types.items():
            if self.host_report.has_chart(chart_type):
                chart_info = {}
                chart_info['path'] = self.graphics_locations[chart_type]
                chart_info['ix'] = chart_ix
                chart_info['caption'] = chart_caption

                chart_list.append(chart_info)
                chart_ix += 1

        template_dir = os.path.join('es_gui', 'resources', 'report_templates')
        output_dir_name = self.report_id

        output_dir = os.path.join('results', 'equity', 'report', output_dir_name)
        os.makedirs(output_dir, exist_ok=True)

        executive_summaries = []
        plt.figure(figsize=(3, 2), dpi=80)
        for ix, op in enumerate(self.host_report.chart_data, start=0):
            eo = op[1]
            if ix == 0:
                plt.plot(range(eo.n),np.sort(eo.plant_dispatch),linewidth=3)
            
            new_plant_dispatch = np.zeros(eo.n)
            if eo.flexible_dispatch == True:
                for i in range(eo.n):
                    if eo.plant_dispatch[i] > 0:
                        new_plant_dispatch[i] = max(eo.plant_dispatch[i] + eo.pe_d[i] + eo.pe_c[i] - eo.pv_capacity*eo.pv_profile[i],0)
            if eo.fixed_dispatch == True:
                for i in range(eo.n):
                    if eo.plant_dispatch[i] > 0:
                        if eo.plant_dispatch[i] > - eo.pe_d[i] - eo.pe_c[i] + eo.pv_capacity*eo.pv_profile[i]:
                            new_plant_dispatch[i] = eo.plant_dispatch[i] 
            
            plt.plot(range(eo.n),np.sort(new_plant_dispatch),label=str(100*eo.replacement_fraction) +'% replacement', linewidth=2)
            executive_summaries.append(self.generate_executive_summary(eo,plant_name))
        
        plt.ylabel('MW')
        plt.xlabel('sorted time (hours)')
        plt.title('Powerplant Power (MW)')
        plt.legend(bbox_to_anchor=(1.02, 0.5), loc="center left", borderaxespad=0, shadow=False, labelspacing=1.8)

        distribution_chart_file = os.path.join(output_dir,'images', 'distribution_chart.png')
        plt.savefig( distribution_chart_file, facecolor='white' )

        results_data = dict()
        results_data['plant_data'] = op_handler_requests['plant_data']
        results_data['analysis_params'] = op_handler_requests['param desc']

        plt.figure(figsize=(3, 2), dpi=80)
        ax = plt.subplot(111)
        max_total_cost = 0
        max_total_pollution_high = 0
        SCALE = 1000000
        iii = 0
        #this loop finds max_total_cost and max_total_pollution_high to use in sizing following plots 
        for ix, op in enumerate(self.host_report.chart_data, start=0):
            eo = op[1]            
            pv_cost =  eo.cost_per_MW_PV_system * eo.pv_capacity + eo.fixed_cost_of_PV_system
            ess_cost = eo.cost_per_MWh_BESS * eo.energy_capacity + eo.cost_per_MW_BESS * eo.power_capacity + eo.fixed_cost_of_the_BESS
            total_cost = pv_cost + ess_cost
            if total_cost  >max_total_cost:
                max_total_cost = total_cost
            total_pollution_low = (eo.Pollution_Low_Value + eo.cost_per_ton_of_CO2*eo.CO2_emissions)*eo.replacement_fraction
            total_pollution_high = (eo.Pollution_High_Value + eo.cost_per_ton_of_CO2*eo.CO2_emissions)*eo.replacement_fraction
            if total_pollution_high > max_total_pollution_high:
                max_total_pollution_high = total_pollution_high

        # payback sROI lines
        slope_5_year = -1/npf.pv(eo.discount_rate,5,1,0)
        slope_10_year = -1/npf.pv(eo.discount_rate,10,1,0)
        slope_15_year = -1/npf.pv(eo.discount_rate,15,1,0)
        slope_20_year = -1/npf.pv(eo.discount_rate,20,1,0)

        capital_range_5y  = 1.2*min(max_total_pollution_high/slope_5_year,max_total_cost)
        capital_range_10y = 1.2*min(max_total_pollution_high/slope_10_year,max_total_cost)
        capital_range_15y = 1.2*min(max_total_pollution_high/slope_15_year,max_total_cost)
        capital_range_20y = 1.2*min(max_total_pollution_high/slope_20_year,max_total_cost)

        payback_after_5_years  = capital_range_5y*slope_5_year 
        payback_after_10_years = capital_range_10y*slope_10_year 
        payback_after_15_years = capital_range_15y*slope_15_year 
        payback_after_20_years = capital_range_20y*slope_20_year 

        ax.plot([0,capital_range_5y/SCALE],[0,payback_after_5_years/SCALE],label='5 year sROI @'+str(100*eo.discount_rate)+'%',linewidth=0.5,color=[0,0.1,0])
        ax.plot([0,capital_range_10y/SCALE],[0,payback_after_10_years/SCALE],label='10 year sROI @'+str(100*eo.discount_rate)+'%',linewidth=0.5,color=[0,0.3,0])
        ax.plot([0,capital_range_15y/SCALE],[0,payback_after_15_years/SCALE],label='15 year sROI @'+str(100*eo.discount_rate)+'%',linewidth=0.5,color=[0,0.7,0])
        ax.plot([0,capital_range_20y/SCALE],[0,payback_after_20_years/SCALE],label='20 year sROI @'+str(100*eo.discount_rate)+'%',linewidth=0.5,color=[0,0.9,0])

        for ix, op in enumerate(self.host_report.chart_data, start=0):
            eo = op[1]            
            pv_cost =  eo.cost_per_MW_PV_system * eo.pv_capacity + eo.fixed_cost_of_PV_system
            ess_cost = eo.cost_per_MWh_BESS * eo.energy_capacity + eo.cost_per_MW_BESS * eo.power_capacity + eo.fixed_cost_of_the_BESS
            total_cost = pv_cost + ess_cost
            total_pollution_low = (eo.Pollution_Low_Value + eo.cost_per_ton_of_CO2*eo.CO2_emissions)*eo.replacement_fraction
            total_pollution_high = (eo.Pollution_High_Value + eo.cost_per_ton_of_CO2*eo.CO2_emissions)*eo.replacement_fraction

            color = PALETTE[divmod(iii, len(PALETTE))[1]]
            text_size = 4*total_cost/max_total_cost
            line_width = 4*total_cost/max_total_cost
            ax.plot([total_cost/SCALE,total_cost/SCALE],[total_pollution_low/SCALE,total_pollution_high/SCALE],label='Low to High Est. R.F. ' +str(100*eo.replacement_fraction) + '%',linewidth=line_width,color=rgba_to_fraction(color))
            ax.text(total_cost/(SCALE),(total_pollution_low/SCALE - max_total_pollution_high*0.05/SCALE),'100%',horizontalalignment='center', verticalalignment='center', size=text_size,color=rgba_to_fraction(color))
            for qq in range(1,10):
                dev = 0.1*qq
                ax.plot([total_cost*dev/(SCALE),total_cost*dev/(SCALE)],[total_pollution_low/SCALE,total_pollution_high/SCALE],linewidth=line_width*dev,color=rgba_to_fraction(color))
                ax.text(total_cost*dev/(SCALE),(total_pollution_low/SCALE - max_total_pollution_high*0.05/SCALE),'{0:.0f}%'.format(100*dev),horizontalalignment='center', verticalalignment='center', size=text_size,color=rgba_to_fraction(color))
            
            results_rp_string = 'results_for_replacement_fraction_{0:.2f}'.format(eo.replacement_fraction)
            results_data[results_rp_string] = {}
            results_data[results_rp_string]['energy_capacity'] = eo.energy_capacity
            results_data[results_rp_string]['energy_capacity'] = eo.energy_capacity
            results_data[results_rp_string]['power_capacity'] = eo.power_capacity
            results_data[results_rp_string]['pv_capacity'] = eo.pv_capacity
            results_data[results_rp_string]['soe'] = eo.soe
            results_data[results_rp_string]['pe_c'] = eo.pe_c
            results_data[results_rp_string]['pe_d'] = eo.pe_d
            iii += 1



        destination_file = os.path.join(output_dir, 'outputfile' + '.json')
        with open(destination_file, 'w') as outfile:
            json.dump(results_data, outfile)

        
        ax.set_ylabel('M$ / year in health and climate benefits \n and Sotial Return On Investment (sROI) thresholds')
        ax.set_xlabel('M$ captial cost')
        ax.set_title('Cost Benefit Analysis')
        ax.legend(bbox_to_anchor=(1.02, 0.5), loc="center left", borderaxespad=0, shadow=False, labelspacing=1.8)

        cost_benefit_chart_file = os.path.join(output_dir,'images', 'cost_benefit.png')
        plt.savefig( cost_benefit_chart_file, facecolor='white' )


        geojon_file = os.path.join(STATIC_HOME, GEOJSON)
        with open(geojon_file) as f:
            counties = json.load(f)

        h_total_value = -plant_dispatch_json['COBRA_results']['Summary']['TotalHealthBenefitsValue_high']

        ben_frac = {}
        max_frac = 0
        for impact in plant_dispatch_json['COBRA_results']['Impacts']:
            FIPS = impact['FIPS']
            #Shannon County, SD (FIPS code = 46113) was renamed Oglala Lakota County and assigned anew FIPS code (46102) effective in 2014.
            if FIPS == '46102':
                FIPS = '46113'
            HV = -impact['C__Total_Health_Benefits_High_Value']
            ben_frac[FIPS] = HV/h_total_value
            if ben_frac[FIPS] > max_frac:
                max_frac = ben_frac[FIPS] 

        fig1 = plt.figure(figsize=(3, 2), dpi=80)
        fig1.subplots_adjust(right=0.95)
        ax = plt.subplot(111)
        colormap = plt.cm.get_cmap('Greens')
        colornorm = mpl.colors.Normalize(vmin=0, vmax=max_frac*100, clip=False)
        n = len(counties['features'])
        for ii in range(n):
            FIPS = counties['features'][ii]['properties']['STATE'] + counties['features'][ii]['properties']['COUNTY']
            #value = dis[FIPS] # set the color value to the % of disadvantaged within a county 
            try:
                value = ben_frac[FIPS]/max_frac 
            except:
                value = 0
            for jj in range(len(counties['features'][ii]['geometry']['coordinates'])):
                try:
                    county_area = Polygon(counties['features'][ii]['geometry']['coordinates'][jj], False,edgecolor='black', facecolor=colormap(value),linewidth=0.25)
                    ax.add_patch(county_area)
                except:
                    nnn = len(counties['features'][ii]['geometry']['coordinates'][jj])
                    for kk in range(nnn):
                        county_area = Polygon(counties['features'][ii]['geometry']['coordinates'][jj][kk], False,edgecolor='black', facecolor=colormap(value),linewidth=0.25)
                        ax.add_patch(county_area)
        ax.set_xlim(-130,-60)
        ax.set_ylim(20,55)
        ax.plot(plant_dispatch_json["lon"],plant_dispatch_json["lat"],"o",color='gold',markersize=1)
        ax.text(plant_dispatch_json["lon"],plant_dispatch_json["lat"]-0.05*35,plant_name,size=6,color='gold',horizontalalignment='center', verticalalignment='center')

        plt.axis('off')
        plt.title('% of Health Benefits That will go to Each US County')
        
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad='1%')
        im = plt.cm.ScalarMappable(norm=colornorm, cmap=colormap)
        fig1.colorbar(im, cax=cax, orientation='vertical')

        benefit_map_file = os.path.join(output_dir,'images', 'benefit_map.png')
        plt.savefig( benefit_map_file, facecolor='white' )

            
        # Initialize Jinja environment.
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(['html']))
        if eo.flexible_dispatch == True:
            template = env.get_template('powerplant_replacement_report_flexible.html')
        if eo.fixed_dispatch == True:
            template = env.get_template('powerplant_replacement_report_fixed.html')
        fname = os.path.join(output_dir, 'powerplant_replacement_report.html')

        # Render output file.
        output = template.render(
                        # GENERAL OUTPUT
                        today=today,
                        header="This report shows the results from optimizations performed by QuESt Equity.",
                        powerplant_name=plant_name, 
                        plant_state=plant_state,
                        plant_county=plant_county,
                        nameplate_capacity = plant_dispatch_json['NameplateCapacity'],
                        fuel_category = plant_dispatch_json['FuelCategory'],
                        capacity_factor = plant_dispatch_json['CapacityFactor'],
                        year = plant_dispatch_json['year'],
                        QuESt_Logo=os.path.join('..', 'images', 'static', 'Quest_Logo_RGB.png'),
                        SNL_image=os.path.join('..', 'images', 'static', 'SNL.png'),
                        DOE_image=os.path.join('..', 'images', 'static', 'DOE.png'),
                        discount_rate               = eo.discount_rate*100,
                        cost_per_ton_of_CO2         = eo.cost_per_ton_of_CO2,
                        cost_per_MW_PV_system       = eo.cost_per_MW_PV_system,
                        fixed_cost_of_PV_system     = eo.fixed_cost_of_PV_system,
                        cost_per_MW_BESS            = eo.cost_per_MW_BESS,
                        cost_per_MWh_BESS           = eo.cost_per_MWh_BESS,
                        fixed_cost_of_the_BESS      = eo.fixed_cost_of_the_BESS,
                        energy_efficiency           = eo.energy_efficiency*100,
                        acknowledgement="Sandia National Laboratories is a multimission laboratory managed and operated by National Technology & Engineering Solutions of Sandia, LLC, a wholly owned subsidiary of Honeywell International Inc., for the U.S. Department of Energy's National Nuclear Security Administration under contract DE-NA0003525.",
                        executive_summaries=executive_summaries,					 
                        # FIGURES
                        charts=chart_list,
                        distribution_chart=os.path.join('images', 'distribution_chart.png'),
                        cost_benefit_chart_file=os.path.join('images', 'cost_benefit.png'),
                        benefit_map_file=os.path.join('images', 'benefit_map.png')
					)
        
        with open(fname,"w") as f:
            f.write(output)

        completion_popup = OpenGeneratedReportPopup()
        completion_popup.report_filename = fname
        completion_popup.open()


class OpenGeneratedReportPopup(MyPopup):
    report_filename = ''

    def open_generated_report(self):
        """Opens the generated report and dismisses the popup,"""
        webbrowser.open('file://' + os.path.realpath(self.report_filename))
        self.dismiss()