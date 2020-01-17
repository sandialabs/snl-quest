# This is for setting the window parameters like the initial size. Goes before any other import statements.
from kivy.config import Config

Config.set('graphics', 'height', '900')
Config.set('graphics', 'width', '1600')
Config.set('graphics', 'minimum_height', '720')
Config.set('graphics', 'minimum_width', '1280')
Config.set('graphics', 'resizable', '1')
Config.set('kivy', 'desktop', 1)

from numpy.random import random, randn
import numpy as np

from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase

from es_gui.proving_grounds import charts
import calendar


class ChartTestApp(App):
    """
    The App class for launching the application.
    """

    def build(self):
        # Sets the window/application title
        self.title = 'Charts'

        # Create ScreenManager
        sm = ScreenManager()
        sm.add_widget(ChartScreen())

        # Create BoxLayout container
        bx = BoxLayout(orientation='vertical')

        # Fill BoxLayout
        bx.add_widget(sm)

        return bx


class ChartScreen(Screen):
    def draw_chart(self, chart):
        bar_data = [
            ['Jan', random(4), randn()],
            ['Feb', random(4), randn()],
            ['Mar', random(4), randn()],
            ['Apr', random(4), randn()],
            ['May', random(4), randn()],
            ['Jun', random(4), randn()],
            ['Jul', random(4), randn()],
            ['Aug', random(4), randn()],
            ['Sep', random(4), randn()],
            ['Oct', random(4), randn()],
            ['Nov', random(4), randn()],
            ['Dec', random(4), randn()],
        ]
        chart.draw_chart(bar_data)

    def draw_stacked_chart(self, chart):
        from collections import OrderedDict

        rgba1 = random(4)
        rgba2 = random(4)
        rgba3 = random(4)

        bar_data = OrderedDict()
        bar_data['Jan'] = [['alpha', rgba1, random()], ['beta', rgba2, random()],
                           ['gamma', rgba3, random()]]
        bar_data['Feb'] = [['alpha', rgba1, random()], ['beta', rgba2, random()],
                           ['gamma', rgba3, random()]]
        bar_data['Mar'] = [['alpha', rgba1, random()], ['beta', rgba2, random()],
                           ['gamma', rgba3, random()]]
        bar_data['Apr'] = [['alpha', rgba1, random()], ['beta', rgba2, random()],
                           ['gamma', rgba3, random()]]
        bar_data['May'] = [['alpha', rgba1, random()], ['beta', rgba2, random()],
                           ['gamma', rgba3, random()]]

        chart.draw_chart(bar_data)

    def draw_multiset_chart(self, chart):
        from collections import OrderedDict

        rgba1 = random(4)
        rgba2 = random(4)
        rgba3 = random(4)

        bar_data = OrderedDict()
        bar_data['Jan'] = [['alpha', rgba1, randn()], ['beta', rgba2, randn()],
                           ['gamma', rgba3, randn()]]
        bar_data['Feb'] = [['alpha', rgba1, randn()], ['beta', rgba2, randn()],
                           ['gamma', rgba3, randn()]]
        bar_data['Mar'] = [['alpha', rgba1, randn()], ['beta', rgba2, randn()],
                           ['gamma', rgba3, randn()]]
        bar_data['Apr'] = [['alpha', rgba1, randn()], ['beta', rgba2, randn()],
                           ['gamma', rgba3, randn()]]
        bar_data['May'] = [['alpha', rgba1, randn()], ['beta', rgba2, randn()],
                           ['gamma', rgba3, randn()]]

        chart.draw_chart(bar_data)

    def draw_pie(self, chart, is_donut=False):
        from random import sample
        from string import ascii_letters
        sample(ascii_letters, 5)

        pie_data = [
            [''.join(sample(ascii_letters, 12)), random(4), random()]
            for x in range(5)
            ]

        chart.draw_chart(pie_data, is_donut=is_donut)

    def draw_donut(self, chart):
        from random import sample
        from string import ascii_letters

        pie_data = [
            [''.join(sample(ascii_letters, 12)), random(4), random()]
            for x in range(4)
        ]
        pie_data.append([''.join(sample(ascii_letters, 12)), random(4), random()])

        chart.draw_chart(pie_data)
    
    def draw_rate_schedule_chart(self, chart):
        n_tiers = np.random.randint(1, 4)
        # print(n_tiers)

        schedule_data = np.random.randint(n_tiers, size=(12,24))
        # print(schedule_data)

        labels = calendar.month_abbr[1:]
        category_colors = [random(4), random(4), random(4)]
        
        chart.draw_chart(schedule_data, category_colors[:n_tiers], labels)

if __name__ == '__main__':
    from kivy.core.window import Window

    # Sets window background color
    Window.clearcolor = get_color_from_hex('#FFFFFF')

    ChartTestApp().run()