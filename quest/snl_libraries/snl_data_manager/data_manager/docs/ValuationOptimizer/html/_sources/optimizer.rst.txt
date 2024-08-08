Optimizer
=========

:py:class:`~.optimizer.Optimizer` is an abstract base class. It is used as a design pattern for framework wrapper classes for creating Pyomo ConcreteModels. The :py:class:`~.valuation_optimizer.ValuationOptimizer` class was the genesis of the design pattern. Eventually, common functionality was factored out of it into the abstract base class Optimizer for future extensibility and class design. For example, wrapper classes for other optimization models (aside from energy storage valuation) can extend the abstract base class.

The concept of the Optimizer class is to abstract away the details of building Pyomo models from the end users. Users supply data and model parameters through the exposed object interfaces and solve and obtain results from the object interface as well. The details of Pyomo model construction and population as well as results processing are handled by class methods. Thus, Pyomo knowledge is not necessary to use the class, but can be used to extend its capabilities.


.. automodule:: optimizer
   :members:
