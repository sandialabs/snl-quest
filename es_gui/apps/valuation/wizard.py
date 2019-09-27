from __future__ import absolute_import, print_function

import logging
from functools import partial
import webbrowser
import calendar
import os

from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition, ScreenManagerException
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, ListProperty, DictProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput

from es_gui.apps.valuation.reporting import ValuationReport
from es_gui.resources.widgets.common import MyPopup, WarningPopup, WizardCompletePopup, TileButton, RecycleViewRow, BASE_TRANSITION_DUR, BUTTON_FLASH_DUR, ANIM_STAGGER,FADEIN_DUR, SLIDER_DUR, fade_in_animation


class ValuationWizard(Screen):
    """The main screen for the valuation wizard. This hosts the nested screen manager for the actual wizard."""
    def on_enter(self):
        ab = self.manager.nav_bar
        ab.reset_nav_bar()
        ab.set_title('Wizard')

    def on_leave(self):
        # Reset wizard to initial state by removing all screens except the first.
        self.sm.current = 'start'

        if len(self.sm.screens) > 1:
            self.sm.clear_widgets(screens=self.sm.screens[1:])


class ValuationWizardScreenManager(ScreenManager):
    """The screen manager for the valuation wizard screens."""
    def __init__(self, **kwargs):
        super(ValuationWizardScreenManager, self).__init__(**kwargs)

        self.transition = SlideTransition()
        self.add_widget(ValuationWizardStart(name='start'))


class ValuationWizardStart(Screen):
    """The starting/welcome screen for the valuation wizard."""
    def _next_screen(self):
        if not self.manager.has_screen('iso_select'):
            screen = ValuationWizardISOSelect(name='iso_select')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'iso_select'


class ValuationWizardTemplate(Screen):
    """A screen template for the valuation wizard."""
    pass


class ToggleTileButton(ToggleButton, TileButton):
    selection_animation = Animation(transition='linear', duration=BUTTON_FLASH_DUR, opacity=0) \
                          + Animation(transition='linear', duration=BUTTON_FLASH_DUR, opacity=1) \
                          + Animation(transition='linear', duration=BUTTON_FLASH_DUR, opacity=0) \
                          + Animation(transition='linear', duration=BUTTON_FLASH_DUR, opacity=1)


class WizardISOTileButton(ToggleTileButton):
    """Tile button with toggle behavior for each ISO option."""
    iso_screen = None

    def __init__(self, name, **kwargs):
        super(WizardISOTileButton, self).__init__(**kwargs)

        self._name = name

    @property
    def name(self):
        """The name of the ISO/market area."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def on_press(self):
        if self.state == 'down':
            self.selection_animation.start(self)
            self.iso_screen.iso = self.name


class ValuationWizardISOSelect(Screen):
    """The ISO selection screen for the valuation wizard."""
    iso = StringProperty('')
    has_selection = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(ValuationWizardISOSelect, self).__init__(**kwargs)

        WizardISOTileButton.iso_screen = self

    def on_pre_enter(self):
        while len(self.iso_select.children) > 0:
            for widget in self.iso_select.children:
                if isinstance(widget, WizardISOTileButton):
                    self.iso_select.remove_widget(widget)
        
        ISO_OPTIONS = App.get_running_app().data_manager.get_markets()

        for iso in ISO_OPTIONS:
            iso_button = WizardISOTileButton(name=iso, text=iso, group='iso')
            self.iso_select.add_widget(iso_button)

    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)

        def _fade_in_buttons(button, *args):
            anim = Animation(transition='out_expo', duration=FADEIN_DUR, opacity=1)
            anim.start(button)

        for ix, iso_button in enumerate(reversed(self.iso_select.children), start=1):
            Clock.schedule_once(partial(_fade_in_buttons, iso_button), ix*ANIM_STAGGER)

    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0

        for iso_button in self.iso_select.children:
            Animation.cancel_all(iso_button)
            iso_button.opacity = 0

    def on_iso(self, instance, value):
        logging.info('ValuationWizard: ISO changed to {0}.'.format(value))

        self.has_selection = True if \
            any([button.state == 'down' for button in self.iso_select.children]) \
            else False

    def on_has_selection(self, instance, value):
        # Enables/disables the next button if an ISO is selected.
        self.next_button.disabled = not value

    def _next_screen(self, *args):
        """Adds the revenue stream selection screen if it does not exist and changes screens to it."""
        if not self.manager.has_screen('node_select'):
            screen = ValuationWizardNodeSelect(name='node_select')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'node_select'


class ValuationWizardNodeSelect(Screen):
    iso = StringProperty('')
    has_selection = BooleanProperty(False)
    node = DictProperty('')

    def __init__(self, **kwargs):
        super(ValuationWizardNodeSelect, self).__init__(**kwargs)

        NodeRecycleViewRow.node_screen = self

    def on_pre_enter(self):
        self.iso = self.manager.get_screen('iso_select').iso

    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)

    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0

    def on_iso(self, instance, value):
        self.has_selection = False
        self.node_rv.deselect_all_nodes()

        try:
            data_manager = App.get_running_app().data_manager
            node_options = [{'name': node[1],
                            'nodeid': node[0]} for node in data_manager.get_nodes(value).items()]
            self.node_rv.data = node_options
            self.node_rv.unfiltered_data = node_options
        except AttributeError:
            pass

    def on_node(self, instance, value):
        logging.info('ValuationWizard: Pricing node changed to {0} (ID: {1}).'.format(self.node['name'], self.node['nodeid']))

        self.has_selection = True

    def on_has_selection(self, instance, value):
        # Enables the next button if a node is selected.
        self.next_button.disabled = not value

    def _next_screen(self):
        """Adds the selection summary screen if it does not exist and changes screens to it."""
        if not self.manager.has_screen('rev_stream_select'):
            screen = ValuationWizardRevenueSelect(name='rev_stream_select')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'rev_stream_select'


class NodeRecycleViewRow(RecycleViewRow):
    """The representation widget for node in the node selector RecycleView."""
    node_screen = None

    def on_touch_down(self, touch):
        """Add selection on touch down."""
        if super(NodeRecycleViewRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected

        if is_selected:
            self.node_screen.node = rv.data[self.index]


class WizardRevToggleButton(ToggleTileButton):
    """Tile button with toggle and hover behavior for each revenue stream option."""
    rev_screen = None
    desc_box = None

    def __init__(self, desc, name, **kwargs):
        super(WizardRevToggleButton, self).__init__(**kwargs)

        self._name = name
        self._desc = desc
        self._final_pos = None

    @property
    def name(self):
        """The name of the market formulation as known to the ValuationOptimizer."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def desc(self):
        """A description of the market formulation."""
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value

    @property
    def final_pos(self):
        """The final position of the button."""
        return self._final_pos

    @final_pos.setter
    def final_pos(self, value):
        self._final_pos = value

    def on_press(self):
        if self.state == 'down':
            self.selection_animation.start(self)
            self.rev_screen.market_formulation = self.text
            self.desc_box.text = '\n'.join(['[b]{0}[/b]'.format(self.text), self.desc])


class ValuationWizardRevenueSelect(Screen):
    """The revenue stream selection screen for the valuation wizard."""
    iso = StringProperty('')
    market_formulation = StringProperty('')
    has_selection = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(ValuationWizardRevenueSelect, self).__init__(**kwargs)

        WizardRevToggleButton.desc_box = self.item_desc
        WizardRevToggleButton.rev_screen = self

    def on_pre_enter(self):
        self.iso = self.manager.get_screen('iso_select').iso

    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)

        def _fly_in_buttons(button, *args):
            button_anim = Animation(transition='out_expo', duration=1, opacity=1)
            button_anim &= Animation(transition='out_circ', duration=1, x=button.final_pos[0], y=button.final_pos[1])
            button_anim.start(button)

        for ix, rev_button in enumerate(reversed(self.rev_select.children), start=1):
            # Record the final intended position for each button.
            if rev_button.x < self.width:
                rev_button.final_pos = (rev_button.x, rev_button.y)
                rev_button.x = self.width
                #rev_button.y = 0

            Clock.schedule_once(partial(_fly_in_buttons, rev_button), ix*ANIM_STAGGER)

    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0

        for rev_button in self.rev_select.children:
            Animation.cancel_all(rev_button)
            rev_button.x = self.width
            #rev_button.y = 0
            rev_button.opacity = 0

    def on_iso(self, instance, value):
        self.item_desc.text = ''
        while len(self.rev_select.children) > 0:
            for widget in self.rev_select.children:
                if isinstance(widget, WizardRevToggleButton):
                    self.rev_select.remove_widget(widget)

        node = self.manager.get_screen('node_select').node['nodeid']
        data_manager = App.get_running_app().data_manager
        market_models_available = data_manager.get_valuation_revstreams(value, node)

        self.has_selection = False

        for name, attributes in market_models_available.items():
            rev_button = WizardRevToggleButton(text=name, name=attributes['market type'],
                                               desc=attributes['desc'], opacity=0)
            self.rev_select.add_widget(rev_button)

    def on_market_formulation(self, instance, value):
        logging.info('ValuationWizard: Market formulation changed to {0}.'.format(value))

        self.has_selection = True if \
            any([button.state == 'down' for button in self.rev_select.children]) \
            else False

    def on_has_selection(self, instance, value):
        # Enables the next button if at least one revenue stream is selected.
        self.next_button.disabled = not value

    def _next_screen(self):
        """Adds the device selection screen if it does not exist and changes screens to it."""
        if not self.manager.has_screen('data_select'):
            screen = ValuationWizardDataSelect(name='data_select')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'data_select'


class WizardDataTileButton(ToggleTileButton):
    """Tile button with toggle behavior for selecting which batch of historical data to run."""
    data_screen = None

    def __init__(self, name, historical_data, **kwargs):
        super(WizardDataTileButton, self).__init__(**kwargs)

        self._name = name
        self._historical_data = historical_data

    @property
    def name(self):
        """The name of the historical data set."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def historical_data(self):
        """List of dictionaries with keys 'month' and 'year' corresponding to historical data."""
        return self._historical_data

    @historical_data.setter
    def historical_data(self, value):
        self._historical_data = value

    def on_press(self):
        if self.state == 'down':
            self.selection_animation.start(self)
            self.data_screen.selected_data_set = self

            self.data_screen.data_desc.text = '\n'.join([calendar.month_name[int(opt['month'])]
                                                         + ' ' + opt['year'] for opt in self.historical_data])


class ValuationWizardDataSelect(Screen):
    iso = StringProperty('')
    has_selection = BooleanProperty(False)
    selected_data_set = ObjectProperty()
    selected_data = ListProperty()

    def __init__(self, **kwargs):
        super(ValuationWizardDataSelect, self).__init__(**kwargs)

        WizardDataTileButton.data_screen = self

    def on_pre_enter(self):
        self.iso = self.manager.get_screen('iso_select').iso

    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)

        self.data_desc.text = ''
        while len(self.data_select.children) > 0:
            for widget in self.data_select.children:
                if isinstance(widget, WizardDataTileButton):
                    self.data_select.remove_widget(widget)

        self.has_selection = False

        node = self.manager.get_screen('node_select').node['nodeid']
        market_formulation = self.manager.get_screen('rev_stream_select').market_formulation
        data_manager = App.get_running_app().data_manager
        HISTORICAL_DATA = data_manager.get_historical_datasets(self.iso, node, market_formulation)
        
        try:
            for (name, data_set) in HISTORICAL_DATA.items():
                button = WizardDataTileButton(name=name, text=name, historical_data=data_set)
                self.data_select.add_widget(button)
        except AttributeError:
            pass



    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0

    def on_iso(self, instance, value):
        self.data_desc.text = ''
        # while len(self.data_select.children) > 0:
        #     for widget in self.data_select.children:
        #         if isinstance(widget, WizardDataTileButton):
        #             self.data_select.remove_widget(widget)

        self.has_selection = False

        # try:
        #     for (name, data_set) in HISTORICAL_DATA[value].items():
        #         button = WizardDataTileButton(name=name, text=name, historical_data=data_set)
        #         self.data_select.add_widget(button)
        # except AttributeError:
        #     pass

        # node = self.manager.get_screen('node_select').node['nodeid']
        # market_formulation = self.manager.get_screen('rev_stream_select').market_formulation
        # data_manager = App.get_running_app().data_manager
        # HISTORICAL_DATA = data_manager.get_historical_datasets(value, node, market_formulation)
        
        # try:
        #     for (name, data_set) in HISTORICAL_DATA.items():
        #         button = WizardDataTileButton(name=name, text=name, historical_data=data_set)
        #         self.data_select.add_widget(button)
        # except AttributeError:
        #     pass

    def on_selected_data_set(self, instance, value):
        logging.info('ValuationWizard: Changed historical data set to {0}.'.format(value.name))

        self.selected_data = value.historical_data

        self.has_selection = True if \
            any([button.state == 'down' for button in self.data_select.children]) \
            else False

    def on_has_selection(self, instance, value):
        # Enables the next button if a data set is selected.
        self.next_button.disabled = not value

    def _next_screen(self):
        """Adds the pricing node selection screen if it does not exist and changes screens to it."""
        if not self.manager.has_screen('device_select'):
            screen = ValuationWizardDeviceSelect(name='device_select')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'device_select'


class WizardDeviceTileButton(ToggleTileButton):
    """Tile button with toggle behavior for each energy storage device option."""
    device_desc_box = None
    param_widget = None
    device_screen = None

    def __init__(self, desc, name, parameters, **kwargs):
        super(WizardDeviceTileButton, self).__init__(**kwargs)

        self._name = name
        self._desc = desc
        self._parameters = parameters

    @property
    def name(self):
        """The name of the energy storage device."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def desc(self):
        """A description of the energy storage device."""
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value

    @property
    def parameters(self):
        """Dictionary of the parameter names and values."""
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    def on_press(self):
        if self.state == 'down':
            self.selection_animation.start(self)

            self.device_desc_box.text = '\n'.join(['[b]{0}[/b]'.format(self.name), self.desc])
            self.param_widget.adjust_sliders(self)
            self.device_screen.device = self.name


class WizardDeviceParameterRow(GridLayout):
    """Grid layout containing parameter descriptor label, slider, and value label."""
    desc = DictProperty()

    def __init__(self, **kwargs):
        super(WizardDeviceParameterRow, self).__init__(**kwargs)

        self.name.text = self.desc['name']

        self.param_min = self.desc.get('min', 0)
        self.param_max = self.desc.get('max', 100)
        self.param_slider.min = self.param_min
        self.param_slider.max = self.param_max

        self.param_slider.value = self.desc.get('default', 50)
        self.param_slider.step = self.desc.get('step', 1)

    def _validate_input(self):
        """Validate entry when unfocusing text input."""
        if not self.text_input.focus:
            try:
                input_value = float(self.text_input.text)
            except ValueError:
                # No text entered.
                input_value = self.param_slider.value
                self.text_input.text = str(input_value)

                return

            if input_value > self.param_max or input_value < self.param_min:
                # If input value is out of range.
                popup = WarningPopup()
                popup.popup_text.text = '{param_name} must be between {param_min} and {param_max} (got {input_val}).'.format(param_name=self.name.text[:1].upper() + self.name.text[1:], param_min=self.param_min, param_max=self.param_max, input_val=input_value)
                popup.open()

                input_value = self.param_slider.value
                self.text_input.text = str(input_value)
            else:
                # Set slider value to input value.
                anim = Animation(transition='out_expo', duration=SLIDER_DUR, value=input_value)
                anim.start(self.param_slider)


class WizardDeviceParameterWidget(GridLayout):
    """Grid layout containing rows of parameter adjustment widgets."""
    def __init__(self, **kwargs):
        super(WizardDeviceParameterWidget, self).__init__(**kwargs)

        # build the widget by creating a row for each dictionary in param_list
        data_manager = App.get_running_app().data_manager
        PARAM_LIST = data_manager.get_valuation_wizard_device_params()

        for param in PARAM_LIST:
            row = WizardDeviceParameterRow(desc=param)
            self.add_widget(row)
            setattr(self, param['attr name'], row)

    def adjust_sliders(self, device):
        """Adjusts the parameter slider values based on the device selected."""
        for (param, val) in device.parameters.items():
            anim = Animation(transition='out_sine', duration=SLIDER_DUR, value=val)
            anim.start(getattr(self, param).param_slider)


class ParamTextInput(TextInput):
    """A TextInput field for entering parameter values."""

    def insert_text(self, substring, from_undo=False):
        # limit # chars
        substring = substring[:4 - len(self.text)]
        return super(ParamTextInput, self).insert_text(substring, from_undo=from_undo)


class ValuationWizardDeviceSelect(Screen):
    device = StringProperty('')
    has_selection = BooleanProperty(False)

    """The screen for describing the energy storage device for the valuation wizard."""
    def __init__(self, **kwargs):
        super(ValuationWizardDeviceSelect, self).__init__(**kwargs)

        WizardDeviceTileButton.device_screen = self
        WizardDeviceTileButton.device_desc_box = self.device_desc
        WizardDeviceTileButton.param_widget = self.param_widget

    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)

        def _fade_in_buttons(button, *args):
            button_anim = Animation(transition='out_expo', duration=FADEIN_DUR, opacity=1)
            button_anim.start(button)
        
        data_manager = App.get_running_app().data_manager
        DEVICE_LIST = data_manager.get_valuation_device_templates()

        if not self.device_select.children:
            for ix, dev in enumerate(DEVICE_LIST):
                device_button = WizardDeviceTileButton(text=dev['name'], name=dev['name'],
                                                       desc=dev['desc'],
                                                       parameters=dev['parameters'], opacity=0)
                self.device_select.add_widget(device_button)

        for ix, dev in enumerate(reversed(self.device_select.children)):
            Clock.schedule_once(partial(_fade_in_buttons, dev), ix*ANIM_STAGGER)

    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0

        for button in self.device_select.children:
            Animation.cancel_all(button)
            button.opacity = 0

    def on_device(self, instance, value):
        logging.info('ValuationWizard: Energy storage device changed to {0}.'.format(value))

        self.has_selection = True if \
            any([button.state == 'down' for button in self.device_select.children]) \
            else False

    def on_has_selection(self, instance, value):
        # Enables the next button if a device is selected.
        self.next_button.disabled = not value

        # Enable parameter sliders and text inputs.
        for param_row in self.param_widget.children:
            param_row.text_input.disabled = False
            param_row.param_slider.disabled = False

    def _next_screen(self):
        """Adds the data selection screen if it does not exist and changes screens to it."""
        if not self.manager.has_screen('selection_summary'):
            screen = ValuationWizardSelectionSummary(name='selection_summary')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'selection_summary'


class WizardSummaryBubble(BoxLayout):
    pass


class ImageButton(ButtonBehavior, Image):
    pass


class WizardHeaderDesc():
    pass

# TODO: Check naming/style conventions: lower case and underscore delimited for class methods, camelcase for class names, etc.
# TODO: Use class rules for common widgets in kv. Example: The labels in the summary screen are all stylistically similar, so they should have a common class rule. (DRY: Don't Repeat Yourself)
# TODO: The WizardBodyText class (defined at top of kv file) is used for body text elements (as opposed to title elements) throughout the wizard. It inherits from the BodyTextBase (defined in look_and_feel.kv) which is the base class for body text throughout the application. This inheritance structure is useful to make sure the look and feel is consistent throughout. For example, if I wanted to change the default font of body text everywhere in the application, I would just change it in the BodyTextBase and it would propagate through the inheritance hierarchy.


class AboutSelectionSummary(ModalView):
    ISOselname = ''
    def __init__(self, **kwargs):
        super(AboutSelectionSummary, self).__init__(**kwargs)

    def openwebbrowser(self):
        if self.ISOselname  == "NYISO":
            webbrowser.open('http://www.nyiso.com/')
        elif self.ISOselname  == "ISONE":
            webbrowser.open('https://www.iso-ne.com/')
        elif self.ISOselname == "PJM":
            webbrowser.open('http://www.pjm.com/')
        elif self.ISOselname == "ERCOT":
            webbrowser.open('http://www.ercot.com/')
        elif self.ISOselname == "MISO":
            webbrowser.open('https://www.misoenergy.org/')
        elif self.ISOselname == "SPP":
            webbrowser.open('https://www.spp.org/')
        elif self.ISOselname == "CAISO":
            webbrowser.open('http://www.caiso.com/')
        else:
            webbrowser.open('http://www.sandia.gov/')

    def setisoinfo(self):
        # TODO: Make better descriptions, these are temporary taken from Wikipedia
        # print('Setting image')
        self.title_abt_selsum.text = '[ref=iso_title]{iso}[/ref]'.format(iso=self.ISOselname)

        if self.ISOselname == "NYISO":
            # self.img_abt_selsum.source = os.path.join('es_gui', 'resources', 'images', 'xNYISOlogo.jpg')
            self.lab_abt_selsum.text = "The New York Independent System Operator (NYISO) operates competitive wholesale markets to manage the flow of electricity across New York."
        elif self.ISOselname == "ISONE":
            # self.img_abt_selsum.source = os.path.join('es_gui', 'resources', 'images', 'xISO-NElogo.jpg')
            self.lab_abt_selsum.text = "ISO New England Inc. (ISO-NE) is an independent, non-profit Regional Transmission Organization (RTO), headquartered in Holyoke, Massachusetts, serving Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, and Vermont. ISO-NE oversees the operation of New England's bulk electric power system and transmission lines, generated and transmitted by its member utilities, as well as Hydro-Quebec, NB Power, the New York Power Authority and utilities in New York state, when the need arises. ISO-NE is responsible for reliably operating New England's bulk electric power generation and transmission system."
        elif self.ISOselname == "PJM":
            # self.img_abt_selsum.source = os.path.join('es_gui', 'resources', 'images', 'xPJMlogo.png')
            self.lab_abt_selsum.text = "PJM Interconnection LLC (PJM) is a regional transmission organization (RTO) in the United States. It is part of the Eastern Interconnection grid operating an electric transmission system serving all or parts of Delaware, Illinois, Indiana, Kentucky, Maryland, Michigan, New Jersey, North Carolina, Ohio, Pennsylvania, Tennessee, Virginia, West Virginia, and the District of Columbia."
        elif self.ISOselname == "ERCOT":
            # self.img_abt_selsum.source = os.path.join('es_gui', 'resources', 'images', 'xERCOTlogo.png')
            self.lab_abt_selsum.text = "The Electric Reliability Council of Texas (ERCOT) manages the flow of electric power on the Texas Interconnection that supplies power to 24 million Texas customers - representing 85 percent of the state's electric load."
        elif self.ISOselname == "MISO":
            # self.img_abt_selsum.source = os.path.join('es_gui', 'resources', 'images', 'xMISOlogo.png')
            self.lab_abt_selsum.text = 'The Midcontinent Independent System Operator, Inc., formerly named Midwest Independent Transmission System Operator, Inc. (MISO) is an Independent System Operator (ISO) and Regional Transmission Organization (RTO) providing open-access transmission service and monitoring the high-voltage transmission system in the Midwest United States and Manitoba, Canada and a southern United States region which includes much of Arkansas, Mississippi, and Louisiana.'
        elif self.ISOselname == "SPP":
            # self.img_abt_selsum.source = os.path.join('es_gui', 'resources', 'images', 'xMISOlogo.png')
            self.lab_abt_selsum.text = 'SPP description TBW.'
        elif self.ISOselname == "CAISO":
            # self.img_abt_selsum.source = os.path.join('es_gui', 'resources', 'images', 'xMISOlogo.png')
            self.lab_abt_selsum.text = 'CAISO description TBW.'

        else:
            # self.img_abt_selsum.source = os.path.join('es_gui', 'resources', 'images', 'SNLlogo.png')
            pass


class ValuationWizardSelectionSummary(Screen):
    """The selection summary screen for the valuation wizard."""
    iso = StringProperty('')
    has_selections = BooleanProperty(False)
    wiz_selections = DictProperty()

    # def on_iso(self, instance, value):
    #     self.node_desc.text = ''
    #
    #     # build options based on ISO selected
    #     try:
    #         ls = self.manager.parent.parent.manager.get_screen('load_data')
    #
    #         node_options = [{'name': ls.dms.get_node_name(x, self.iso),
    #                          'nodeid': x} for x in ls.nodeid[self.iso]]
    #         self.node_rv.data = node_options
    #     except AttributeError:
    #         pass

    def on_enter(self):
        Clock.schedule_once(partial(fade_in_animation, self.content), 0)

        # clear widgets
        # while len(self.content.children) > 0:
        #     for widget in self.content.children:
        #         if isinstance(widget, WizardSummaryBubble):
        #             self.content.remove_widget(widget)

        # extract selections from each screen
        summary_bubble = WizardSummaryBubble(size_hint=(1, 1))

        selections = {}
        selections['iso'] = self.manager.get_screen('rev_stream_select').iso
        selections['node'] = self.manager.get_screen('node_select').node['name']
        selections['nodeid'] = self.manager.get_screen('node_select').node['nodeid']
        selections['rev_streams'] = self.manager.get_screen('rev_stream_select').market_formulation
        selections['selected_data'] = self.manager.get_screen('data_select').selected_data
        selections['device'] = [x for x in self.manager.get_screen('device_select').param_widget.children]

        self.wiz_selections = selections  # assign to DictProperty of screen

        # convert to displayable text
        iso = self.wiz_selections['iso']
        node = self.wiz_selections['node']
        nodeid = self.wiz_selections['nodeid']
        rev_streams = self.wiz_selections['rev_streams']
        #hist_data = ', '.join([opt['name'] for opt in self.wiz_selections['selected_data']])
        device = '   \n'.join([
                     '   {0}: {1}'.format(x.name.text, str(x.param_slider.value))
                     for x in self.wiz_selections['device']
                 ])

        # summary_bubble.body.text += '\n\n'.join(
        #     [iso,
        #      node,
        #      rev_streams,
        #      hist_data,
        #      device,
        #      ]
        # )

        buttons_dev_sel = self.manager.get_screen('device_select').device_select.children
        but_press_dev_sel = [x.text for x in buttons_dev_sel if x.state == "down"]

        if not but_press_dev_sel:
            # print("empty list")
            but_press_dev_sel = "-"
        else:
            but_press_dev_sel = but_press_dev_sel[0]# print("NOT empty list")

        #print(but_press_dev_sel[0])

        isotextSW = '[u][ref={ref_in}]{textisosel} [/ref][/u]'.format(ref_in=iso, textisosel=iso)
        month_ini = calendar.month_name[int(self.wiz_selections['selected_data'][0]['month'])]
        year_ini = self.wiz_selections['selected_data'][0]['year']
        month_end = calendar.month_name[int(self.wiz_selections['selected_data'][-1]['month'])]
        year_end = self.wiz_selections['selected_data'][-1]['year']

        self.isolabel.text = '[b]Market Area:[/b] ' + isotextSW
        self.isolabel.markup = True
        self.isolabel.bind(on_ref_press=self.OpenAbSelSum)

        self.pcnodelabel.text = "[b]Pricing Node:[/b] " + node + " (id: " + str(nodeid) + ")"
        self.pcnodelabel.markup = True

        histdattext = '{m_i} {y_i} to {m_e} {y_e}'.format(m_i=month_ini, y_i=year_ini, m_e=month_end, y_e=year_end)
        self.histdatlabel.text = "[b]Dates Analyzed: [/b]" + histdattext
        self.histdatlabel.markup = True

        self.revstreamlabel.text = "[b]Revenue Streams: [/b]" + rev_streams
        self.revstreamlabel.markup = True

        self.esdevlabel.text = "[b]ES Device: [/b]" + but_press_dev_sel + '\n' + device
        self.esdevlabel.markup = True

        # print(rev_streams)
        # print(hist_data)
        # self.content.add_widget(summary_bubble)
        #
        #
        # # build bubbles for each selection made
        # iso_bubble = WizardSummaryBubble()
        # iso_bubble.cat_title.text = 'ISO'
        # iso_bubble.body.text = self.manager.get_screen('rev_stream_select').iso
        # self.content.add_widget(iso_bubble)
        #
        # rev_bubble = WizardSummaryBubble()
        # rev_bubble.cat_title.text = 'Revenue streams'
        # rev_selected = [opt.name for opt in self.manager.get_screen('rev_stream_select').rev_select.children
        #                 if opt.state == 'down']
        # rev_bubble.body.text = '\n'.join(rev_selected)
        # self.content.add_widget(rev_bubble)
        #
        # data_bubble = WizardSummaryBubble()
        # data_bubble.cat_title.text = 'Data'
        # selected_data = [x.selected_data for x in self.manager.get_screen('data_select').data_select.children
        #                  if x.state == 'down'][0]
        # data_bubble.body.text = '\n'.join([opt['name'] for opt in selected_data])
        # self.content.add_widget(data_bubble)
        #
        # node_bubble = WizardSummaryBubble()
        # node_bubble.cat_title.text = 'Node'
        # node_bubble.body.text = [x['name'] for x in self.manager.get_screen('node_select').node_rv.data
        #                          if x.get('selected', False)][0]
        # self.content.add_widget(node_bubble)
        #
        # device_bubble = WizardSummaryBubble()
        # device_bubble.cat_title.text = 'Device description'
        # device_bubble.body.text = '\n'.join([
        #     '{0}: {1}'.format(x.name.text, str(x.param_slider.value))
        #     for x in self.manager.get_screen('device_select').param_widget.children
        # ])
        # self.content.add_widget(device_bubble)

    def OpenAbSelSum(self,*args):
        # print(args[1])

        isoAboutSelectionSummary = AboutSelectionSummary()
        isoAboutSelectionSummary.ISOselname = args[1]
        isoAboutSelectionSummary.setisoinfo()
        isoAboutSelectionSummary.open()


    def on_leave(self):
        Animation.stop_all(self.content, 'opacity')
        self.content.opacity = 0

    def _next_screen(self):
        """Adds the execute screen if it does not exist and changes screens to it."""
        if not self.manager.has_screen('execute'):
            screen = ValuationWizardExecute(name='execute')
            self.manager.add_widget(screen)

        self.manager.transition.duration = BASE_TRANSITION_DUR
        self.manager.transition.direction = 'left'
        self.manager.current = 'execute'


class ValuationWizardExecute(Screen):
    """The screen for executing the prescribed optimizations for the valuation wizard."""
    solved_ops = []
    report_attributes = {}

    def on_enter(self):
        self.execute_run()

    def on_leave(self):
        self.progress_label.text = 'This may take a while. Please wait patiently!'

    def execute_run(self):
        valuation_home = self.manager.parent.parent.manager.get_screen('valuation_home')
        ss = self.manager.get_screen('selection_summary')

        # Parse selection summary for arguments to pass to ValOp handler.
        wiz_selections = ss.wiz_selections
        iso = wiz_selections['iso']
        node = wiz_selections['node']
        nodeid = wiz_selections['nodeid']

        data_manager = App.get_running_app().data_manager
        rev_streams = data_manager.get_valuation_revstreams(iso, nodeid)[wiz_selections['rev_streams']]['market type']

        hist_data = wiz_selections['selected_data']
        device = wiz_selections['device']

        handler_requests = {}
        handler_requests['iso'] = iso
        handler_requests['market type'] = rev_streams  # need this as string, not list
        handler_requests['months'] = [(entry['month'], entry['year']) for entry in hist_data]
        handler_requests['node id'] = nodeid
        handler_requests['param set'] = [{param.desc['attr name']: param.param_slider.value
                                         for param in device}]

        # Send requests to ValOp handler.
        valop_handler = valuation_home.handler
        valop_handler.solver_name = App.get_running_app().config.get('optimization', 'solver')
        self.solved_ops, handler_status = valop_handler.process_requests(handler_requests)

        popup = WizardCompletePopup()

        # Check ValOp handler status.
        if len(handler_status) > 0:
            if self.solved_ops:
                # At least one model solved successfully.
                popup.title = "Success!*"
                popup.popup_text.text = '\n'.join([
                    'All finished, but we found these issues:',
                ]
                + list(handler_status)
                )
            else:
                # No models solved successfully.
                popup.title = "Hmm..."
                popup.popup_text.text = '\n'.join([
                    'Unfortunately, none of the models were able to be solved. We found these issues:',
                ]
                + list(handler_status)
                )

                popup.results_button.text = "Take me back"
                popup.bind(on_dismiss=lambda x: self.manager.parent.parent.manager.nav_bar.go_up_screen())  # Go back to Valuation Home
                popup.open()
                return

        popup.bind(on_dismiss=self._next_screen)
        popup.open()

        # Save selection summary details to pass to report generator.
        deviceSelectionButtons = self.manager.get_screen('device_select').device_select.children
        selectedDeviceName = [x.text for x in deviceSelectionButtons if x.state == "down"][0]

        self.report_attributes = {'market area': iso,
                                  'pricing node': node,
                                  'selected device': selectedDeviceName,
                                  'dates analyzed': ' to '.join([
                                      ' '.join([calendar.month_name[int(hist_data[0]['month'])], hist_data[0]['year']]),
                                      ' '.join([calendar.month_name[int(hist_data[-1]['month'])], hist_data[-1]['year']]),
                                      ]),
                                  'revenue streams': wiz_selections['rev_streams'],
                                  'market type': rev_streams,
                                 }

        for param in device:
            self.report_attributes[param.desc['attr name']] = param.param_slider.value

    def _next_screen(self, *args):
        """Adds the report screen if it does not exist and changes screens to it."""
        report = ValuationReport(name='report', chart_data=self.solved_ops, market=self.report_attributes['market type'], report_attributes=self.report_attributes)
        self.manager.switch_to(report, direction='left', duration=BASE_TRANSITION_DUR)

