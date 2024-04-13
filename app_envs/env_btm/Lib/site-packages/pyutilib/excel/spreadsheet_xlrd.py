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
import sys

import xlrd

from pyutilib.excel.base import ExcelSpreadsheet_base


class ExcelSpreadsheet_xlrd(ExcelSpreadsheet_base):

    def can_read(self):
        return True

    def can_write(self):
        return False

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
        self.wb = xlrd.open_workbook(self.xlsfile)
        self.worksheets = set(worksheets)
        self._ws = {}
        for wsid in worksheets:
            if type(wsid) is int:
                self._ws[wsid] = self.wb.sheet_by_index(wsid - 1)
            else:
                self._ws[wsid] = self.wb.sheet_by_name(wsid)
        self.default_worksheet = default_worksheet

    def ws(self):
        """ The active worksheet """
        return self._ws[self.default_worksheet]

    def __del__(self):
        """
        Close the spreadsheet when deleting this object.
        """
        if self is None:
            return
        self.close()

    def close(self):
        """
        Close the spreadsheet
        """
        if self is None:  #pragma:nocover
            return
        if self._ws is None:
            return
        self._ws = {}

    def activate(self, name):
        """ Activate a specific sheet """
        if name is None:
            return
        if not name in self._ws:
            raise ValueError("Cannot activate a missing sheet with xlrd")
        self.default_worksheet = name

    def calc_iterations(self, val=None):
        raise ValueError(
            "ExcelSpreadsheet calc_iterations() is not supported with xlrd")

    def max_iterations(self, val=None):
        raise ValueError(
            "ExcelSpreadsheet max_iterations() is not supported with xlrd")

    def calculate(self):
        """
        Perform calculations in a spreadsheet
        """
        raise ValueError(
            "ExcelSpreadsheet calculate() is not supported with xlrd")

    def set_array(self, row, col, val, wsid=None):
        """
        Set an array of cells to a given value
        """
        raise IOError("Cannot write to ranges with xlrd")

    def get_array(self, row, col, row2, col2, wsid=None, raw=False):
        """
        Return a range of cells
        """
        return self.get_range(
            (self.ws().Cells(row, col), self.ws().Cells(row2, col2)), wsid, raw)

    def set_range(self, rangename, val, wsid=None):
        """
        Set a range with a given value (or set of values)
        """
        raise IOError("Cannot write to ranges with xlrd")

    def get_column(self, colname, wsid=None, raw=False, contiguous=False):
        """
        Select the values of a column.
        This ignores blank cells at the top and bottom of the column.

        If contiguous is False, a list is returned with all cell values
        starting from the first non-blank cell until the last non-blank cell.

        If contiguous if True, a list is returned with all cell values
        starting from the first non-blank cell until the first blank cell.
        """
        raise IOError("Cannot get a named column with xlrd")

    def get_range(self, rangename, wsid=None, raw=False):
        """
        Get values for a specified range
        """
        rangeid = self._range(rangename)
        if not rangeid is None:
            return self._get_range_data(rangeid, raw)

    def _get_range_data(self, _range, raw):
        """
        Return data for the specified range.
        """
        sheet, rowxlo, rowxhi, colxlo, colxhi = _range.area2d()
        if (rowxhi - rowxlo) == 1 and (colxhi - colxlo) == 1:
            return self._translate(sheet.cell(rowxlo, colxlo))
        else:
            #
            # If the range is a column or row of data, then return a list of values.
            # Otherwise, return a tuple of tuples
            #
            ans = []
            for i in range(rowxhi - rowxlo):
                col = []
                for j in range(colxhi - colxlo):
                    val = self._translate(sheet.cell(i + rowxlo, j + colxlo))
                    col.append(val)
                if len(col) == 1:
                    ans.append(col[0])
                else:
                    ans.append(list(col))
            return list(ans)

    def get_range_nrows(self, rangename, wsid=None):
        """
        Get the number of rows in a specified range
        """
        _range = self._range(rangename)
        sheet, rowxlo, rowxhi, colxlo, colxhi = _range.area2d()
        return rowxhi - rowxlo

    def get_range_ncolumns(self, rangename, wsid=None):
        """
        Get the number of columns in a specified range
        """
        _range = self._range(rangename)
        sheet, rowxlo, rowxhi, colxlo, colxhi = _range.area2d()
        return colxhi - colxlo

    def _range(self, rangeid, wsid=None):
        """
        Return a range for a given worksheet
        """
        self.activate(wsid)
        #
        # If rangeid is a tuple, then this is a list of arguments to pass
        # to the Range() method.
        #
        if type(rangeid) is tuple:
            return self.ws().Range(*rangeid)
        #
        # Otherwise, we assume that this is a range name.
        #
        else:
            tmp_ = self.wb.name_map.get(rangeid.lower(), None)
            if tmp_ is None:
                raise IOError("Range %s is not found" % rangeid)
            if len(tmp_) > 1:
                raise IOError("Cannot process scoped names")
            return tmp_[0]

    def _translate(self, cell):
        """
        Translate the cell value to a standard type
        """
        if cell.ctype == 0:
            return ""
        if cell.ctype == 1:
            return str(cell.value)
        if cell.ctype == 2 or cell.ctype == 3 or cell.ctype == 4:
            return cell.value
        if cell.ctype == 6:
            return None
        raise ValueError("Unexpected cell error")
