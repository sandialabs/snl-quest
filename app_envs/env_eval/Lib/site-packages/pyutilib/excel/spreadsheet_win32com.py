#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
"""
A class for interacting with an Excel spreadsheet.
"""

#
# Imports
#
import os

#
# Attempt to import win32com stuff.  If this fails, then
# set a flag to tell the ExcelSpreadsheet class that it should
# raise an exception in its constructor.

# BLN: Use DispatchEx instead of Dispatch to make sure we launch
# BLN: a new instance of Excel, otherwise we unintentionally 
# BLN: close any open Excel Windows when importing Pyomo 
# BLN: See https://github.com/Pyomo/pyomo/issues/355
from win32com.client import DispatchEx as Dispatch
from pythoncom import CoInitialize, CoUninitialize, com_error

from pyutilib.excel.base import ExcelSpreadsheet_base


class ExcelSpreadsheet_win32com(ExcelSpreadsheet_base):

    xlToLeft = 1
    xlToRight = 2
    xlUp = 3
    xlDown = 4
    xlThick = 4
    xlThin = 2
    xlEdgeBottom = 9

    _excel_app_ptr = None
    _excel_app_ctr = 0

    def can_read(self):
        return True

    def can_write(self):
        return True

    def can_calculate(self):
        return True

    def __init__(self, filename=None, worksheets=(1,), default_worksheet=1):
        """
        Constructor.
        """
        self.xl = None
        self.xlsfile = None
        if filename is not None:
            self.open(filename, worksheets, default_worksheet)

    def open(self, filename, worksheets=(1,), default_worksheet=1):
        """
        Initialize this object from a file.
        """
        #
        # Set the excel spreadsheet name
        #
        if filename[1] == ":":
            self.xlsfile = filename
        else:
            self.xlsfile = os.getcwd() + "\\" + filename
        #
        # Start the excel spreadsheet
        #
        try:
            self.xl = self._excel_dispatch()
        except com_error:
            raise IOError("Excel not installed.")
        self.wb = self.xl.Workbooks.Open(self.xlsfile)
        self.worksheets = set(worksheets)
        self._ws = {}
        for wsid in worksheets:
            self._ws[wsid] = self.wb.Worksheets.Item(wsid)
            self._ws[wsid].Activate()
        self.default_worksheet = default_worksheet

    def ws(self):
        """ The active worksheet """
        return self._ws[self.default_worksheet]

    def __del__(self):
        """
        Close the spreadsheet when deleting this object.
        """
        self.close()

    def activate(self, name):
        """ Activate a specific sheet """
        if name is None:
            return
        if not name in self._ws:
            self.worksheets.add(name)
            self._ws[name] = self.wb.Worksheets.Item(name)
            self._ws[name].Activate()
        self.default_worksheet = name

    def close(self):
        """
        Close the spreadsheet
        """
        if self is None:  #pragma:nocover
            return
        if self.xl is None:
            return
        if self.xl.ActiveWorkbook is not None:
            self.xl.ActiveWorkbook.Close(SaveChanges=0)
        self._excel_quit()

    def calc_iterations(self, val=None):
        if val is None:
            return self.xl.Iteration
        if not type(val) is bool:
            raise ValueError(
                "ExcelSpreadsheet calc_iterations can only be set to a boolean")
        self.xl.Iteration = val

    def max_iterations(self, val=None):
        if val is None:
            return self.xl.MaxIterations
        if (not type(val) in [int, float, long]) or val < 0:
            raise ValueError(
                "ExcelSpreadsheet max_iterations can only be set to nonnegative integer")
        self.xl.MaxIterations = val

    def calculate(self):
        """
        Perform calculations in a spreadsheet
        """
        self.xl.Calculate()

    def set_array(self, row, col, val, wsid=None):
        self.activate(wsid)
        nrows = len(val)
        return self.set_range((self.ws().Cells(row, col), self.ws().Cells(
            row + nrows - 1, col + 1)), val)

    def get_array(self, row, col, row2, col2, wsid=None, raw=False):
        return self.get_range(
            (self.ws().Cells(row, col), self.ws().Cells(row2, col2)), wsid, raw)

    def set_range(self, rangename, val, wsid=None):
        """
        Set a range with a given value (or set of values)
        """
        self.activate(wsid)
        if type(val) in (int, float):
            val = ((val,),)
        if len(val) != self.get_range_nrows(rangename):
            raise IOError("Setting data with " + str(len(val)) +
                          " rows but range has " + str(
                              self.get_range_nrows(rangename)))
        if type(val) is tuple:
            data = val
        elif type(val) not in (float, int, bool):
            data = []
            for item in val:
                if type(item) is tuple:
                    data.append(item)
                elif type(item) in (float, int, bool):
                    data.append((item,))
                else:
                    data.append(tuple(item))
            data = tuple(data)
        self._range(rangename).Value = data

    def get_column(self, colname, wsid=None, raw=False, contiguous=False):
        """
        Select the values of a column.
        This ignores blank cells at the top and bottom of the column.

        If contiguous is False, a list is returned with all cell values
        starting from the first non-blank cell until the last non-blank cell.

        If contiguous if True, a list is returned with all cell values
        starting from the first non-blank cell until the first blank cell.
        """
        self.activate(wsid)
        name = colname + "1"
        if self.get_range(name) is None:
            start = self.ws().Range(name).End(self.xlDown)
        else:
            start = self.ws().Range(name)
        if contiguous:
            range = self.ws().Range(start, start.End(self.xlDown))
        else:
            range = self.ws().Range(
                start, self.ws().Range(colname + "65536").End(self.xlUp))
        tmp = self._get_range_data(range, raw)
        return tmp

    def get_range(self, rangename, wsid=None, raw=False):
        """
        Get values for a specified range
        """
        self.activate(wsid)
        range = self._range(rangename)
        return self._get_range_data(range, raw)

    def _get_range_data(self, range, raw):
        if raw:
            return range.Value
        nrows = range.Rows.Count
        ncols = range.Columns.Count
        if range.Columns.Count == 1:
            if nrows == 1:
                #
                # The range is a singleton, so return a float
                #
                return range.Value
            else:
                #
                # The range is a column of data, so return a tuple of floats
                #
                ans = []
                for val in range.Value:
                    ans.append(val[0])
                return tuple(ans)
        else:
            if nrows == 1:
                #
                # The range is a row of data, so return a tuple of floats
                #
                return range.Value[0]
            else:
                #
                # The range is a two-dimensional array, so return the values
                # as a tuple of tuples.
                #
                return range.Value

    def get_range_nrows(self, rangename, wsid=None):
        """
        Get the number of rows in a specified range
        """
        self.activate(wsid)
        return self._range(rangename).Rows.Count

    def get_range_ncolumns(self, rangename, wsid=None):
        """
        Get the number of columns in a specified range
        """
        self.activate(wsid)
        return self._range(rangename).Columns.Count

    def _range(self, rangeid, wsid=None):
        """
        Return a range for a given worksheet
        """
        self.activate(wsid)
        try:
            #
            # If rangeid is a tuple, then this is a list of arguments to pass
            # to the Range() method.
            #
            if type(rangeid) is tuple:
                return self.ws().Range(*rangeid)
            #
            # Otherwise, we assume that this is a range name.
            #
            # to the Range() method.
            #
            else:
                return self.ws().Range(rangeid)
        except com_error:
            raise IOError("Unknown range name `" + str(rangeid) + "'")

    def _excel_dispatch(self):
        """
        A private method that launches Excel.
        This keeps a counter of the number of ExcelSpreadsheet objects
        that are running.
        """
        if ExcelSpreadsheet_win32com._excel_app_ctr == 0:
            ExcelSpreadsheet_win32com._excel_app_ptr = Dispatch(
                'Excel.Application')
        ExcelSpreadsheet_win32com._excel_app_ctr += 1
        return ExcelSpreadsheet_win32com._excel_app_ptr

    def _excel_quit(self):
        """
        A method that quits from Excel after all spreadsheets are closed.
        """
        if ExcelSpreadsheet_win32com._excel_app_ctr == 0:
            return None
        if ExcelSpreadsheet_win32com._excel_app_ctr > 1:
            ExcelSpreadsheet_win32com._excel_app_ctr -= 1
            return ExcelSpreadsheet_win32com._excel_app_ctr
        ExcelSpreadsheet_win32com._excel_app_ctr = 0
        ExcelSpreadsheet_win32com._excel_app_ptr.Quit()
        del ExcelSpreadsheet_win32com._excel_app_ptr
        return 0
