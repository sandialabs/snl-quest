# Master branch changelog

## Release 1.0
The official release version of QuESt.

### QuESt
#### QuESt Data Manager
An application for downloading data from RTO/ISO/market operators for use in other QuESt applications.

* Market and operations data for the following RTOs/ISOs are available using the download utility:
    * ERCOT
    * MISO
    * PJM

#### QuESt Valuation
An application for performing energy storage valuation. Using historical data from market area operators, set up and solve optimization problems to estimate an upper bound on the revenue that a energy storage device could have generated over the horizon of the data.

* Features
    * Wizard: a streamlined, guided interface for setting up sets of valuation runs
        * Pick a market area, pricing node, energy storage device, and historical dataset
        * Perform a valuation for the device each month in the set
        * Generate a pro forma report to summarize the findings in a convenient document
    * Single Run: a more flexible interface for setting up valuation runs for one month at a time
        * Offers more customization in terms of energy storage device and simulation parameters than the wizard
    * Batch Runs: an even more flexible interface for setting up large sets of valuation runs
        * Expands upon the wizard, allowing for the selection of multiple months for valuation
        * Perform parameter sweeps to look at the sensitivity of certain device or market parameters
    * Results viewer: a convenient tool for quickly checking your valuation results
        * Plot time series of revenue, state of charge, or scheduled charging/discharging actions
        * View the statistics of electricity prices for each month
        * Export .csv files for external viewing or processing

### Known issues
* An issue where the solver does not exit successfully for certain optimization problems.
* An issue where certain downloaded data may not appear as options for use in QuESt Valuation.
* An issue where results for MISO valuations have constant objective functions leading to trivial optimization problems are obtained when they should be excluded.

## Patch 2018.07.24
Merged WIP of Data Manager.

### QuESt
#### General
* Due to data downloader issues, ISO-NE support will be considered experimental at this time. It will likely be removed from the release version.

#### QuESt Data Manager
* ISO/RTO data downloader general interface has been implemented.
* Temporarily, data will be downloaded to a separate `./data/` directory (rather than `./data_bank/`) for testing and development. Therefore, it will not impact data saved in the old data_bank or operation of the Valuation application.
* ERCOT data downloader has been implemented.
* ISO-NE data downloader has been generally implemented. However, due to connection issues with the API, it is not considered complete.

#### QuESt Valuation
* "Pro forma" report generation from the wizard has been implemented.

### Resolved issues
* An issue where simulations with PJM models would crash the program.
* An issue where exporting to CSV from the results viewer would crash the program.

### Known issues
* ISO-NE API

## Patch 2018.06.22

### QuESt
#### General
* Implemented font and color changes according to graphics design update.
* Added copyright notice to landing screen.

### Resolved issues
* An issue where values set for `fraction_reg_up` and `fraction_reg_down` after ValuationOptimizer object instantiation were being ignored and defaults were being used.

## Patch 2018.06.13

The selected name and tagline QuESt: Optimizing Energy Storage has been implemented. This patch addresses much of the feedback received during R1 of usability testing.

### Valuation Optimizer
* Added check for self-discharge/conversion efficiencies: If value > 1.0, it is interpreted as percentage. Equalities/inequalities still use unit of fractions.
* Added electricity prices to results dataframe.
* Added bad parameter checking.
* Renamed `S_max` to `Energy_capacity`.
* Removed `S_min` in favor of `Reserve_charge_min` (in terms of fraction of energy capacity).
* Renamed `Storage_efficiency` to `Self_discharge_efficiency`.
* Renamed `Conversion_efficiency` to `Round_trip_efficiency`.

### QuESt
#### Codebase
* `main.py` has been moved to the repository root.
* Directory references like `\x\y\z.file` have been changed to `os.path.join(x, y, z.file)` when possible. (.py files)

#### General
* "Select market formulation" has been changed to "Select revenue streams".
* The default and minimum window size has been increased to 1600x900.
* Font sizes have been increased.
* The appearance of spinners/dropdowns have been adjusted to be more recognizable.
* The color, width, and activity behavior of the scroll bar in scroll views have been adjusted for visibility.
* Keyboard shortcuts partially implemented. Enter or NumpadEnter keys can now be used to close most warning popups (typically popups with only a single button for closing them).
* The keyboard shortcut for exiting the application (Esc) has been disabled.
* Efficiencies have been given display units of (%/h) and value ranges have been adjusted accordingly.
* Maximum state of charge has been renamed to "energy capacity (MWh)."
* Added select-all behavior when tabbing among text input fields.

#### Landing screen
* The "About", "Settings", and "Help" buttons on the landing screen have been moved to the top navigation bar.
    * They will remain consistently at the beginning of the navigation button sequence.
    * The "Quit" button has been removed.
* The landing screen layout has been slightly adjusted to increase the call to action for proceeding.

#### Settings
* The "Settings" screen has been converted to a modal view with a sidebar menu interface.
    * It is now accessible from any screen.

#### Single Run
* The parameter entry widget has been changed to a three column grid layout to match the batch runs tool.
* The "run optimization" popup text has been adjusted.
* Interface when completing runs matches that of batch run.
* The node selector interface has been adjusted.

#### Batch Runs
* The look and feel has been adjusted to facilitate the logical order of progression.
    * The month/data and pricing node selection RV's have their alpha values set to 0.05 until both a market area and revenue streams are selected.
        * Changing the market area will reset the alpha values back and reset the revenue stream selection.
* The parameter sweep selection spinner now displays "Select a parameter to sweep" by default.
* A warning now appears if you try to run a batch when anything in the parameter sweep range text input fields is entered but no parameter is specified.
* Upon completion of a batch, a button can take you to the results viewer.

#### Results Viewer
* "View Results" has been renamed to "Results Viewer"
* The "Results Viewer" screen has been redesigned.
    * No axes are displayed until a plot is actually drawn.
    * The toolbar has been condensed.
    * The run selector has been implemented directly into the results viewer interface.
        * The run names contain most information about the specific run, including all parameters set differently from defaults.
        * The hover behavior has been removed.
    * The time selector has been implemented directly into the results viewer interface.
        * Pressing Enter/NumpadEnter after entering into the text inputs now automatically calls Plot/Redraw.
* The plot figure layout has been adjusted.
    * The legend has been moved to outside the plot.
    * In accordance with the run name adjustments, the legend label now displays more information.
        * With the potential of extremely long legend labels, the amount of simultaneous traces that can be comfortably displayed may be affected.
    * All plots have been changed to "stair"/"step" plots.
    * Major grid lines have been implemented.
    * x-axis labels have been changed to "ending hour."
* Additional spacing between legend entries has been added.
* A "Deselect all" button has been added for the run selector.
* Leaving the results viewer completely resets it, including removing the active plot, deselecting any run selections, and reverting time selectors to defaults.
* Added plot options for electricity prices (line and box plots).

#### Wizard
* The sequence of screens has been adjusted.
    * ISO select, rev. stream select, device select, data select, node select -> ISO select, node select, rev. stream select, data select, node select
* The minimum state of charge (MWh) parameter setter has been removed.
* Filter by node name text input has been implemented.
* Node ID and name description has been removed.

#### Report
* The names of reports have been adjusted.
    * Activity (by source) -> Participation (by month)
    * Activity (%, total) -> Participation (total)
    * Report titles and text have been adjusted accordingly.
    * The activity stacked bar chart (non-normalized) has been removed.
* Certain additional words have been bolded in report text.

### Resolved Issues

### Known Issues

## Patch 2018.05.09

### Resolved issues
* An issue where ISO-NE simulations would not properly handle an exception due to an exception class not available in Python 2.x, leading to an UnboundLocalError.

## Patch 2018.05.07

### Systems

#### Software tool
* The summary of selections screen for the valuation wizard has been implemented.

### Resolved issues
* An issue where an ImportError would occur for op_handler when the application was executed outside of an IDE project.

## Patch 2018.05.04

This patch brings an extensive visual design overhaul and a number of redesigned features.

### Systems

#### Valuation Optimizer
* A single "power rating (Q_max)" has been implemented to replace max charge/discharge ratings (Q_r_max and Q_d_max, respectively).
    * Constraints have been replaced accordingly.
* Reserve_charge and Reserve_reg parameters have been split into scalar parameters.
    * Reserve_charge_min, Reserve_charge_max, Reserve_reg_min, Reserver_reg_max

#### Data
* The node list for ISO-NE has been reduced to 8 "zones."
* April 2015-November 2017 have been added as options for ISO-NE.
* PJM for H2 2017 has been added. Options for it in the GUI have been added as well.
* PJM and MISO price node selection has been reduced.

#### Software tool
* Compatibility for Python versions prior to 3.0 will no longer be checked.
* New fonts and palette implemented. Subject to change as software branding is developed.
* Animations and transitions have been generally sped up.
* Numerous "content definitions" that were previously hard-coded have been factored out into definition .json files (/es_gui/apps/valuation/definition/). This is aimed at centralizing content changes; e.g., if new sets of historical data are added, we can update all the UI changes by adjusting these definitions, rather than changing hardcoded values in numerous files.

* The landing/index screen has been redesigned.
* The help link has been removed, pending an overhaul.
* The about screen has been redesigned into a popup.
* The welcome splash screen has been removed.
* The settings panel has been updated.
    * Removed setting regarding welcome splash screen.
    * Added category headers.
    * Added settings regarding the Valuation data cache.

* ValuationDMS object persistence has been implemented. This allows for the preservation of the ValuationDMS's loaded data, even when the software tool has been closed and reopened. The maximum size of the persisting object, as well as the feature as a whole, can be adjusted in the settings panel.

NOTE: This object is stored as a pickle (/es_gui/valuation_dms.p) and is not compatible between Python versions. If you encounter errors upon software initialization regarding inability to read the pickle, delete the file.

* Several visual design adjustments to the Valuation Wizard have been made.
* Selection of "revenue streams" has become selection of "market formulation."

* A "ValuationOptimizationHandler" class has been implemented. This class consolidates a lot of behavior that was spread across numerous objects. Its function is to receive sets of instructions and interpret them to load the appropriate data and create and solve the ValOptimizer models as requested. It also handles access to solved models.
    * Essentially, other objects just need to generate the instructions and send it to the ValOpHandler. It's the ValOpHandler's responsibility to handle interactions with the DMS and ValOptimizer instances. This is also aimed at centralizing content-specific changes; e.g., if a new market type is implemented in ValOptimizer, only the ValOpHandler needs to know how to use it.

* The Batch Runs screen has been redesigned.
    * Market-specific "static" parameter input fields have been implemented.

* The View Results screen has been adjusted.
    * Selecting a data type to display no longer automatically redraws the plot.
    * Closing the "time selector" popup no longer automatically redraws the plot.
    * "Plot/Redraw" must be pressed to update the graph.

* The Load Data screen has been adjusted.
    * Arrow buttons have been added.
    * Loading data is no longer actually handled on this screen.
    * It has been renamed "Select Data" in the GUI to reflect these changes.

* The Set Parameters screen has been redesigned.
    * The parameters displayed dynamically change when entering the screen, based on the market area selected in the Load Data screen.
    * No button required to explicitly set values.

* The flow of the single month valuation run has been adjusted.
    * The valuation run that is performed is based on whatever is displayed in the UI upon execution. The UI does not reset after execution.
    * Due to back end changes, background threading of certain tasks has been removed.

* The menu structure of the Energy Storage Valuation application has been adjusted.
    * The landing screen presents three options for simulation: Wizard, Single Run, and Batch Runs. It presents one option for analysis: View Results.
    * Batch Runs and Wizard lead directly to their interfaces.
    * Single Run leads directly to Select Data and only links to Set Parameters and View Results.

### Resolved issues
* An issue where the run selector on the View Results screen would fail to identify that runs have been selected for viewing.
* An issue where the description text for the activity donut report chart would not be fully displayed.

## Patch 2018.04.06

NOTE: If you experience import errors, try clearing your compiled Python files (*.pyc). In PyCharm, you can do this by right-clicking the top level directory in the project viewer and clicking "Clean Python Compiled Files."

### Systems

* Relative imports for package modules have been reimplemented.
* Fixes for compatibility with Python 3.4 have been implemented.
    * RC: I cannot get Kivy to run in Python 3.6 on OSX...

### Resolved issues
* An issue where get_node_name() under ValuationDMS would return None, causing the app to crash when loading the node list in Wizard in Python 3.x.
* An issue where loading certain charts in the Wizard would cause the app to crash due to dictionary changes in Python 3.x.
* An issue where the app would fail to initialize due to a non-Python 3.x-compliant print() statement in the hoverable module.

### Known issues
* An issue where LMP data for MISO nodes in the node list is not available.
* An issue where the wizard execute screen says it is finished when it is not.

## Patch 2018.04.05

NOTE: If you experience import errors, try clearing your compiled Python files (*.pyc). In PyCharm, you can do this by right-clicking the top level directory in the project viewer and clicking "Clean Python Compiled Files."

### Systems

#### Optimizer
The class formerly known as Optimizer has been redesigned for future extensibility. The focus was on minimal interface design, encapsulation, and designing for inheritance.

* Factored out an abstract base class (ABC) "Optimizer"; this ABC is intended to serve as a template class to inherit from when creating future Pyomo model frameworks. This ABC lives in `/es_gui/tools/optimizer.py`.
* Renamed the class formerly known as Optimizer to "ValuationOptimizer." It resides in `/es_gui/tools/valuation/valuation_optimizer.py`
* Created test class for ValuationOptimizer. You can run a test by running `valuation_optimizer.py`. It runs a couple of optimizations and gives you a value to check the result against.
* The market_type 'arbreg' has been renamed 'ercot_arbreg'.
* The var, param, and validate_attr modules have been encapsulated into the ValuationOptimizer class.
* The public interface of the class has been streamlined according to minimal interface design. Parameters have been named/renamed as follows:
    * lmp --> price_electricity
    * ru --> price_reg_up
    * rd --> price_reg_down
    * regCCP --> price_reg_capacity
    * regPCP --> price_reg_performance
    * cost_charge (NEW)
    * cost_discharge (NEW)
    * regA_mi --> mileage_slow
    * regD_mi --> mileage_fast
    * mi_ratio --> mileage_ratio
    * gamma_ru --> fraction_reg_up
    * gamma_rd --> fraction_reg_down
    * Gamma_s --> Storage_efficiency
    * Gamma_c --> Conversion_efficiency
    * Reserve_reg (NEW)
    * Reserve_charge (NEW)
    * Make_whole (NEW)
    * time_interval --> time

* Names were selected to be generic and minimize conflation with market-specific terminology.
* Regulation prices are matched to the appropriate interface. For example, PJM's RMCCP is matched to price_reg_capacity. MISO's RegMCP is matched to price_reg_performance. (RC: I picked this because it's the only reg. price and it's multiplied by Perf_score in the revenue calculation.)
* The matching of Val.Opt. interface parameters to Pyomo model attributes is done in the instantiate_model class method.
* At the moment, the actual parameter names used in the Pyomo expressions are largely unchanged. These are implementation details that can be changed at any time.
* Greek letter names have been removed from the code. These symbols should be used for documentation/publications as necessary.
* Cost of charging/discharging parameters have been declared, but not yet implemented.
* Reserve_reg and Reserve_charge parameters have been implemented. These adjust the state of charge limits at each time step. Reserve_reg is defined in terms of fractions of the regulation bid at the current time step. Reserve_charge is defined in terms of fractions of S_max. These parameters are provided as length-2 array-likes (tuple, list, ...). From the IEEE Access article, Reserve_reg is roughly equivalent to ($`a_0`$, $`b_0`$) and Reserve_charge is roughly equivalent to ($`a_1`$, $`b_1`$).
* `block.py` and `constraints_optimizer.py` have been rolled into `constraints.py`. The functionality of block was rolled into a class "ExpressionsBlock," an object that interacts with the Val.Opt. object. The constraint and objective functions are functions in the `constraints.py` module.
* Console output from the Pyomo solver has been eliminated.
* Logging functionality has been introduced to Val.Opt.

#### ValuationDMS
* Logging functionality has been introduced to Val.Opt.

#### App
* Integrated Val.Opt. changes.
* Removed placeholder accordion items from Index.
* Changed About screen to a modal view and changed its content.
* Removed "Quick Demo" button from the Valuation - Advanced screen.
* Adjusted size_hint_x values in View Results screen to reduce clipping.
* Added two more energy storage device templates to the Wizard.
* The ValuationDMS has been moved to be a property of the Valuation - Home screen.

### Resolved issues
* An issue where "regulation capacity offered" was incorrectly calculated as "reg_up - reg_down" in ERCOT arbreg plots in the View Results screen.
* An issue where a blank field in "Select time" in "View Results" screen can be entered, causing the app to crash.
* An issue where View Screen's toolbar would remain disabled after selecting runs to view.

### Known issues
* An issue where LMP data for MISO nodes in the node list is not available.
* An issue where the wizard execute screen says it is finished when it is not.

## Patch 2018.03.29

### Systems

#### Optimizer
* Overloaded gamma_ru and gamma_rd to accept single value or arrays.
    * If single value, it is constant over entire time horizon.
    * If no value is provided, a default is used (defined in param.py).
* Added iso_ne_pfp market_type.
* Removed redundant constraint definitions (state of charge min/max).
* Added results and net_revenue properties. results gives you a DataFrame representation of the solution. net_revenue gives you the objective function value.

#### ValuationDMS
* Reworked ERCOT to use datafiles from their website ("historical").
* Transitioning out of nested dictionary setup of DMS. Will use a single key that can be parsed for utility function arguments.

#### Data
* Added ERCOT data from 2013-2017. Replaced the 2011 data.
* Added ISONE zonal data for 2013-2017.

#### App
* Integrated ISO-NE into advanced, wizard, and report sections.
* Updated for new ERCOT data.
* Changed ISO select buttons to be in a grid layout to fix their dimensions.

### Resolved issues
* An issue where MISO data in 12/2014 was incomplete or corrupted.

### Known issues
* An issue where LMP data for MISO nodes in the node list is not available.
* An issue where the wizard execute screen says it is finished when it is not.