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

from es_gui.proving_grounds.charts import BarChart, StackedBarChart, MultisetBarChart, PieChart, DonutChart
from es_gui.resources.widgets.common import TWO_ABC_WIDTH, THREE_ABC_WIDTH, MyPopup, ReportScreen, PALETTE, WizardReportInterface, ReportChartToggle


class ValuationReport(WizardReportInterface):
    chart_types = OrderedDict({'Revenue (by month)': 'revenue_bar',
                   'Revenue (by stream)': 'revenue_multisetbar',
                   'Participation (total)': 'activity_donut',
                   #'Activity (by source)': 'activity_stackedbar',
                   'Participation (by month)': 'activity_stackedbar_normalized'
                   })

    def __init__(self, chart_data, report_attributes, market=None, **kwargs):
        super(ValuationReport, self).__init__(**kwargs)

        self.chart_type = type
        self.chart_data = chart_data
        self.report_attributes = report_attributes
        self.market = market

        sm = self.report_sm

        # build chart type selection buttons and corresponding ReportScreens
        for opt in self.chart_types.items():
            button = ReportChartToggle(text=opt[0])
            button.bind(state=partial(self.add_report, opt[1]))
            self.chart_type_toggle.add_widget(button)

            screen = ValuationReportScreen(type=opt[1], chart_data=self.chart_data, market=self.market, name=opt[1])
            sm.add_widget(screen)

    def add_report(self, chart_type, *args):
        # adds a ReportScreen of type chart_type to the screen manager
        sm = self.report_sm
        sm.transition = WipeTransition(duration=0.8, clearcolor=[1, 1, 1, 1])

        if not sm.has_screen(chart_type):
            screen = ValuationReportScreen(type=chart_type, chart_data=self.chart_data, market=self.market, name=chart_type)
            sm.add_widget(screen)

        sm.current = chart_type
    
    def open_generate_report_menu(self):
        GenerateReportMenu.host_report = self
        gen_report_menu = GenerateReportMenu()
        gen_report_menu.open()


class ReportScreenManager(ScreenManager):
    transition = WipeTransition(duration=0.8, clearcolor=[1, 1, 1, 1])


class ValuationReportScreen(ReportScreen):
    """"""

    # lookup table for decision variables for each model formulation
    activities = dict()
    activities['arbitrage'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'),]
    activities['pjm_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_reg', 'regulation'), ]
    activities['ercot_arbreg'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_ru', 'regulation up'), ('q_rd', 'regulation down'), ]
    activities['miso_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_reg', 'regulation'), ]
    activities['isone_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_reg', 'regulation'), ]
    activities['nyiso_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_reg', 'regulation'), ]
    activities['spp_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_ru', 'regulation up'), ('q_rd', 'regulation down'), ]
    activities['caiso_pfp'] = [('q_r', 'buy (arbitrage)'), ('q_d', 'sell (arbitrage)'), ('q_ru', 'regulation up'), ('q_rd', 'regulation down'), ]

    # lookup table for actions that constitute regulation services for each model formulation
    regulation_def = dict()
    regulation_def['arbitrage'] = []
    regulation_def['pjm_pfp'] = ['regulation', ]
    regulation_def['ercot_arbreg'] = ['regulation up', 'regulation down', ]
    regulation_def['miso_pfp'] = ['regulation', ]
    regulation_def['isone_pfp'] = ['regulation', ]
    regulation_def['nyiso_pfp'] = ['regulation', ]
    regulation_def['spp_pfp'] = ['regulation up', 'regulation down', ]
    regulation_def['caiso_pfp'] = ['regulation up', 'regulation down', ]

    def __init__(self, type, chart_data, market=None, do_animation=True, **kwargs):
        super(ValuationReportScreen, self).__init__(**kwargs)

        self.chart_type = type
        self.chart_data = chart_data
        self.do_animation = do_animation

        # if not market:
        #     # infer market type from Optimizer property
        #     market = self.chart_data[0][1].market_type

        if self.chart_type == 'revenue_bar':
            # bar chart for revenue by month
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = BarChart(bar_spacing=25, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_revenue_bar_chart)
        elif self.chart_type == 'revenue_multisetbar':
            # multiset bar chart for revenue by month by revenue stream
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            self.chart = MultisetBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='${0:,.0f}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=self.generate_revenue_multisetbar_chart)
        elif self.chart_type == 'activity_donut':
            # donut chart for overall device activity
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.66

            self.chart = DonutChart(do_animation=self.do_animation)
            self.bind(on_enter=partial(self.generate_activity_donut_chart, market))
        elif self.chart_type == 'activity_stackedbar':
            # set up vertical orientation for stackedbar chart
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            # generate stackedbar chart
            self.chart = StackedBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='{0:n}', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=partial(self.generate_activity_stackedbar_chart, market, False))
        elif self.chart_type == 'activity_stackedbar_normalized':
            # set up vertical orientation for stackedbar chart
            self.chart_bx.orientation = 'vertical'

            #self.desc.width = THREE_ABC_WIDTH
            self.desc_bx.size_hint_y = 0.33

            # generate stackedbar chart
            self.chart = StackedBarChart(bar_spacing=25, legend_width=TWO_ABC_WIDTH/4, y_axis_format='{0:n}%', size_hint_x=1.0, do_animation=self.do_animation)
            self.bind(on_enter=partial(self.generate_activity_stackedbar_chart, market, True))
        else:
            raise(ValueError('An improper chart type was specified. (got {0})'.format(self.chart_type)))

        self.chart_bx.add_widget(self.chart)

    def rgba_to_fraction(self, rgba):
        """Converts rgb values in int format to fractional values suitable for Kivy."""
        if len(rgba) > 3:
            return float(rgba[0])/255, float(rgba[1])/255, float(rgba[2])/255, rgba[3]
        else:
            return float(rgba[0])/255, float(rgba[1])/255, float(rgba[2])/255, 1

    def on_leave(self):
        # reset the chart
        self.chart.clear_widgets()

    def generate_revenue_bar_chart(self, *args):
        bar_data = []

        # select chart colors
        if len(self.chart_data) > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, len(self.chart_data))

        for ix, op in enumerate(self.chart_data, start=0):
            name = op[0]
            _, _, year, month, _ = name.split(' | ')
            #label = ' '.join([year, month])
            #label = calendar.month_abbr[int(month)]
            label = month

            solved_op = op[1]
            results = solved_op.results

            bar_color = colors[divmod(ix, len(colors))[1]]

            # need convert numpy float to native float for calculations
            bar_data.append([label, self.rgba_to_fraction(bar_color), float(solved_op.gross_revenue)])

        # generate chart
        self.chart.draw_chart(bar_data)
        max_bar = self.chart.max_bar
        min_bar = self.chart.min_bar

        # generate report text
        self.title.text = "Here's how much revenue the device generated each month."
        self.desc.text = 'Revenue was generated based on participation in the selected revenue streams. '
        report_templates = [
            'The gross revenue generated over the evaluation period was [b]${0:,.2f}[/b].'.format(sum([op[1].gross_revenue for op in self.chart_data])),
            'The highest revenue in a month was [b]${0:,.2f}[/b], generated in [b]{1}[/b].'.format(max_bar.value,
                                                                                                   calendar.month_name[list(calendar.month_abbr).index(max_bar.name)]),
        'The lowest revenue in a month was [b]${0:,.2f}[/b], generated in [b]{1}[/b].'.format(min_bar.value,
                                                                                              calendar.month_name[list(calendar.month_abbr).index(min_bar.name)]),
        ]

        self.desc.text += ' '.join(report_templates)

    def generate_revenue_multisetbar_chart(self, *args):
        n_rev_cats = 2

        # select chart colors
        if n_rev_cats > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, n_rev_cats)

        multisetbar_data = OrderedDict()

        # compute activity counts
        for ix, op in enumerate(self.chart_data, start=0):
            name = op[0]
            _, _, year, month, _ = name.split(' | ')
            # label = ' '.join([year, month])
            #label = calendar.month_abbr[int(month)]
            label = month

            solved_op = op[1]
            results = solved_op.results

            try:
                rev_arb = float(results['rev_arb'].tail(1))
                rev_reg = float(results['rev_reg'].tail(1))
            except TypeError:
                rev_arb = 0
                rev_reg = 0

            bar_group = [['arbitrage', self.rgba_to_fraction(colors[0]), rev_arb]]
            bar_group.append(['regulation', self.rgba_to_fraction(colors[1]), rev_reg])

            multisetbar_data[label] = bar_group

        # generate chart
        self.chart.draw_chart(multisetbar_data)

        # generate report text
        self.title.text = "Here's how the device generated revenue each month."
        self.desc.text = 'Revenue was generated based on participation in the selected revenue streams. '
        report_templates = [
            'The [b]gross revenue[/b] generated over the evaluation period was [b]${0:,.2f}[/b].'.format(sum([op[1].gross_revenue for op in self.chart_data])),
        ]

        try:
            total_rev_arb = sum([float(op[1].results['rev_arb'].tail(1)) for op in self.chart_data])
        except TypeError:
            total_rev_arb = 0

        if total_rev_arb >= 0:
            rev_arb_format = '${:,.2f}'.format(total_rev_arb)
        else:
            rev_arb_format = '-${:,.2f}'.format(-total_rev_arb)

        if total_rev_arb < 0:
            report_templates.append('The gross revenue from [b]arbitrage[/b] was [b]{0}[/b], an overall deficit. ' \
                                    'This implies participation in arbitrage was solely for the purpose of having capacity to offer regulation up services.'.format(rev_arb_format))

        self.desc.text += ' '.join(report_templates)

    def generate_activity_donut_chart(self, market=None, *args):
        donut_data = []
        n_activities = dict()
        n_total = 0

        try:
            activities = self.activities[market]
            regulation_def = self.regulation_def[market]
        except KeyError:
            raise(ValueError('Invalid or no market type/formulation specified.'))

        n_activity_cats = len(activities)

        # select chart colors
        if n_activity_cats > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, n_activity_cats)

        # compute activity counts
        for ix, (var, name) in enumerate(activities, start=0):
            n_activity = sum([len(op[1].results[var].values.nonzero()[0]) for op in self.chart_data])
            n_total += n_activity

            n_activities[name] = n_activity

            donut_data.append([name, self.rgba_to_fraction(colors[ix]), n_activity])

        # generate chart
        self.chart.draw_chart(donut_data)

        # generate report text
        self.title.text = "Here's how much the device participated in each revenue stream."
        self.desc.text = 'Each sector represents the share of total state of charge management actions attributed to the specific activity. For example, if 33% of the actions were \"buy (arbitrage),\" that means 33% of the total actions performed were for buying energy through arbitrage. \n\n'
        report_templates = [
            'The [b]total[/b] number of actions performed over the evaluation period was [b]{0:n}[/b].'.format(
                n_total),
        ]

        if n_activities['sell (arbitrage)']/float(n_total) < n_activities['buy (arbitrage)']/float(n_total):
            report_templates.append(
                'The [b]percentage[/b] of actions of selling in the [b]arbitrage[/b] market was [b]{0:.2f}%[/b], less than the percentage for buying. ' \
                'This implies that participation in arbitrage was for the purpose of having energy to offer regulation up services.'.format(
                    n_activities['sell (arbitrage)']/float(n_total)*100))
        #
        # if sum([n_activities[name] for name in regulation_def])/float(n_total) > 0.50:
        #     report_templates.append(
        #         'The device spent a majority of its actions on offering regulation services.'
        #     )

        self.desc.text += ' '.join(report_templates)

    def generate_activity_stackedbar_chart(self, market=None, normalized=False, *args):
        """
        Creates a stacked bar chart counting the number of times each decision variable was nonzero. The number and labels of bar components are determined by the market type/formulation.

        :param market: str for the name of the market type/formulation. This is used for the lookup table in the Screen properties.
        :param normalized: Boolean; if true, bar stacks add up to 100% and each stack element represents percentage of the total.

        :return:
        """
        stackedbar_data = OrderedDict()

        try:
            activities = self.activities[market]
            regulation_def = self.regulation_def[market]
        except KeyError:
            raise(ValueError('Invalid or no market type/formulation specified.'))

        n_activity_cats = len(activities)

        # select chart colors
        if n_activity_cats > len(PALETTE):
            colors = PALETTE
        else:
            colors = sample(PALETTE, n_activity_cats)

        # compute activity counts
        for ix, op in enumerate(self.chart_data, start=0):
            name = op[0]
            _, _, year, month, _ = name.split(' | ')
            # label = ' '.join([year, month])
            #label = calendar.month_abbr[int(month)]
            label = month

            solved_op = op[1]
            results = solved_op.results

            bar_stack = []

            if normalized:
                # use percentages instead of counts for bar value

                # compute the total number of actions in the stack
                n_month_total = float(sum([len(results[var].values.nonzero()[0]) for (var, cat) in activities]))

                for iy, (var, cat) in enumerate(activities, start=0):
                    component_color = colors[iy]
                    n_activity = sum([len(results[var].values.nonzero()[0])])

                    try:
                        n_activity_normalized = n_activity/n_month_total*100
                    except ZeroDivisionError:
                        n_activity_normalized = 0

                    bar_stack.append([cat, self.rgba_to_fraction(component_color), n_activity_normalized])
            else:
                # use counts for bar value
                for iy, (var, cat) in enumerate(activities, start=0):
                    component_color = colors[iy]
                    n_activity = sum([len(results[var].nonzero()[0])])

                    bar_stack.append([cat, self.rgba_to_fraction(component_color), n_activity])

            stackedbar_data[label] = bar_stack

        # generate chart
        self.chart.draw_chart(stackedbar_data)

        # generate report text
        self.title.text = "Here's how the device participated in each revenue stream each month."

        if normalized:
            self.desc.text = 'Each bar segment represents the share of total actions attributed to each activity per month. \n\n'
        else:
            self.desc.text = 'Each bar segment represents the number of times the corresponding activity was performed during that month. \n\n'

        report_templates = [
        ]

        self.desc.text += ' '.join(report_templates)


class GenerateReportMenu(ModalView):
    host_report = None
    graphics_locations = {}
    report_id = None

    def __init__(self, **kwargs):
        super(GenerateReportMenu, self).__init__(**kwargs)

        self.sm.transition = NoTransition()

        # Assign a virtually unique ID to this report generator instance
        self.report_id = '_'.join([
            datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S'), 
            self.host_report.report_attributes['market area']
        ]
        )

    def save_figure(self, screen, *args):
        if not self.sm.has_screen(screen.name):
            self.sm.add_widget(screen)

        self.sm.current = screen.name
        chart_images_dir = os.path.join('results', 'valuation', 'report', self.report_id, 'images')
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
            screen = ValuationReportScreen(type=opt[1], chart_data=self.host_report.chart_data, market=self.host_report.market, name=opt[1], do_animation=False)

            Clock.schedule_once(partial(self.save_figure, screen), ix * screen_flip_interval)

        self.generate_report_button.disabled = True

        # Generate report.
        Clock.schedule_once(lambda dt: self.generate_report_from_template(), (n_charts+1)*screen_flip_interval)

    def generate_report_from_template(self):
        # Get current date.
        now = datetime.datetime.now()
        today = now.strftime("%B %d, %Y")

        # Get report-specific data.
        report_attributes = self.host_report.report_attributes

        ISO = report_attributes['market area']
        pricing_node = report_attributes['pricing node']
        ES_device = report_attributes['selected device']
        revenue_streams = report_attributes['revenue streams']
        dates_analyzed = report_attributes['dates analyzed']
        power_rating = report_attributes['Power_rating']
        energy_capacity = report_attributes['Energy_capacity']
        storage_efficiency = report_attributes['Self_discharge_efficiency']
        conversion_efficiency = report_attributes['Round_trip_efficiency']

        # Retrieve HTML template based on selected ISO.
        template_dir = os.path.join('es_gui', 'resources', 'report_templates')
        output_dir_name = self.report_id

        output_dir = os.path.join('results', 'valuation', 'report', output_dir_name)
        os.makedirs(output_dir, exist_ok=True)

        # Initialize Jinja environment.
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(['html']))
        fname = os.path.join(output_dir, '{0}_valuation_report.html'.format('_'.join([ISO, pricing_node])))

        if ISO == "ERCOT":
            template = env.get_template('valuation_report_ERCOT.html')
            
        elif ISO == "MISO":
            template = env.get_template('valuation_report_MISO.html')
            
        elif ISO == "PJM":
            template = env.get_template('valuation_report_PJM.html')

        elif ISO == "ISONE":
            template = env.get_template('valuation_report_ISONE.html')
        elif ISO == "NYISO":
            template = env.get_template('valuation_report_NYISO.html')
        elif ISO == "SPP":
            template = env.get_template('valuation_report_SPP.html')
        elif ISO == "CAISO":
            template = env.get_template('valuation_report_CAISO.html')
        else :
            raise ValueError('The selected ISO does not have a reporting template.')

        # Render output file.
        output = template.render(
					 # GENERAL OUTPUT
					 today=today,
			  		 market_area=ISO,
			  		 header="This report shows the results from optimizations performed by QuESt Valuation.",
			  		 pricing_node=pricing_node,						 
			  		 dates_analyzed=dates_analyzed,
			  		 revenue_streams=revenue_streams,
			  		 ES_device=ES_device,
                     QuESt_Logo=os.path.join('..', 'images', 'static', 'Quest_Logo_RGB.png'),
			  		 SNL_image=os.path.join('..', 'images', 'static', 'SNL.png'),
			  		 DOE_image=os.path.join('..', 'images', 'static', 'DOE.png'),
			  		 acknowledgement="Sandia National Laboratories is a multimission laboratory managed and operated by National Technology & Engineering Solutions of Sandia, LLC, a wholly owned subsidiary of Honeywell International Inc., for the U.S. Department of Energy's National Nuclear Security Administration under contract DE-NA0003525.",
					 # PARAMETER VALUES TABLE
					 power_rating=power_rating,
					 energy_capacity=energy_capacity,
					 storage_efficiency=storage_efficiency,
					 conversion_efficiency=conversion_efficiency,						 
					 # FIGURES
					 revenue_total=self.graphics_locations['revenue_bar'],
					 revenue_source=self.graphics_locations['revenue_multisetbar'],
					 activity_total_percent=self.graphics_locations['activity_donut'],
					 activity_source=self.graphics_locations['activity_stackedbar_normalized'],
					 activity_source_percent=self.graphics_locations['activity_stackedbar_normalized']
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