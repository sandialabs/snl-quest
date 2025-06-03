# This is for setting the window parameters like the initial size. Goes before any other import statements.
from kivy.config import Config

Config.set('graphics', 'height', '720')
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'minimum_height', '720')
Config.set('graphics', 'minimum_width', '1280')
Config.set('graphics', 'resizable', '1')
Config.set('kivy', 'desktop', 1)

import os

from kivy.app import App
from kivy.app import Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase

from performance.es_gui.proving_grounds.help_carousel import HelpCarouselModalView

from performance.paths import get_path
dirname = get_path()
Builder.load_file(os.path.join(dirname, 'es_gui', 'resources', 'widgets', 'common.kv'))

LabelBase.register(name='Exo 2',
                   fn_regular=os.path.join(dirname, 'es_gui', 'resources', 'fonts', 'Exo_2', 'Exo2-Regular.ttf'),
                   fn_bold=os.path.join(dirname, 'es_gui', 'resources', 'fonts', 'Exo_2', 'Exo2-Bold.ttf'),
                   fn_italic=os.path.join(dirname, 'es_gui', 'resources', 'fonts', 'Exo_2', 'Exo2-Italic.ttf'))

LabelBase.register(name='Open Sans',
                   fn_regular=os.path.join(dirname, 'es_gui', 'resources', 'fonts', 'Open_Sans', 'OpenSans-Regular.ttf'),
                   fn_bold=os.path.join(dirname, 'es_gui', 'resources', 'fonts', 'Open_Sans', 'OpenSans-Bold.ttf'),
                   fn_italic=os.path.join(dirname, 'es_gui', 'resources', 'fonts', 'Open_Sans', 'OpenSans-Italic.ttf'))

LabelBase.register(name='Modern Pictograms',
                   fn_regular=os.path.join(dirname, 'es_gui', 'resources', 'fonts', 'modernpictograms', 'ModernPictograms.ttf'))


class Home(BoxLayout):
    def open_help(self):
        HelpCarouselModalView().open()


class HelpCarouselTestApp(App):
    def build(self):
        return Home()


if __name__ == '__main__':
    HelpCarouselTestApp().run()