Constraints
===========

The :py:mod:`~.constraints` module is for defining sets of Pyomo expressions and constraints. Sets of objective function expressions and constraints are defined a switch-case style in the :py:class:`~.constraints.ExpressionsBlock` class with the :py:meth:`~.constraints.ExpressionsBlock.set_expressions()` method. Private class methods are used to define each set of expresssions, each of which are defined in module level functions.


.. automodule:: constraints
   :members: