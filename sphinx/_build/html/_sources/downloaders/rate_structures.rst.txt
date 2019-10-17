Utility rate structures
=======================

The :py:mod:`~.downloaders.utility_rates` module is for interacting with the `OpenEI U.S. Utility Rate Database API <https://openei.org/apps/USURDB/>`_ to obtain utility rate structures.

The following example illustrates how to perform a proper query. The :py:func:`~.downloaders.utility_rates.get_utility_rate_structures` function is used to perform an API query.

.. code-block:: python
    :linenos:

    api_key = ''  # Use your OpenEI API key

    # Get the table of utilities in the database
    utility_reference_table, cnx_error_occurred = get_utility_reference_table()

    # Get the EIA ID of an arbitrary utility
    eia_id = str(utility_reference_table.iloc[0]['eiaid'])

    # Get the list of records of rate structures for that utility
    records, connection_error_occurred = get_utility_rate_structures(
        eia_id, 
        api_key
    )

    # Select an arbitrary rate structure
    rate_structure = records[0]

.. automodule:: es_gui.downloaders.utility_rates
   :members: