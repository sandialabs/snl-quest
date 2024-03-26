# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 13:01:05 2023

@author: ylpomer
"""

from PySide6.QtWidgets import (
    QWidget,
)

from app.about_pages.ui.ui_about_stack import Ui_help_land


class about_land(QWidget, Ui_help_land):
    """A page that displays information about quest"""
    def __init__(self):
        """sets up the ui file to show in the application"""
        super().__init__()
#           Set up the ui        

        self.setupUi(self)
#       connecting the what is quest page
        self.what_push.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.what_is_quest))
        self.what_back.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.quest_help_home))
    
#       connecting the install questions page
        self.inst_push.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.install_apps_page))
        self.inst_back.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.quest_help_home))

#       connecting the docs page
        self.doc_push.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.docs_page))
        self.docs_back.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.quest_help_home))
        
#       connecting the acknowledgements page
        self.ack_push.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.acknowledge_page))
        self.ack_back.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.quest_help_home))
        
#       connecting the getting help page
        self.get_push.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.getting_help))
        self.help_back.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.quest_help_home))
        
        
#       connecting the who uses quest page
        self.who_push.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.users_page))
        self.use_back.clicked.connect(lambda: self.help_widge.setCurrentWidget(self.quest_help_home))
        
        self.doc_push.setEnabled(False)