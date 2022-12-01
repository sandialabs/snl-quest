# QuESt
# version: 1.2
# 
# by
# Sandia National Laboratories
# 
# Copyright 2018 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

# NOTICE:
#
# For five (5) years from 8/16/2018 the United States Government is granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable worldwide license in this data to reproduce, prepare derivative works, and perform publicly and display publicly, by or on behalf of the Government. There is provision for the possible extension of the term of this license. Subsequent to that period or any extension granted, the United States Government is granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable worldwide license in this data to reproduce, prepare derivative works, distribute copies to the public, perform publicly and display publicly, and to permit others to do so. The specific term of the license can be identified by inquiry made to National Technology and Engineering Solutions of Sandia, LLC or DOE.
#
# NEITHER THE UNITED STATES GOVERNMENT, NOR THE UNITED STATES DEPARTMENT OF ENERGY, NOR NATIONAL TECHNOLOGY AND ENGINEERING SOLUTIONS OF SANDIA, LLC, NOR ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LEGAL RESPONSIBILITY FOR THE ACCURACY, COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE PRIVATELY OWNED RIGHTS.
# 
# Any licensee of this software has the obligation and responsibility to abide by the applicable export control laws, regulations, and general prohibitions relating to the export of technical data. Failure to obtain an export control license or other authority from the Government may result in criminal liability under U.S. laws.


from __future__ import absolute_import

# This is for setting the window parameters like the initial size. Goes before any other import statements.
from kivy.config import Config, ConfigParser

Config.set('graphics', 'height', '900')
Config.set('graphics', 'width', '1600')
Config.set('graphics', 'minimum_height', '900')
Config.set('graphics', 'minimum_width', '1600')
#Config.set('graphics', 'borderless', '1')
Config.set('graphics', 'resizable', '1')
#Config.set('graphics', 'fullscreen', 'auto')
Config.set('kivy', 'desktop', 1)
Config.set('kivy', 'exit_on_escape', '0')  # disables Esc to quit
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disables red dot creation

from functools import partial
import os
import webbrowser
import threading

from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition, SwapTransition
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.actionbar import ActionBar, ActionGroup
from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase

from es_gui.apps.data_manager.data_manager import DataManager
from es_gui.resources.widgets.common import MyPopup, WarningPopup, APP_NAME, APP_TAGLINE, NavigationButton
from es_gui.proving_grounds.help_carousel import HelpCarouselModalView

dirname = os.path.dirname(__file__)

# Import common widgets from look_and_feel
Builder.load_file(os.path.join(dirname, 'es_gui', 'resources', 'widgets', 'common.kv'))

from es_gui.settings import ESAppSettings

# Data Manager
from es_gui.apps.data_manager.home import DataManagerHomeScreen
from es_gui.apps.data_manager.widgets import DataManagerRTOMOdataScreen
from es_gui.apps.data_manager.rate_structure import RateStructureDataScreen
from es_gui.apps.data_manager.load import DataManagerLoadHomeScreen, DataManagerCommercialLoadScreen, DataManagerResidentialLoadScreen
from es_gui.apps.data_manager.pv import PVwattsSearchScreen
from es_gui.apps.data_manager.nsrdb import NSRDBDataScreen

# Valuation
from es_gui.apps.valuation.home import ValuationHomeScreen
from es_gui.apps.valuation.batchrunscreen import BatchRunScreen
from es_gui.apps.valuation.results_viewer import ValuationResultsViewer
from es_gui.apps.valuation.wizard import ValuationWizard

# Behind-the-meter
from es_gui.apps.btm.home import BehindTheMeterHomeScreen
from es_gui.apps.btm.cost_savings import CostSavingsWizard
from es_gui.apps.btm.results_viewer import BtmResultsViewer

from es_gui.apps.performance.home import PerformanceHomeScreen
from es_gui.apps.performance.performance_sim import PerformanceSimRunScreen
from es_gui.apps.performance.results_viewer import PerformanceResultsViewer

# Technology selection
from es_gui.apps.tech_selection.home import TechSelectionHomeScreen
from es_gui.apps.tech_selection.tech_selection_wizard import TechSelectionWizard
from es_gui.apps.tech_selection.results_viewer import TechSelectionFeasible

# Font registration.
LabelBase.register(name='Exo 2',
                   fn_regular=os.path.join('es_gui', 'resources', 'fonts', 'Exo_2', 'Exo2-Regular.ttf'),
                   fn_bold=os.path.join('es_gui', 'resources', 'fonts', 'Exo_2', 'Exo2-Bold.ttf'),
                   fn_italic=os.path.join('es_gui', 'resources', 'fonts', 'Exo_2', 'Exo2-Italic.ttf'))

LabelBase.register(name='Open Sans',
                   fn_regular=os.path.join('es_gui', 'resources', 'fonts', 'Open_Sans', 'OpenSans-Regular.ttf'),
                   fn_bold=os.path.join('es_gui', 'resources', 'fonts', 'Open_Sans', 'OpenSans-Bold.ttf'),
                   fn_italic=os.path.join('es_gui', 'resources', 'fonts', 'Open_Sans', 'OpenSans-Italic.ttf'))

LabelBase.register(name='Modern Pictograms',
                   fn_regular=os.path.join('es_gui', 'resources', 'fonts', 'modernpictograms', 'ModernPictograms.ttf'))


class IndexScreen(Screen):
    """The landing screen."""
    def on_leave(self):
        """Sets NavigationBar.reset_nav_bar() to fire on_enter for the index screen after the first time loading it."""
        self.bind(on_enter=self.manager.nav_bar.reset_nav_bar)
    
    def open_intro_help_carousel(self):
        """
        """
        help_carousel_view = HelpCarouselModalView()
        help_carousel_view.title.text = "Welcome to QuESt"

        slide_01_text = "QuESt is an application suite for energy storage valuation.\n\nThe list on the left contains the currently available applications. Click on an application to learn a little more about it. Once you have selected an application, click on the 'Get started' button underneath its description to open it."

        slide_02_text = "At the top of the QuESt window is the action bar. The QuESt logo on the left end of the action bar serves as a back button; click on it to return to the previous screen. On the right end of the action bar is the navigation toolbar. The buttons here change depending on the context but several, like those pictured, persist.\n\nYou can use the 'home' button to return to this index screen at any time."

        slide_03_text = "In QuESt, input data management is separate from the analysis tools. Use the QuESt Data Manager to acquire data before proceeding to other QuESt applications and using their analysis tools."

        slide_04_text = "In some QuESt applications, it is possible to import and use your own data. Look out for prompts such as these to open the data importer interface. Please refer to each individual application and tool for specific details!"

        slide_05_text = "Looking for more help? Check the navigation bar while in each QuESt application for a 'help' button to open an information carousel like this one for application-specific help."

        slides = [
            (os.path.join("es_gui", "resources", "help_views", "index", "01.png"), slide_01_text),
            (os.path.join("es_gui", "resources", "help_views", "index", "02.png"), slide_02_text),
            (os.path.join("es_gui", "resources", "help_views", "index", "03.png"), slide_03_text),
            (os.path.join("es_gui", "resources", "help_views", "index", "04.png"), slide_04_text),
            (os.path.join("es_gui", "resources", "help_views", "index", "05.png"), slide_05_text),
        ]

        help_carousel_view.add_slides(slides)
        help_carousel_view.open()


class AboutScreen(ModalView):
    """The about/contact screen."""
    def __init__(self, **kwargs):
        super(AboutScreen, self).__init__(**kwargs)

        def _ref_link(text, ref):
            return '[ref={0}][color=003359][u]{1}[/u][/color][/ref]'.format(ref, text)

        def _go_to_webpage(instance, value):
            if value == 'kivy':
                webbrowser.open('http://kivy.org/')
            elif value == 'pyomo':
                webbrowser.open('http://pyomo.org/')
            elif value == 'sandia-ess':
                webbrowser.open('http://energy.sandia.gov/energy/ssrei/energy-storage/')
            elif value == 'sandia-epsr':
                webbrowser.open('http://energy.sandia.gov/energy/ssrei/gridmod/transmission-planning-and-operations/')
            elif value == 'sandia':
                webbrowser.open('http://sandia.gov/')
        
        version_statement = 'QuESt v1.2.f \n 2020.01.17'

        developed_by = '{app_name} is developed by the {ess} and {espr} departments at {sandia}.'.format(app_name=APP_NAME, ess=_ref_link('Energy Storage Technology and Systems', 'sandia-ess'), espr=_ref_link('Electric Power Systems Research', 'sandia-espr'), sandia=_ref_link('Sandia National Laboratories', 'sandia'))

        powered_by = '{app_name} is powered by Kivy and Pyomo. {kivy_ref} is an open-source Python library for rapid development of applications that make use of innovative user interfaces, such as multi-touch apps. {pyomo_ref} is a Python-based open-source software package that supports a diverse set of optimization capabilities for formulating, solving, and analyzing optimization models.'.format(app_name=APP_NAME, kivy_ref=_ref_link('Kivy', 'kivy'), pyomo_ref=_ref_link('Pyomo', 'pyomo'))

        acknowledgement = 'The developers would like to thank [b]Dr. Imre Gyuk[/b] at the Energy Storage Program at the U.S. Department of Energy for funding the development of this software.'

        ntess_statement = 'Sandia National Laboratories is a multimission laboratory managed and operated by National Technology and Engineering Solutions of Sandia, LLC, a wholly owned subsidiary of Honeywell International, Inc., for the U.S. Department of Energy\'s National Nuclear Security Administration under contract DE-NA0003525.'

        copyright_statement = 'Copyright 2018 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software. \n\n NOTICE: \n\n For five (5) years from 8/16/2018 the United States Government is granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable worldwide license in this data to reproduce, prepare derivative works, and perform publicly and display publicly, by or on behalf of the Government. There is provision for the possible extension of the term of this license. Subsequent to that period or any extension granted, the United States Government is granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable worldwide license in this data to reproduce, prepare derivative works, distribute copies to the public, perform publicly and display publicly, and to permit others to do so. The specific term of the license can be identified by inquiry made to National Technology and Engineering Solutions of Sandia, LLC or DOE. \n\n NEITHER THE UNITED STATES GOVERNMENT, NOR THE UNITED STATES DEPARTMENT OF ENERGY, NOR NATIONAL TECHNOLOGY AND ENGINEERING SOLUTIONS OF SANDIA, LLC, NOR ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LEGAL RESPONSIBILITY FOR THE ACCURACY, COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE PRIVATELY OWNED RIGHTS. \n\n Any licensee of this software has the obligation and responsibility to abide by the applicable export control laws, regulations, and general prohibitions relating to the export of technical data. Failure to obtain an export control license or other authority from the Government may result in criminal liability under U.S. laws.'

        third_party_code_statement = 'This software uses the following open source components under their respective licenses. Portions of these components are the copyrighted material of their respective authors.'

        holidays_license = 'Holidays is used for determining when weekend rates apply for utility rate structures. \n\n Copyright (c) 2014-2017 <ryanssdev@icloud.com> \n Copyright (c) 2018 <maurizio.montel@gmail.com> \n\n Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: \n\n The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. \n\n THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'

        jinja2_license = 'Jinja2 is used for creating auto-generated HTML reports. \n\n Copyright (c) 2009 by the Jinja Team, see AUTHORS for more details. \n\n Some rights reserved. \n\n Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: \n\n * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. \n\n * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. \n\n * The names of the contributors may not be used to endorse or promote products derived from this software without specific prior written permission. \n\n THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'

        kivy_license = 'Kivy is used to build the GUI. \n\n Copyright (c) 2010-2018 Kivy Team and other contributors \n\n Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: \n\n The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. \n\n THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'

        kivy_garden_license = 'Kivy Garden is used to extend the capabilities of Kivy. \n\n Copyright (c) 2010-2014 Kivy Team and other contributors \n\n Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: \n\n The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. \n\n THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'

        kivy_garden_matplotlib_license = 'Kivy Garden.Matplotlib is used to enable Matplotlib capabilities, such as plotting, within QuESt. \n\n The MIT License (MIT) \n\n Copyright (c) 2015 Kivy Garden \n\n Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: \n\n The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. \n\n THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'

        matplotlib_license = 'Matplotlib is used to plot data in results viewers. \n\n Copyright (c) 2012-2013 Matplotlib Development Team; All Rights Reserved. \n\n License agreement for matplotlib 2.2.2 \n\n 1. This LICENSE AGREEMENT is between the Matplotlib Development Team (“MDT”), and the Individual or Organization (“Licensee”) accessing and otherwise using matplotlib software in source or binary form and its associated documentation. \n\n 2. Subject to the terms and conditions of this License Agreement, MDT hereby grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative works, distribute, and otherwise use matplotlib 2.2.2 alone or in any derivative version, provided, however, that MDT’s License Agreement and MDT’s notice of copyright, i.e., “Copyright (c) 2012-2013 Matplotlib Development Team; All Rights Reserved” are retained in matplotlib 2.2.2 alone or in any derivative version prepared by Licensee. \n\n 3. In the event Licensee prepares a derivative work that is based on or incorporates matplotlib 2.2.2 or any part thereof, and wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in any such work a brief summary of the changes made to matplotlib 2.2.2. \n\n 4. MDT is making matplotlib 2.2.2 available to Licensee on an “AS IS” basis. MDT MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, MDT MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF MATPLOTLIB 2.2.2 WILL NOT INFRINGE ANY THIRD PARTY RIGHTS. \n\n 5. MDT SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF MATPLOTLIB 2.2.2 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING MATPLOTLIB 2.2.2, OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF. \n\n 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions. \n\n 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint venture between MDT and Licensee. This License Agreement does not grant permission to use MDT trademarks or trade name in a trademark sense to endorse or promote products or services of Licensee, or any third party. \n\n 8. By copying, installing or otherwise using matplotlib 2.2.2, Licensee agrees to be bound by the terms and conditions of this License Agreement.'

        numpy_license = 'NumPy is used for array objects. \n\n Copyright © 2005-2018, NumPy Developers. \n All rights reserved. \n\n Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: \n\n Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. \n Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. \n Neither the name of the NumPy Developers nor the names of any contributors may be used to endorse or promote products derived from this software without specific prior written permission. \n\n THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'

        pandas_license = 'Pandas is used for data processing capabilities. \n\n BSD 3-Clause License \n\n Copyright (c) 2008-2012, AQR Capital Management, LLC, Lambda Foundry, Inc. and PyData Development Team \n All rights reserved. \n\n Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: \n\n * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. \n\n * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. \n\n * Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission. \n\n THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'

        pyomo_license = 'Pyomo is used to construct mathematical programs and to interface with solvers. \n\n Copyright 2008 Sandia Corporation. Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains certain rights in this software. \n\n All rights reserved. \n\n Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: \n\n Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. \n\n Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. \n\n Neither the name of the Sandia National Laboratories nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission. \n\n THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'

        requests_license = 'Requests is used for making HTTP requests, namely in the Data Manager. \n\n Copyright 2018 Kenneth Reitz. All rights reserved.  Licensed under the Apache License, Version 2.0, you may not use this file except in compliance with the Apache License.  You may obtain a copy of the Apache License at http://www.apache.org/licenses/LICENSE-2.0.  Unless required by applicable law or agreed to in writing, software distributed under the Apache License is distributed on an “AS IS” BASIS, WITHOUT WARRENTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the Apache License for the specific language governing permissions and limitations under the Apache License.'

        scipy_license = 'SciPy is used for scientific and engineering data processing. \n\n Copyright © 2001, 2002 Enthought, Inc. \n All rights reserved. \n\n Copyright © 2003-2013 SciPy Developers. \n All rights reserved. \n\n Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: \n\n Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. \n Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. \n Neither the name of Enthought nor the names of the SciPy Developers may be used to endorse or promote products derived from this software without specific prior written permission. \n\n THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'

        six_license = 'Six is used for Python compatibility utilities. \n\n Copyright (c) 2010-2018 Benjamin Peterson \n\n Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: \n\n The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. \n\n THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'

        xlrd_license = 'xlrd is used for handling Microsoft Excel (tm) files. \n\n There are two licenses associated with xlrd. This one relates to the bulk of the work done on the library:: \n\n Portions copyright © 2005-2009, Stephen John Machin, Lingfo Pty Ltd \n All rights reserved. \n\n Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: \n\n 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. \n\n 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. \n\n 3. None of the names of Stephen John Machin, Lingfo Pty Ltd and any contributors may be used to endorse or promote products derived from this software without specific prior written permission. \n\n THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. \n\n This one covers some earlier work:: \n\n Copyright (c) 2001 David Giffin. \n All rights reserved. \n Based on the the Java version: Andrew Khan Copyright (c) 2000. \n\n Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: \n\n 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. \n 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. \n 3. All advertising materials mentioning features or use of this software must display the following acknowledgment: \n "This product includes software developed by David Giffin <david@giffin.org>." \n 4. Redistributions of any form whatsoever must retain the following acknowledgment: \n "This product includes software developed by David Giffin <david@giffin.org>." \n\n THIS SOFTWARE IS PROVIDED BY DAVID GIFFIN ``AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DAVID GIFFIN OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'

        third_party_code_licenses = '\n\n====================\n'.join([third_party_code_statement, holidays_license, jinja2_license, kivy_license, kivy_garden_license, kivy_garden_matplotlib_license, numpy_license, pandas_license, pyomo_license, requests_license, scipy_license, six_license, xlrd_license])

        self.about_label.text = '\n\n'.join([version_statement,
        developed_by, 
        #powered_by, 
        acknowledgement, 
        #ntess_statement, 
        copyright_statement,  
        third_party_code_licenses])

        self.about_label.bind(on_ref_press=_go_to_webpage)


class SettingsScreen(ModalView):
    """The settings screen. Driven by a custom Settings panel."""
    def on_close(self):
        self.dismiss()

        return True


class QuEStScreenManager(ScreenManager):
    """The screen manager for the overall application."""
    nav_bar = ObjectProperty()
    help_popup = ObjectProperty()

    def __init__(self, **kwargs):
        super(QuEStScreenManager, self).__init__(**kwargs)

        # Add new screens here.
        self.add_widget(IndexScreen())
        self.about_screen = AboutScreen()
        self.settings_screen = SettingsScreen()

        # Data manager.
        self.add_widget(DataManagerHomeScreen(name='data_manager_home'))
        self.add_widget(DataManagerRTOMOdataScreen(name='data_manager_rto_mo_data'))
        self.add_widget(RateStructureDataScreen(name='data_manager_rate_structure_data'))
        self.add_widget(DataManagerLoadHomeScreen(name='data_manager_load_home'))
        self.add_widget(DataManagerCommercialLoadScreen(name='data_manager_commercial_load'))
        self.add_widget(DataManagerResidentialLoadScreen(name='data_manager_residential_load'))
        self.add_widget(PVwattsSearchScreen(name='data_manager_pvwatts'))
        self.add_widget(NSRDBDataScreen(name='data_manager_nsrdb'))

        # Energy storage valuation.
        self.add_widget(ValuationHomeScreen(name='valuation_home'))
        self.add_widget(BatchRunScreen(name='batch_run'))
        self.add_widget(ValuationResultsViewer(name='valuation_results_viewer'))
        self.add_widget(ValuationWizard(name='valuation_wizard'))

        # Behind-the-meter applications.
        self.add_widget(BehindTheMeterHomeScreen(name='btm_home'))
        self.add_widget(CostSavingsWizard(name='cost_savings_wizard'))
        self.add_widget(BtmResultsViewer(name='btm_results_viewer'))
        
        #Performance applications.
        self.add_widget(PerformanceHomeScreen(name='performance_home'))
        self.add_widget(PerformanceSimRunScreen(name='performance_sim'))
        self.add_widget(PerformanceResultsViewer(name='performance_results_viewer'))
        
        # Technology selection application
        self.add_widget(TechSelectionHomeScreen(name='tech_selection_home'))
        self.add_widget(TechSelectionWizard(name='tech_selection_wizard'))
        self.add_widget(TechSelectionFeasible(name='feasible_techs'))
    
    def launch_valuation(self):
        """"""
        data_manager = App.get_running_app().data_manager

        try:
            data_manager.scan_valuation_data_bank()
        except FileNotFoundError:
            # 'data' directory does not exist.
            no_data_popup = WarningPopup()
            no_data_popup.popup_text.text = "Looks like you haven't downloaded any data yet. Try using QuESt Data Manager to get some data before returning here!"
            no_data_popup.open()
        else: 
            self.current = 'valuation_home'
    
    def launch_btm(self):
        """"""
        data_manager = App.get_running_app().data_manager

        try:
            data_manager.scan_btm_data_bank()
        except FileNotFoundError:
            # 'data' directory does not exist.
            no_data_popup = WarningPopup()
            no_data_popup.popup_text.text = "Looks like you haven't downloaded any data yet. Try using QuESt Data Manager to get some data before returning here!"
            no_data_popup.open()
        else: 
            self.current = 'btm_home'
            
    def launch_performance(self):
        """"""
        data_manager = App.get_running_app().data_manager
        
        try:
            data_manager.scan_performance_data_bank()
        except FileNotFoundError:
            # 'data' directory does not exist.
            no_data_popup = WarningPopup()
            no_data_popup.popup_text.text = "Looks like you haven't downloaded any data yet. Try using QuESt Data Manager to get some data before returning here!"
            no_data_popup.open()
        else: 
            self.current = 'performance_home'
            
    def launch_tech_selection(self):
        """"""    
        self.current = 'tech_selection_home'


class NavigationBar(ActionBar):
    """The dynamically updating navigation bar for traversing around the application."""
    parent_screen = {'index': 'index',
                     'valuation_home': 'index',
                     'batch_run': 'valuation_home',
                     'valuation_results_viewer': 'valuation_home',
                     'valuation_wizard': 'valuation_home',
                     'valuation_advanced': 'valuation_home',
                     'data_manager_home': 'index',
                     'data_manager_rto_mo_data': 'data_manager_home',
                     'data_manager_rate_structure_data': 'data_manager_home',
                     'data_manager_load_home': 'data_manager_home',
                     'data_manager_commercial_load': 'data_manager_load_home',
                     'data_manager_residential_load': 'data_manager_load_home',
                     'data_manager_pvwatts': 'data_manager_home',
                     'btm_home': 'index',
                     'cost_savings_wizard': 'btm_home',
                     'btm_results_viewer': 'btm_home',
                     'performance_home': 'index',
                     'performance_sim': 'performance_home',
                     'performance_results_viewer': 'performance_home',
                     'tech_selection_home': 'index',
                     'tech_selection_wizard': 'tech_selection_home',
                     }

    def __init__(self, sm):
        super(NavigationBar, self).__init__()
        self.sm = sm

        self.build_index_nav_bar()
    
    def build_data_manager_nav_bar(self):
        """Builds the navigation bar for data manager appliations."""
        data_manager_home_button = NavigationButton(
            text='data manager home',
            on_release=partial(self.go_to_screen, 'data_manager_home'),
        )

        self.reset_nav_bar()

        self.action_view.add_widget(data_manager_home_button)

    def build_valuation_advanced_nav_bar(self):
        """Builds the navigation bar for valuation applications."""
        view_results_button = NavigationButton(
            text='view results',
            on_release=partial(self.go_to_screen, 'valuation_results_viewer'),
        )

        run_op_button = NavigationButton(
            text='run optimization',
            on_release=self.sm.get_screen('set_parameters').execute_single_run,
        )

        load_data_button = NavigationButton(
            text='select data',
            on_release=partial(self.go_to_screen, 'load_data'),
        )

        set_parameters_button = NavigationButton(
            text='set parameters',
            on_release=partial(self.go_to_screen, 'set_parameters'),
        )

        self.reset_nav_bar()

        self.action_view.add_widget(load_data_button)
        self.action_view.add_widget(set_parameters_button)
        self.action_view.add_widget(run_op_button)
        self.action_view.add_widget(view_results_button)

    def build_valuation_results_nav_bar(self):
        """
        Builds the navigation bar for viewing results in valuation applications.
        """
        view_results_button = NavigationButton(
            text='view results',
            on_release=partial(self.go_to_screen, 'valuation_results_viewer'),
        )

        batch_processing_button = NavigationButton(
            text='batch runs',
            on_release=partial(self.go_to_screen, 'batch_run'),
        )

        self.reset_nav_bar()

        self.action_view.add_widget(view_results_button)
        self.action_view.add_widget(batch_processing_button)

    def build_valuation_batch_nav_bar(self):
        """Builds the navigation bar for batch processing in valuation applications."""
        view_results_button = NavigationButton(
            text='view results',
            on_release=partial(self.go_to_screen, 'valuation_results_viewer'),
        )

        batch_processing_button = NavigationButton(
            text='batch runs',
            on_release=partial(self.go_to_screen, 'batch_run'),
        )

        self.reset_nav_bar()

        self.action_view.add_widget(view_results_button)
        self.action_view.add_widget(batch_processing_button)
        
    def build_performance_nav_bar(self):
        """Builds the navigation bar for performance application"""
        performance_home_button = NavigationButton(
                text = 'performance home',
                on_release=partial(self.go_to_screen,'performance_home'))
        
        
        
        self.reset_nav_bar()

        self.action_view.add_widget(performance_home_button)

    def reset_nav_bar(self, *args):
        """Resets the navigation bar to its initial state."""
        # remove navigation buttons
        while len(self.action_view.children) > 1:
            for widget in self.action_view.children:
                if isinstance(widget, NavigationButton):
                    self.action_view.remove_widget(widget)

        # add home button and change title to 'Index'
        self.build_index_nav_bar()
        self.set_title('')

    def build_index_nav_bar(self):
        """Adds a home button to the navigation bar."""
        home_button = NavigationButton(
            text='home',
            on_release=partial(self.go_to_screen, 'index'),
        )

        settings_button = NavigationButton(
            text='settings',
            on_release=self.sm.settings_screen.open,
        )

        about_button = NavigationButton(
            text='about',
            on_release=self.sm.about_screen.open,
        )

        self.action_view.add_widget(home_button)
        self.action_view.add_widget(about_button)
        self.action_view.add_widget(settings_button)

    def go_to_screen(self, screen_name, *args):
        """Changes the current screen of the given screen manager."""
        self.sm.current = screen_name
    
    def go_up_screen(self):
        try:
            self.go_to_screen(self.parent_screen[self.sm.current])
        except:
            self.go_to_screen('index')

    def set_title(self, title):
        """Sets the title of the navigation bar."""
        self.action_view.action_previous.title = title


class QuEStApp(App):
    """
    The App class for launching the application.
    """
    config = ConfigParser()
    settings = ESAppSettings()

    def build_config(self, config):
        """Set default settings here."""
        config.setdefaults('optimization', {'solver': 'glpk'})
        config.setdefaults('connectivity', {'use_proxy': 0, 'http_proxy': '', 'https_proxy': '', 'use_ssl_verify': 1})
        config.setdefaults('valuation', {'valuation_dms_save': 1, 'valuation_dms_size': 20000})
        config.setdefaults('btm', {'btm_dms_save': 1, 'btm_dms_size': 20000})
        config.setdefaults('datamanager-pjm', {'pjm_subscription_key': ''})
        config.setdefaults('datamanager-isone', {'iso-ne_api_username': ''})
        config.setdefaults('datamanager-openei', {'openei_key': ''})
        config.setdefaults('performance', {'performance_dms_save': 1, 'performance_dms_size': 20000})

    def build(self):
        # Sets the window/application title.
        self.title = APP_NAME
        self.icon = 'es_gui/resources/logo/Quest_App_Icon_256.png'

        # Create ScreenManager.
        sm = QuEStScreenManager(transition=RiseInTransition(duration=0.2, clearcolor=[1, 1, 1, 1]))
        #sm = QuEStScreenManager(transition=SwapTransition(duration=0.2))

        # Instantiate DataManager.
        self.data_manager = DataManager()

        # Create BoxLayout container.
        bx = BoxLayout(orientation='vertical')

        # Add stop flag for threading management.
        bx.stop = threading.Event()

        # Create ActionBar and pass it a reference to the screen manager.
        ab = NavigationBar(sm)
        ab.sm = sm

        # Fill BoxLayout.
        bx.add_widget(ab)
        bx.add_widget(sm)

        # Pass reference of navigation bar to screen manager.
        sm.nav_bar = ab

        # Create Settings widget and add to settings screen.
        with open(os.path.join(dirname, 'es_gui', 'resources', 'settings', 'general.json'), 'r') as settings_json:
            self.settings.add_json_panel('General', self.config, data=settings_json.read())
        
        with open(os.path.join(dirname, 'es_gui', 'resources', 'settings', 'data_manager.json'), 'r') as settings_json:
            self.settings.add_json_panel('QuESt Data Manager', self.config, data=settings_json.read())
        
        with open(os.path.join(dirname, 'es_gui', 'resources', 'settings', 'valuation.json'), 'r') as settings_json:
            self.settings.add_json_panel('QuESt Valuation', self.config, data=settings_json.read())
        
        with open(os.path.join(dirname, 'es_gui', 'resources', 'settings', 'btm.json'), 'r') as settings_json:
            self.settings.add_json_panel('QuESt BTM', self.config, data=settings_json.read())
            
        with open(os.path.join(dirname,'es_gui','resources','settings','performance.json'),'r') as settings_json:
            self.settings.add_json_panel('QuESt Performance',self.config,data=settings_json.read())

        self.settings.bind(on_close=sm.settings_screen.dismiss)
        sm.settings_screen.settings_box.add_widget(self.settings)

        return bx

    def on_start(self):
        pass
    
    def on_stop(self):
        # Signal that the app is about to close
        self.root.stop.set()

if __name__ == '__main__':
    from kivy.core.window import Window

    # Sets window background color
    Window.clearcolor = get_color_from_hex('#FFFFFF')

    QuEStApp().run()
