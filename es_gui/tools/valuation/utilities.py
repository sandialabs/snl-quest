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
        rega = dfMILEAGE['rega_hourly'].replace([np.inf, -np.inf], np.nan).fillna(method='ffill').values
        regd = dfMILEAGE['regd_hourly'].replace([np.inf, -np.inf], np.nan).fillna(method='ffill').values
        mr = dfMILEAGE['MILEAGE RATIO'].replace([np.inf, -np.inf], np.nan).fillna(method='ffill').values
    except FileNotFoundError:
        logging.warning('read_pjm_data: No MILEAGE data matching input parameters found, returning empty array. (got {fname}, {year}, {month})'.format(fname=fnameMILEAGE, year=year, month=month))

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

##################################################################################################################
#///////////////////////////////////////////////////////#
def read_isone_data(fpath, year, month, nodeid):
    """"
    Reads the historical LMP, regulation capacity, and regulation service (mileage) prices for the year 'year',
    the month 'month' and for the node 'nodeid'. Returns NumPy ndarrays for those three prices.
    :param fpath: A string containing the path to the relevant historical ancillary services data file.
    :param year: An int corresponding to the year of interest
    :param month: An int corresponding to the month of interest (1: Jan., 2: Feb., etc.)
    :return: daLMP, RegCCP, RegPCP: NumPy ndarrays containing hourly LMP as well as regulation capacity/performance clearing price values.
    """

    if isinstance(month, str):
        month = int(month)

    if isinstance(year, str):
        year = int(year)

    if isinstance(nodeid, (int, float, complex)):
        nodeid = str(nodeid)

    if year < 2018:
        if year == 2017 and month == 12:
            fnameLMP = "{0:d}{1:02d}_fmlmp_{2:s}.csv".format(year, month, nodeid)
            fnameRCP = "{0:d}{1:02d}_fmrcp.csv".format(year ,month)
        else:
            fnameLMP = "{0:d}{1:02d}_dalmp_{2:s}.csv".format(year, month, nodeid)
            fnameRCP = "{0:d}{1:02d}_rcp.csv".format(year ,month)
    else:
        fnameLMP = "{0:d}{1:02d}_fmlmp_{2:s}.csv".format(year, month, nodeid)
        fnameRCP = "{0:d}{1:02d}_fmrcp.csv".format(year ,month)

    fname_path_LMP = os.path.join(fpath, 'LMP', str(nodeid), str(year), fnameLMP)
    fname_path_RCP = os.path.join(fpath, 'RCP', str(year), fnameRCP)
    fname_path_MILEAGE = os.path.join(fpath, 'MileageFile.xlsx')

    daLMP = np.empty([0])
    RegCCP = np.empty([0])
    RegPCP = np.empty([0])
    miMULT = np.empty([0])


    try:
        dfLMP = pd.read_csv(fname_path_LMP, index_col=False)
        daLMP = dfLMP['LmpTotal'].values
    except FileNotFoundError:
        logging.warning \
            ('read_isone_data: No LMP data matching input parameters found, returning empty array. (got {fname}, {year}, {month}, {nodeid})'.format
                (fname=fnameLMP, year=year, month=month, nodeid=nodeid))

    try:
        if year > 2014:
            if year == 2015 and month < 4:
                dfRCP = pd.read_csv(fname_path_RCP, index_col=False)
                RegCCP = dfRCP['RegClearingPrice'].values
                RegPCP = []
            else:
                dfRCP = pd.read_csv(fname_path_RCP, index_col=False)
                RegCCP = dfRCP['RegCapacityClearingPrice'].values
                RegPCP = dfRCP['RegServiceClearingPrice'].values
                                   
                dataF_mileage_file = pd.read_excel(fname_path_MILEAGE, sheet_name = 'Energy Neutral Trinary', usecols = ['Fleet ATRR dispatch [MW]'])
                dataF_mileage_file = dataF_mileage_file.append(pd.DataFrame([-10]*15, columns = ['Fleet ATRR dispatch [MW]']), ignore_index = True) #   changes number of data points to 24 hours; doesn't change mileage
                            
                #   AGC setpoints given every 4 seconds, take the total mileage for each hour; total of one day of mileage
                hours = [i for i in range(len(dataF_mileage_file.index)//900)]
                
                mileage_day = []
                for hour in hours:
                    dataF_mileage_hour = dataF_mileage_file[900*hour:900*(hour + 1)] #    every 900 values represents an hour (900*4 = 3600)
                    mileage_hour = 0 
                    for i in range(len(dataF_mileage_hour.index)):
                        if i == len(dataF_mileage_hour.index) - 1:
                            break
                    
                        if not dataF_mileage_hour.iloc[i, 0] == dataF_mileage_hour.iloc[i + 1, 0]:
                            mileage_hour += abs(dataF_mileage_hour.iloc[i, 0] - dataF_mileage_hour.iloc[i + 1, 0])/10
                            
                    mileage_day.append(mileage_hour)
            
                dataF_mileage_day = pd.DataFrame(mileage_day, columns = ['Trinary Mileage'])
                
                #   have one days worth of data, need one months worth
                days = len(daLMP)//24
                mileage_mult = pd.DataFrame(columns = ['Trinary Mileage'])
                for day in range(days):
                    mileage_mult = mileage_mult.append(dataF_mileage_day, ignore_index = True)
                #   if the len are offset, make them match
                if not len(daLMP) == len(mileage_mult):
                    diff = len(daLMP) - len(mileage_mult)
                    
                    for i in range(diff):
                        mileage_mult = mileage_mult.append(dataF_mileage_day.iloc[i], ignore_index = True)
                        
                miMULT = mileage_mult['Trinary Mileage'].values
        else:
            dfRCP = pd.read_csv(fname_path_RCP, index_col=False)
            RegCCP = dfRCP['RegClearingPrice'].values
            RegPCP = []

    except FileNotFoundError:
        logging.warning \
            ('read_isone_data: No ASP data matching input parameters found, returning empty array. (got {fname}, {year}, {month})'.format
                (fname=fnameRCP, year=year, month=month))
    

    return daLMP, RegCCP, RegPCP, miMULT
#///////////////////////////////////////////////////////#


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




#######################################################################################################################
# NYISO
#######################################################################################################################

def read_nyiso_data(fpath, year, month, nodeid, typedat="both", RT_DAM="both"):
    """"
    Reads the historical LBMP, regulation capacity, and regulation movement prices for the year 'year',
    the month 'month' and for the node 'nodeid'. Returns NumPy ndarrays for those three prices.

    :param fpath: The path to the root of the NYISO data directory
    :type fpath: str
    :param year: Year of data to read
    :type year: int or str
    :param month: Month of data to read
    :type month: int or str
    :param nodeid: ID of the node to read
    :type nodeid: int or str
    :return: daLBMP, rtLBMP, daCAP, rtCAP, rtMOV: Hourly LBMP and regulation capacity/movement clearing price values.
    :rtype: NumPy ndarraysx
    """
    ############################################################

    daLBMP = np.empty([0])
    rtLBMP = np.empty([0])
    daCAP = np.empty([0])
    rtCAP = np.empty([0])
    rtMOV = np.empty([0])

    if isinstance(month, str):
        month = int(month)

    if isinstance(year, str):
        year = int(year)

    if isinstance(nodeid, str):
        nodeid = int(nodeid)

    ############################################################################################
    # folderfile = fpath
    # # TODO: path_nodes_file is a folder to adjust when integrating it to QuESt
    # path_nodes_file = 'C:/Users/fwilche/Documents/data_bank/NYISO/'
    path_nodes_file = '../../es_gui/apps/data_manager/_static/'
    pathf_nodeszones = os.path.join(fpath, path_nodes_file, 'nodes_nyiso.csv')
    df_nodeszones = pd.read_csv(pathf_nodeszones, index_col=False)
    df_nodeszones_x = df_nodeszones.loc[df_nodeszones['Node ID'] == nodeid, :]

    if df_nodeszones_x.empty:
        print("The node does NOT exists in NYISO")
        # raise ValueError('Not a valid bus number!!!')
        return daLBMP, rtLBMP, daCAP, rtCAP, rtMOV
    else:
        if df_nodeszones_x.iloc[0,0] == df_nodeszones_x.iloc[0,2]:
            print("It's a zone node")
            zoneid = nodeid
            zone_gen = "zone"
        else:
            print("It's a gen node")
            zoneid = df_nodeszones_x.iloc[0,2]
            zone_gen = "gen"
    print("Identified zone:")
    print(zoneid)
    ############################################################################################

    ndaysmonth = calendar.monthrange(year, month)
    ndaysmonth = int(ndaysmonth[1])


    for ix in range(ndaysmonth):
        day_x = ix+1
        date_str = str(year)+ str(month).zfill(2)+str(day_x).zfill(2)
        # print(date_str)

        fnameLBMP_DA = date_str + "damlbmp_" + zone_gen + ".csv"
        fnameASP_DA = date_str + "damasp.csv"

        fnameLBMP_RT = date_str + "realtime_" + zone_gen + ".csv"
        fnameASP_RT = date_str + "rtasp.csv"

        fname_path_LBMP_DA = os.path.join(fpath, 'LBMP', 'DAM', zone_gen, str(year), str(month).zfill(2),fnameLBMP_DA)
        fname_path_ASP_DA = os.path.join(fpath, 'ASP', 'DAM', str(year), str(month).zfill(2),fnameASP_DA)

        fname_path_LBMP_RT = os.path.join(fpath, 'LBMP', 'RT', zone_gen, str(year), str(month).zfill(2),fnameLBMP_RT)
        fname_path_ASP_RT = os.path.join(fpath, 'ASP', 'RT', str(year), str(month).zfill(2),fnameASP_RT)

        if typedat == "asp" or typedat == "both":
            # 20170201damasp.csv
            # 20180501rtasp.csv
            if RT_DAM == "RT" or RT_DAM == "both":
                try:
                    df_file = pd.read_csv(fname_path_ASP_RT, index_col=False)
                except FileNotFoundError:
                    rtCAP = np.empty([0])
                    rtMOV = np.empty([0])
                    logging.warning('read_nyiso_data: RT ASP file missing, returning empty array.')
                    break

                if (year>=2016 and month>=6 and day_x>=23) or (year>=2016 and month>=7) or (year>=2017):
                    # NYCA Regulation Capacity ($/MWHr) - for newest type of data
                    df_file_rtCAP = df_file.loc[df_file['PTID'] == zoneid, ['NYCA Regulation Capacity ($/MWHr)']]
                    rtCAP = np.append(rtCAP, df_file_rtCAP.values)
                    # NYCA Regulation Movement ($/MW)
                    df_file_rtMOV = df_file.loc[df_file['PTID'] == zoneid, ['NYCA Regulation Movement ($/MW)']]
                    rtMOV = np.append(rtMOV, df_file_rtMOV.values)
                elif (year>=2001 and month>=10 and day_x>=0) or (year>=2001 and month>=11) or \
                     (year>=2002 and not ((year>=2016 and month>=6 and day_x>=23) or (year>=2016 and month>=7) or (year>=2017))):
                    df_file_rtCAP = df_file['East Regulation ($/MWHr)']
                    rtCAP = np.append(rtCAP, df_file_rtCAP.values)
                    df_file_rtMOV = df_file[' NYCA Regulation Movement ($/MW)']
                    rtMOV = np.append(rtMOV, df_file_rtMOV.values)
                    # RT ancillary services for NYISO start on July 2004


            if RT_DAM == "DAM" or RT_DAM == "both":
                try:
                    df_file = pd.read_csv(fname_path_ASP_DA, index_col=False)
                except FileNotFoundError:
                    daCAP = np.empty([0])
                    logging.warning('read_nyiso_data: DA ASP file missing, returning empty array.')
                    break

                if (year >= 2016 and month >= 6 and day_x >= 23) or (year >= 2016 and month >= 7) or (year >= 2017):
                    df_file_daCAP = df_file.loc[df_file['PTID'] == zoneid, ['NYCA Regulation Capacity ($/MWHr)']]
                    daCAP = np.append(daCAP, df_file_daCAP.values)
                elif (year >= 2001 and month >= 10 and day_x >= 0) or (year >= 2001 and month >= 11) or \
                     (year >= 2002 and not ((year >= 2016 and month >= 6 and day_x >= 23) or (year >= 2016 and month >= 7) or (year >= 2017))):
                    df_file_daCAP = df_file['East Regulation ($/MWHr)']
                    daCAP = np.append(daCAP, df_file_daCAP.values)
                else:
                    df_file_daCAP = df_file['Regulation ($/MWHr)']
                    daCAP = np.append(daCAP, df_file_daCAP.values)

        if typedat == "lbmp" or typedat == "both":
            # 20170201damlbmp_gen.csv
            # 20170201damlbmp_zone.csv
            # 20170201realtime_gen.csv
            if RT_DAM == "RT" or RT_DAM == "both":
                try:
                    df_rtLBMP = pd.read_csv(fname_path_LBMP_RT, index_col=False)
                except FileNotFoundError:
                    rtLBMP = np.empty([0])
                    logging.warning('read_nyiso_data: RT LMP file missing, returning empty array.')
                    break

                rtLBMP_node_x = df_rtLBMP.loc[df_rtLBMP['PTID'] == nodeid, ['LBMP ($/MWHr)']]
                rtLBMP = np.append(rtLBMP, rtLBMP_node_x.values)
                if rtLBMP_node_x.empty:
                    return np.empty([0]), np.empty([0]), np.empty([0]), np.empty([0]), np.empty([0])

            if RT_DAM == "DAM" or RT_DAM == "both":
                try:
                    df_daLBMP = pd.read_csv(fname_path_LBMP_DA, index_col=False)
                except FileNotFoundError:
                    daLBMP = np.empty([0])
                    logging.warning('read_nyiso_data: DA LMP file missing, returning empty array.')
                    break

                daLBMP_node_x = df_daLBMP.loc[df_daLBMP['PTID'] == nodeid, ['LBMP ($/MWHr)']]
                daLBMP = np.append(daLBMP, daLBMP_node_x.values)
                if daLBMP_node_x.empty:
                    return np.empty([0]), np.empty([0]), np.empty([0]), np.empty([0]), np.empty([0])

    return daLBMP, rtLBMP, daCAP, rtCAP, rtMOV


#TODO: delete function below:
def read_nyiso_data_old(fpath, year, month, nodeid, typedat="both", RT_DAM="both"):
    """"
    Reads the historical LBMP, regulation capacity, and regulation movement prices for the year 'year',
    the month 'month' and for the node 'nodeid'. Returns NumPy ndarrays for those three prices.

    :param fpath: The path to the root of the NYISO data directory
    :type fpath: str
    :param year: Year of data to read
    :type year: int or str
    :param month: Month of data to read
    :type month: int or str
    :param nodeid: ID of the node to read
    :type nodeid: int or str
    :return: daLBMP, rtLBMP, daCAP, rtCAP, rtMOV: Hourly LBMP and regulation capacity/movement clearing price values.
    :rtype: NumPy ndarraysx
    """
    ############################################################

    if isinstance(month, str):
        month = int(month)

    if isinstance(year, str):
        year = int(year)

    if isinstance(nodeid, str):
        nodeid = int(nodeid)

    # folderfile = fpath
    pathfile_aspzones = os.path.join(fpath, 'NYISO_aspnodes_list.csv')
    df_aspzones = pd.read_csv(pathfile_aspzones, index_col=False)

    df_aspzones_x = df_aspzones.loc[df_aspzones['PTID']== nodeid, :]

    if df_aspzones_x.empty:
        print("It's empty -must be a gen and not a zone node")

        # pathfile_genzones = folderfile + 'generator_NYISO.csv'
        pathfile_genzones = os.path.join(fpath, 'generator_NYISO.csv')
        df_genzones = pd.read_csv(pathfile_genzones, index_col=False)

        df_genzones_x = df_genzones.loc[df_genzones['PTID'] == nodeid, ['Zone']]

        if not df_genzones_x.empty:
            zone_gen = "gen"
            zone_x = df_genzones_x.iloc[0,0]

            df_zoneid_x = df_aspzones.loc[df_aspzones['Name'] == zone_x, 'PTID']

            if not df_zoneid_x.empty:
                print("Identified zone:")
                print(df_zoneid_x)
                zoneid = df_zoneid_x.iloc[0]
            else:
                raise ValueError('Bus outside NYISO!!!')

        else:
            raise ValueError('Not a valid bus number!!!')



    else:
        print("It's a zone node")
        zoneid = nodeid
        zone_gen = "zone"

    ############################################################

    ndaysmonth = calendar.monthrange(year, month)
    ndaysmonth = int(ndaysmonth[1])

    daLBMP = np.empty([0])
    rtLBMP = np.empty([0])
    daCAP = np.empty([0])
    rtCAP = np.empty([0])
    rtMOV = np.empty([0])

    for ix in range(ndaysmonth):
        day_x = ix+1
        date_str = str(year)+ str(month).zfill(2)+str(day_x).zfill(2)
        # print(date_str)

        fnameLBMP_DA = date_str + "damlbmp_" + zone_gen + ".csv"
        fnameASP_DA = date_str + "damasp.csv"

        fnameLBMP_RT = date_str + "realtime_" + zone_gen + ".csv"
        fnameASP_RT = date_str + "rtasp.csv"

        fname_path_LBMP_DA = os.path.join(fpath, 'LBMP', 'DAM', zone_gen, str(year), str(month).zfill(2),fnameLBMP_DA)
        fname_path_ASP_DA = os.path.join(fpath, 'ASP', 'DAM', str(year), str(month).zfill(2),fnameASP_DA)

        fname_path_LBMP_RT = os.path.join(fpath, 'LBMP', 'RT', zone_gen, str(year), str(month).zfill(2),fnameLBMP_RT)
        fname_path_ASP_RT = os.path.join(fpath, 'ASP', 'RT', str(year), str(month).zfill(2),fnameASP_RT)

        if typedat == "asp" or typedat == "both":
            # 20170201damasp.csv
            # 20180501rtasp.csv
            if RT_DAM == "RT" or RT_DAM == "both":
                try:
                    df_file = pd.read_csv(fname_path_ASP_RT, index_col=False)
                except FileNotFoundError:
                    rtCAP = np.empty([0])
                    rtMOV = np.empty([0])
                    logging.warning('read_nyiso_data: RT ASP file missing, returning empty array.')
                    break

                if (year>=2016 and month>=6 and day_x>=23) or (year>=2016 and month>=7) or (year>=2017):
                    # NYCA Regulation Capacity ($/MWHr) - for newest type of data
                    df_file_rtCAP = df_file.loc[df_file['PTID'] == zoneid, ['NYCA Regulation Capacity ($/MWHr)']]
                    rtCAP = np.append(rtCAP, df_file_rtCAP.values)
                    # NYCA Regulation Movement ($/MW)
                    df_file_rtMOV = df_file.loc[df_file['PTID'] == zoneid, ['NYCA Regulation Movement ($/MW)']]
                    rtMOV = np.append(rtMOV, df_file_rtMOV.values)
                elif (year>=2001 and month>=10 and day_x>=0) or (year>=2001 and month>=11) or \
                     (year>=2002 and not ((year>=2016 and month>=6 and day_x>=23) or (year>=2016 and month>=7) or (year>=2017))):
                    df_file_rtCAP = df_file['East Regulation ($/MWHr)']
                    rtCAP = np.append(rtCAP, df_file_rtCAP.values)
                    df_file_rtMOV = df_file[' NYCA Regulation Movement ($/MW)']
                    rtMOV = np.append(rtMOV, df_file_rtMOV.values)
                    # RT ancillary services for NYISO start on July 2004


            if RT_DAM == "DAM" or RT_DAM == "both":
                try:
                    df_file = pd.read_csv(fname_path_ASP_DA, index_col=False)
                except FileNotFoundError:
                    daCAP = np.empty([0])
                    logging.warning('read_nyiso_data: DA ASP file missing, returning empty array.')
                    break

                if (year >= 2016 and month >= 6 and day_x >= 23) or (year >= 2016 and month >= 7) or (year >= 2017):
                    df_file_daCAP = df_file.loc[df_file['PTID'] == zoneid, ['NYCA Regulation Capacity ($/MWHr)']]
                    daCAP = np.append(daCAP, df_file_daCAP.values)
                elif (year >= 2001 and month >= 10 and day_x >= 0) or (year >= 2001 and month >= 11) or \
                     (year >= 2002 and not ((year >= 2016 and month >= 6 and day_x >= 23) or (year >= 2016 and month >= 7) or (year >= 2017))):
                    df_file_daCAP = df_file['East Regulation ($/MWHr)']
                    daCAP = np.append(daCAP, df_file_daCAP.values)
                else:
                    df_file_daCAP = df_file['Regulation ($/MWHr)']
                    daCAP = np.append(daCAP, df_file_daCAP.values)

        if typedat == "lbmp" or typedat == "both":
            # 20170201damlbmp_gen.csv
            # 20170201damlbmp_zone.csv
            # 20170201realtime_gen.csv
            if RT_DAM == "RT" or RT_DAM == "both":
                try:
                    df_rtLBMP = pd.read_csv(fname_path_LBMP_RT, index_col=False)
                except FileNotFoundError:
                    rtLBMP = np.empty([0])
                    logging.warning('read_nyiso_data: RT LMP file missing, returning empty array.')
                    break

                rtLBMP_node_x = df_rtLBMP.loc[df_rtLBMP['PTID'] == nodeid, ['LBMP ($/MWHr)']]
                rtLBMP = np.append(rtLBMP, rtLBMP_node_x.values)


            if RT_DAM == "DAM" or RT_DAM == "both":
                try:
                    df_daLBMP = pd.read_csv(fname_path_LBMP_DA, index_col=False)
                except FileNotFoundError:
                    daLBMP = np.empty([0])
                    logging.warning('read_nyiso_data: DA LMP file missing, returning empty array.')
                    break

                daLBMP_node_x = df_daLBMP.loc[df_daLBMP['PTID'] == nodeid, ['LBMP ($/MWHr)']]
                daLBMP = np.append(daLBMP, daLBMP_node_x.values)

    return daLBMP, rtLBMP, daCAP, rtCAP, rtMOV

#######################################################################################################################

#######################################################################################################################
# SPP
#######################################################################################################################

def read_spp_data(fpath, year, month, node, typedat="both"):
    """"
    Reads the historical LMP, regulation capacity, and regulation service (mileage) prices for the year 'year',
    the month 'month' and for the node 'nodeid'. Returns NumPy ndarrays for those three prices.
    :param fpath: A string containing the path to the relevant historical ancillary services data file.
    :param year: An int corresponding to the year of interest
    :param month: An int corresponding to the month of interest (1: Jan., 2: Feb., etc.)
    :param node: A string with the name of the node in SPP
    :param typedat: xxxxxx xxxxxxx
    :param RT_DAM: xxxxxxxxx xxxx
    :return: daLMP, daMCPRU, daMCPRD: NumPy ndarrays containing hourly LMP as well as regulation up and down prices for the SPP market
    """

    daLMP = np.empty([0])
    daMCPRU = np.empty([0])
    daMCPRD = np.empty([0])

    if isinstance(month, str):
        month = int(month)

    if isinstance(year, str):
        year = int(year)

    ############################################################################################
    # TODO: path_nodes_file is a folder to adjust when integrating it to QuESt
    path_nodes_file = '../../es_gui/apps/data_manager/_static/'
    pathf_nodeszones = os.path.join(fpath, path_nodes_file, 'nodes_spp.csv')
    df_nodes = pd.read_csv(pathf_nodeszones, index_col=False, encoding="cp1252")
    df_nodes_x = df_nodes.loc[df_nodes['Node ID'] == node, :]

    if df_nodes_x.empty:
        print("The node does NOT exists in SPP")
        # raise ValueError('Not a valid bus number!!!')
        return daLMP, daMCPRU, daMCPRD
    else:
        nodetype = df_nodes_x.iloc[0,2]
        if nodetype == 'Location':
            # print('It is a Location node')
            bus_loc = ["location", "SL"]
        elif nodetype == 'Bus':
            # print('It is a Bus node')
            bus_loc = ["bus", "B"]

    # TODO: figure out the reserve zone for each node, for SPP there are 5 reserve zones and there should be a correspondance with the nodes
    ResZone = 1
    ############################################################################################

    # Read only the DA market

    ndaysmonth = calendar.monthrange(year, month)
    ndaysmonth = int(ndaysmonth[1])

    for ix in range(ndaysmonth):
        day_x = ix+1

        fnameLMP_DA = "DA-LMP-{0:s}-{1:d}{2:02d}{3:02d}0100.csv".format(bus_loc[1], year, month, day_x)
        fnameMCP_DA = "DA-MCP-{0:d}{1:02d}{2:02d}0100.csv".format(year, month, day_x)

        fname_path_LMP_DA = os.path.join(fpath, 'LMP', 'DAM', bus_loc[0], str(year), str(month).zfill(2),fnameLMP_DA)
        fname_path_MCP_DA = os.path.join(fpath, 'MCP', 'DAM', str(year), str(month).zfill(2),fnameMCP_DA)

        if typedat == "lmp" or typedat == "both":
            # DA-LMP-B-201707010100.csv
            # DA-LMP-SL-201707010100.csv
            try:
                df_daLMP = pd.read_csv(fname_path_LMP_DA, index_col=False)
            except FileNotFoundError:
                daLMP = np.empty([0])
                logging.warning('read_spp_data: LMP file missing, returning empty array.')
                break

            daLMP_node_x = df_daLMP.loc[df_daLMP['Pnode'] == node, ['LMP']]
            daLMP_node_x.drop_duplicates(inplace=True)
            daLMP = np.append(daLMP, daLMP_node_x.values)
            if daLMP_node_x.empty:
                return np.empty([0]), np.empty([0]), np.empty([0])

        if typedat == "mcp" or typedat == "both":
            # DA-MCP-201707010100.csv
            try:
                df_daMCP = pd.read_csv(fname_path_MCP_DA, index_col=False)
            except FileNotFoundError:
                daMCPRU = np.empty([0])
                daMCPRD = np.empty([0])
                logging.warning('read_spp_data: MCP file missing, returning empty arrays.')
                break

            # print('Warning -reserve zone not figured out!!!')
            daMCPRU_node_x = df_daMCP.loc[df_daMCP['Reserve Zone'] == str(ResZone), ['RegUP']]
            daMCPRD_node_x = df_daMCP.loc[df_daMCP['Reserve Zone'] == str(ResZone), ['RegDN']]

            daMCPRU = np.append(daMCPRU, daMCPRU_node_x.values)
            daMCPRD = np.append(daMCPRD, daMCPRD_node_x.values)

    return daLMP, daMCPRU, daMCPRD


def read_spp_data_old(fpath, year, month, node, typedat="both"):
    """"
    Reads the historical LMP, regulation capacity, and regulation service (mileage) prices for the year 'year',
    the month 'month' and for the node 'nodeid'. Returns NumPy ndarrays for those three prices.
    :param fpath: A string containing the path to the relevant historical ancillary services data file.
    :param year: An int corresponding to the year of interest
    :param month: An int corresponding to the month of interest (1: Jan., 2: Feb., etc.)
    :param node: A string with the name of the node in SPP
    :param typedat: xxxxxx xxxxxxx
    :param RT_DAM: xxxxxxxxx xxxx
    :return: daLMP, daMCPRU, daMCPRD: NumPy ndarrays containing hourly LMP as well as regulation up and down prices for the SPP market
    """

    ############################################################
    path_nodes_file = '../../es_gui/apps/data_manager/_static/'
    pathf_nodeszones = os.path.join(fpath, path_nodes_file, 'nodes_spp.csv')

    ############################################################
    ############################################################

    pathfile_locations = os.path.join(fpath, 'SPP_locations_list.csv')
    df_locations = pd.read_csv(pathfile_locations, index_col=False)

    df_locations_x = df_locations.loc[df_locations['Pnode']== node, :]

    if not df_locations_x.empty:
        print('It is a Location node')
        bus_loc = ["location", "SL"]
        pnode_x = df_locations_x.iloc[0,0]
    else:
        # pathfile_buses = folderfile + 'SPP_buses_list.csv'
        pathfile_buses = os.path.join(fpath, 'SPP_buses_list.csv')
        df_buses = pd.read_csv(pathfile_buses, index_col=False)
        df_buses_x = df_buses.loc[df_buses['Pnode'] == node, :]
        if not df_buses_x.empty:
            print('It is a Bus node')
            bus_loc = ["bus", "B"]
            pnode_x = df_buses_x.iloc[0,0]
        else:
            raise ValueError('Unknown Node!!!')

    # TODO: figure out the reserve zone for each node, for SPP there are 5 reserve zones and there should be a correspondance with the nodes
    # Reserve Zone:
    ResZone = 1


    # Read only the DA market

    ndaysmonth = calendar.monthrange(year, month)
    ndaysmonth = int(ndaysmonth[1])

    daLMP = np.empty([0])
    daMCPRU = np.empty([0])
    daMCPRD = np.empty([0])

    for ix in range(ndaysmonth):
        day_x = ix+1

        fnameLMP_DA = "DA-LMP-{0:s}-{1:d}{2:02d}{3:02d}0100.csv".format(bus_loc[1], year, month, day_x)
        fnameMCP_DA = "DA-MCP-{0:d}{1:02d}{2:02d}0100.csv".format(year, month, day_x)

        fname_path_LMP_DA = os.path.join(fpath, 'LMP', 'DAM', bus_loc[0], str(year), str(month).zfill(2),fnameLMP_DA)
        fname_path_MCP_DA = os.path.join(fpath, 'MCP', 'DAM', str(year), str(month).zfill(2),fnameMCP_DA)

        if typedat == "lmp" or typedat == "both":
            # DA-LMP-B-201707010100.csv
            # DA-LMP-SL-201707010100.csv
            try:
                df_daLMP = pd.read_csv(fname_path_LMP_DA, index_col=False)
            except FileNotFoundError:
                daLMP = np.empty([0])
                logging.warning('read_spp_data: LMP file missing, returning empty array.')
                break

            daLMP_node_x = df_daLMP.loc[df_daLMP['Pnode'] == node, ['LMP']]
            daLMP = np.append(daLMP, daLMP_node_x.values)

        if typedat == "mcp" or typedat == "both":
            # DA-MCP-201707010100.csv
            try:
                df_daMCP = pd.read_csv(fname_path_MCP_DA, index_col=False)
            except FileNotFoundError:
                daMCPRU = np.empty([0])
                daMCPRD = np.empty([0])
                logging.warning('read_spp_data: MCP file missing, returning empty arrays.')
                break

            print('Warning -reserve zone not figured out!!!')
            daMCPRU_node_x = df_daMCP.loc[df_daMCP['Reserve Zone'] == ResZone, ['RegUP']]
            daMCPRD_node_x = df_daMCP.loc[df_daMCP['Reserve Zone'] == ResZone, ['RegDN']]

            daMCPRU = np.append(daMCPRU, daMCPRU_node_x.values)
            daMCPRD = np.append(daMCPRD, daMCPRD_node_x.values)

    return daLMP, daMCPRU, daMCPRD
#######################################################################################################################

#######################################################################################################################
# CAISO
#######################################################################################################################

def read_caiso_data(fpath, year, month, nodeid):
    """"
    Reads the historical LMP, regulation up/down and regulation mileage up/down for the year 'year',
    the month 'month' and for the node 'nodeid'. Returns NumPy ndarrays for those three prices.

    :param fpath: The path to the root of the PJM data directory
    :type fpath: str
    :param year: Year of data to read
    :type year: int or str
    :param month: Month of data to read
    :type month: int or str
    :param nodeid: ID of the node to read
    :type nodeid: str
    :return: daLMP, RegCCP, RegPCP: Hourly LMP and regulation capacity/performance clearing price values.
    :rtype: NumPy ndarrays
    """

    """"
    For CAISO certain prices have:
    _CAISO
    _CAISO_EXP
    _NP26
    _NP26_EXP
    _SP26
    _SP26_EXP

    we only use the _CAISO_EXP ones (for mileage prices they are the only ones)

    AS_CAISO_EXP_RD_CLR_PRC
    AS_CAISO_EXP_RU_CLR_PRC

    AS_CAISO_EXP_RMD_CLR_PRC
    AS_CAISO_EXP_RMU_CLR_PRC
    """

    daLMP = np.empty([0])
    daREGU = np.empty([0])
    daREGD = np.empty([0])
    daRMU = np.empty([0])
    daRMD = np.empty([0])
    RMU_MM = np.empty([0])
    RMD_MM = np.empty([0])
    RMU_PACC = np.empty([0])
    RMD_PACC = np.empty([0])

    if isinstance(month, str):
        month = int(month)

    if isinstance(year, str):
        year = int(year)

    # Names examples:
    # 201601_dalmp_LAKESID2_7_UNITS-APND.csv
    # 201601_asp.csv
    # 201601_regm.csv
    fnameLMP = "{0:d}{1:02d}_dalmp_{2:s}.csv".format(year, month, nodeid)
    fnameASP = "{0:d}{1:02d}_asp.csv".format(year, month)
    fnameMILEAGE = "{0:d}{1:02d}_regm.csv".format(year, month)

    fname_path_LMP = os.path.join(fpath, 'LMP', str(nodeid), str(year), fnameLMP)
    fname_path_ASP = os.path.join(fpath, 'ASP', str(year), fnameASP)
    fname_path_MILEAGE = os.path.join(fpath, 'MILEAGE', str(year), fnameMILEAGE)

    try:
        dfLMP = pd.read_csv(fname_path_LMP, index_col=False)
        daLMP = dfLMP['LMP'].values
    except FileNotFoundError:
        logging.warning \
            (
                'read_caiso_data: No LMP data matching input parameters found, returning empty array. (got {fname}, {year}, {month}, {nodeid})'.format
                (fname=fnameLMP, year=year, month=month, nodeid=nodeid))

    try:
        dfASP = pd.read_csv(fname_path_ASP, index_col=False)
        daREGU = dfASP['AS_CAISO_EXP_RU_CLR_PRC'].values
        daREGD = dfASP['AS_CAISO_EXP_RD_CLR_PRC'].values
        daRMU = dfASP['AS_CAISO_EXP_RMU_CLR_PRC'].values
        daRMD = dfASP['AS_CAISO_EXP_RMD_CLR_PRC'].values

    except FileNotFoundError:
        logging.warning \
            (
                'read_caiso_data: No ASP data matching input parameters found, returning empty array. (got {fname}, {year}, {month})'.format
                (fname=fnameASP, year=year, month=month))

    try:
        dfMIL_ACC = pd.read_csv(fname_path_MILEAGE, index_col=False)
        RMU_MM = dfMIL_ACC['RMU_SYS_MIL_MUL'].values
        RMD_MM = dfMIL_ACC['RMD_SYS_MIL_MUL'].values
        RMU_PACC = dfMIL_ACC['RMU_SYS_PERF_ACC'].values
        RMD_PACC = dfMIL_ACC['RMD_SYS_PERF_ACC'].values

    except FileNotFoundError:
        logging.warning \
            (
                'read_caiso_data: No MILEAGE and PERFORMANCE ACCURACY data matching input parameters found, returning empty array. (got {fname}, {year}, {month})'.format
                (fname=fnameMILEAGE, year=year, month=month))

    return daLMP, daREGU, daREGD, daRMU, daRMD, RMU_MM, RMD_MM, RMU_PACC, RMD_PACC
    # TODO: understand the units of the MILEAGE MULTIPLIERS

#######################################################################################################################

#######################################################################################################################
#######################################################################################################################









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
