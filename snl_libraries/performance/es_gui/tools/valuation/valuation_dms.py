from __future__ import absolute_import
import logging
import os
import json

import pandas as pd

from es_gui.tools.dms import DataManagementSystem
from es_gui.tools.valuation.utilities import *


class ValuationDMS(DataManagementSystem):
    """
    A class for managing data for the energy storage valuation optimization functions. Class methods for each type of file to be loaded are included, extending from the get_data() method of the superclass. Each of these methods uses get_data() to retrieve the relevant data and loads the file and adds it to the DMS if the data is not loaded. An optional class method for calling each of the individual data methods can be included to, e.g., form the necessary arguments and return the desired variables.

    :param home_path: A string indicating the relative path to where data is saved.
    """
    def __init__(self, home_path, **kwargs):
        DataManagementSystem.__init__(self, **kwargs)

        self.home_path = home_path

        # with open(os.path.abspath(os.path.join(self.home_path, '..', 'es_gui', 'apps', 'valuation', 'definitions', 'nodes.json')), 'r') as fp:
        #     self.NODES = json.load(fp)

        #self.node_names = pd.read_excel(self.home_path+'nodeid.xlsx', sheetname=None)
        self.delimiter = ' @ '  # delimiter used to split information in id_key

    def get_node_name(self, node_id, ISO):
        """
        Retrieves the node name corresponding to the given node_id using the lookup table loaded during initialization.
        :param node_id: A string or int of a node ID.
        :return: The corresponding node name as a string.
        """
        # TODO: map node_id to node name

        return str(node_id)

        # try:
        #     node_name = self.NODES[ISO][node_id]['name']
        # except KeyError as e:
        #     raise e
        # else:
        #     return node_name

    def get_ercot_spp_data(self, id_key):
        """Retrieves DAM-SPP data for ERCOT."""
        logging.info('DMS: Loading ERCOT DA-SPP')
        try:
            # attempt to access data if it is already loaded
            spp_da = self.get_data(id_key)
        except KeyError:
            # load the data and add it to the DMS

            # deconstruct id_key to obtain args for read function
            spp_da = read_ercot_da_spp(*id_key.split(self.delimiter))
            self.add_data(spp_da, id_key)
        finally:
            return spp_da

    def get_ercot_ccp_data(self, id_key):
        """Retrieves DAM-CCP data for ERCOT."""
        logging.info('DMS: Loading ERCOT DA-CCP')
        try:
            # attempt to access data if it is already loaded
            REGUP = self.get_data(id_key + self.delimiter + 'REGUP')
            REGDN = self.get_data(id_key + self.delimiter + 'REGDN')
        except KeyError:
            # load the data and add it to the DMS

            # deconstruct id_key to obtain args for read function
            REGDN, REGUP = read_ercot_da_ccp(*id_key.split(self.delimiter)[:2])

            self.add_data(REGUP, id_key + self.delimiter + 'REGUP')
            self.add_data(REGDN, id_key + self.delimiter + 'REGDN')
        finally:
            return REGDN, REGUP

    def get_ercot_data(self, year, month, settlement_point):
        # construct file name paths
        path = os.path.join(self.home_path, 'ERCOT')  # path to data_bank root

        if isinstance(month, int):
            month = str(month)

        spp_fpath = os.path.join(path, 'SPP', str(year))
        
        try:
            for filename in os.listdir(spp_fpath):
                if filename.lower().endswith('.xlsx'):
                    fname = filename
        except ValueError as e:
            raise(e)

        spp_fname = os.path.join(spp_fpath, fname)

        ccp_fpath = os.path.join(path, 'CCP', str(year))

        try:
            for filename in os.listdir(ccp_fpath):
                if filename.lower().endswith('.csv'):
                    fname = filename
        except ValueError as e:
            raise(e)

        ccp_fname = os.path.join(ccp_fpath, fname)

        # construct identifier keys
        spp_id = self.delimiter.join([spp_fname, month, settlement_point])
        ccp_id = self.delimiter.join([ccp_fname, month])

        # retrieve data
        spp_da = self.get_ercot_spp_data(spp_id)
        rd, ru = self.get_ercot_ccp_data(ccp_id)

        return spp_da, rd, ru

    def get_pjm_lmp_data(self, *args):
        """Deprecated since 1.0"""
        logging.info('DMS: Loading PJM DA-LMP')
        try:
            # attempt to access data if it is already loaded
            lmp_da = self.get_data(*args)
        except KeyError:
            # load the data and add it to the DMS
            lmp_da = read_pjm_da_lmp(*args)
            self.add_data(lmp_da, *args)
        finally:
            return lmp_da

    def get_pjm_reg_price_data(self, *args):
        """Deprecated since 1.0"""
        logging.info('DMS: Loading PJM regulation prices')
        try:
            # attempt to access data if it is already loaded
            RegCCP = self.get_data(*args+('RegCCP',))
            RegPCP = self.get_data(*args+('RegPCP',))
        except KeyError:
            # load the data and add it to the DMS
            RegCCP, RegPCP = read_pjm_reg_price(*args)
            self.add_data({'RegCCP': RegCCP, 'RegPCP': RegPCP}, *args)
        finally:
            return RegCCP, RegPCP

    def get_pjm_mileage_data(self, *args):
        """Deprecated since 1.0"""
        logging.info('DMS: Loading PJM mileage data')
        try:
            # attempt to access data if it is already loaded
            MR = self.get_data(*args+('MR',))
            RA = self.get_data(*args+('RA',))
            RD = self.get_data(*args+('RD',))
        except KeyError:
            # load the data and add it to the DMS
            MR, RA, RD = read_pjm_mileage(*args)
            self.add_data({'MR': MR, 'RA': RA, 'RD': RD}, *args)
        finally:
            return MR, RA, RD

    def get_pjm_reg_signal_data(self, *args):
        """Deprecated since 1.0"""
        logging.info('DMS: Loading PJM regulation signal')
        try:
            # attempt to access data if it is already loaded
            RUP = self.get_data(*args+('RegUp',))
            RDW = self.get_data(*args+('RegDown',))
        except KeyError:
            # load the data and add it to the DMS
            RUP, RDW = read_pjm_reg_signal(*args)
            self.add_data({'RegUp': RUP, 'RegDown': RDW}, *args)
        finally:
            return RUP, RDW

    def get_pjm_data(self, year, month, nodeid):
        path = os.path.join(self.home_path, 'PJM')
        
        nodeid = str(nodeid)
        year = str(year)
        month = str(month)

        lmp_key = self.delimiter.join([path, year, month, nodeid, 'SPP'])
        mr_key = self.delimiter.join([path, year, month, 'MR'])
        ra_key = self.delimiter.join([path, year, month, 'RA'])
        rd_key = self.delimiter.join([path, year, month, 'RD'])
        rccp_key = self.delimiter.join([path, year, month, 'RegCCP'])
        rpcp_key = self.delimiter.join([path, year, month, 'RegPCP'])

        try:
            # attempt to access data if it is already loaded
            lmp_da = self.get_data(lmp_key)
            MR = self.get_data(mr_key)
            RA = self.get_data(ra_key)
            RD = self.get_data(rd_key)
            RegCCP = self.get_data(rccp_key)
            RegPCP = self.get_data(rpcp_key)
        except KeyError:
            # load the data and add it to the DMS
            lmp_da, MR, RA, RD, RegCCP, RegPCP = read_pjm_data(path, year, month, nodeid)

            self.add_data(lmp_da, lmp_key)
            self.add_data(MR, mr_key)
            self.add_data(RA, ra_key)
            self.add_data(RD, rd_key)
            self.add_data(RegCCP, rccp_key)
            self.add_data(RegPCP, rpcp_key)

        return lmp_da, MR, RA, RD, RegCCP, RegPCP
    
    def get_miso_lmp_data(self, *args):
        """Deprecated since 1.0"""
        logging.info('DMS: Loading MISO DA-LMP')
        try:
            # attempt to access data if is already loaded
            lmp_da = self.get_data(*args)
        except KeyError:
            # load the data and add it to the DMS
            lmp_da = read_miso_da_lmp(*args)
            self.add_data(lmp_da, *args)
        finally:
            return lmp_da

    def get_miso_reg_data(self, *args):
        """Deprecated since 1.0"""
        logging.info('DMS: Loading MISO RegMCP')
        try:
            # attempt to access data if is already loaded
            RegMCP = self.get_data(*args)
        except KeyError:
            # load the data and add it to the DMS
            RegMCP = read_miso_reg_price(*args)
            self.add_data(RegMCP, *args)
        finally:
            return RegMCP

    def get_miso_data(self, year, month, nodeid):
        path = os.path.join(self.home_path, 'MISO')

        year = str(year)
        month = str(month)

        lmp_key = self.delimiter.join([path, year, month, nodeid, 'LMP'])
        regmcp_key = self.delimiter.join([path, year, month, 'MCP'])

        try:
            # attempt to access data if it is already loaded
            lmp_da = self.get_data(lmp_key)
            RegMCP = self.get_data(regmcp_key)
        except KeyError:
            # load the data and add it to the DMS
            lmp_da, RegMCP = read_miso_data(path, year, month, nodeid)

            self.add_data(lmp_da, lmp_key)
            self.add_data(RegMCP, regmcp_key)

        return lmp_da, RegMCP

    ####################################################################################################################

    def get_isone_data(self, year, month, nodeid):
        path = os.path.join(self.home_path, 'ISONE')

        year = str(year)
        month = str(month)

        lmp_key = self.delimiter.join([path, year, month, nodeid, 'LMP'])
        rccp_key = self.delimiter.join([path, year, month, 'RegCCP'])
        rpcp_key = self.delimiter.join([path, year, month, 'RegPCP'])
        mimult_key = self.delimiter.join([path, year, month, 'MiMult'])

        try:
            # attempt to access data if it is already loaded
            lmp_da = self.get_data(lmp_key)
            rccp = self.get_data(rccp_key)
            rpcp = self.get_data(rpcp_key)
            mi_mult = self.get_data(mimult_key)
        except KeyError:
            # load the data and add it to the DMS
            lmp_da, rccp, rpcp, mi_mult = read_isone_data(path, year, month, nodeid)

            self.add_data(lmp_da, lmp_key)
            self.add_data(rccp, rccp_key)
            self.add_data(rpcp, rpcp_key)
            self.add_data(mi_mult, mimult_key)

        return lmp_da, rccp, rpcp, mi_mult

    ####################################################################################################################

    def get_nyiso_data(self, year, month, nodeid):
        path = os.path.join(self.home_path, 'NYISO')

        nodeid = str(nodeid)
        year = str(year)
        month = str(month)

        lbmp_key = self.delimiter.join([path, year, month, nodeid, 'LBMP'])
        rcap_key = self.delimiter.join([path, year, month, 'RegCAP'])

        try:
            # attempt to access data if it is already loaded
            lbmp_da = self.get_data(lbmp_key)
            rcap_da = self.get_data(rcap_key)
        except KeyError:
            # load the data and add it to the DMS
            lbmp_da, lbmp_rt, rcap_da, rcap_rt, rmov_da = read_nyiso_data(path, year, month, nodeid, typedat="both", RT_DAM="DAM")

            self.add_data(lbmp_da, lbmp_key)
            self.add_data(rcap_da, rcap_key)

        return lbmp_da, rcap_da


    def get_spp_data(self, year, month, nodeid):
        path = os.path.join(self.home_path, 'SPP')

        year = str(year)
        month = str(month)

        lmp_key = self.delimiter.join([path, year, month, nodeid, 'LMP'])
        mcpru_key = self.delimiter.join([path, year, month, 'MCPRU'])
        mcprd_key = self.delimiter.join([path, year, month, 'MCPRD'])

        try:
            # attempt to access data if it is already loaded
            lmp_da = self.get_data(lmp_key)
            mcpru_da = self.get_data(mcpru_key)
            mcprd_da = self.get_data(mcprd_key)
        except KeyError:
            # load the data and add it to the DMS
            # lmp_da, MR, RA, RD, RegCCP, RegPCP = read_pjm_data(path, year, month, nodeid)
            lmp_da, mcpru_da, mcprd_da = read_spp_data(path, year, month, nodeid, typedat="both")

            self.add_data(lmp_da, lmp_key)
            self.add_data(mcpru_da, mcpru_key)
            self.add_data(mcprd_da, mcprd_key)

        return lmp_da, mcpru_da, mcprd_da


    def get_caiso_data(self, year, month, nodeid):
        path = os.path.join(self.home_path, 'CAISO')

        year = str(year)
        month = str(month)

        lmp_key = self.delimiter.join([path, year, month, nodeid, 'LMP'])
        aspru_key = self.delimiter.join([path, year, month, 'ASPRU'])
        asprd_key = self.delimiter.join([path, year, month, 'ASPRD'])
        asprmu_key = self.delimiter.join([path, year, month, 'ASPRMU'])
        asprmd_key = self.delimiter.join([path, year, month, 'ASPRMD'])
        rmu_mm_key = self.delimiter.join([path, year, month, 'RMU_MM'])
        rmd_mm_key = self.delimiter.join([path, year, month, 'RMD_MM'])
        rmu_pacc_key = self.delimiter.join([path, year, month, 'RMU_PACC'])
        rmd_pacc_key = self.delimiter.join([path, year, month, 'RMD_PACC'])

        try:
            # attempt to access data if it is already loaded
            lmp_da = self.get_data(lmp_key)
            aspru_da = self.get_data(aspru_key)
            asprd_da = self.get_data(asprd_key)
            asprmu_da = self.get_data(asprmu_key)
            asprmd_da = self.get_data(asprmd_key)
            rmu_mm = self.get_data(rmu_mm_key)
            rmd_mm = self.get_data(rmd_mm_key)
            rmu_pacc = self.get_data(rmu_pacc_key)
            rmd_pacc = self.get_data(rmd_pacc_key)
        except KeyError:
            # load the data and add it to the DMS
            # lmp_da, MR, RA, RD, RegCCP, RegPCP = read_pjm_data(path, year, month, nodeid)
            lmp_da, aspru_da, asprd_da, asprmu_da, asprmd_da, rmu_mm, rmd_mm, rmu_pacc, rmd_pacc = read_caiso_data(path, year, month, nodeid)

            self.add_data(lmp_da, lmp_key)
            self.add_data(aspru_da, aspru_key)
            self.add_data(asprd_da, asprd_key)
            self.add_data(asprmu_da, asprmu_key)
            self.add_data(asprmd_da, asprmd_key)
            self.add_data(rmu_mm, rmu_mm_key)
            self.add_data(rmd_mm, rmd_mm_key)
            self.add_data(rmu_pacc, rmu_pacc_key)
            self.add_data(rmd_pacc, rmd_pacc_key)

        return lmp_da, aspru_da, asprd_da, asprmu_da, asprmd_da, rmu_mm, rmd_mm, rmu_pacc, rmd_pacc

    ####################################################################################################################

if __name__ == '__main__':
    dms = ValuationDMS(save_name='valuation_dms.p', home_path='data')
    
    # # ERCOT - data doesn't exist
    # year = 2010
    # month = 1
    # settlement_point = 'HB_HOUSTON'

    # spp_da, rd, ru = dms.get_ercot_data(year, month, settlement_point)

    # # ERCOT
    # year = 2010
    # month = 12
    # settlement_point = 'HB_HOUSTON'

    # spp_da, rd, ru = dms.get_ercot_data(year, month, settlement_point)

    # PJM
    # year = 2016
    # month = 5
    # nodeid = 1

    # lmp_da, MR, RA, RD, RegCCP, RegPCP = dms.get_pjm_data(year, month, nodeid)

    # MISO
    year = 2015
    month = 3
    nodeid = 'AEC'

    lmp_da, RegMCP = dms.get_miso_data(year, month, nodeid)