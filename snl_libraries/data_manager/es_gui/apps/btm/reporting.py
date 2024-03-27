from random import sample, choice
from functools import partial
from collections import OrderedDict
import calendar
import os
import datetime
import webbrowser
import base64
from time import sleep

from jinja2 import Environment, FileSystemLoader, select_autoescape
from kivy.uix.screenmanager import Screen, ScreenManager, WipeTransition, NoTransition
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.modalview import ModalView
from kivy.clock import Clock

from es_gui.proving_grounds.charts import BarChart, StackedBarChart, MultisetBarChart, PieChart, DonutChart, format_dollar_string
from es_gui.resources.widgets.common import TWO_ABC_WIDTH, THREE_ABC_WIDTH, MyPopup, TileButton, PALETTE, rgba_to_fraction, ReportScreen, WizardReportInterface, ReportChartToggle


class BtmCostSavingsReport(WizardReportInterface):
    chart_types = OrderedDict({
        'Total bill': 'total_bill_bar',
        # 'Total bill (by source)': 'total_bill_stacked',
        'Total bill comparison': 'total_bill_comparison_multiset',
        'Demand charge comparison': 'demand_charge_comparison_multiset',
        'Energy charge comparison': 'energy_charge_comparison_multiset',
        'NEM comparison': 'nem_comparison_multiset',
        'Peak demand comparison': 'peak_demand_comparison_multiset',
        # 'Total savings': 'total_savings_donut',
                   })
    
    # Sometimes the charges/bills/savings can be negative so we can't use stacked bar or donut charts.

    def __init__(self, chart_data, report_attributes, **kwargs):
        super(BtmCostSavingsReport, self).__init__(**kwargs)

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

            screen = BtmCostSavingsReportScreen(type=opt[1], chart_data=self.chart_data, name=opt[1])
            sm.add_widget(screen)
    
    def has_chart(self, name):
        """Returns True if chart_data will generate a chart."""
        if name in {'demand_charge_comparison_multiset'}:
            has_chart_status = any(op[1].has_demand_charges() for op in self.chart_data)
        elif name in {'energy_charge_comparison_multiset'}:
            has_chart_status = any(op[1].has_energy_charges() for op in self.chart_data)
        elif name in {'nem_comparison_multiset'}:
            has_chart_status = any(op[1].has_nem_charges() for op in self.chart_data)
        else:
            has_chart_status = True
        
        return has_chart_status

    def add_report(self, chart_type, *args):
        # Adds a ReportScreen of type chart_type to the screen manager.
        sm = self.report_sm
        sm.transition = WipeTransition(duration=0.8, clearcolor=[1, 1, 1, 1])

        if not sm.has_screen(chart_type):
            screen = BtmCostSavingsReportScreen(type=chart_type, chart_data=self.chart_data, name=chart_type)
            sm.add_widget(screen)

        sm.current = chart_type
    
    def open_generate_report_menu(self):
        BtmCostSavingsGenerateReportMenu.host_report = self
        gen_report_menu = BtmCostSavingsGenerateReportMenu()
        gen_report_menu.open()


class ReportScreenManager(ScreenManager):
    transition = WipeTransition(duration=0.8, clearcolor=[1, 1, 1, 1])


class BtmCostSavingsReportScreen(ReportScreen):
    """A report screen for the BTM Cost Savings Wizard."""

    def __init__(self, type, chart_data, do_animation=True, **kwargs):
        super(BtmCostSavingsReportScreen, self).__init__(**kwargs)

        self.chart_type = type
        self.chart_data = chart_data
        self.do_animation = do_animation

        if self.chart_type == 'total_bill_bar':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = BarChart(bar_spacing=25, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_total_bill_bar_chart)
        elif self.chart_type == 'total_bill_comparison_multiset':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = MultisetBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_total_bill_comparison_chart)
        elif self.chart_type == 'demand_charge_comparison_multiset':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = MultisetBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_demand_charge_comparison_chart)
        elif self.chart_type == 'energy_charge_comparison_multiset':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = MultisetBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_energy_charge_comparison_chart)
        elif self.chart_type == 'nem_comparison_multiset':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = MultisetBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_nem_charge_comparison_chart)
        elif self.chart_type == 'peak_demand_comparison_multiset':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = MultisetBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='{0:n} kW', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_peak_demand_comparison_chart)
        elif self.chart_type == 'total_savings_donut':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.66

            self.chart = DonutChart(do_animation=self.do_animation)
            self.bind(on_enter=self.generate_total_savings_donut_chart)
        elif self.chart_type == 'total_bill_stacked':
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = StackedBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_total_bill_stackedbar_chart)
        else:
            raise(ValueError('An improper chart type was specified. (got {0})'.format(self.chart_type)))

        self.chart_bx.add_widget(self.chart)

    def on_leave(self):
        # reset the chart
        self.chart.clear_widgets()

    def generate_total_bill_bar_chart(self, *args):
        """Generates bar chart showing the total bill with energy storage each month."""
        bar_data = []

        if len(self.chart_data) > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, len(self.chart_data))

        for ix, op in enumerate(self.chart_data, start=0):
            name = op[0]
            month = name.split(' | ')[1]
            label = month

            solved_op = op[1]
            results = solved_op.results

            bar_color = colors[divmod(ix, len(colors))[1]]
            bar_data.append([label, rgba_to_fraction(bar_color), float(solved_op.total_bill_with_es)])

        self.chart.draw_chart(bar_data)
        max_bar = self.chart.max_bar
        min_bar = self.chart.min_bar

        # generate report text
        self.title.text = "Here's the total bill for each month."
        self.desc.text = 'The total bill is the sum of demand charges, energy charges, and net metering charges. '

        total_charges_str = format_dollar_string(sum(op[1].total_bill_with_es for op in self.chart_data))
        month_high_str = format_dollar_string(max_bar.value)
        month_low_str = format_dollar_string(min_bar.value)

        report_templates = [
        'The total charges for the year was [b]{0}[/b].'.format(total_charges_str),
        'The highest bill for a month was [b]{0}[/b] in [b]{1}[/b].'.format(month_high_str, calendar.month_name[list(calendar.month_abbr).index(max_bar.name)]),
        'The lowest bill for a month was [b]{0}[/b] in [b]{1}[/b].'.format(month_low_str, calendar.month_name[list(calendar.month_abbr).index(min_bar.name)]),
        ]

        self.desc.text += ' '.join(report_templates)
        self.is_drawn = True

    def generate_total_bill_comparison_chart(self, *args):
        """Generates the multiset bar chart comparing total bill with and without energy storage each month."""
        n_cats = 2

        if n_cats > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, n_cats)

        multisetbar_data = OrderedDict()

        for ix, op in enumerate(self.chart_data, start=0):
            name = op[0]
            month = name.split(' | ')[1]
            label = month

            solved_op = op[1]

            bar_group = [['without ES', rgba_to_fraction(colors[0]), float(solved_op.total_bill_without_es)]]
            bar_group.append(['with ES', rgba_to_fraction(colors[1]), float(solved_op.total_bill_with_es)])

            multisetbar_data[label] = bar_group

        self.chart.draw_chart(multisetbar_data)

        # generate report text
        self.title.text = "Here's the total bill with and without energy storage for each month."
        self.desc.text = 'The total bill is the sum of demand charges, energy charges, and net metering charges or credits. '

        report_templates = [
        ]

        total_bill_difference = sum(op[1].total_bill_with_es - op[1].total_bill_without_es for op in self.chart_data)

        if total_bill_difference < 0:
            relation = 'decrease'
            total_difference_str = "It looks like the ESS was able to [b]{0}[/b] the total charges over the year by [b]{1}[/b].".format(relation, format_dollar_string(abs(total_bill_difference)))
            report_templates.append(total_difference_str)

        self.desc.text += ' '.join(report_templates)
        self.is_drawn = True
    
    def generate_demand_charge_comparison_chart(self, *args):
        """Generates the multiset bar chart comparing total demand charges with and without energy storage each month."""
        if any(op[1].has_demand_charges() for op in self.chart_data):
            n_cats = 2

            if n_cats > len(PALETTE):
                colors = PALETTE
            else:
                colors = sample(PALETTE, n_cats)

            multisetbar_data = OrderedDict()

            for ix, op in enumerate(self.chart_data, start=0):
                name = op[0]
                month = name.split(' | ')[1]
                label = month

                solved_op = op[1]
                results = solved_op.results

                bar_group = [['without ES', rgba_to_fraction(colors[0]), float(solved_op.demand_charge_without_es)]]
                bar_group.append(['with ES', rgba_to_fraction(colors[1]), float(solved_op.demand_charge_with_es)])

                multisetbar_data[label] = bar_group

            self.chart.draw_chart(multisetbar_data)

            self.title.text = "Here are the demand charge totals each month."
            self.desc.text = 'The demand charge total consists of time-of-use peak demand charges in addition to a flat peak demand charge, if applicable. The time-of-use demand charge is based on the peak demand during each time period and the corresponding rate. The flat demand charge is based on the peak demand over the entire month, sometimes subject to minimum and/or maximum values. The ESS is useful for reducing net power draw during high time-of-use rates. '
            report_templates = [
            ]

            total_demand_charge_difference = sum(op[1].demand_charge_with_es - op[1].demand_charge_without_es for op in self.chart_data)

            if total_demand_charge_difference < 0:
                relation = 'decrease'
                total_difference_str = "It looks like the ESS was able to [b]{0}[/b] the total demand charges over the year by [b]{1}[/b].".format(relation, format_dollar_string(abs(total_demand_charge_difference)))
                report_templates.append(total_difference_str)

            self.desc.text += ' '.join(report_templates)
            self.is_drawn = True
        else:
            self.title.text = "It looks like there were no demand charges."
            self.desc.text = "The particular rate structure you selected resulted in no demand charges. Either there are no demand charges or no savings on demand charges were accrued using energy storage."

    def generate_energy_charge_comparison_chart(self, *args):
        """Generates the multiset bar chart comparing total energy charges with and without energy storage each month."""
        if any(op[1].has_energy_charges() for op in self.chart_data):
            n_cats = 2

            if n_cats > len(PALETTE):
                colors = PALETTE
            else:
                colors = sample(PALETTE, n_cats)

            multisetbar_data = OrderedDict()

            for ix, op in enumerate(self.chart_data, start=0):
                name = op[0]
                month = name.split(' | ')[1]
                label = month

                solved_op = op[1]
                results = solved_op.results

                bar_group = [['without ES', rgba_to_fraction(colors[0]), float(solved_op.energy_charge_without_es)]]
                bar_group.append(['with ES', rgba_to_fraction(colors[1]), float(solved_op.energy_charge_with_es)])

                multisetbar_data[label] = bar_group

            self.chart.draw_chart(multisetbar_data)

            self.title.text = "Here are the energy charge totals each month."
            self.desc.text = 'The energy charge total is based on net energy consumption and different time-of-use rates. The ESS is useful for reducing energy consumption during high time-of-use periods. '
            report_templates = [
            ]

            total_energy_charge_difference = sum(op[1].energy_charge_with_es - op[1].energy_charge_without_es for op in self.chart_data)

            if total_energy_charge_difference < 0:
                relation = 'decrease'
                total_difference_str = "It looks like the ESS was able to [b]{0}[/b] the total energy charges over the year by [b]{1}[/b].".format(relation, format_dollar_string(abs(total_energy_charge_difference)))
                report_templates.append(total_difference_str)
            else:
                relation = 'increased'
                total_difference_str = "It looks like the total energy charges over the year with the ESS [b]{0}[/b] by [b]{1}[/b]. This is likely due to opportunities for decreasing demand charges or obtaining net metering credits.".format(relation, format_dollar_string(abs(total_energy_charge_difference)))
                report_templates.append(total_difference_str)

            self.desc.text += ' '.join(report_templates)
            self.is_drawn = True
        else:
            self.title.text = "It looks like there were no energy charges."
            self.desc.text = "The particular rate structure you selected resulted in no energy charges. Either there are no time-of-use energy charges or no savings on energy charges were accrued using energy storage."
    
    def generate_nem_charge_comparison_chart(self, *args):
        """Generates the multiset bar chart comparing total net energy metering charges with and without energy storage each month."""
        if any(op[1].has_nem_charges() for op in self.chart_data):
            n_cats = 2

            if n_cats > len(PALETTE):
                colors = PALETTE
            else:
                colors = sample(PALETTE, n_cats)

            multisetbar_data = OrderedDict()

            for ix, op in enumerate(self.chart_data, start=0):
                name = op[0]
                month = name.split(' | ')[1]
                label = month

                solved_op = op[1]

                bar_group = [['without ES', rgba_to_fraction(colors[0]), float(solved_op.nem_charge_without_es)]]
                bar_group.append(['with ES', rgba_to_fraction(colors[1]), float(solved_op.nem_charge_with_es)])

                multisetbar_data[label] = bar_group
            
            self.chart.draw_chart(multisetbar_data)

            self.title.text = "Here are the net energy metering (NEM) totals each month."

            net_metering_type = self.chart_data[0][1].nem_type
            net_metering_rate = self.chart_data[0][1].nem_rate
            
            if net_metering_type == 2:
                net_metering_type_str = '[b]Net energy metering 2.0[/b] uses the time-of-use energy rate for energy.'
            else:
                net_metering_type_str = '[b]Net energy metering 1.0[/b] uses a fixed price for energy, which was [b]{0}[/b]/kWh.'.format(format_dollar_string(net_metering_rate))

            self.desc.text = "{0} Negative values represent credits. ".format(net_metering_type_str)
            report_templates = [
            ]

            total_nem_difference = sum(op[1].nem_charge_with_es - op[1].nem_charge_without_es for op in self.chart_data)

            relation = 'increase' if total_nem_difference < 0 else 'decrease'
            total_difference_str = "The total [b]{0}[/b] in NEM credits with energy storage was [b]{1}[/b].".format(relation, format_dollar_string(abs(total_nem_difference)))
            report_templates.append(total_difference_str)

            self.desc.text += ' '.join(report_templates)
            self.is_drawn = True
        else:
            self.title.text = "It looks like there were no net energy metering charges or credits."
            self.desc.text = "The particular rate structure you selected resulted in no net energy metering charges. Either that or no savings on net energy metering charges were accrued using energy storage."

    def generate_peak_demand_comparison_chart(self, *args):
        """Generates the multiset bar chart comparing peak monthly demand with and without energy storage each month."""
        n_cats = 2

        if n_cats > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, n_cats)

        multisetbar_data = OrderedDict()

        for ix, op in enumerate(self.chart_data, start=0):
            name = op[0]
            month = name.split(' | ')[1]
            label = month

            solved_op = op[1]
            results = solved_op.results

            pfpk_with_es = solved_op.model.pfpk.value
            pfpk_without_es = max(solved_op.model.pnet)

            bar_group = [['without ES', rgba_to_fraction(colors[0]), int(pfpk_without_es)]]
            bar_group.append(['with ES', rgba_to_fraction(colors[1]), int(pfpk_with_es)])

            multisetbar_data[label] = bar_group

        self.chart.draw_chart(multisetbar_data)

        self.title.text = "Here are the peak demand values each month."
        self.desc.text = 'The peak demand value each month is used to compute flat demand charges, if applicable. '
        report_templates = [
        ]

        if all(op[1].model.flt_dr == 0 for op in self.chart_data):
            report_templates.append("For this rate structure, there were no flat demand charges.")

        self.desc.text += ' '.join(report_templates)
        self.is_drawn = True

    def generate_total_savings_donut_chart(self, *args):
        """TODO: Probably deprecate this since we can't guarantee non-negative quantities."""
        donut_data = []
        savings_sources = [
            ('energy charges', 'energy_charge_with_es', 'energy_charge_without_es'),
            ('demand charges', 'demand_charge_with_es', 'demand_charge_without_es'),
            ('NEM charges', 'nem_charge_with_es', 'nem_demand_charge_without_es'),
        ]
        total_savings = 0

        if sum([x[1].nem_charge_without_es for x in self.chart_data]) + sum([x[1].nem_charge_with_es for x in self.chart_data]) <= 0:
            n_cats = 2
        else:
            n_cats = 3

        if n_cats > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, n_cats)

        for ix, source in enumerate(savings_sources[:n_cats], start=0):
            savings = sum([getattr(op[1], source[-1]) - getattr(op[1], source[1]) for op in self.chart_data])
            total_savings += savings

            donut_data.append([source[0], rgba_to_fraction(colors[ix]), savings])

        # generate chart
        self.chart.draw_chart(donut_data)

        # generate report text
        self.title.text = "Here are the savings from each charge source when using energy storage."
        self.desc.text = ''
        report_templates = [
            'The [b]total[/b] savings from energy storage was [b]${0:,.2f}[/b].'.format(total_savings),
        ]

        self.desc.text += ' '.join(report_templates)

    def generate_total_bill_stackedbar_chart(self, *args):
        """TODO: Probably deprecate this since we can't guarantee non-negative quantities."""
        stackedbar_data = OrderedDict()

        charge_sources = [
            ('energy charges', 'energy_charge_with_es'),
            ('demand charges', 'demand_charge_with_es'),
            ('NEM charges', 'nem_charge_with_es'),
        ]

        if sum([x[1].nem_charge_without_es for x in self.chart_data]) + sum([x[1].nem_charge_with_es for x in self.chart_data]) == 0:
            n_cats = 2
        else:
            n_cats = 3

        if n_cats > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, n_cats)

        for op in self.chart_data:
            name = op[0]
            month = name.split(' | ')[1]
            label = month

            solved_op = op[1]
            bar_stack = []

            for iy, source in enumerate(charge_sources[:n_cats], start=0):
                component_color = colors[iy]
                savings = float(getattr(solved_op, source[-1]))

                bar_stack.append([source[0], rgba_to_fraction(component_color), savings])

            stackedbar_data[label] = bar_stack

        self.chart.draw_chart(stackedbar_data)

        self.title.text = "Here's the breakdown of the total bill with energy storage each month."
        self.desc.text = ''

        report_templates = [
        ]

        self.desc.text += ' '.join(report_templates)


class BtmCostSavingsGenerateReportMenu(ModalView):
    host_report = None
    graphics_locations = {}
    report_id = None

    def __init__(self, **kwargs):
        super(BtmCostSavingsGenerateReportMenu, self).__init__(**kwargs)

        self.sm.transition = NoTransition()

        self.report_id = datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')

    def save_figure(self, screen, *args):
        if not self.sm.has_screen(screen.name):
            self.sm.add_widget(screen)

        self.sm.current = screen.name

        chart_images_dir = os.path.join('results', 'btm_cost_savings', 'report', self.report_id, 'images')
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
                screen = BtmCostSavingsReportScreen(type=chart_name, chart_data=self.host_report.chart_data, name=chart_name, do_animation=False)
                Clock.schedule_once(partial(self.save_figure, screen), ix * screen_flip_interval)

        self.generate_report_button.disabled = True

        # Generate report.
        Clock.schedule_once(lambda dt: self.generate_report_from_template(), (n_charts+1)*screen_flip_interval)
    
    def generate_executive_summary(self):
        """Generates an executive summary similar to the report screen using chart data."""
        chart_data = self.host_report.chart_data

        executive_summary_strings = []

        total_bill_summary = "The total bill is the sum of demand charges, energy charges, and net metering charges. The total charges for the year was <b>{total_charges}</b>. The highest bill for a month was <b>{highest_bill}</b>. The lowest bill for a month was <b>{lowest_bill}</b>.".format(
            total_charges=format_dollar_string(sum(op[1].total_bill_with_es for op in chart_data)),
            highest_bill=format_dollar_string(max(op[1].total_bill_with_es for op in chart_data)),
            lowest_bill=format_dollar_string(min(op[1].total_bill_with_es for op in chart_data)),
        )

        executive_summary_strings.append(total_bill_summary)

        bill_comparison_summary = "The total bill without energy storage was <b>{total_bill_without_es}</b>. The total bill with energy storage was <b>{total_bill_with_es}</b>: a difference of <b>{total_bill_diff}</b>.".format(
            total_bill_without_es=format_dollar_string(sum(op[1].total_bill_without_es for op in chart_data)),
            total_bill_with_es=format_dollar_string(sum(op[1].total_bill_with_es for op in chart_data)),
            total_bill_diff=format_dollar_string(abs(sum(op[1].total_bill_with_es - op[1].total_bill_without_es for op in chart_data))),
        )

        executive_summary_strings.append(bill_comparison_summary)

        demand_charge_strings = []
        demand_charge_strings.append("The demand charge total consists of time-of-use (TOU) peak demand charges in addition to flat peak demand charges, if applicable. The TOU demand charge is based on the peak demand during each time period and the corresponding rate. The flat demand charge is based on the peak demand over the entire month, sometimes subject to minimum and/or maximum values. The ESS is useful for reducing net power draw during high TOU rates.")

        demand_charge_summary = ' '.join(demand_charge_strings)
        executive_summary_strings.append(demand_charge_summary)
        demand_charge_strings = []

        peak_demand_without_es = max(max(op[1].model.pnet for op in chart_data))
        peak_demand_with_es = max(op[1].model.pfpk.value for op in chart_data)

        demand_charge_strings.append("Without energy storage, the peak demand observed during the evaluation period was <b>{peak_demand_without_es:.2f} kW</b>. By adding energy storage, this value was changed to <b>{peak_demand_with_es:.2f} kW</b>.".format(
            peak_demand_without_es=peak_demand_without_es,
            peak_demand_with_es=peak_demand_with_es,
        ))

        if any(op[1].has_demand_charges() for op in chart_data):
            demand_charge_with_es = sum(op[1].demand_charge_with_es for op in chart_data)
            demand_charge_without_es = sum(op[1].demand_charge_without_es for op in chart_data)
            total_demand_charge_difference = demand_charge_with_es - demand_charge_without_es

            if total_demand_charge_difference < 0:
                relation = 'decrease'
            else:
                relation = 'increase'
            
            demand_charge_strings.append(
                "It looks like the ESS was able to <b>{relation}</b> the total demand charges over the year from <b>{demand_charge_without_es}</b> to <b>{demand_charge_with_es}</b> for a total difference of <b>{total_demand_charge_difference}</b>.".format(
                    relation=relation,
                    demand_charge_without_es=format_dollar_string(demand_charge_without_es),
                    demand_charge_with_es=format_dollar_string(demand_charge_with_es),
                    total_demand_charge_difference=format_dollar_string(total_demand_charge_difference),
                )
            )
        else:
            demand_charge_strings.append(
                "It looks like there were no demand charges. The particular rate structure you selected resulted in no demand charges. Either there are no demand charges or no savings on demand charges were accrued using energy storage."
            )
        
        demand_charge_summary = ' '.join(demand_charge_strings)
        executive_summary_strings.append(demand_charge_summary)

        energy_charge_strings = []
        energy_charge_strings.append("The energy charge total is based on the net energy consumption and TOU rates. The ESS is useful for reducing energy consumption during high TOU periods.")

        if any(op[1].has_energy_charges for op in chart_data):
            energy_charge_with_es = sum(op[1].energy_charge_with_es for op in chart_data)
            energy_charge_without_es = sum(op[1].energy_charge_without_es for op in chart_data)
            total_energy_charge_difference = energy_charge_with_es - energy_charge_without_es

            if total_energy_charge_difference < 0:
                relation = 'decrease'
                total_difference_str = "It looks like the ESS was able to <b>{relation}</b> the total energy charges over the year by <b>{total_difference}</b> from <b>{energy_charge_without_es}</b> to <b>{energy_charge_with_es}</b>.".format(
                    relation=relation,
                    total_difference=format_dollar_string(total_energy_charge_difference),
                    energy_charge_without_es=format_dollar_string(energy_charge_without_es),
                    energy_charge_with_es=format_dollar_string(energy_charge_with_es),
                )
            else:
                relation = 'increased'
                total_difference_str = "It looks like the total energy charges over the year with the ESS <b>{relation}</b> by <b>{total_difference}</b> from <b>{energy_charge_without_es}</b> to <b>{energy_charge_with_es}</b>. This is likely due to opportunities for decreasing demand charges or obtaining net metering credits.".format(
                    relation=relation,
                    total_difference=format_dollar_string(total_energy_charge_difference),
                    energy_charge_without_es=format_dollar_string(energy_charge_without_es),
                    energy_charge_with_es=format_dollar_string(energy_charge_with_es),
                )
            
            energy_charge_strings.append(total_difference_str)
        else:
            energy_charge_strings.append("It looks like there were no energy charges. Either there are no TOU energy charges or no savings on energy charges were accrued using energy storage.")
        
        energy_charge_summary = ' '.join(energy_charge_strings)
        executive_summary_strings.append(energy_charge_summary)

        net_metering_strings = []
        net_metering_rate = chart_data[0][1].nem_rate
        net_metering_type = chart_data[0][1].nem_type

        if net_metering_type == 2:
            net_metering_strings.append("<b>Net energy metering (NEM) 2.0</b> uses the TOU energy rate for energy.")
        else:
            net_metering_strings.append("<b>Net energy metering (NEM) 1.0</b> uses a fixed price for energy, which was set as <b>{net_metering_rate}/kWh</b>.".format(net_metering_rate=format_dollar_string(net_metering_rate)))

        if any(op[1].has_nem_charges() for op in chart_data):
            net_metering_without_es = sum(op[1].nem_charge_without_es for op in chart_data)
            net_metering_with_es = sum(op[1].nem_charge_with_es for op in chart_data)
            total_net_metering_difference = net_metering_with_es - net_metering_without_es

            relation = 'increase' if total_net_metering_difference < 0 else 'decrease'

            net_metering_strings.append("The total <b>{relation}</b> in NEM credits with energy storage was <b>{total_nem_difference}</b>, from <b>{nem_without_es}</b> to <b>{nem_with_es}</b>.".format(
                relation=relation,
                total_nem_difference=format_dollar_string(total_net_metering_difference),
                nem_without_es=format_dollar_string(net_metering_without_es),
                nem_with_es=format_dollar_string(net_metering_with_es),
            ))
        else:
            net_metering_strings.append("It looks like there were no net energy metering charges or credits. Either that or no savings on NEM charges were accrued using energy storage.")
        
        net_metering_summary = ' '.join(net_metering_strings)
        executive_summary_strings.append(net_metering_summary)

        return executive_summary_strings

    def generate_report_from_template(self):
        # Get current date.
        now = datetime.datetime.now()
        today = now.strftime("%B %d, %Y")

        # Get report-specific data.
        op_handler_requests = self.host_report.report_attributes
        load_profile = op_handler_requests['load_profile']
        pv_profile = op_handler_requests['pv_profile']
        system_params = op_handler_requests['param desc']
        rate_structure = op_handler_requests['rate_structure']

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

        utility = {'name': 'Utility', 'value': rate_structure['utility']['utility name']}
        utility_rate_structure = {'name': 'Rate Structure', 'value': rate_structure['utility']['rate structure name']}
        load_profile_name = {'name': 'Load Profile', 'value': load_profile['name']}

        summary_components = [
            utility,
            utility_rate_structure,
            load_profile_name
        ]

        pv_profile_summary = pv_profile.get('descriptors', [])

        system_parameters_summary = []

        for parameter in system_params:
            name, val_units = parameter.split(':')
            value, units = val_units.split()

            system_parameters_summary.append({'name': name, 'value': value, 'units': units})
        
        executive_summary = self.generate_executive_summary()

        template_dir = os.path.join('es_gui', 'resources', 'report_templates')
        output_dir_name = self.report_id

        output_dir = os.path.join('results', 'btm_cost_savings', 'report', output_dir_name)
        os.makedirs(output_dir, exist_ok=True)

        # Initialize Jinja environment.
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(['html']))
        template = env.get_template('btm_cost_savings.html')
        fname = os.path.join(output_dir, 'BTM_cost_savings_report.html')

        # Render output file.
        output = template.render(
                        # GENERAL OUTPUT
                        today=today,
                        header="This report shows the results from optimizations performed by QuESt BTM.",
                        summary_components=summary_components,
                        pv_profile_summary=pv_profile_summary,
                        system_parameters_summary=system_parameters_summary,   
                        QuESt_Logo=os.path.join('..', 'images', 'static', 'Quest_Logo_RGB.png'),
                        SNL_image=os.path.join('..', 'images', 'static', 'SNL.png'),
                        DOE_image=os.path.join('..', 'images', 'static', 'DOE.png'),
                        acknowledgement="Sandia National Laboratories is a multimission laboratory managed and operated by National Technology & Engineering Solutions of Sandia, LLC, a wholly owned subsidiary of Honeywell International Inc., for the U.S. Department of Energy's National Nuclear Security Administration under contract DE-NA0003525.",
                        executive_summary=executive_summary,					 
                        # FIGURES
                        charts=chart_list,
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