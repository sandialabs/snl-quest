#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['ExcelSpreadsheet']

import pyutilib.common
from pyutilib.excel.base import ExcelSpreadsheet_base

class _Interface(object):
    def __init__(self, available, module):
        self.available = available
        self.module = module

class Interfaces(object):
    singleton = None

    def __new__(cls):
        if Interfaces.singleton is None:
            Interfaces.singleton = super(Interfaces,cls).__new__(cls)
        return Interfaces.singleton

    def __init__(self):
        self.options = ['xlrd','win32com','openpyxl']
        self._modules = {}

        try:
            import xlrd
            from pyutilib.excel.spreadsheet_xlrd import (
                ExcelSpreadsheet_xlrd as module
            )
            self._modules['xlrd'] = _Interface(True, module)
        except ImportError:
            self._modules['xlrd'] = _Interface(False, None)

        try:
            from win32com.client.dynamic import Dispatch
            from pythoncom import CoInitialize, CoUninitialize
            from pythoncom import CoInitialize, CoUninitialize, com_error
            from pyutilib.excel.spreadsheet_win32com import (
                ExcelSpreadsheet_win32com as module
            )
            self._modules['win32com'] = _Interface(True, module)
        except ImportError:
            self._modules['win32com'] = _Interface(False, None)

        try:
            import openpyxl
            from pyutilib.excel.spreadsheet_openpyxl import (
                ExcelSpreadsheet_openpyxl as module
            )
            self._modules['openpyxl'] = _Interface(True, module)
        except ImportError:
            self._modules['openpyxl'] = _Interface(False, None)

    def __getitem__(self, item):
        return self._modules[item]


class ExcelSpreadsheet(ExcelSpreadsheet_base):

    def __new__(cls, *args, **kwds):
        #
        # Note that this class returns class instances rather than
        # class types.  This is because these classes are not
        # subclasses of ExcelSpreadsheet, and thus the __init__
        # method will not be called unless we construct the
        # class instances here.
        #
        ctype = kwds.pop('ctype', None)
        interfaces = Interfaces()

        if not ctype:
            for interface in interfaces.options:
                if interfaces[interface].available:
                    ctype = interface
                    break
            if not ctype:
                raise RuntimeError("No excel interface (from %s) available"
                                   % (interfaces.options,))

        if ctype not in interfaces.options:
            raise RuntimeError(
                "Excel interface %s not in known interfaces (%s)"
                % (ctype, interfaces.options,))

        if not interfaces[ctype].available:
            raise ImportError("Excel interface %s is not available" % (ctype,))

        return interfaces[ctype].module(*args, **kwds)
