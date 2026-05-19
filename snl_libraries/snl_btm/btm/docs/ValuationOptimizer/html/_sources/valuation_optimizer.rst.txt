ValuationOptimizer
==================

The :py:class:`~.valuation_optimizer.ValuationOptimizer` class is a wrapper class for building and solving Pyomo ConcreteModels for energy storage valuation. It extends the abstract base class :py:class:`~.optimizer.Optimizer`.

In accordance with the Optimizer class design concept, several interfaces and class method are exposed. Keyword arguments at instantiation are provided for describing the model to be created. For example, :py:attr:`~.valuation_optimizer.ValuationOptimizer.market_type` is a string property for determining which model (equations and constraints) to use; it may be specified at object instantiation or afterwards through the property setter. The interfaces are typically for providing data in array-like objects, such as assigning a NumPy array of locational marginal prices (LMP) to :py:attr:`~.valuation_optimizer.ValuationOptimizer.price_electricity`. While specific terminology may vary among market models, the most appropriate property interface should be used. For example, even if an ISO calls a type of data "LMP" while another calls it "LBMP", they should both use the :py:attr:`~.valuation_optimizer.ValuationOptimizer.price_electricity` interface. What happens under the hood to the data that is provided through that interface should not concern the end user; whether the resulting data is assigned to a Pyomo Parameter named ``model.lmp`` or ``model.lbmp`` is merely an implementation detail.

Usage
^^^^^

Creating an instance::

   from valuation_optimizer import ValuationOptimizer

   my_op = ValuationOptimizer()

No arguments or keyword arguments are required at initialization. To specify an optimization model/market type::

   my_op = ValuationOptimizer(market_type='miso_pfp')

This is exactly equivalent to::

   my_op = ValuationOptimizer()
   my_op.market_type = 'miso_pfp'

The available ``market_type`` values are:

============ =========================================
market_type  Description
============ =========================================
arbitrage    Arbitrage only
ercot_arbreg ERCOT arbitrage and frequency regulation
pjm_pfp      PJM arbitrage and frequency regulation
miso_pfp     MISO arbitrage and frequency regulation
isone_pfp    ISO-NE arbitrage and frequency regulation
============ =========================================

Data can be provided at instantiation::

   lmp = get_lmp(month, year, node_id)  # obtain array-like of electricity price data through some means

   my_op = ValuationOptimizer(price_electricity=lmp)

Or afterwards::

   lmp = get_lmp(month, year, node_id)  # obtain array-like of electricity price data through some means

   my_op = ValuationOptimizer()
   my_op.price_electricity = lmp

Parameters such as ``Energy_capacity`` have default values if not specified, but may also be set using the :py:meth:`~.optimizer.Optimizer.set_model_parameters()` method::

   my_op = ValuationOptimizer()
   my_op.set_model_parameters(Energy_capacity=20)

Or multiple parameters at a time::

   my_op = ValuationOptimizer()
   my_op.set_model_parameters(Energy_capacity=20, Power_rating=10)

Available model parameters are defined in :py:meth:`~.valuation_optimizer.ValuationOptimizer._set_model_param()` method.

========================== ===============================================================================
Attribute name             Description                                            
========================== ===============================================================================
Power_rating               Power rating; equivalently, the maximum energy charged in one hour [MW].                         
R                          Discount/interest rate [hour^(-1)].
Energy_capacity            Energy capacity [MWh].
Self_discharge_efficiency  Fraction of energy maintained over one time period.                                              
Round_trip_efficiency      Fraction of input energy that gets stored over one time period.     
Reserve_reg_min            Fraction of q_reg bid to increase state of charge minimum by.                                  
Reserve_reg_max            Fraction of q_reg bid to decrease state of charge maximum by.
Reserve_charge_min         Fraction of energy capacity to increase state of charge minimum by.
Reserve_charge_max         Fraction of energy capacity to decrease state of charge maximum by.
State_of_charge_init       Initial state of charge [MWh], defaults to the amount reserved for discharging.
fraction_reg_up            Fraction of regulation up bid actually deployed.
fraction_reg_down          Fraction of regulation down bid actually deployed.
Perf_score                 Performance score.
Make_whole                 Make whole parameter (MISO).
========================== ===============================================================================

After assigning data and model parameter values to your heart's content, you may decide it's time to actually solve the mathematical program and get the answers that you seek. There are two ways to do so. One, you can use the shortcut :py:meth:`~.optimizer.Optimizer.run()` method::

   # Assume my_op is fully populated with whatever data is required.
   results_df, gross_revenue = my_op.run()

The alternative way is to essentially do what :py:meth:`~.optimizer.Optimizer.run()` is doing::

   # Assume my_op is fully populated with whatever data is required.
   my_op.instantiate_model()
   my_op.populate_model()
   my_op.solve_model()  # Solves model

   results_df = my_op.results
   results_df, gross_revenue = my_op.get_results()

Adding capabilities
^^^^^^^^^^^^^^^^^^^

ValuationOptimizer is designed for energy storage valuation using the discrete time, energy-based models described in :ref:`op_model_desc`. New types of analysis or models likely warrant a new class design using the Optimizer design pattern. The addition of new market types within this paradigm can justify capability expansion. Here are the changes that must be done:

- A unique ``market_type`` indicator string will need to be selected.
- New properties for class interface may need to be defined. It is **preferred** that existing interfaces be reused as much as possible. Conversion from class interface attributes to Pyomo parameters is done in :py:meth:`~.valuation_optimizer.ValuationOptimizer.instantiate_model()`; by example, different Pyomo equation notation variables can make use of the same class properties.
- New parameters or decision variables may be defined in :py:meth:`~.valuation_optimizer.ValuationOptimizer._set_model_param()` and :py:meth:`~.valuation_optimizer.ValuationOptimizer._set_model_var()`. Again, reusing existing parameters and variables is **preferred**.
- Results processing case must be added in :py:meth:`~.valuation_optimizer.ValuationOptimizer._process_results()` for computing results of interest.
- New constraint and objective expressions must be added to the :py:mod:`~.constraints` module.

  - A case and associated methods must be added to the :py:class:`~.constraints.ExpressionsBlock` class.
  - "Generic" constraints (common to other models) should be reused if possible.
  - New functions of creating ``Expression`` or ``Constraint`` Pyomo objects are added at the module level.

.. automodule:: valuation_optimizer
   :members: