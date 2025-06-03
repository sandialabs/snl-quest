import json
import calendar
import collections
import copy
import os

import pandas as pd

dirname = os.path.dirname(__file__)

IMPLEMENTED_ISO = ['PJM', 'ERCOT', 'MISO', 'ISO-NE']

MONTHS = {}

MONTHS['PJM'] = collections.OrderedDict()
MONTHS['PJM']['2016'] = [repr(n) for n in range(6, 13)]
MONTHS['PJM']['2017'] = [repr(n) for n in range(1, 13)]

MONTHS['ERCOT'] = collections.OrderedDict()
MONTHS['ERCOT']['2013'] = [repr(n) for n in range(1, 13)]
MONTHS['ERCOT']['2014'] = [repr(n) for n in range(1, 13)]
MONTHS['ERCOT']['2015'] = [repr(n) for n in range(1, 13)]
MONTHS['ERCOT']['2016'] = [repr(n) for n in range(1, 13)]
MONTHS['ERCOT']['2017'] = [repr(n) for n in range(1, 13)]

MONTHS['MISO'] = collections.OrderedDict()
MONTHS['MISO']['2014'] = [repr(n) for n in range(1, 13)]
MONTHS['MISO']['2015'] = [repr(n) for n in range(1, 13)]

MONTHS['ISO-NE'] = collections.OrderedDict()
MONTHS['ISO-NE']['2015'] = [repr(n) for n in range(4, 13)]
MONTHS['ISO-NE']['2016'] = [repr(n) for n in range(1, 13)]
MONTHS['ISO-NE']['2017'] = [repr(n) for n in range(1, 12)]

# Months by ISO.
with open(os.path.join(dirname, 'months.json'), 'w') as fp:
    json.dump(MONTHS, fp, indent=True)

# Node IDs and names.
nodes = dict()

node_sheets = pd.read_excel('data_bank/zoneid.xlsx', sheet_name=IMPLEMENTED_ISO)

for iso in IMPLEMENTED_ISO:
    nodes[iso] = {row[0]: {'name': row[1], 'ID': row[0]}
                  for row in zip(node_sheets[iso]['Node ID'], node_sheets[iso]['Node Name'])}

with open(os.path.join(dirname, 'nodes.json'), 'w') as fp:
    json.dump(nodes, fp, indent=True)

# Specify the descriptions for each of the revenue streams for each ISO/market area.
rev_streams_dict = dict()

rev_streams_dict['PJM'] = {
    'Arbitrage':
         {'market type': 'arbitrage',
     'desc': 'Arbitrage generally refers to the buying and selling of electrical energy to generate revenue. Prices are based on day-ahead locational marginal pricing (LMP). The differences between day-ahead and real-time LMP are not considered.'},
    'Arbitrage and regulation':
         {'market type': 'pjm_pfp',
     'desc': 'In PJM, frequency regulation services are compensated with a pay-for-performance model. Both fast and slow regulation signals are given. Remuneration for faster devices that are able to more closely follow the fast signal is available. However, compensation based on regulation capacity offered is also available.'
          }
}

rev_streams_dict['ERCOT'] = {
    'Arbitrage':
        {'market type': 'arbitrage',
     'desc': 'Arbitrage generally refers to the buying and selling of electrical energy to generate revenue. Prices are based on day-ahead locational marginal pricing (LMP). The differences between day-head and real-time LMP are not considered.'},
    'Arbitrage and regulation':
        {'market type': 'ercot_arbreg',
     'desc': 'In ERCOT, frequency regulation services are compensated for by the amount of regulation up or down capacity that is offered on a per MW basis. There is no guarantee that the entirety of the capacity that is bid into the market is actually deployed; this is modeled using regulation efficiency fractions. There are two separate regulation capacity products, but there is no credit based on device performance.'}
}

rev_streams_dict['MISO'] = {
    'Arbitrage':
        {'market type': 'arbitrage',
     'desc': 'Arbitrage generally refers to the buying and selling of electrical energy to generate revenue. Prices are based on day-ahead locational marginal pricing (LMP). The differences between day-head and real-time LMP are not considered.'},
    'Arbitrage and regulation':
        {'market type': 'miso_pfp',
     'desc': 'abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz'}
}

rev_streams_dict['ISO-NE'] = {
    'Arbitrage':
        {'market type': 'arbitrage',
     'desc': 'Arbitrage generally refers to the buying and selling of electrical energy to generate revenue. Prices are based on day-ahead locational marginal pricing (LMP). The differences between day-head and real-time LMP are not considered.'},
    'Arbitrage and regulation':
        {'market type': 'isone_pfp',
     'desc': 'abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz'}
}

with open(os.path.join(dirname, 'rev_streams.json'), 'w') as fp:
    json.dump(rev_streams_dict, fp, indent=True)


# Specify the sets of historical data for each ISO/market area.
def gen_my_tuples(code, year_ending):
    # generates list of (month, year) tuples based on code and year_ending

    if code == 'Q1':
        return [(str(m), str(year_ending)) for m in [1, 2, 3]]
    elif code == 'Q2':
        return [(str(m), str(year_ending)) for m in [4, 5, 6]]
    elif code == 'Q3':
        return [(str(m), str(year_ending)) for m in [7, 8, 9]]
    elif code == 'Q4':
        return [(str(m), str(year_ending)) for m in [10, 11, 12]]
    elif code == 'H1':
        return [(str(m), str(year_ending)) for m in range(1, 7)]
    elif code == 'H2':
        return [(str(m), str(year_ending)) for m in range(7, 13)]
    elif code == 'CY':
        return [(str(m), str(year_ending)) for m in range(1, 13)]
    elif code == 'FY':
        return [(str(m), str(year_ending-1)) for m in range(10, 13)]+[(str(m), str(year_ending)) for m in range(1, 10)]


def gen_list(code, year_ending, iso):
    return [{'name': ' '.join([y, m]), 'month': m, 'year': y, 'iso': iso} for (m, y) in gen_my_tuples(code, year_ending)]

hist_data_dict = dict()

hist_data_dict['PJM'] = {
    '2016-2017':
        [{'name': ' '.join([str(y), str(m)]), 'month': str(m), 'year': str(y), 'iso': 'PJM'} for (m, y) in [(6, 2016), (7, 2016), (8, 2016), (9, 2016), (10, 2016), (11, 2016), (12, 2016), (1, 2017), (2, 2017), (3, 2017), (4, 2017), (5, 2017),]],
    'CY 2017': gen_list('CY', 2017, 'PJM'),
}

hist_data_dict['ERCOT'] = {
    'CY 2013': gen_list('CY', 2013, 'ERCOT'),
    'CY 2014': gen_list('CY', 2014, 'ERCOT'),
    'CY 2015': gen_list('CY', 2015, 'ERCOT'),
    'CY 2016': gen_list('CY', 2016, 'ERCOT'),
    'CY 2017': gen_list('CY', 2017, 'ERCOT'),
}

hist_data_dict['MISO'] = {
    'CY 2014': gen_list('CY', 2014, 'MISO'),
    'CY 2015': gen_list('CY', 2015, 'MISO'),
    'FY 2015': gen_list('FY', 2015, 'MISO'),
}

hist_data_dict['ISO-NE'] = {
    'H2 2015': gen_list('H2', 2015, 'ISO-NE'),
    'CY 2016': gen_list('CY', 2016, 'ISO-NE'),
    'H1 2017': gen_list('H1', 2017, 'ISO-NE'),
}

with open(os.path.join(dirname, 'hist_data.json'), 'w') as fp:
    json.dump(hist_data_dict, fp, indent=True)

# All available months and years of historical data for each ISO.
hist_data_all = dict()

for iso in IMPLEMENTED_ISO:
    mmyy_list = []

    for year, month_list in MONTHS[iso].items():
        for month in month_list:
            tmp_entry = {'name': ' '.join([year, calendar.month_name[int(month)]]),
                         'month': month,
                         'year': year,
                         'iso': iso}

            mmyy_list.append(tmp_entry)

    hist_data_all[iso] = mmyy_list

with open(os.path.join(dirname, 'hist_data_all.json'), 'w') as fp:
    json.dump(hist_data_all, fp, indent=True)

# Specify the different adjustable parameters in a list of dictionaries.
# name: The string used for the descriptor label
# attr name: The class attribute name. Used as attribute name for WizardDeviceParameterWidget to reference the associated WizardDeviceParameterRow. Also matches the attributes in the Optimizer() class.
# default, min, max, step: Associated with the param_slider widget. min, max, and step describe the slider range and resolution and default sets the initial value of the slider.
params = [{'name': 'self-discharge efficiency (%/h)',
           'attr name': 'Self_discharge_efficiency',
           'max': 100,
           'default': 100,
           'step': 1},
          {'name': 'round trip efficiency (%)',
           'attr name': 'Round_trip_efficiency',
           'max': 100,
           'default': 100,
           'step': 1},
        #   {'name': 'minimum state of charge (MWh)',
        #    'attr name': 'S_min',
        #    'max': 100,
        #    'default': 0,
        #    'step': 1},
          {'name': 'energy capacity (MWh)',
           'attr name': 'Energy_capacity',
           'max': 100,
           'default': 10,
           'step': 1},
          {'name': 'power rating (MW)',
           'attr name': 'Power_rating',
           'max': 100,
           'default': 10,
           'step': 1},
          ]

with open(os.path.join(dirname, 'device_param.json'), 'w') as fp:
    json.dump(params, fp, indent=True)

# Specify the different energy storage device templates.
# name: The string used for the text on the WizardDeviceTileButton.
# desc: The string used in the description of the device.
# parameters: A dictionary with (key, value) pairs describing the parameters of the template. The keys match the attribute names of each of the parameters. The values are the parameter slider values that will be set for the matching key.
device_list = [
               {'name': 'Li-ion Battery',
                'desc': 'Modeled after the Notrees Battery Storage Project in western TX.',
                'parameters': {'Self_discharge_efficiency': 100,
                               'Round_trip_efficiency': 90,
                               'Energy_capacity': 24,
                               'Power_rating': 36}},
               {'name': 'Advanced Lead-acid Battery',
                'desc': 'Modeled after the Kaheawa Wind Power Project II storage system in Maalea, HI.',
                'parameters': {'Self_discharge_efficiency': 99,
                               'Round_trip_efficiency': 95,
                               'Energy_capacity': 7.5,
                               'Power_rating': 10}},
               {'name': 'Flywheel',
                'desc': 'Modeled after the Beacon Power facility in Hazle Township, PA.',
                'parameters': {'Self_discharge_efficiency': 98,
                               'Round_trip_efficiency': 85,
                               'Energy_capacity': 5,
                               'Power_rating': 20}},
               {'name': 'Vanadium Redox Flow Battery',
                'desc': 'Modeled after the Minamihayakita Transformer Station storage system in Abira-chou, Hokkaido, Japan.',
                'parameters': {'Self_discharge_efficiency': 80,
                               'Round_trip_efficiency': 85,
                               'Energy_capacity': 60,
                               'Power_rating': 15}},
               {'name': 'Li-Iron Phosphate Battery',
                'desc': 'Modeled after the Jake Energy Storage Center in Joliet, IL.',
                'parameters': {'Self_discharge_efficiency': 100,
                               'Round_trip_efficiency': 93,
                            #    'S_min': 0,
                               'Energy_capacity': 7.8,
                               'Power_rating': 19.8}},
               ]

with open(os.path.join(dirname, 'device_list.json'), 'w') as fp:
    json.dump(device_list, fp, indent=True)


# Model parameters.

model_params_common = [{'name': 'self-discharge efficiency (%/h)',
                        'attr name': 'Self_discharge_efficiency',
                        'max': 1,
                        'default': 100},
                       {'name': 'round trip efficiency (%)',
                        'attr name': 'Round_trip_efficiency',
                        'max': 1,
                        'default': 100},
                       {'name': 'energy capacity (MWh)',
                        'attr name': 'Energy_capacity',
                        'default': 5},
                       {'name': 'power rating (MW)',
                        'attr name': 'Power_rating',
                        'default': 20},
                       {'name': '% of capacity reserved for discharging',
                        'attr name': 'Reserve_charge_min',
                        'default': 0},
                       {'name': '% of capacity reserved for charging',
                        'attr name': 'Reserve_charge_max',
                        'default': 0},
                       {'name': '% of reg. bid reserved for discharging',
                        'attr name': 'Reserve_reg_min',
                        'default': 0},
                       {'name': '% of reg. bid reserved for charging',
                        'attr name': 'Reserve_reg_max',
                        'default': 0},

                      ]

model_params = dict()

for iso in IMPLEMENTED_ISO:
    tmp_list = copy.deepcopy(model_params_common)

    if iso in {'PJM', 'MISO', 'ERCOT', 'ISO-NE'}:
        tmp_list.append({'name': 'frac. of reg. up capacity deployed',
                         'attr name': 'fraction_reg_up',
                         'default': 0.25})

        tmp_list.append({'name': 'frac. of reg. down capacity deployed',
                         'attr name': 'fraction_reg_down',
                         'default': 0.25})

    if iso in {'PJM', 'MISO'}:
        tmp_list.append({'name': 'performance score',
                         'attr name': 'Perf_score',
                         'default': 0.95})

    if iso in {'MISO'}:
        tmp_list.append({'name': 'make whole',
                         'attr name': 'Make_whole',
                         'default': 0.03})

    model_params[iso] = tmp_list

with open(os.path.join(dirname, 'model_params.json'), 'w') as fp:
    json.dump(model_params, fp, indent=True)