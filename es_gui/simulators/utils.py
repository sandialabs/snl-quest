"""Utility classes and functions for the simulator modules.

This module provides: a simulator base class.

"""

from abc import ABCMeta, abstractmethod, abstractproperty
from six import with_metaclass


class Simulator(with_metaclass(ABCMeta)):
    """Abstract base class for Simulator classes.

    Simulator classes are designed to have interfaces similar to the Optimizer objects that they 
    are composed of, particularly for obtaining simulation results. Their purpose is to facilitate
    simulation based on the optimization problems modeled in Optimizer objects, including
    simulations composed of many sub-problems. 
    
    For example, a ValuationOptimizer object solves a revenue maximization problem with a time 
    horizon of one month. A Simulator for the same object can support that type of simulation or 
    other simulation methods such as: breaking up the one month into 24-hour time horizon 
    optimization problems for each day and combining the results, using forecasted data in the
    optimization and recalculating the objective value using the actuals data, and more.

    These classes are designed to facilitate using different estimation methods for the energy
    storage valuation problem.
    """

    def __init__(self):
        self._solved_ops = []
        self._results = None
        self._optimizer = None

    @property
    def optimizer(self):
        """An Optimizer-derived class. The interfaces of this class will determine the
        implementation of the other Simulator class methods.
        """
        return self._optimizer

    @optimizer.setter
    def optimizer(self, value):
        self._optimizer = value
    
    @property
    def solved_ops(self):
        """A list containing the solved Optimizer objects after running the simulation.
        """
        return self._solved_ops
    
    @solved_ops.setter
    def solved_ops(self, value):
        self._solved_ops = value
    
    @property
    def results(self):
        """A Pandas DataFrame containing all of the optimization results.

        When the Simulator is composed of many Optimizer objects, this DataFrame should
        combine each of their results appropriately. For example, the index should reflect
        the time horizon of the larger problem. Several Optimizer-derived classes include
        cumulative quantities in their results DataFrame (e.g., revenue); the accumulation
        should also be properly represented in the combined DataFrame.
        """
        return self._results

    @results.setter
    def results(self, value):
        self._results = value

    @staticmethod
    def set_optimizer_properties(op, **kwargs):
        """Assigns attribute values to the Optimizer object `op`.

        This static method is for interacting with the Optimizer interfaces that are
        implemented as object properties by using the **kwargs construct as a shortcut.

        Parameters
        ----------
        op : Optimizer-derived object
            An Optimizer-derived object that is the target of the assignment operations.

        kwargs : dict
            A dictionary where each key is the Optimizer attribute name and each value is
            the attribute value. 

        Returns
        -------
        op : Optimizer-derived object
            The same Optimizer-derived object as the input `op` after the assignment statements.

        Examples
        --------
        >>> assignments = {'price_electricity': lmp_da, 'solver': 'gurobi'}

        >>> op = set_optimizer_properties(op, **assignments)
        
        is equivalent to:

        >>> op.price_electricity = lmp_da

        >>> op.solver = 'gurobi'
        """
        for kw_key, kw_value in kwargs.items():
            setattr(op, kw_key, kw_value)
        
        return op
    
    @abstractmethod
    def run(self, properties, data, simulation_type, model_parameters=None, **kwargs):
        """Sets up and runs all Optimizer instances as prescribed by simulation.

        This is the primary interface for running simulations. It should use the
        `simulation_type` input parameter to switch among different simulation modes.
        Additional keyword arguments can be specified as needed to differentiate among
        simulation modes.

        In addition to performing a simulation, this method should also call
        `_process_results` in order to prepare the simulation results to be 
        accessible after this method is executed.

        Parameters
        ----------
        properties : dict
            A dictionary consisting of (attribute, value) pairs to assign to each
            Optimizer instance in the simulation. See `set_optimizer_properties`.
        
        data : dict
            A dictionary consisting of (attribute, value) pairs. This should be used to
            separately deal with, e.g., time series data, that may be processed in the
            simulation prior to assigning to an Optimizer instance. 
        
        simulation_type : str
            Name of the simulation mode to be performed. The specific valid choices
            should be enumerated in the derived class docstring.
        
        model_parameters : dict
            A dictionary consisting of (attribute, value) pairs to assign to the 
            Pyomo model of each Optimizer instance in the simulation. This is for
            parameters that don't use the Optimizer attributes as an interface but
            instead `Optimizer.set_model_parameters` to assign attributes directly
            to the Pyomo model. 

        """
        pass
    
    @abstractmethod
    def _process_results(self, simulation_type):
        """Processes the results of the simulation.

        This method is for processing the results of the simulation such that it is
        accessible through the `results` attribute. Different simulation modes may
        have different processing needs, including the need to concatenate results
        from a collection of Optimizer objects.

        Parameters
        ----------
        simulation_type : str
            Name of the simulation mode to be performed. The specific valid choices
            should be enumerated in the derived class docstring.

        """
        pass
