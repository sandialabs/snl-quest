from __future__ import absolute_import

import os

from kivy.uix.screenmanager import Screen

from es_gui.resources.widgets.common import NavigationButton
from es_gui.proving_grounds.help_carousel import HelpCarouselModalView


class TechSelectionHomeScreen(Screen):
    """The home screen for performing energy storage technology selection analysis."""

    def __init__(self, **kwargs):
        super(TechSelectionHomeScreen, self).__init__(**kwargs)

    def on_enter(self):
        ab = self.manager.nav_bar
        ab.reset_nav_bar()
        ab.set_title('Energy Storage Technology Selection Application')

        help_button = NavigationButton(text='help', on_release=self.open_help_carousel)
        ab.action_view.add_widget(help_button)

    def open_help_carousel(self, *args):
        help_carousel_view = HelpCarouselModalView()
        help_carousel_view.title.text = 'QuESt Technology Selection'

        slide_01_text = ('QuESt Technology Selection is an application with tools for identifying feasible storage '
                         'technlogies for a given project.')
        slide_02_text = ('The technology selection wizard identifies which energy storage technologies satisfy the minimum '
                         'application requirements (such as discharge duration and response time) and rank them. The user '
                         'is required to indicate the grid location where the storage system will be deployed, which set '
                         'default values for the other types of inputs.')
        slide_03_text = ('Upon completion of the wizard, you will be taken to the first results screen, which indicates '
                         'whether each energy storage technology is a feasible option for the desired project.')
        slide_04_text = ('The next results screen displays a rank of the feasible technologies based on four factors. The '
                         'user can modify the weights assigned to each one of these factors, as well as the desired target '
                         'cost (the latter affects the Cost Score). These adjustments will be reflected in the new Total '
                         'Score for each technology.')
        slide_05_text = 'Finally, the user can export any of the previous results to .png or .csv files.'

        slides = [
            (os.path.join('es_gui', 'resources', 'help_views', 'tech_selection', '01.png'), slide_01_text),
            (os.path.join('es_gui', 'resources', 'help_views', 'tech_selection', '03.png'), slide_02_text),
            (os.path.join('es_gui', 'resources', 'help_views', 'tech_selection', '05.png'), slide_03_text),
            (os.path.join('es_gui', 'resources', 'help_views', 'tech_selection', '06.png'), slide_04_text),
            (os.path.join('es_gui', 'resources', 'help_views', 'tech_selection', '07.png'), slide_05_text),
        ]

        help_carousel_view.add_slides(slides)
        help_carousel_view.open()