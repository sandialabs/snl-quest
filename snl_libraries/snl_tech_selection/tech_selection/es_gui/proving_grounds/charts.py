from functools import partial
from collections import namedtuple, OrderedDict
from abc import ABCMeta, abstractmethod, abstractproperty

from kivy.graphics import Ellipse, Color, Rectangle, Line
from kivy.animation import Animation
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stencilview import StencilView


def format_dollar_string(value):
    """Formats a float representing USD with comma separators, dollar sign, cents precision, and proper negative sign placement."""
    if value >= 0:
        return_str = "${0:,.2f}".format(value)
    else:
        return_str = "-${0:,.2f}".format(-value)
    
    return return_str


class Chart(RelativeLayout):
    def __init__(self, do_animation=True, **kwargs):
        super(Chart, self).__init__(**kwargs)

        self._do_animation = do_animation
        self._is_drawn = False

    @property
    def do_animation(self):
        """Set to True to animate the chart when the draw_chart() method is called."""
        return self._do_animation

    @do_animation.setter
    def do_animation(self, value):
        self._do_animation = value
    
    @property
    def is_drawn(self):
        """Returns True if a chart has been drawn."""
        return self._is_drawn
    
    @is_drawn.setter
    def is_drawn(self, value):
        self._is_drawn = value

    @abstractmethod
    def draw_chart(self, data):
        pass

    def export_chart(self, data, fname):
        self.draw_chart(data)
        self.export_to_png(fname)


class Bar(Widget):
    height_final = NumericProperty

    def __init__(self, rgba=None, height_final=None, info=None, **kwargs):
        """
        A widget for bars in bar charts.

        :param rgba: Length-4 iterable representing R, G, B, Alpha values in [0, 1].
        :param height_final: Float representing the value of the bar.
        :param info: BarChartEntry, a named tuple with fields ('name', 'rgba', 'value')
        :param kwargs:
        """
        super(Bar, self).__init__(**kwargs)

        self.size_hint_x = None
        self.size_hint_y = None

        self.info = info

        self.color = rgba
        self.height_final = height_final

        with self.canvas.after:
            # draws the bar as a rectangle graphic
            Color(*rgba)
            self.bar = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_bar, size=self._update_bar)

    def _update_bar(self, instance, value):
        """Updates Bar graphic size and position whenever widget size or position changes."""
        self.bar.pos = instance.pos
        self.bar.size = instance.size


class StackedBarChart(Chart):
    def __init__(self, y_axis_format=None, bar_spacing=50, legend_width=170, x_padding=50, y_padding=50, **kwargs):
        """
        A vertically-orientated stacked bar chart. Call draw-chart() with bar_data to draw the chart.

        :param y_axis_format: str; format string for the y-axis labels. Namely for determining precision/separators/etc.
        :param bar_spacing: int (px) representing the space between adjacent bar groups.
        :param legend_width: int (px) representing the width of the legend. Increase if the labels do not render completely.
        :param x_padding: int (px) representing the space between the left and right edges of the chart and chart elements.
        :param y_padding: int (px) representing the space between the top and bottom edges of the chart and chart elements.
        """
        super(StackedBarChart, self).__init__(**kwargs)

        # sets default y-axis label format to two decimal place precision (fixed point)
        if not y_axis_format:
            self.y_axis_format = '{0:.2f}'
        else:
            self.y_axis_format = y_axis_format

        self.legend_width = legend_width
        self.bar_spacing = bar_spacing
        self.x_padding = x_padding
        self.y_padding = y_padding

        self.max_height = None
        self.bar_width = None

        self.max_bar = None
        self.min_bar = None

        self.bar_groups = OrderedDict()
        self.legend = None

    def generate_bars(self, bar_data):
        """
        Computes the size and positions of the bars using bar_data. Adds the bars and axis labels to StackedBarChart. Only supports data values >= 0.

        :param bar_data: OrderedDict where key: name and value: list of lists in format ['category', 'color (rgba iterable)', 'data value'].
        """
        # create a namedtuple to keep track of the information needed to describe each bar stack component
        BarChartEntry = namedtuple('BarChartEntry', ['category', 'rgba', 'value'])
        bars = OrderedDict()

        # form dictionary with key: bar stack name and value: list of BarChartEntry namedtuples corresponding to stack components
        for bar_set_name in bar_data.keys():
            bars[bar_set_name] = [BarChartEntry._make(x) for x in bar_data[bar_set_name]]

            # catch any negative-valued data and raise exception
            if any([bar_component.value < 0 for bar_component in bars[bar_set_name]]):
                raise (ValueError('StackedBarChart does not support negative values!'))

        # determine the tallest and shortest stacks by adding up their values
        self.max_bar = max(bars.items(), key=lambda bar: sum([x.value for x in bar[1]]))
        self.min_bar = min(bars.items(), key=lambda bar: sum([x.value for x in bar[1]]))

        # determine the maximum and minimum stack values
        max_value = sum([x.value for x in self.max_bar[1]])
        min_value = sum([x.value for x in self.min_bar[1]])

        # compute origin coordinates, maximum bar height, and bar width
        x0 = self.legend_width + self.x_padding  # x-coordinate of leftmost bar
        y0 = self.y_padding  # y-coordinate of bar bottom
        self.max_height = self.height - 2*self.y_padding  # y-coordinate of top of tallest bar

        # calculate the total amount of width available for allocating to bars and distributing it evenly
        self.bar_width = (self.width - x0 - self.x_padding - self.bar_spacing*(len(bars) - 1))/len(bars)

        # compute bar height:value ratio
        dydv = self.max_height/(max_value - min(0, min_value))  # ensure that y=0 is included in chart

        # iterate over each bar stack
        for ix, bar_list in enumerate(bars.items(), start=0):
            # unpack tuple
            name = bar_list[0]
            bars = bar_list[1]

            # determine bar position based on index
            bar_pos = (x0 + ix * (self.bar_width + self.bar_spacing), y0)

            # create x-axis label using name
            bar_label = Label(pos=(bar_pos[0] - self.width/2 + self.bar_width/2, self.y_padding/2 - self.height/2),
                              text=name, color=[0, 0, 0, 1])
            self.add_widget(bar_label)

            # initialize stack position and bar stack list
            initial_pos = (bar_pos[0], y0)
            self.bar_groups[name] = []

            # iterate over each component of the stack
            for bar in bars:
                # calculate height based on value
                bar_height = bar.value*dydv

                # generate bar widget and add to appropriate stack
                bar_widget = Bar(size=(self.bar_width, 0), pos=initial_pos, rgba=bar.rgba, height_final=bar_height)
                self.bar_groups[name].append(bar_widget)

                # calculate new starting y-coordinate for next stack element
                initial_pos = (initial_pos[0], initial_pos[1]+bar_height)

        # create y-axis label for maximum value in chart
        max_label = Label(pos=(0.75*x0 - self.width/2, self.max_height + self.y_padding - self.height/2),
                              text=self.y_axis_format.format(max_value), halign='right', color=[0, 0, 0, 1])
        self.add_widget(max_label)

        # line across chart to indicate maximum value
        with self.canvas:
            Color(0, 0, 0, 1)
            Line(points=[x0, self.max_height + self.y_padding,
                         self.width - self.x_padding, self.max_height + self.y_padding],
                 width=1,)

        # create y-axis label for y=0
        zero_label = Label(pos=(0.75*x0 - self.width/2, self.max_height - max_value*dydv + self.y_padding - self.height/2),
                           text='0', halign='right', color=[0, 0, 0, 1])
        self.add_widget(zero_label)

    def draw_chart(self, bar_data):
        """
        Draws the StackedBarChart.

        :param bar_data: OrderedDict where key: name and value: list of lists in format ['category', 'color (rgba iterable)', 'data value'].
        """
        # clear all widgets from the chart
        while len(self.children) > 0:
            for widget in self.children:
                self.remove_widget(widget)

        with self.canvas.before:
            self.canvas.clear()
            Color(1, 1, 1, 1)
            Rectangle(pos=self.pos, size=self.size)

        # generate bar widgets
        self.generate_bars(bar_data)

        if not self._do_animation:
            t_anim = 0  # the length [s] of the growing bar element animation
        else:
            t_anim = 0.5
        n_stack_comp = max([len(x) for x in bar_data.values()])  # the number of elements in each group

        def _anim_bar(bar, height, *args):
            anim = Animation(size=(bar.size[0], height), duration=t_anim, t='out_circ')
            anim.start(bar)

        # iterate over the bar groups
        for name in bar_data.keys():

            # iterate over the bar group elements
            for ix, bar in enumerate(self.bar_groups[name], start=0):
                # add the bar to the chart and schedule its animation
                self.add_widget(bar)
                Clock.schedule_once(partial(_anim_bar, bar, bar.height_final), ix*t_anim)

        # generate legend
        leg_pos = (0, 0)
        leg_size = (self.legend_width, self.height)

        self.legend = ChartLegend(leg_pos, size=leg_size, opacity=0)
        self.add_widget(self.legend)

        # form the legend input [[name, rgba] for each entry]
        legend_data = [[x[0], x[1]] for x in bar_data[list(bar_data.keys())[0]]]

        self.legend.gen_legend(legend_data)

        def _anim_legend(legend, *args):
            if self._do_animation:
                t_anim_legend = 1.0
            else:
                t_anim_legend = 0

            anim = Animation(opacity=1, duration=t_anim_legend, t='linear')
            anim.start(legend)

        # animate the legend opacity after all bars have been built
        Clock.schedule_once(partial(_anim_legend, self.legend), t_anim*n_stack_comp)

        self.is_drawn = True


class MultisetBarChart(StackedBarChart):
    def __init__(self, y_axis_format=None, bar_spacing=50, legend_width=160, x_padding=50, y_padding=50, **kwargs):
        """
        A vertically-orientated multi-set bar chart. Call draw-chart() with bar_data to draw the chart. Subclassed from StackedBarChart.

        :param y_axis_format: str; format string for the y-axis labels. Namely for determining precision/separators/etc.
        :param bar_spacing: int (px) representing the space between adjacent bar groups.
        :param legend_width: int (px) representing the width of the legend. Increase if the labels do not render completely.
        :param x_padding: int (px) representing the space between the left and right edges of the chart and chart elements.
        :param y_padding: int (px) representing the space between the top and bottom edges of the chart and chart elements.
        """
        super(MultisetBarChart, self).__init__(**kwargs)

        # sets default y-axis label format to two decimal place precision (fixed point)
        if not y_axis_format:
            self.y_axis_format = '{0:.2f}'
        else:
            self.y_axis_format = y_axis_format

        self.bar_spacing = bar_spacing
        self.legend_width = legend_width
        self.x_padding = x_padding
        self.y_padding = y_padding

        self.max_height = None
        self.bar_group_width = None
        self.bar_width = None

        self.max_bar = None
        self.min_bar = None

        self.bar_groups = OrderedDict()
        self.legend = None

    def generate_bars(self, bar_data):
        """
        Computes the size and positions of the bars using bar_data. Adds the bars and axis labels to MultisetBarChart.

        :param bar_data: OrderedDict where key: name and value: list of lists in format ['category', 'color (rgba iterable)', 'data value'].
        """
        # create a namedtuple to keep track of the information needed to describe each bar group component
        BarChartEntry = namedtuple('BarChartEntry', ['category', 'rgba', 'value'])
        bars = OrderedDict()

        # form dictionary with key: bar stack name and value: list of BarChartEntry tuples corresponding to set components
        for bar_set_name in bar_data.keys():
            bars[bar_set_name] = [BarChartEntry._make(x) for x in bar_data[bar_set_name]]
        
        # max value by category
        all_bar_components = [bar for bar_set in bars.values() for bar in bar_set]
        categories = {bar_component.category for bar_component in all_bar_components}

        max_bar_entries = {}

        for category in categories:
            category_components = []

            for bar_component in all_bar_components:
                if bar_component.category == category:
                    category_components.append(bar_component)

            max_bar_entries[category] = max(category_components, key=lambda x: abs(x.value))

        # determine the tallest and shortest bars and their respective values
        self.max_bar = max([bar_entry for bar_set in bars.values() for bar_entry in bar_set], key=lambda x: x.value)
        self.min_bar = min([bar_entry for bar_set in bars.values() for bar_entry in bar_set], key=lambda x: x.value)

        max_value = self.max_bar.value
        min_value = self.min_bar.value

        # compute origin coordinates, maximum bar height, and bar width
        x0 = self.legend_width + self.x_padding  # x-coordinate of leftmost bar

        self.max_height = self.height - 2 * self.y_padding  # y-coordinate of top of tallest bar

        # calculate the total amount of width available for allocating to bar groups and distributing it evenly
        self.bar_group_width = (self.width - x0 - self.x_padding - self.bar_spacing * (len(bars) - 1)) / len(bars)

        # calculate width of bars in each in group, assuming no spacing among them
        self.bar_width = self.bar_group_width /max([len(x) for x in bars.values()])

        # compute bar height:value ratio
        try:
            dydv = self.max_height/(max(0, max_value) - min(0, min_value))
        except ZeroDivisionError:
            dydv = 1

        # if negative values: determine coordinate of y=0
        if min_value < 0:
            y0 = self.y_padding + abs(min_value) * dydv
        else:
            y0 = self.y_padding
        
        if max_value < 0:
            y0 = self.max_height + self.y_padding

        # iterate over each bar group
        for ix, bar_list in enumerate(bars.items(), start=0):
            # unpack tuple
            name = bar_list[0]
            bars = bar_list[1]

            # determine bar group position based on index
            bar_pos = (x0 + ix * (self.bar_group_width + self.bar_spacing), y0)

            # create x-axis label using name
            bar_label = Label(pos=(bar_pos[0] - self.width/2 + self.bar_group_width/2, self.y_padding/2 - self.height/2),
                              text=name, color=[0, 0, 0, 1])
            self.add_widget(bar_label)

            # initialize group position and bar group list
            initial_pos = (bar_pos[0], y0)
            self.bar_groups[name] = []

            # iterate over each bar in the group
            for bar in bars:
                # calculate height based on value
                bar_height = bar.value*dydv

                # generate bar widget and add to appropriate group
                bar_widget = Bar(size=(self.bar_width, 0), pos=initial_pos, rgba=bar.rgba, height_final=bar_height)
                self.bar_groups[name].append(bar_widget)

                # calculate new starting x-coordinate for next bar
                initial_pos = (initial_pos[0] + self.bar_width, initial_pos[1])

        # create y-axis label for maximum value in chart
        if max_value > 0:
            max_label = Label(pos=(0.75*x0 - self.width/2, self.max_height + self.y_padding - self.height/2),
                                text=self.y_axis_format.format(max_value), halign='right', color=[0, 0, 0, 1])
            self.add_widget(max_label)

            # line across chart to indicate maximum value
            with self.canvas:
                Color(0, 0, 0, 1)
                Line(points=[x0, self.max_height + self.y_padding,
                            self.width - self.x_padding, self.max_height + self.y_padding],
                    width=1,)

            # create y-axis label for y=0
            zero_label = Label(pos=(0.75*x0 - self.width/2, self.max_height - max_value*dydv + self.y_padding - self.height/2),
                            text='0', halign='right', color=[0, 0, 0, 1])
        else:
            with self.canvas:
                # line to indicate zero value
                Color(0, 0, 0, 1)
                Line(points=[x0, self.max_height + self.y_padding,
                            self.width - self.x_padding, self.max_height + self.y_padding],
                    width=1,)

            zero_label = Label(pos=(0.75*x0 - self.width/2, self.max_height + self.y_padding - self.height/2),
                           text='0', halign='right',color=[0, 0, 0, 1])  
                           
        self.add_widget(zero_label)

        # label y=0 if minimum value < 0
        if min_value < 0:
            # fix y_axis_format specification for proper $ representation for negative values
            if self.y_axis_format[0] == '$':
                label_text = '-' + self.y_axis_format.format(-min_value)
            else:
                label_text = self.y_axis_format.format(min_value)

            min_label = Label(pos=(0.75*x0 - self.width/2, self.y_padding - self.height/2),
                              text=label_text, halign='right', color=[0, 0, 0, 1])
            self.add_widget(min_label)

            # line across chart to indicate minimum value
            with self.canvas:
                Color(0, 0, 0, 1)
                Line(points=[x0, self.y_padding,
                             self.width - self.x_padding, self.y_padding],
                     width=1,)
        
        # label the maximum value for each multibar set
        for category in categories:
            category_max_bar = max_bar_entries[category]

            category_max_value = category_max_bar.value

            if category_max_value != max_value and category_max_value != min_value:
                label_text = self.y_axis_format.format(category_max_value)

                if category_max_value < 0:
                    if self.y_axis_format[0] == '$':
                        label_text = '-' + self.y_axis_format.format(-category_max_value)

                if max_value > 0:
                    component_max_label = Label(pos=(0.75*x0 - self.width/2, self.max_height - (max_value - category_max_value)*dydv + self.y_padding - self.height/2),
                                        text=label_text, halign='right', color=category_max_bar.rgba)
                    self.add_widget(component_max_label)

                    with self.canvas:
                        Color(*category_max_bar.rgba)
                        Line(points=[x0, self.max_height + self.y_padding - (max_value - category_max_value)*dydv,
                                    self.width - self.x_padding, self.max_height + self.y_padding - (max_value - category_max_value)*dydv],
                            width=1,)
                else:
                    component_max_label = Label(pos=(0.75*x0 - self.width/2, self.max_height + category_max_value*dydv + self.y_padding - self.height/2),
                                        text=label_text, halign='right', color=category_max_bar.rgba)
                    self.add_widget(component_max_label)

                    with self.canvas:
                        Color(*category_max_bar.rgba)
                        Line(points=[x0, self.max_height + self.y_padding + category_max_value*dydv,
                                    self.width - self.x_padding, self.max_height + self.y_padding + category_max_value*dydv],
                            width=1,)


class BarChart(Chart):
    def __init__(self, y_axis_format=None, bar_spacing=50, x_padding=25, y_padding=40, **kwargs):
        """
        A vertically-orientated bar chart. Call draw_chart() with bar_data to draw the chart.

        :param y_axis_format: str; format string for the y-axis labels. Namely for determining precision/separators/etc.
        :param bar_spacing: int (px) representing the space between adjacent bars.
        :param x_padding: int (px) representing the space between the left and right edges of the chart and chart elements.
        :param y_padding: int (px) representing the space between the top and bottom edges of the chart and chart elements.
        """
        super(BarChart, self).__init__(**kwargs)

        # sets default y-axis label format to two decimal place precision (fixed point)
        if not y_axis_format:
            self.y_axis_format = '{0:.2f}'
        else:
            self.y_axis_format = y_axis_format

        self.bar_spacing = bar_spacing
        self.x_padding = x_padding
        self.y_padding = y_padding

        self.max_height = None
        self.bar_width = None

        self.bars = []
        self.max_bar = None
        self.min_bar = None

    def generate_bars(self, bar_data):
        """
        Computes the size and positions of the bars using bar_data. Adds the bars and axis labels to BarChart.

        :param bar_data: List of lists in format ['name', 'color (rgba iterable)', 'data value'].
        """
        # create a namedtuple to keep track of the information needed to describe each bar
        BarChartEntry = namedtuple('BarChartEntry', ['name', 'rgba', 'value'])
        bars = [BarChartEntry._make(x) for x in bar_data]

        # determine the tallest and shortest bars
        self.max_bar = max(bars, key=lambda x: x.value)
        self.min_bar = min(bars, key=lambda x: x.value)

        max_value = self.max_bar.value  # the largest value among all prospective bars
        min_value = self.min_bar.value  # the smallest value among all prospective bars

        # compute origin coordinates, maximum bar height, and bar width
        x0 = 5*self.x_padding

        self.max_height = self.height - 2*self.y_padding

        # calculate the total amount of width available for allocating to bars and distributing it evenly
        self.bar_width = (self.width - x0 - self.x_padding - self.bar_spacing*(len(bars) - 1))/len(bars)

        # compute bar height:value ratio
        try:
            dydv = self.max_height/(max(0, max_value) - min(0, min_value))  # ensure that y=0 is included in chart
        except ZeroDivisionError:
            dydv = 1

        if min_value < 0:
            y0 = self.y_padding + abs(min_value)*dydv
        else:
            y0 = self.y_padding
        
        if max_value < 0:
            y0 = self.max_height + self.y_padding

        self.bars = []

        # iterate over each bar
        for ix, bar in enumerate(bars, start=0):
            # generate bars, labels, and bar heights
            bar_pos = (x0 + ix*(self.bar_width + self.bar_spacing), y0)

            bar_height = bar.value * dydv

            bar_widget = Bar(size=(self.bar_width, 0), pos=bar_pos, rgba=bar.rgba, height_final=bar_height, info=bar)
            bar_label = Label(pos=(bar_pos[0] - self.width/2 + self.bar_width/2, self.y_padding/2 - self.height/2),
                              text=bar.name, color=[0, 0, 0, 1])

            self.bars.append(bar_widget)
            self.add_widget(bar_widget)
            self.add_widget(bar_label)

        # create y-axis label for maximum value in chart
        if max_value > 0:
            max_label = Label(pos=(0.5*x0 - self.width/2, self.max_height + self.y_padding - self.height/2),
                            text=self.y_axis_format.format(max_value), halign='right', color=[0, 0, 0, 1])
            self.add_widget(max_label)

            # line across chart to indicate maximum value
            with self.canvas:
                Color(0, 0, 0, 1)
                Line(points=[x0, self.max_height + self.y_padding,
                            self.width - self.x_padding, self.max_height + self.y_padding],
                    width=1,)

            zero_label = Label(pos=(0.5*x0 - self.width/2, self.max_height - max_value*dydv + self.y_padding - self.height/2),
                           text='0', halign='right',color=[0, 0, 0, 1])
        else:
            with self.canvas:
                # line to indicate zero value
                Color(0, 0, 0, 1)
                Line(points=[x0, self.max_height + self.y_padding,
                            self.width - self.x_padding, self.max_height + self.y_padding],
                    width=1,)

            zero_label = Label(pos=(0.5*x0 - self.width/2, self.max_height + self.y_padding - self.height/2),
                           text='0', halign='right',color=[0, 0, 0, 1])        

        self.add_widget(zero_label)

        # label y=0 if minimum value < 0
        if min_value < 0:
            # fix y_axis_format specification for proper $ representation for negative values
            if self.y_axis_format[0] == '$':
                label_text = '-' + self.y_axis_format.format(-min_value)
            else:
                label_text = self.y_axis_format.format(min_value)

            min_label = Label(pos=(0.5 * x0 - self.width / 2, self.y_padding - self.height / 2),
                              text=label_text, halign='right', color=[0, 0, 0, 1])

            self.add_widget(min_label)

            # line across chart to indicate minimum value
            with self.canvas:
                Color(0, 0, 0, 1)
                Line(points=[x0, self.y_padding,
                             self.width - self.x_padding, self.y_padding],
                     width=1,)

    def draw_chart(self, bar_data):
        """
        Draws the BarChart.

        :param bar_data: List of lists in format ['name', 'color (rgba iterable)', 'data value'].
        """
        # clear all widgets from the BarChart
        while len(self.children) > 0:
            for widget in self.children:
                self.remove_widget(widget)

        with self.canvas.before:
            self.canvas.clear()
            Color(1, 1, 1, 1)
            Rectangle(size=self.size, pos=self.pos)

        self.generate_bars(bar_data)

        def _anim_bar(bar, height, *args):
            anim = Animation(size=(bar.size[0], height), duration=1.0, t='out_back')
            anim.start(bar)

        # animate the bars
        for ix, bar in enumerate(self.bars, start=0):
            if isinstance(bar, Bar):
                if self._do_animation:
                    Clock.schedule_once(partial(_anim_bar, bar, bar.height_final), ix*0.05)
                else:
                    bar.height = bar.height_final
        
        self.is_drawn = True


class DonutChart(Chart):
    def __init__(self, **kwargs):
        """
        A donut chart with a legend. Call draw_chart() with pie_data to draw the chart.
        """
        super(DonutChart, self).__init__(**kwargs)

        self.pie = None
        self.legend = None

    def draw_chart(self, pie_data):
        """
        Generates donut chart using pie_data and draws it.

        :param pie_data: List of lists in format ['name', 'color (rgba iterable)', 'data value']
        """
        # clear all widgets
        while len(self.children) > 0:
            for widget in self.children:
                self.remove_widget(widget)

        with self.canvas.before:
            self.canvas.clear()
            Color(1, 1, 1, 1)
            Rectangle(size=self.size, pos=self.pos)

        DonutChartEntry = namedtuple('DonutChartEntry', ['name', 'rgba', 'value'])
        slice_data = [DonutChartEntry._make(x) for x in pie_data]

        # compute donut size and pos
        pie_d = min(self.size[1], self.size[0]/2)
        pie_size = [pie_d, pie_d]
        pie_pos = [0, (self.size[1] - pie_d)/2]

        # generate pie and its slices
        self.pie = Pie(pos=pie_pos, size=pie_size, is_donut=True)
        self.add_widget(self.pie)
        self.pie.gen_slices(pie_data)

        # animate slices
        if self._do_animation:
            t_anim = 0.16
            t_anim_slice = 1.0
            t_anim_legend = 1.0
        else:
            t_anim = 0
            t_anim_slice = 0
            t_anim_legend = 0

        n_slices = len(pie_data)

        def _anim_slice(slice, *args):
            anim = Animation(opacity=1, duration=t_anim_slice, t='out_circ')
            anim.start(slice)

        for ix, slice in enumerate(self.pie.slices, start=0):
            Clock.schedule_once(partial(_anim_slice, slice), t_anim * ix)

        # generate legend
        leg_pos = [pie_pos[0] + pie_d, 0]
        leg_size = [pie_d, self.height]

        self.legend = ChartLegend(position=leg_pos, size=leg_size, opacity=0)
        #self.legend.padding = (0, self.height/4)
        self.add_widget(self.legend)

        val_total = float(sum([x.value if x.value > 0 else 0 for x in slice_data]))
        legend_data = []

        for entry in slice_data:
            legend_text = '{0:.2f}% {1}'.format(entry.value/val_total*100, entry.name)
            legend_data.append([legend_text, entry.rgba])

        self.legend.gen_legend(legend_data)

        # animate legend
        def _anim_legend(legend, *args):
            anim = Animation(opacity=1, duration=t_anim_legend, t='out_circ')
            anim.start(legend)

        Clock.schedule_once(partial(_anim_legend, self.legend), t_anim * n_slices)

        self.is_drawn = True

        # # generate legend
        # hole_proportion = 0.33
        # pie_radius = pie_d
        # hole_radius = pie_radius*(1 - hole_proportion)
        #
        # from math import sqrt
        #
        # leg_pos = [pie_pos[0] + hole_proportion*pie_radius, pie_pos[1] + hole_proportion*pie_radius]
        # leg_size = [2*hole_radius/sqrt(2), 2*hole_radius/sqrt(2)]
        #
        # self.legend = ChartLegend(leg_pos, leg_size, opacity=0)
        # with self.legend.canvas.before:
        #     Rectangle(pos=self.legend.pos, size=self.legend.size, color=Color(1, 0, 0, 0.1))
        # self.add_widget(self.legend)
        # self.legend.gen_legend(pie_data)
        #
        # # animate legend
        # def _anim_legend(legend, *args):
        #     anim = Animation(opacity=1, duration=1.0, t='out_circ')
        #     anim.start(legend)
        #
        # Clock.schedule_once(partial(_anim_legend, self.legend), t_anim * n_slices)


class PieChart(Chart):
    def __init__(self, **kwargs):
        """
        A pie chart with a legend. Call draw_chart() with pie_data to draw the chart.
        """
        super(PieChart, self).__init__(**kwargs)

        self.pie = None
        self.legend = None

    def draw_chart(self, pie_data, is_donut=False):
        """
        Generates pie chart and legend using pie_data and draws them.

        :param pie_data: List of lists in format ['name', 'color (rgba iterable)', 'data value']
        """
        # clear all widgets
        while len(self.children) > 0:
            for widget in self.children:
                self.remove_widget(widget)

        with self.canvas.before:
            self.canvas.clear()
            Color(1, 1, 1, 1)
            Rectangle(size=self.size, pos=self.pos)

        PieChartEntry = namedtuple('PieChartEntry', ['name', 'rgba', 'value'])
        slice_data = [PieChartEntry._make(x) for x in pie_data]

        # compute pie size and pos
        pie_d = min(self.size[1], self.size[0]/2)
        pie_size = [pie_d, pie_d]
        pie_pos = [0, (self.size[1] - pie_d)/2]

        # generate pie and its slices
        self.pie = Pie(pos=pie_pos, size=pie_size, is_donut=is_donut)
        self.add_widget(self.pie)
        self.pie.gen_slices(pie_data)

        # animate slices
        n_slices = len(self.pie.slices)
        if self._do_animation:
            t_anim = 0.16
            t_anim_slice = 1.0
            t_anim_legend = 1.0
        else:
            t_anim = 0
            t_anim_slice = 0
            t_anim_legend = 0

        def _anim_slice(slice, *args):
            anim = Animation(opacity=1, duration=t_anim_slice, t='out_circ')
            anim.start(slice)

        for ix, slice in enumerate(self.pie.slices, start=0):
            Clock.schedule_once(partial(_anim_slice, slice), t_anim*ix)

        # generate legend
        leg_pos = [pie_pos[0] + pie_d, 0]
        leg_size = [pie_d, self.height]

        self.legend = ChartLegend(leg_pos, size=leg_size, opacity=0)
        self.add_widget(self.legend)

        val_total = float(sum([x.value for x in slice_data]))
        legend_data = []

        for entry in slice_data:
            legend_text = '{0:.2f}% {1}'.format(entry.value/val_total*100, entry.name)
            legend_data.append([legend_text, entry.rgba])

        self.legend.gen_legend(legend_data)

        # animate legend
        def _anim_legend(legend, *args):
            anim = Animation(opacity=1, duration=t_anim_legend, t='out_circ')
            anim.start(legend)
        Clock.schedule_once(partial(_anim_legend, self.legend), t_anim*n_slices)

        self.is_drawn = True


class Pie(Widget):
    slices = ListProperty()

    def __init__(self, is_donut=False, separator_width=1.5, **kwargs):
        """
        A widget whose children are its constituting pie chart slices.

        :param is_donut: If True, cuts out a donut hole to transform it into a donut chart.
        :param separator_width: Width of line separating adjacent pie slices (px).
        """
        super(Pie, self).__init__(**kwargs)

        self.is_donut = is_donut
        self.separator_width = separator_width

    def gen_slices(self, pie_data):
        PieChartEntry = namedtuple('PieChartEntry', ['name', 'rgba', 'value'])
        slice_data = [PieChartEntry._make(x) for x in pie_data]
        slice_data.sort(key=lambda x: x.value, reverse=True)

        val_total = float(sum([x.value if x.value > 0 else 0 for x in slice_data]))

        self.slices = []

        total_arc = 360
        angle_start_pos = 0
        angle_start_neg = 0

        if self.is_donut:
            hole_proportion = 0.33  # "radius" of outer layer as fraction of given pie size
            pie_radius = self.size[0]/2
            hole_radius = pie_radius*(1 - hole_proportion)

            if any([entry.value < 0 for entry in slice_data]):
                # positive layer takes inner ring, negative takes original position
                positive_pos = (self.pos[0] + hole_proportion*pie_radius, self.pos[1] + hole_proportion*pie_radius)
                positive_radius = hole_radius
                negative_pos = self.pos
                negative_radius = pie_radius
            else:
                # positive layer only
                positive_pos = self.pos
                positive_radius = pie_radius

            for ix, slice_entry in enumerate(slice_data, start=0):
                # draw outer layer, negative values
                percentage = abs(slice_entry.value)/val_total
                color = slice_entry.rgba

                if slice_entry.value < 0:
                    angle_end_neg = angle_start_neg + percentage*total_arc
                    new_slice = PieSlice(pos=negative_pos,
                                         size=(negative_radius*2, negative_radius*2),
                                         angle_start=angle_start_neg, angle_end=angle_end_neg,
                                         color=color, name=slice_entry.name,
                                         separator_width=self.separator_width,
                                         opacity=0)
                    angle_start_neg = angle_end_neg

                    self.slices.append(new_slice)
                    self.add_widget(self.slices[ix])
                else:
                    break

            # cut outer donut hole
            with self.canvas:
                Color(1, 1, 1, 1)
                Ellipse(pos=positive_pos,
                        size=(2*positive_radius, 2*positive_radius), )

            for iy, slice_entry in enumerate(slice_data[ix:], start=ix):
                # draw inner layer, positive values
                percentage = slice_entry.value/val_total
                color = slice_entry.rgba

                if slice_entry.value > 0:
                    angle_end_pos = angle_start_pos + percentage*total_arc
                    new_slice = PieSlice(pos=positive_pos,
                                         size=(positive_radius*2, positive_radius*2),
                                         angle_start=angle_start_pos, angle_end=angle_end_pos,
                                         color=color, name=slice_entry.name,
                                         separator_width=self.separator_width,
                                         opacity=0)
                    angle_start_pos = angle_end_pos

                    self.slices.append(new_slice)
                    self.add_widget(self.slices[iy])

            with self.canvas:
                Color((1, 1, 1, 1))
                if any([entry.value < 0 for entry in slice_data]):
                    # inner hole
                    Ellipse(pos=(self.pos[0] + 2*hole_proportion*pie_radius, self.pos[1] + 2*hole_proportion*pie_radius),
                            size=(hole_radius, hole_radius),)

                    # pos/neg layer separator
                    Line(ellipse=(self.pos[0] + hole_proportion*pie_radius, self.pos[1] + hole_proportion*pie_radius,
                                  hole_radius*2, hole_radius*2), width=self.separator_width)
                else:
                    # inner hole
                    Ellipse(pos=(self.pos[0] + hole_proportion*pie_radius, self.pos[1] + hole_proportion*pie_radius),
                            size=(2*hole_radius, 2*hole_radius),)

            # label sectors
            # angle_start = 0
            # from math import cos, sin, pi
            #
            # for ix, slice_entry in enumerate(slice_data, start=0):
            #     percentage = slice_entry.value/val_total
            #     angle_end = angle_start + percentage*total_arc
            #     angle_midpoint = (angle_start + angle_end)/2
            #
            #     pct_label_pos = (pie_center[0] + 0.75*hole_radius*sin(angle_midpoint*pi/180),
            #                      pie_center[1] + 0.75*hole_radius*cos(angle_midpoint*pi/180))
            #
            #     pct_label = Label(text=str('%.2f' % (percentage*100) + '%'), color=(0, 0, 0, 1),
            #                       pos=pct_label_pos,
            #                       size_hint_x=None, size_hint_y=None,
            #                       halign='left', valign='center',
            #                       size=(90, 60),
            #                       text_size=(90, 60),
            #                       )
            #
            #     with pct_label.canvas.before:
            #         Rectangle(pos=pct_label_pos, size=pct_label.size, color=Color(1, 0, 0, 0.1))
            #
            #     self.add_widget(pct_label)
            #
            #     angle_start = angle_end
        else:
            pie_radius = self.size[0] / 2
            angle_start = 0

            if any([entry.value < 0 for entry in slice_data]):
                raise(ValueError('Negative values not supported for PieChart.'))

            for ix, slice_entry in enumerate(slice_data, start=0):
                # draw outer layer, negative values
                percentage = abs(slice_entry.value) / val_total
                color = slice_entry.rgba

                angle_end = angle_start + percentage * total_arc
                new_slice = PieSlice(pos=self.pos,
                                     size=(pie_radius * 2, pie_radius * 2),
                                     angle_start=angle_start, angle_end=angle_end,
                                     color=color, name=slice_entry.name,
                                     separator_width=self.separator_width,
                                     opacity=0)
                angle_start = angle_end

                self.slices.append(new_slice)
                self.add_widget(self.slices[ix])

        # redraw 0 degree slice separator
        with self.canvas.after:
            Color((1, 1, 1, 1))
            pie_center = (self.pos[0] + pie_radius, self.pos[1] + pie_radius)

            Line(points=[pie_center[0], pie_center[1],  # pie center
                         pie_center[0],  # pie perimeter x
                         pie_center[1] + pie_radius],  # pie perimeter y
                 width=self.separator_width)


class PieSlice(Widget):
    def __init__(self, pos, color, size, angle_start, angle_end, name, separator_width, **kwargs):
        """
        A widget that represents a slice of a pie chart.

        :param pos: Lower left corner of pie.
        :param color: Color (rgba) of slice.
        :param size: Size (width, height) of pie.
        :param angle_start: Starting angle of slice in degrees (0 = positive y-axis).
        :param angle_end: Ending angle of slice in degrees (0 = positive y-axis).
        :param name: Label of data corresponding to slice.
        :param separator_width: Width of line separating adjacent pie slices (px).
        :param kwargs:
        """
        super(PieSlice, self).__init__(**kwargs)

        self.name = name

        with self.canvas.before:
            # draw slice
            Color(*color)
            self.slice = Ellipse(pos=pos, size=size, angle_start=angle_start, angle_end=angle_end)

            # draw slice separator
            Color((1, 1, 1, 1))
            pie_radius = size[0]/2
            pie_center = (pos[0] + pie_radius, pos[1] + pie_radius)

            from math import cos, sin, pi

            Line(points=[pie_center[0], pie_center[1],
                         pie_center[0] + pie_radius*sin(angle_start*pi/180),
                         pie_center[1] + pie_radius*cos(angle_start*pi/180)],
                 width=separator_width)

        #self.bind(size=self._update_slice, pos=self._update_slice)

    # def _update_slice(self, instance, value):
    #     print(instance.pos, instance.size)
    #     self.slice.pos = instance.pos
    #     self.slice.size = instance.size


class ChartLegend(GridLayout):
    def __init__(self, position, key_height=30, font_size=20, **kwargs):
        super(ChartLegend, self).__init__(**kwargs)

        # Layout properties
        self.cols = 1
        self.padding = (25, self.height/3)
        self.spacing = (0, 10)

        self.pos = position
        self.key_height = key_height
        self.font_size = font_size

        #self.leg_pos = position

    def gen_legend(self, legend_data):
        # background to check widgets size and position
        # with self.canvas.before:
        #     Rectangle(pos=self.pos, size=self.size, color=Color(0.9, 0.9, 0.7, 0.3))
        #     Color(0, 0, 0, 1)
        #     Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]))

        LegEntry = namedtuple('LegEntry', ['text', 'rgba'])
        legend_entries = [LegEntry._make(x) for x in legend_data]

        for entry in legend_entries:
            color = entry.rgba
            legend_text = entry.text

            # leg_entry = LegendEntry(color=color, text=legend_text,
            #                         key_height=(self.leg_size[1]-2*self.padding[1]-self.spacing[1]*(len(legend_entries)-1))/len(legend_entries),
            #                         legend_width=self.leg_size[0])
            leg_entry = LegendEntry(color=color, text=legend_text,
                                    key_height=self.key_height,
                                    legend_width=self.size[0],
                                    font_size=self.font_size,
                                    )

            self.row_default_height = self.key_height
            self.row_force_default = True

            self.add_widget(leg_entry)


class LegendEntry(RelativeLayout):
    def __init__(self, color, text, key_height, legend_width, font_size=20, **kwargs):
        super(LegendEntry, self).__init__(**kwargs)

        self.key_color = color
        self.key_text = text
        self.key_height = key_height
        self.key_width = legend_width

        bx = GridLayout(cols=2, row_default_height=self.key_height, row_force_default=True, spacing=10)

        col_key = BoxLayout(size_hint_x=None, width=self.key_height, height=self.key_height)

        # draw key color
        with col_key.canvas:
            Rectangle(pos=col_key.pos, size=col_key.size, color=Color(*self.key_color))

        # add legend label
        col_text = Label(text=self.key_text, color=(0, 0, 0, 1),
                         pos=(self.key_height+10, 0),
                         size_hint_x=None, size_hint_y=1,
                         halign='left',
                         width=self.key_width - self.key_height,
                         height=self.key_height,
                         font_size=font_size,
                         )

        #col_text.size = col_text.texture_size
        col_text.text_size = col_text.size

        bx.add_widget(col_key)
        bx.add_widget(col_text)

        self.add_widget(bx)

        self.key_label = col_text
        self.key_square = col_key


class RateScheduleChart(Chart):
    def __init__(self, y_axis_format=None, legend_width=90, tile_spacing=2, x_padding=35, y_padding=35, **kwargs):
        """
        A rate schedule chart using colored tiles to communicate the rate tier.

        :param y_axis_format: str; format string for the y-axis labels. Namely for determining precision/separators/etc.
        :param tile_spacing: int (px) representing the space between adjacent squares.
        :param x_padding: int (px) representing the space between the left and right edges of the chart and chart elements.
        :param y_padding: int (px) representing the space between the top and bottom edges of the chart and chart elements.
        """
        super(RateScheduleChart, self).__init__(**kwargs)

        # sets default y-axis label format to two decimal place precision (fixed point)
        if not y_axis_format:
            self.y_axis_format = '{0:.2f}'
        else:
            self.y_axis_format = y_axis_format

        self.tile_spacing = tile_spacing
        self.x_padding = x_padding
        self.y_padding = y_padding
        self.legend_width = legend_width

        self.tiles = []

    def generate_tiles(self, schedule_data, category_colors, labels):
        """
        Computes the size and positions of the tiles using schedule_data. Adds the tiles and axis labels to RateScheduleChart.

        :param schedule_data: List of lists or 2D NumPy array.
        :param category_colors: List of rgba tuples to label categories.
        :param labels: List of label strings for each row.
        """
        n_rows, n_cols = schedule_data.shape        

        # Compute origin coordinates.
        x0 = self.legend_width + 3*self.x_padding
        self.max_height = self.height - self.y_padding

        # Calculate the total amount of width and height available for allocating to tiles and distribute it evenly.
        self.tile_width = (self.width - x0 - self.x_padding - self.tile_spacing*(n_cols - 1))/n_cols
        self.tile_height = (self.max_height - self.y_padding - self.tile_spacing*(n_rows - 1))/n_rows

        self.tiles = []

        # Iterate over each tile
        for iy, row in enumerate(schedule_data, start=0):
            row_label = Label(pos=(0.80*x0 - self.width/2, self.max_height/2 - (iy+0.5)*(self.tile_height + self.tile_spacing)),
            text=labels[iy], color=[0, 0, 0, 1], font_size=12, height=self.tile_height)
            self.add_widget(row_label)

            for ix, tile_value in enumerate(row, start=0):
                pos = (x0 + ix*(self.tile_width + self.tile_spacing), self.max_height - iy*(self.tile_height + self.tile_spacing))
                
                tile_widget = ScheduleTile(size=(self.tile_width, self.tile_height), pos=pos, rgba=category_colors[tile_value])
                # bar_label = Label(pos=(x0 - (self.width - self.tile_width)/2 + ix*(self.tile_width + self.tile_spacing), self.max_height/2 - iy*(self.tile_height + self.tile_spacing)), text=str(tile_value), color=[0, 0, 0, 1])

                self.tiles.append(tile_widget)
                self.add_widget(tile_widget)
                # self.add_widget(bar_label)

                if iy == 0:
                    # Column labels for hours.
                    col_label = Label(pos=(x0 - (self.width - self.tile_width)/2 + ix*(self.tile_width + self.tile_spacing), self.max_height/2 + self.y_padding/2),
                              text=str(ix).zfill(2), color=[0, 0, 0, 1], font_size=12)
                    self.add_widget(col_label)

    def draw_chart(self, schedule_data, category_colors, labels, legend_labels=None):
        """Draws the RateScheduleChart."""
        # Clear all widgets from the RateScheduleChart.
        while len(self.children) > 0:
            for widget in self.children:
                self.remove_widget(widget)

        # with self.canvas.before:
        #     Color(1, 1, 1, 1)
        #     Rectangle(size=self.size, pos=self.pos)

        self.generate_tiles(schedule_data, category_colors, labels)

        def _anim_tile(tile, *args):
            anim = Animation(opacity=1, duration=1.0, t='out_back')
            anim.start(tile)

        # Animate the tiles.
        TILE_ANIM_LENGTH = 0.005

        for ix, tile in enumerate(self.tiles, start=0):
            if isinstance(tile, ScheduleTile):
                if self._do_animation:
                    Clock.schedule_once(partial(_anim_tile, tile), ix*TILE_ANIM_LENGTH)
                else:
                    tile.opacity = 1

        # Generate legend.
        leg_pos = (0, 0)
        leg_size = (self.legend_width, self.height)

        self.legend = ChartLegend(leg_pos, size=leg_size, opacity=0, key_height=15, font_size=10)
        self.add_widget(self.legend)

        # Form the legend input [[name, rgba] for each entry.
        if not legend_labels:
            legend_data = [[str(ix), color] for ix, color in enumerate(category_colors)]
        else:
            legend_data = [[legend_labels[ix], color] for ix, color in enumerate(category_colors)]

        self.legend.gen_legend(legend_data)

        def _anim_legend(legend, *args):
            if self._do_animation:
                t_anim_legend = 0.5
            else:
                t_anim_legend = 0

            anim = Animation(opacity=1, duration=t_anim_legend, t='linear')
            anim.start(legend)

        # Animate the legend opacity
        if self._do_animation:
            Clock.schedule_once(partial(_anim_legend, self.legend), len(self.tiles)*TILE_ANIM_LENGTH)
        else:
            self.legend.opacity = 1
            
        self.is_drawn = True


class ScheduleTile(Widget):
    height_final = NumericProperty

    def __init__(self, rgba=None, **kwargs):
        """
        A widget for tiles in Rate Schedule Charts.

        :param rgba: Length-4 iterable representing R, G, B, Alpha values in [0, 1].
        :param kwargs:
        """
        super(ScheduleTile, self).__init__(**kwargs)

        self.size_hint_x = None
        self.size_hint_y = None

        self.opacity = 0

        self.color = rgba

        with self.canvas.after:
            # draws the bar as a rectangle graphic
            Color(*rgba)
            self.tile = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_tile, size=self._update_tile)

    def _update_tile(self, instance, value):
        """Updates tile graphic size and position whenever widget size or position changes."""
        self.tile.pos = instance.pos
        self.tile.size = instance.size


class RateScheduleGridLayout(GridLayout):
    pass