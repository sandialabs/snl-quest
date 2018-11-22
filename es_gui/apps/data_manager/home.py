from __future__ import absolute_import

from kivy.uix.screenmanager import Screen

class DataManagerHomeScreen(Screen):
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.build_data_manager_nav_bar()
        ab.set_title('Data Manager')