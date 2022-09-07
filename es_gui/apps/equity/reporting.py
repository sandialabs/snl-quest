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


class PeakerRepReport(WizardReportInterface):
    chart_types = OrderedDict({
        'Capital Cost': 'cost_bar',
        'Power and Energy': 'power_and_energy',
        'Pollution Reduction benefits': 'pollution_reduction_benefits',
        'Disadvantaged benefits Fraction': 'disadvantaged_stackedbar_normalized',
        'Low-Income benefits Fraction': 'low_income_stackedbar_normalized',
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

            self.chart = BarChart(bar_spacing=25, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_cost_bar_chart)
        elif self.chart_type == 'power_and_energy':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = BarChart(bar_spacing=25, y_axis_format='{0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)            
            self.bind(on_enter=self.generate_power_energy_bar_chart)
        elif self.chart_type == 'pollution_reduction_benefits':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = BarChart(bar_spacing=25, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_pollution_bar_chart)
        elif self.chart_type == 'disadvantaged_stackedbar_normalized':
            # set up vertical orientation for stackedbar chart
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            # generate stackedbar chart
            self.chart = StackedBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='{0:n}%', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=partial(self.generate_disadvantaged_stackedbar_chart))
        
        elif self.chart_type == 'low_income_stackedbar_normalized':
            # set up vertical orientation for stackedbar chart
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            # generate stackedbar chart
            self.chart = StackedBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='{0:n}%', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=partial(self.generate_low_income_stackedbar_chart))
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
            text = ('Rep. Frac.: {0:.0f}%'.format(eo.replacement_fraction*100)
                   +'total cost: ${0:.2f}'.format(total_cost)+'\n')
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
            
            bar_color = colors[divmod(1, len(colors))[1]]
            bar_data.append(['ess-p:'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), eo.power_capacity])

            bar_color = colors[divmod(2, len(colors))[1]]
            bar_data.append(['ess-e:'+str(eo.replacement_fraction*100)+'%', rgba_to_fraction(bar_color), eo.energy_capacity])
            text = ('R.F.: {0:.0f}%'.format(eo.replacement_fraction*100)
                   +' pv: {0:.0f}MW'.format(eo.pv_capacity)
                   +' ess-p: {0:.0f}MW'.format(eo.power_capacity)
                   +' ess-e: {0:.0f}MWh'.format(eo.energy_capacity)+'\n')
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
    
            bar_color = colors[divmod(0, len(colors))[1]]
            bar_data.append(['Total Low', rgba_to_fraction(bar_color), eo.Pollution_Low_Value])
            bar_data.append(['Total High', rgba_to_fraction(bar_color), eo.Pollution_High_Value])
            bar_color = colors[divmod(1, len(colors))[1]]
            bar_data.append(['Disadvantaged Low', rgba_to_fraction(bar_color), eo.total_impact_on_disadvantaged_population_low])
            bar_data.append(['Disadvantaged High', rgba_to_fraction(bar_color), eo.total_impact_on_disadvantaged_population_high])
            bar_color = colors[divmod(2, len(colors))[1]]
            bar_data.append(['Low-Income Low', rgba_to_fraction(bar_color), eo.total_impact_on_low_income_population_low])
            bar_data.append(['Low-Income High', rgba_to_fraction(bar_color), eo.total_impact_on_low_income_population_high])

            break
            
        text = ('Total Health benefits : Low Estemate ${0:.0f}, High Estemate ${1:.0f}'.format(eo.Pollution_Low_Value,eo.Pollution_High_Value)+'\n'
                +'Disadvantaged Communities: Low ${0:.0f}, High ${1:.0f}'.format(eo.total_impact_on_disadvantaged_population_low,eo.total_impact_on_disadvantaged_population_high)+'\n'
                +'Low-Income (<200% poverty): Low ${0:.0f}, High ${1:.0f}'.format(eo.total_impact_on_low_income_population_low,eo.total_impact_on_low_income_population_high) )

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
    
            bar_color = colors[divmod(0, len(colors))[1]]
            population_bar_stack.append(['Disad', rgba_to_fraction(bar_color), eo.disadvantaged_population_fraction*100])
            bar_color = colors[divmod(1, len(colors))[1]]
            population_bar_stack.append(['Non-Disad', rgba_to_fraction(bar_color), 100-eo.disadvantaged_population_fraction*100])

            stackedbar_data['population'] = population_bar_stack

            benefits_bar_stack = []
    
            bar_color = colors[divmod(0, len(colors))[1]]
            benefits_bar_stack.append(['to Disad', rgba_to_fraction(bar_color), eo.impact_on_disadvantaged_population_fraction*100])
            bar_color = colors[divmod(1, len(colors))[1]]
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
    
            bar_color = colors[divmod(0, len(colors))[1]]
            population_bar_stack.append(['Low', rgba_to_fraction(bar_color), eo.low_income_population_fraction*100])
            bar_color = colors[divmod(1, len(colors))[1]]
            population_bar_stack.append(['Non-Low', rgba_to_fraction(bar_color), 100-eo.low_income_population_fraction*100])

            stackedbar_data['population'] = population_bar_stack

            benefits_bar_stack = []
    
            bar_color = colors[divmod(0, len(colors))[1]]
            benefits_bar_stack.append(['to Low', rgba_to_fraction(bar_color), eo.impact_on_low_income_population_fraction*100])
            bar_color = colors[divmod(1, len(colors))[1]]
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
    
    def generate_executive_summary(self,eo):
        """Generates an executive summary similar to the report screen using chart data."""
        #eo = self.host_report.chart_data

        total_cost = eo.cost_per_MWh_BESS * eo.energy_capacity + eo.cost_per_MW_BESS * eo.power_capacity + eo.fixed_cost_of_the_BESS + eo.cost_per_MW_PV_system * eo.pv_capacity + eo.fixed_cost_of_PV_system

        executive_summary_strings = []

        BESS_and_PV_summary = "The selected power plant can be replaced by a combenation of energy storage and PV. The optimal mix is to use a {ess_power} MW, {ess_energy} MWh ESS and {pv_power} MW of PV. The total investment cost for this would be {total_cost}.".format(
            ess_power=eo.power_capacity,
            ess_energy=eo.energy_capacity,
            pv_power=eo.pv_capacity,
            total_cost=format_dollar_string(total_cost)
        )

        executive_summary_strings.append(BESS_and_PV_summary)

        return executive_summary_strings

    def generate_report_from_template(self):
        # Get current date.
        now = datetime.datetime.now()
        today = now.strftime("%B %d, %Y")

        for ix, op in enumerate(self.host_report.chart_data, start=0):
            label = op[0]
            peaker_name = label.split(' | ')[1]

            eo = op[1]
            pv_cost =  eo.cost_per_MW_PV_system * eo.pv_capacity + eo.fixed_cost_of_PV_system
            ess_cost = eo.cost_per_MWh_BESS * eo.energy_capacity + eo.cost_per_MW_BESS * eo.power_capacity + eo.fixed_cost_of_the_BESS

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

        '''plant = {'name': 'Power plant', 'value': plant_data['Name']}

        summary_components = [
            plant
        ]

        

        system_parameters_summary = []

        for parameter in system_params:
            name, val_units = parameter.split(':')
            value, units = val_units.split()

            system_parameters_summary.append({'name': name, 'value': value, 'units': units})'''
        
        executive_summary = self.generate_executive_summary(eo)

        template_dir = os.path.join('es_gui', 'resources', 'report_templates')
        output_dir_name = self.report_id

        output_dir = os.path.join('results', 'equity', 'report', output_dir_name)
        os.makedirs(output_dir, exist_ok=True)
        destination_file = os.path.join(output_dir, 'outputfile' + '.json')

        op_handler_requests = self.host_report.report_attributes
        
        plant_data = op_handler_requests['plant_data']
        system_params = op_handler_requests['param desc']

        results_data = dict()
        results_data['plant_data'] = plant_data
        results_data['system_params'] = system_params
        results_data['energy_capacity'] = eo.energy_capacity
        results_data['power_capacity'] = eo.power_capacity
        results_data['pv_capacity'] = eo.pv_capacity
        results_data['soe'] = eo.soe
        results_data['pe_c'] = eo.pe_c
        results_data['pe_d'] = eo.pe_d

        with open(destination_file, 'w') as outfile:
            json.dump(results_data, outfile)

        '''# Initialize Jinja environment.
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(['html']))
        template = env.get_template('equity_peaker_rep.html')
        fname = os.path.join(output_dir, 'Equity_peaker_rep_report.html')

        # Render output file.
        output = template.render(
                        # GENERAL OUTPUT
                        today=today,
                        header="This report shows the results from optimizations performed by QuESt Equity.",
                        summary_components=summary_components,
                        pv_profile_summary=pv_profile_summary,
                        system_parameters_summary=system_parameters_summary,   
                        QuESt_Logo=os.path.join('..', 'images', 'static', 'Quest_Logo_RGB.png'),
                        SNL_image=os.path.join('..', 'images', 'static', 'SNL.png'),
                        DOE_image=os.path.join('..', 'images', 'static', 'DOE.png'),
                        acknowledgement="Sandia National Laboratories is a multimission laboratory managed and operated by National Technology & Engineering Solutions of Sandia, LLC, a wholly owned subsidiary of Honeywell International Inc., for the U.S. Department of Energy's National Nuclear Security Administration under contract DE-NA0003525.",
                        executive_summary=executive_summary,					 
                        # FIGURES
                        #charts=chart_list,
					)
        

        with open(fname,"w") as f:
            f.write(output)
        '''

        completion_popup = OpenGeneratedReportPopup()
        completion_popup.report_filename = destination_file
        completion_popup.open()


class OpenGeneratedReportPopup(MyPopup):
    report_filename = ''

    def open_generated_report(self):
        """Opens the generated report and dismisses the popup,"""
        webbrowser.open('file://' + os.path.realpath(self.report_filename))
        self.dismiss()