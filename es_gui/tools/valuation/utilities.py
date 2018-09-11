from __future__ import absolute_import

import pandas as pd
import numpy as np
import os
import calendar
import logging

from xlrd.biffh import XLRDError


def read_ercot_da_spp(fname, month, settlement_point):
    """
    Reads the day-ahead market historical settlement point prices file at fname and returns the NumPy ndarray corresponding to the hourly price at settlement_point.

    :param fname: string giving location of DAM SPPs file
    :type fname: str
    :param month: which month to read data for; (int) [1, 12] OR (str) ['1', '12']
    :type month: int or str
    :param settlement_point: string giving settlement point name (hub or load zone)
    :type settlement_point: str
    :return spp_da: NumPy ndarray with SPPs for month and settlement point
    :rtype: NumPy ndarray
    """
    spp_da = np.array([])

    # if month is provided as an int, map it to the correct calendar month
    if isinstance(month, int):
        month_abbr = calendar.month_abbr(month)
    elif isinstance(month, str):
        month_ix = int(month)        
        month_abbr = calendar.month_abbr[month_ix]

    # Retrieve the correct worksheet for the month.
    wkbk = pd.ExcelFile(fname)
    wkbk_sheetnames = [name[:3] for name in wkbk.sheet_names]

    try:
        wkst_ix = wkbk_sheetnames.index(month_abbr)
    except ValueError:
        # The worksheet for the requested month does not exist.
        logging.warning('read_ercot_da_spp: Could not load data (the specified month of data could not be found in the given file), returning empty array. (got {fname}, {month}, {settlement_point})'.format(fname=fname, month=month, settlement_point=settlement_point))
        return spp_da
    else:
        df = wkbk.parse(wkst_ix)

        # filter DataFrame by settlement_point and extract series
        df0 = df.loc[df['Settlement Point'] == settlement_point]
        df1 = df0['Settlement Point Price']

        # convert to NumPy array and remove NaN
        spp_da = df1.astype('float').values
        spp_da = spp_da[~np.isnan(spp_da)]

    return spp_da


def read_ercot_da_ccp(fname, month):
    """
    Reads the day-ahead market historical capacity clearing prices file at fname and returns NumPy ndarrays corresponding to the hourly regdn and regup prices.

    :param fname: 
    :param month: which month to read data for; (int) [1, 12] OR (str) ['1', '12']
    
    :param fname: string giving location of DAM CCPs file
    :type fname: str
    :param month: which month to read data for; (int) [1, 12] OR (str) ['1', '12']
    :type month: int or str
    :return: NumPy ndarrays with regdn and regup CCPs for month
    :rtype: Numpy ndarrays
    """
    regdn = np.array([])
    regup = np.array([])

    # if month is provided as an int, map it to the correct calendar month
    if isinstance(month, int):
        month_ix = month
    elif isinstance(month, str):
        month_ix = int(month)
    
    # Read .csv and generate a Series for the month from "Delivery Date" column.
    df = pd.read_csv(fname, low_memory=False)
    series_month = pd.to_datetime(df['Delivery Date']).dt.month

    # Filter DataFrame by month.
    df1 = df.loc[series_month == month_ix]

    if len(df1) > 0:
        regdn = df1['REGDN'].astype('float').values
        regdn = regdn[~np.isnan(regdn)]

        try:
            regup = df1['REGUP '].astype('float').values  # why is there an extra space in the key
        except KeyError:
            regup = df1['REGUP'].astype('float').values
        finally:
            regup = regup[~np.isnan(regup)]
    else:
        logging.warning('read_ercot_da_ccp: No data matching input parameters found, returning empty array. (got {fname}, {month})'.format(fname=fname, month=month))
    
    return regdn, regup


def read_nodeid(fname,iso):
    from xlrd import open_workbook
    wb = open_workbook(filename = fname)
    ws = wb.sheet_by_name(iso)
    nodeid=[]
    for i in range(1,ws.nrows-1):
        cell=ws.cell(i,0)
        text=str(cell.value)
        text=text.replace('.0','')
        nodeid+=[text]
    return nodeid


def read_pjm_data(fpath, year, month, nodeid):
    """"
    Reads the historical LMP, regulation capacity, and regulation service (mileage) prices for the year 'year',
    the month 'month' and for the node 'nodeid'. Returns NumPy ndarrays for those three prices.

    :param fpath: The path to the root of the PJM data directory
    :type fpath: str
    :param year: Year of data to read
    :type year: int or str
    :param month: Month of data to read
    :type month: int or str
    :return: daLMP, RegCCP, RegPCP: Hourly LMP and regulation capacity/performance clearing price values.
    :rtype: NumPy ndarrays
    """
    daLMP = np.array([])
    RegCCP = np.array([])
    RegPCP = np.array([])
    rega = np.array([])
    regd = np.array([])
    mr = np.array([])

    if isinstance(month, str):
        month = int(month)
    
    if isinstance(year, str):
        year = int(year)
    
    if isinstance(nodeid, str):
        nodeid = int(nodeid)

    fnameLMP = "{0:d}{1:02d}_dalmp_{2:d}.csv".format(year, month, nodeid)
    fnameREG = "{0:d}{1:02d}_regp.csv".format(year,month)
    fnameMILEAGE = "{0:d}{1:02d}_regm.csv".format(year,month)

    fname_path_LMP = os.path.join(fpath, 'LMP', str(nodeid), str(year), fnameLMP)
    fname_path_REG = os.path.join(fpath, 'REG', str(year), fnameREG)
    fname_path_MILEAGE = os.path.join(fpath, 'MILEAGE', str(year), fnameMILEAGE)

    try:
        dfLMP = pd.read_csv(fname_path_LMP,index_col=False)
        daLMP = dfLMP['total_lmp_da'].values
    except FileNotFoundError:
        logging.warning('read_pjm_data: No LMP data matching input parameters found, returning empty array. (got {fname}, {year}, {month}, {nodeid})'.format(fname=fnameLMP, year=year, month=month, nodeid=nodeid))
    
    try:
        dfREG = pd.read_csv(fname_path_REG,index_col=False)
        RegCCP = dfREG['rmccp'].values
        RegPCP = dfREG['rmpcp'].values
    except FileNotFoundError:
        logging.warning('read_pjm_data: No REG data matching input parameters found, returning empty array. (got {fname}, {year}, {month})'.format(fname=fnameREG, year=year, month=month))

    try:
        dfMILEAGE = pd.read_csv(fname_path_MILEAGE,index_col=False)
        dfMILEAGE['MILEAGE RATIO'] = dfMILEAGE['regd_hourly']/dfMILEAGE['rega_hourly']

        # TODO: Handling NaNs/missing data intelligently. The current method just fills forward.
        rega = dfMILEAGE['rega_hourly'].fillna(method='ffill').values
        regd = dfMILEAGE['regd_hourly'].fillna(method='ffill').values
        mr = dfMILEAGE['MILEAGE RATIO'].fillna(method='ffill').values
    except FileNotFoundError:
        logging.warning('read_pjm_data: No MILEAGE data matching input parameters found, returning empty array. (got {fname}, {year}, {month})'.format(fname=fnameREG, year=year, month=month))

    return daLMP, mr, rega, regd, RegCCP, RegPCP


def read_pjm_da_lmp(fname, node_name):
    """
    Reads the day-ahead LMP file at fname and returns the NumPy ndarray corresponding to the hourly LMP at node_name.
    :param fname: A string containing the path to the relevant day-ahead LMP file.
    :param node_name: A string containing the name of the pricing node of interest.
    :return: LMP: A NumPy ndarray containing the hourly LMP at node-name.
    """
    # read in the .csv file
    df = pd.read_csv(fname, low_memory=False)

    # filter rows by node_name
    col2 = df.axes[1][2]
    pnode_ix = df.index[df[col2] == node_name]
    df1 = df.iloc[pnode_ix, :]

    # filter Total LMP columns
    df2 = df1[df1.axes[1][7:79:3]]

    # convert to NumPy ndarray, ravel, and remove NaNs
    LMP = np.ravel(df2.astype('float').values)
    LMP = LMP[~np.isnan(LMP)]

    return LMP


def read_pjm_reg_signal(fname):
    """
    Reads the regulation signal file at fname and returns the NumPy ndarray corresponding to the hourly integrated signal.
    :param fname: A string containing the path to the relevant regulation signal file.
    :return: RU, RD: NumPy ndarrays containing the hourly integrated regulation up/down signals.
    """
    # read in the Excel file
    df = pd.read_excel(fname, skip_footer=1)

    # create DateTime indexing to facilitate resampling
    dt_ix = pd.date_range('2017-11-01', periods=30*60*24, freq='2S')
    df.index = dt_ix

    # define function for performing hourly integration
    def _hourly_integration(array_like):
        # ZOH integration
        dt = 2.0/(60*60)
        return np.sum(array_like)*dt

    # use resample to apply hourly integration
    df1 = df.resample(rule='H', closed='left').apply(_hourly_integration)

    # convert DataFrame to NumPy ndarray and ravel
    REG = np.ravel(df1.astype('float').values, 'F')

    # assign reg up/down values appropriately based on sign of regulation signal
    RU = REG * (REG >= 0)
    RD = REG * (REG < 0)

    return RU, RD


def read_pjm_mileage(fname, month):
    """
    Reads the historic regulation market data file at fname and returns the NumPy ndarrays for mileage data.
    :param fname: A string containing the path to the relevant historic regulation market data file.
    :param month: An int corresponding to the month of interest (1: Jan., 2: Feb., etc.)
    :return: Mileage_Ratio, RegA_milage, RegD_mileage: NumPy ndarrays containing computed mileage ratio and RegA/RegD hourly mileage signals.
    """
    # read in the Excel file and parse the relevant worksheet
    wkbk = pd.ExcelFile(fname)
    df = wkbk.parse(month)

    # replace "UNAPPROVED" entries with previous filled value
    df.fillna(method='ffill', inplace=True)

    # compute hourly mileage ratio
    # TODO: what do infinite mileage ratio? (REGA = 0)
    df['MILEAGE RATIO'] = df['REGD_HOURLY'] / df['REGA_HOURLY']

    RegA_mileage = df['REGA_HOURLY'].values
    RegD_mileage = df['REGD_HOURLY'].values
    Mileage_Ratio = df['MILEAGE RATIO'].values

    return Mileage_Ratio, RegA_mileage, RegD_mileage


def read_pjm_reg_price(fname, month):
    """
    Reads the historical ancillary services data file at fname and returns the NumPy ndarrays for regulation clearing prices.
    :param fname: A string containing the path to the relevant historical ancillary services data file.
    :param month: An int corresponding to the month of interest (1: Jan., 2: Feb., etc.)
    :return: RegCCP, RegPCP: NumPy ndarrays containing hourly regulation capacity/performance clearing price values.
    """
    # read in the Excel file and parse relevant worksheet
    wkbk = pd.ExcelFile(fname)
    df = wkbk.parse(month)

    # parse the relevant service
    df1 = df[df['SERVICE'] == 'REG']

    # DLS hour gives NaN
    df1.fillna(method='ffill', inplace=True)

    RegCCP = df1['REG_CCP'].values
    RegPCP = df1['REG_PCP'].values

    return RegCCP, RegPCP


def read_miso_da_lmp(fname, node_name):
    """
    Reads the day-ahead LMP file at fname and returns the NumPy ndarray corresponding to the hourly LMP at node_name.
    :param fname: A string containing the path to the relevant day-ahead LMP file.
    :param node_name: A string containing the name of the pricing node of interest.
    :return: LMP: A NumPy ndarray containing the hourly LMP at node-name.
    """
    # parse fname for month and year values
    month = int(fname[-2:])
    year = int(fname[-6:-2])

    nday = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    if year%4 == 0:
        nday[2] = 29

    LMP = np.empty([0])
    for day in range(1, nday[month]+1):
    
        if (year <= 2014) or (year == 2015 and month <= 2):
            fname_ = fname + str(day).zfill(2) + "_da_lmp.csv"
        else: 
            fname_ = fname + str(day).zfill(2) + "_da_exante_lmp.csv"
        
        df = pd.read_csv(fname_, skiprows=4, low_memory=False)
        # filter rows by node_name
        col1 = df.axes[1][0]
        col3 = df.axes[1][2]
        pnode_ix1 = df.index[df[col1] == node_name]
        df1 = df.iloc[pnode_ix1, :]
        
        # find LMP values
        pnode_ix2 = df1.index[df1[col3] == "LMP"]
        df2 = df.iloc[pnode_ix2, :]
        
        # filter Total LMP columns
        df3 = df2[df2.axes[1][3:27]]

        # convert to NumPy ndarray, ravel, and remove NaNs
        LMP_day = np.ravel(df3.astype('float').values)
        LMP_day = LMP_day[~np.isnan(LMP_day)] 
        LMP = np.append(LMP, LMP_day)
    
    return LMP


def read_miso_reg_price(fname):
    """
    Reads the historical ancillary services data file at fname and returns the NumPy ndarrays for regulation clearing prices.
    :param fname: A string containing the path to the relevant historical ancillary services data file.
    :return: RegMCP: NumPy ndarrays containing hourly regulation capacity/mileage clearing price values.
    """
    # parse fname for month and year values
    month = int(fname[-2:])
    year = int(fname[-6:-2])

    nday = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    if year%4 == 0:
        nday[2] = 29

    RegMCP = np.empty([0])

    for day in range(1, nday[month] + 1):
        if (year <= 2014) or (year == 2015 and month <= 2):
            fname_ = fname + str(day).zfill(2) + "_asm_damcp.csv"
        else: 
            fname_ = fname + str(day).zfill(2) + "_asm_exante_damcp.csv"

        # read in the .csv file
        df = pd.read_csv(fname_, skiprows=4, nrows=7, low_memory=False)
        
        # find SERREGMCP values
        col3 = df.axes[1][2]
        pnode_ix1 = df.index[df[col3] == "SERREGMCP"]
        df1 = df.iloc[pnode_ix1, :]
        df2 = df1[df1.axes[1][3:27]]
    
        # convert to NumPy ndarray, ravel, and remove NaNs
        RegMCP_day = np.ravel(df2.astype('float').values)
        RegMCP_day = RegMCP_day[~np.isnan(RegMCP_day)] 
        RegMCP = np.append(RegMCP, RegMCP_day)
    
    return RegMCP


def read_isone_data(fpath,year,month,nodeid):
    """"
    Reads the historical LMP, regulation capacity, and regulation service (mileage) prices for the year 'year',
    the month 'month' and for the node 'nodeid'. Returns NumPy ndarrays for those three prices.
    :param fpath: A string containing the path to the relevant historical ancillary services data file.
    :param year: An int corresponding to the year of interest
    :param month: An int corresponding to the month of interest (1: Jan., 2: Feb., etc.)
    :return: daLMP, RegCCP, RegPCP: NumPy ndarrays containing hourly LMP as well as regulation capacity/performance clearing price values.
    """
    fnameLMP = "DA_node{0:d}_month{1:d}_year{2:d}.csv".format(nodeid,month,year)
    fnameREG = "REG_month{0:d}_year{1:d}.csv".format(month,year)

    fname_path_LMP = fpath + "LMP/" + str(year) + "/" + str(month).zfill(2) + "/" + fnameLMP
    fname_path_REG = fpath + "REG/" + str(year) + "/" + fnameREG

    try:
        dfLMP = pd.read_csv(fname_path_LMP,index_col=False) #-ISO-NE data is in csv files
    except EnvironmentError:
        fnameLMP = "DA_zone{0:d}_month{1:d}_year{2:d}.csv".format(nodeid, month, year)
        fname_path_LMP = fpath + "LMP/" + str(year) + "/" + str(month).zfill(2) + "/" + fnameLMP

        dfLMP = pd.read_csv(fname_path_LMP, index_col=False)

    daLMP = dfLMP['daLmpTotal'].values

    dfREG = pd.read_csv(fname_path_REG,index_col=False) #-ISO-NE data is in csv files
    RegCCP = dfREG['rcpRegCapacityClearingPrice'].values
    RegPCP = dfREG['rcpRegServiceClearingPrice'].values

    return daLMP, RegCCP, RegPCP

def read_miso_data(fpath, year, month, nodeid):
    """Reads the daily MISO data files and returns the NumPy ndarrays for LMP and MCP.

    
    :param fpath: root of the MISO data folder
    :type fpath: str
    :param year: year of data
    :type year: int or str
    :param month: month of data
    :type month: int or str
    :param nodeid: pricing node ID
    :type nodeid: str
    :return: arrays of data specified
    :rtype: NumPy ndarrays
    """
    LMP = np.array([])
    RegMCP = np.array([])

    _, n_days_month = calendar.monthrange(int(year), int(month))

    for day in range(1, n_days_month+1):
        # Read daily files.
        date_str = '{year}{month}{day}'.format(year=year, month=str(month).zfill(2), day=str(day).zfill(2))

        if (int(year) <= 2014) or (int(year) == 2015 and int(month) <= 2):
            lmp_fname = os.path.join(fpath, 'LMP', str(year), str(month).zfill(2), '{prefix}_da_lmp.csv'.format(prefix=date_str))
            mcp_fname = os.path.join(fpath, 'MCP', str(year), str(month).zfill(2), '{prefix}_asm_damcp.csv'.format(prefix=date_str))
        else: 
            lmp_fname = os.path.join(fpath, 'LMP', str(year), str(month).zfill(2), '{prefix}_da_exante_lmp.csv'.format(prefix=date_str))
            mcp_fname = os.path.join(fpath, 'MCP', str(year), str(month).zfill(2), '{prefix}_asm_exante_damcp.csv'.format(prefix=date_str))
        
        # LMP file.
        try:
            df = pd.read_csv(lmp_fname, skiprows=4, low_memory=False)
        except FileNotFoundError:
            logging.warning('read_miso_data: LMP file missing, returning empty array.')
            break

        # Filter rows by node_name.
        col1 = df.axes[1][0]
        col3 = df.axes[1][2]
        pnode_ix1 = df.index[df[col1] == nodeid]
        df1 = df.iloc[pnode_ix1, :]
        
        # Find LMP values.
        pnode_ix2 = df1.index[df1[col3] == "LMP"]
        df2 = df.iloc[pnode_ix2, :]
        
        # Filter Total LMP columns.
        df3 = df2[df2.axes[1][3:27]]

        if len(df3) == 0:
            LMP = np.array([])
            logging.warning('read_miso_data: A daily LMP file is missing required data, returning empty array.')
            break

        # Convert to NumPy ndarray, ravel, and remove NaNs.
        LMP_day = np.ravel(df3.astype('float').values)
        LMP_day = LMP_day[~np.isnan(LMP_day)] 
        LMP = np.append(LMP, LMP_day)

        # MCP file.
        try:
            df = pd.read_csv(mcp_fname, skiprows=4, nrows=7, low_memory=False)
        except FileNotFoundError:
            RegMCP = np.array([])
            logging.warning('read_miso_data: MCP file missing, returning empty array.')
            break
        
        # Find SERREGMCP values.
        col3 = df.axes[1][2]
        pnode_ix1 = df.index[df[col3] == "SERREGMCP"]
        df1 = df.iloc[pnode_ix1, :]
        df2 = df1[df1.axes[1][3:27]]
    
        # convert to NumPy ndarray, ravel, and remove NaNs
        RegMCP_day = np.ravel(df2.astype('float').values)
        RegMCP_day = RegMCP_day[~np.isnan(RegMCP_day)] 
        RegMCP = np.append(RegMCP, RegMCP_day)
    
    return LMP, RegMCP


if __name__ == '__main__':
    from es_gui.tools.valuation.valuation_optimizer import ValuationOptimizer

    fpath = os.path.join('data', 'PJM')
    year = 2015
    month = 1
    nodeid = '1'

    for month in [12]:
        daLMP, mr, rega, regd, RegCCP, RegPCP = read_pjm_data(fpath,year,month,nodeid)

        op = ValuationOptimizer(market_type='pjm_pfp')

        op.price_electricity = daLMP
        op.mileage_ratio = mr
        op.mileage_slow = rega
        op.mileage_fast = regd
        op.price_reg_capacity = RegCCP
        op.price_reg_performance = RegPCP

        handler_requests = {}
        handler_requests['iso'] = 'PJM'
        handler_requests['market type'] = 'pjm_pfp'
        handler_requests['months'] = [(month, year),]
        handler_requests['node id'] = nodeid

        results, gross_revenue = op.run()
        print(gross_revenue)
