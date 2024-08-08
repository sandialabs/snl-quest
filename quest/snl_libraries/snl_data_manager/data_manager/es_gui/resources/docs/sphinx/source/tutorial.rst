Tutorial
========

This application was designed to be with a mouse and keyboard at a minimum resolution of 960x540 pixels in a horizontal orientation. You may expand the window or even run it full screen if you wish.

.. note::
    You may press the Esc key at any time to close the application.


Home
----

.. figure:: images/tutorial/index_01.png
    :width: 800px
    :align: center
    :figclass: align-center

    The home screen.

Upon opening the application, you are greeted with the home screen. This is the top level of the application where you can select among the different tools available for use. Clicking on each title opens the accordion to reveal the item, including its description and the large tile button to take you to the sub-application.

.. figure:: images/tutorial/index_02.png
    :width: 800px
    :align: center
    :figclass: align-center

    Clicking on a title in the accordion reveals its contents. Clicking on the large tile button takes you to the sub-application.

The navigation bar at the top is used to quickly navigate around the application. The left button, the icon, is used to "go up one level" from the current screen. The text buttons aligned on the right dynamically change depending on what part of the application you are on and help you navigate among that section's functions. The "home" button will always take you back to this screen.

Settings
--------

From the home screen you can also access the application settings from the bottom button.

.. figure:: images/tutorial/settings_01.png
    :width: 800px
    :align: center
    :figclass: align-center

    The settings screen.

Here is where a number of settings that globally affect the application can be configured:

* **Optimization solver**: Selects the solver that Pyomo will use to solve its models.
* **Show welcome screen**: Show the welcome splash screen upon opening the application.

.. note::

    On desktop, you may also access this menu at any time with the F1 key.

Changing any of these settings, unless otherwise stated, will take effect immediately. Additionally, these settings will persist upon closing the application.

Energy Storage Valuation
------------------------

The energy storage valuation tool uses historical data to estimate the value that a particular energy storage device can provide. A device with perfect foresight can operate to maximize revenue given a particular market structure. This tool solves for the optimal policy and the resulting revenue is a useful upper bound on the value of the device. The general flow for using this tool is as follows:

#. Load the appropriate historical data.

    #. Select an ISO/market for the device.
    #. Select the type of revenue streams to operate on.
    #. Select the year and month of historical data to study.
    #. Select the pricing node where the device is located.

#. Define the parameters of the energy storage device and optimization routine.

    #. Device parameters: storage and conversion efficiencies, minimum/maximum state of charge, etc.
    #. Optimization parameters: discount/interest rate, decision time step size, etc.

#. Run the optimization by building the Pyomo model as defined by the above and solving the mathematical program.

#. Analyze the results.

.. figure:: images/tutorial/valuation_01.png
    :width: 800px
    :align: center
    :figclass: align-center

    The valuation home screen.

Upon entering the valuation sub-application, these four parts are defined in four distinct tile buttons. Clicking on any of them will take you to the appropriate function.

.. note:: The navigation bar changes upon entering this area to allow quick access to each function from within any of the related screens.

Load data
^^^^^^^^^

.. figure:: images/tutorial/valuation_02.png
    :width: 800px
    :align: center
    :figclass: align-center

    The load data screen.

A number of input widgets in logical progression from left to right are displayed on the bottom toolbar. Clicking the "Select Market Area" spinner reveals the market area choices, corresponding to the displayed map. Selecting a market area changes the text of the spinner and filters the available choices for the next spinner, "Select Data Type." Similarly, the choices for selecting year and month are downselected based on previous choices. The "Node ID" field may be used in two ways. If you already know the Node ID used in the data, you may enter it into the text input field directly. If you are unsure if the exact name or just want to explore the choices, you can click on the spinner and scroll through the available node IDs.

.. note:: The Node ID in the text input field is what the application will ultimately use when loading data. Selecting from the Node ID spinner automatically populates the text input field.

Regardless of which method you use, once all input widgets have been populated, clicking the "Load Data" loads the appropriate data into memory. Depending on the data selected, it may take some time for the data to be completely processed and loaded.

Set parameters
^^^^^^^^^^^^^^

.. figure:: images/tutorial/valuation_03.png
    :width: 800px
    :align: center
    :figclass: align-center

    The set parameters screen.

A number of text inputs with corresponding descriptions is displayed on this screen. The input fields are automatically populated with valid values that fit constraints on the parameter ranges. The "Set Parameter" button next to each field finalizes the value in the adjacent field.

.. note:: If no parameters are changed on this screen, the initial values are automatically used if the optimization performed.


Run optimization
^^^^^^^^^^^^^^^^

.. figure:: images/tutorial/valuation_04.png
    :width: 800px
    :align: center
    :figclass: align-center

    The run optimization window.

Clicking on "run optimization" from either the valuation home screen or from the navigation bar brings up the run window. If data has not been loaded yet, an error message will be displayed instead. Clicking on "Run" will initiate the optimization routine. While the Pyomo model is being constructed, the application will remain responsive and you may dismiss the window and go to other parts of the application.

.. note:: You can access the "run optimization" window after dismissing it to check on progress at any time while the application is responsive.

After constructing the model, Pyomo will attempt to solve the model. At this time, the application will become unresponsive as the solver is being used. Once the entire process is complete, the "run" window will update to notify you and you may examine your results.

View results
^^^^^^^^^^^^

.. figure:: images/tutorial/valuation_05.png
    :width: 800px
    :align: center
    :figclass: align-center

    The view results screen.

Following the solve process, the Pyomo model updates itself with the decision variables as they were solved. The application provides a number of ways in which you can view your results from this screen. Clicking on the "Select decision variable" opens a spinner in which you may select which decision variable or derived quantity time series that you wish to view. After making a selection, clicking on the "Plot" button generates the corresponding figure. Clicking on the "Save results" button save a ``.png`` copy of the currently displayed figure to the ``results/plots/`` folder in the application directory.

.. note:: Click on the "Plot" button after transforming the application window to redraw the figure.