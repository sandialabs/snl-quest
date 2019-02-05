import json
import collections
import os
import copy
from functools import partial
from random import choice

from kivy.app import App
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.properties import BooleanProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.popup import Popup
from kivy.uix.spinner import SpinnerOption, Spinner
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton

cwd = os.getcwd()

# Animation durations in seconds #
BASE_TRANSITION_DUR = 0.600
BUTTON_FLASH_DUR = 0.100
ANIM_STAGGER = 0.200
FADEIN_DUR = 1.000
SLIDER_DUR = 1.200
LOADING_DUR = 1.000

# Widget sizes #
TWO_ABC_WIDTH = 800
THREE_ABC_WIDTH = 1200

# Software name and information #
APP_NAME = 'QuESt'
APP_TAGLINE = 'Optimizing Energy Storage'

# Palette #
PALETTE = [(0, 83, 118), (132, 189, 0),
     (0, 173, 208), (255, 163, 0), (255, 88, 93), (174, 37, 115)]

def rgba_to_fraction(rgba):
    """Converts rgb values in int format to fractional values suitable for Kivy."""
    if len(rgba) > 3:
        return float(rgba[0])/255, float(rgba[1])/255, float(rgba[2])/255, rgba[3]
    else:
        return float(rgba[0])/255, float(rgba[1])/255, float(rgba[2])/255, 1

def fade_in_animation(content, *args):
    """Fade in animation (on opacity); to be used with Clock scheduler."""
    anim = Animation(transition='out_expo', duration=FADEIN_DUR, opacity=1)
    anim.start(content)


class LeftAlignedText(Label):
    """Label subclass for left-aligned text labels."""
    pass


class BodyTextBase(LeftAlignedText):
    """Base class for body text labels."""
    pass


class TitleTextBase(LeftAlignedText):
    """Base class for title text labels."""
    pass


class TileButton(Button):
    """Button subclass for the tile buttons used throughout the application."""
    pass


class MenuTileButton(TileButton):
    """Large tile button used for main menus."""
    pass


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    """The BoxLayout for displaying RecycleView. Adds selection and focus behavior to the RecycleView."""
    pass


class RecycleViewRow(RecycleDataViewBehavior, BoxLayout):
    """The representation for data entries in the RecycleView. A selectable Label with the name of the saved run."""
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    # run_selector = None

    def refresh_view_attrs(self, rv, index, data):
        """
        Catch and handle the view changes.
        """
        self.index = index
        return super(RecycleViewRow, self).refresh_view_attrs(
            rv, index, data)

    def on_enter(self):
        """Update the description boxes when hovered over."""
        pass
        # run_obj = self.run_selector.rv.data[self.index]
        # run_desc_box = self.run_selector.rv_desc
        #
        # # Update the preview text based on the hovered upon object.
        # run_desc_box.text = '\n'.join(
        #     ['[b]{0}[/b]'.format(run_obj['name']),
        #      '[b]Date: [/b] ' + run_obj['time'],
        #      '[b]ISO:[/b] ' + run_obj['iso'],
        #      '[b]Market Type:[/b] ' + run_obj['market type'],
        #      '[b]Year:[/b] ' + run_obj['year'],
        #      '[b]Month:[/b] ' + run_obj['month'],
        #      '[b]Node:[/b] ' + run_obj['node'],
        #      '[b]Parameters set:[/b] ' + repr(run_obj.get('params', 'Used defaults.')),
        #      ]
        # )

    def on_leave(self):
        """
        Update the description boxes when not hovering over an entry.
        """
        pass
        # run_desc_box = self.run_selector.rv_desc
        #
        # # update the text
        # run_desc_box.text = 'Hover over a saved run to view its details.'

    def on_touch_down(self, touch):
        """
        Add selection on touch down.
        """
        if super(RecycleViewRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """
        Respond to the selection of items in the view.
        """
        self.selected = is_selected


class MyRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super(MyRecycleView, self).__init__(**kwargs)

        self.unfiltered_data = self.data

    def filter_rv_data(self, filter_text):
        self.deselect_all_nodes()
                
        if filter_text:
            self.data = [rv_entry for rv_entry in self.unfiltered_data if filter_text.lower() in rv_entry['name'].lower()]
        else:
            self.data = self.unfiltered_data
    
    def deselect_all_nodes(self):
        while len(self.layout_manager.selected_nodes) > 0:
            for selected_node in self.layout_manager.selected_nodes:
                self.layout_manager.deselect_node(selected_node)


class MyPopup(Popup):
    pass


class WarningPopup(MyPopup):
    def __init__(self, **kwargs):
        super(WarningPopup, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')

        if self._keyboard.widget:
            pass

        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ('enter', 'numpadenter'):
            self.dismiss()

        return True


class ValuationRunCompletePopup(MyPopup):
    pass


class PlotSpinner(Spinner, TileButton):
    pass


class PlotSpinnerOptionCls(SpinnerOption):
    pass


class InputError(Exception):
    pass


class LoadingModalView(ModalView):
    pass
    # def on_open(self):
    #     loading_animation = Animation(transition='linear', duration=LOADING_DUR, opacity=0) + Animation(transition='linear', duration=LOADING_DUR, opacity=1)

    #     for x in range(5):
    #         loading_animation += Animation(transition='linear', duration=LOADING_DUR, opacity=0) + Animation(transition='linear', duration=LOADING_DUR, opacity=1)
    #     # loading_animation.repeat = True

    #     Clock.schedule_once(lambda dt: loading_animation.start(self.logo), 0)


class ReportScreen(Screen):
    pass


class WizardCompletePopup(MyPopup):
    pass


class WizardReportInterface(Screen):
    def on_enter(self):
        # Randomly open one chart.
        def _random_start(*args):
            random_report = choice(self.chart_type_toggle.children)
            random_report.state = 'down'

        if not any([button.state == 'down' for button in self.chart_type_toggle.children]):
            Clock.schedule_once(lambda dt: _random_start(), 0.25)


class ReportChartToggle(ToggleButton, TileButton):
    pass


class ParameterRow(GridLayout):
    """Grid layout containing parameter name, description, text input, and units."""
    def __init__(self, desc, **kwargs):
        super(ParameterRow, self).__init__(**kwargs)

        self._desc = desc

        self.name.text = self.desc.get('name', '')
        self.notes.text = self.desc.get('notes', '')
        self.text_input.hint_text = str(self.desc.get('default', ''))
        self.units.text = self.desc.get('units', '')

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value


class ParamTextInput(TextInput):
    """A TextInput field for entering parameter values. Limited to float values."""
    def insert_text(self, substring, from_undo=False):
        # limit to 8 chars
        substring = substring[:8 - len(self.text)]
        return super(ParamTextInput, self).insert_text(substring, from_undo=from_undo)


class DataGovAPIhelp(ModalView):
    """ModalView to display instructions on how to get a Data.gov (NREL Developer Network) API key."""