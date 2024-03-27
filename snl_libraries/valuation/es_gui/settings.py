from __future__ import absolute_import

from kivy.uix.settings import InterfaceWithSidebar, Settings, SettingItem
from kivy.uix.label import Label
from kivy.properties import ListProperty


class ESAppSettingsInterface(InterfaceWithSidebar):
    pass


class ESAppSettings(Settings):
    interface_cls = 'ESAppSettingsInterface'

    def __init__(self, **kwargs):
        super(ESAppSettings, self).__init__(**kwargs)
        #self.register_type('title', SettingsTitle)

    def add_kivy_panel(self):
        """
        Hides the Kivy settings.
        """
        pass


class SettingsItem(SettingItem):
    pass


class SettingsTitle(Label):
    title = Label.text


class SettingsBoolean(SettingsItem):
    values = ListProperty(['0', '1'])