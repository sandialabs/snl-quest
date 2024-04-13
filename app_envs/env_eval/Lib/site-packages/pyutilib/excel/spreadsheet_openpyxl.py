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
import warnings
import openpyxl

from pyutilib.excel.base import ExcelSpreadsheet_base


class ExcelSpreadsheet_openpyxl(ExcelSpreadsheet_base):

    def can_read(self):
        return True

    def can_write(self):
        return True

    def can_calculate(self):
        return False

    def __init__(self, filename=None, worksheets=(1,), default_worksheet=1):
        """
        Constructor.
        """
        self.wb = None
        self.xlsfile = None
        self._ws = {}
        if filename is not None:
            self.open(filename, worksheets, default_worksheet)

    def open(self, filename, worksheets=(1,), default_worksheet=1):
        """
        Initialize this object from a file.
        """
        #
        # Set the excel spreadsheet name
        #
        self.xlsfile = filename
        #
        # Start the excel spreadsheet
        #
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.wb = openpyxl.load_workbook(self.xlsfile)
        self.worksheets = self.wb.sheetnames
        self._ws = {}
        for wsid in worksheets:
            self._ws[wsid] = self.wb[self.worksheets[wsid - 1]]
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
        """
        Activate a specific sheet
        """
        if name is None:
            return
        if name in self.worksheets:
            idx = self.worksheets.index(name)
            self.wb.active = idx
        elif not name in self._ws:
            self.wb.add_sheet(name)
            idx = len(self.wb.get_sheet_names()) - 1
            self._ws[idx] = self.wb.Worksheets.Item(name)
            self._ws[idx].Activate()
        self.default_worksheet = idx

    def close(self):
        """
        Close the spreadsheet
        """
        if self is None:  #pragma:nocover
            return
        if self._ws is None:
            return
        self._ws = {}

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
        ws = self.wb.active
        xlo = row
        xhi = row + len(val) - 1
        ylo = col
        yhi = col + 1
        for row in range(xhi - xlo + 1):
            for col in range(yhi - ylo + 1):
                #print(row,col)
                ws.cell(row=xlo + row, column=ylo + col).value = val[row][col]

    def get_array(self, row, col, row2, col2, wsid=None, raw=False):
        self.activate(wsid)
        ws = self.wb.active
        ans = []
        for row in ws.iter_rows(min_col=col, min_row=row, max_col=col2, max_row=row2):
            ans_ = []
            for col in row:
                ans_.append(col.value)
            if len(ans_) == 1:
                ans.append(ans_[0])
            else:
                ans.append(list(ans_))
        return list(ans)

    def set_range(self, rangename, val, wsid=None):
        """
        Set a range with a given value (or set of values)
        """
        #
        # Process data into tuples
        #
        if type(val) in (int, float):
            val = ((val,),)
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
        #
        # Set the data
        #
        self.activate(wsid)
        _range = self._range(rangename)
        if not _range is None and len(val) != self.get_range_nrows(rangename):
            raise IOError("Setting data with " + str(len(val)) +
                          " rows but range has " + str(
                              self.get_range_nrows(rangename)))
        _destinations = list(_range.destinations)
        ws = self.wb[_destinations[0][0]]
        #
        ylo, xlo, yhi, xhi = openpyxl.worksheet.worksheet.range_boundaries(
            _destinations[0][1])
        for row in range(xhi - xlo + 1):
            for col in range(yhi - ylo + 1):
                ws.cell(row=xlo + row, column=ylo + col).value = data[row][col]

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
        _range = self._range(rangename)
        data = self._get_range_data(_range, raw)
        if len(data) == 1:
            return data[0]
        return data

    def _get_range_data(self, _range, raw):
        ans = []
        if type(_range) is tuple:
            _data = _range
        else:
            _destinations = list(_range.destinations)
            ws = self.wb[_destinations[0][0]]
            #
            # If we have a since cell, just return its value
            #
            if not ':' in _destinations[0][1]:
                return [ ws[_destinations[0][1]].value ]
            #
            # If we have a range, return a list of values
            #
            _data = ws[_destinations[0][1]]
        #
        # Process Data
        #
        for row in _data:
            rvals = []
            for cell in row:
                rvals.append(cell.value)
            if len(rvals) == 1:
                ans.append(rvals[0])
            else:
                ans.append(list(rvals))
        return list(ans)

    def get_range_nrows(self, rangename, wsid=None):
        """
        Get the number of rows in a specified range
        """
        self.activate(wsid)
        _range = self._range(rangename)
        data = self._get_range_data(_range, False)
        return len(data)

    def get_range_ncolumns(self, rangename, wsid=None):
        """
        Get the number of columns in a specified range
        """
        self.activate(wsid)
        _range = self._range(rangename)
        data = self._get_range_data(_range, False)
        if type(data[0]) is tuple:
            return len(data[0])
        return 1

    def _range(self, rangeid, wsid=None, exception=True):
        """
        Return a range for a given worksheet
        """
        self.activate(wsid)
        try:
            #
            # If rangeid is a tuple, then this is a list of arguments 
            #
            if type(rangeid) is tuple:
                return self.wb.get_squared_range(*rangeid)
            #
            # Otherwise, we assume that this is a range name.
            #
            try:
                return self.wb.defined_names[rangeid]
            except KeyError:
                pass
            ws = self.wb.active
            if ':' in rangeid:
                _rangeid = rangeid.split(':')
                return ws[_rangeid[0]:_rangeid[1]]
            else:
                return ws[rangeid:rangeid]
        except:
            raise IOError("Unknown range name `" + str(rangeid) + "'")
