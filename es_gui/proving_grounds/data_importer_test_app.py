# This is for setting the window parameters like the initial size. Goes before any other import statements.
# from kivy.config import Config

# Config.set('graphics', 'height', '900')
# Config.set('graphics', 'width', '1600')
# Config.set('graphics', 'minimum_height', '720')
# Config.set('graphics', 'minimum_width', '1280')
# Config.set('graphics', 'resizable', '1')
# Config.set('kivy', 'desktop', 1)

from kivy.app import App
from kivy.uix.widget import Widget


class PongGame(Widget):
    pass


class DataImporterTestApp(App):
    def build(self):
        return PongGame()


if __name__ == '__main__':
    DataImporterTestApp().run()