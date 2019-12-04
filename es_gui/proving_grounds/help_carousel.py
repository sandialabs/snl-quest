"""This module is for the HelpCarousel widget.

A HelpCarousel is a modal view. It contains a carousel which hosts a series of slides with accompanying text. The primary purpose of this widget is to provide additional help illustrated with screenshots or other relevant figures without overloading the main user interface with information. The modal view includes previous and next buttons to navigate the slides in addition to a group of radio buttons to indicate progress in the carousel's slide deck. The view does not have a dismiss button but auto_dismiss is enabled; the view can be dismissed by clicking outside of it.

The HelpCarouselModalView is designed to be instantiated then populated using the `add_slides()` class method. This method populates the carousel's slides with pairs of image sources and text.
"""

import logging
import os

import pandas as pd

from kivy.uix.checkbox import CheckBox
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty


class HelpCarouselSlide(BoxLayout):
    """A slide for the HelpCarousel consisting of a large image (80%) and text (20%) in horizontal orientation.
    """
    pass


class HelpCarouselModalView(ModalView):
    """A ModalView with a series of prompts for importing time series data from a csv file.
    """
    current_slide_index = NumericProperty()

    def add_slides(self, slide_deck):
        """Adds image and text to a new slide in the carousel slide deck.

        Each slide consists of a large image on the left and accompanying text on the right.

        Parameters
        ----------
        slide_deck : list(tuple)
            Content for each slide (source, caption) where the source is the path to the slide image and the caption is the text
        
        Notes
        -----
        The source is relative to the current working directory (alongside main.py).
        """
        self.slide_progress_radio_buttons = []

        for source, caption in slide_deck:
            slide = HelpCarouselSlide()
            slide.img.source = source
            slide.img_caption.text = caption

            self.carousel.add_widget(slide)
            self.slide_progress_radio_buttons.append(SlideProgressRadioButton())
            
        for ix, button in enumerate(self.slide_progress_radio_buttons):
            button.active = ix == 0
            self.slide_progress_bx.add_widget(button)
    
    def change_slide(self, direction):
        """Changes carousel slide in the specified direction.
        """
        getattr(self.carousel, 'load_{0}'.format(direction))()

        if direction == 'previous':
            destination_slide = self.carousel.previous_slide
        else:
            destination_slide = self.carousel.next_slide
        
        if destination_slide is not None:
            self.current_slide_index = self.carousel.slides.index(destination_slide)
    
    def on_current_slide_index(self, instance, value):
        # Changes the active button in the slide progress group to reflect the new slide.
        self.slide_progress_radio_buttons[value].active = True


class SlideProgressRadioButton(CheckBox):
    """Radio button representing progress within the HelpCarousel slide deck.
    """
    pass