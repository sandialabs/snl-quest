PV power profiles
=================

The :py:mod:`~.downloaders.pv_power_data` module is for interacting with the `PVWatts API <https://developer.nrel.gov/docs/solar/pvwatts/v6/>`_ to obtain simulated hourly generation profiles of photovoltaic power arrays. 

The following example illustrates how to perform a proper query. The :py:func:`~.downloaders.pv_power_data.get_pv_profile_data` function is used to perform an API query with the given parameters and save the resulting .json to disk.

.. code-block:: python
    :linenos:

    pv_params = {}

    pv_params['dataset'] = 'tmy3'
    pv_params['radius'] = '0'
    pv_params['timeframe'] = 'hourly'
    pv_params['api_key'] =  # Use your NREL Developer Network/OpenEI API key
    pv_params['lat'] = 35.08
    pv_params['lon'] = -106.65
    pv_params['system_capacity'] = 1000
    pv_params['losses'] = 14
    pv_params['azimuth'] = 180
    pv_params['tilt'] = 35.08
    pv_params['array_type'] =  0
    pv_params['module_type'] = 0

    get_pv_profile_data(pv_params, save_path='test_pv.json')

.. automodule:: es_gui.downloaders.pv_power
   :members: