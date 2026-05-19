from abc import ABCMeta, abstractmethod, abstractproperty
import logging
import os
import shutil
import sys

from pyutilib.common._exceptions import ApplicationError

from six import with_metaclass
from pyomo.environ import *
from pyomo.opt import TerminationCondition


class Optimizer(with_metaclass(ABCMeta)):
    """Abstract base class for Pyomo ConcreteModel optimization framework."""

    def __init__(self, solver="glpk"):
        self._model = ConcreteModel()
        self._solver = solver

        self._results = None

    @property
    def model(self):
        """Pyomo ConcreteModel."""
        return self._model

    @property
    def solver(self):
        """The name of the solver for Pyomo to use."""
        return self._solver

    @property
    def results(self):
        """A results DataFrame containing series of indices, decision variables, and/or model parameters or derived quantities."""
        return self._results

    @abstractmethod
    def _set_model_param(self):
        """A method for assigning model parameters and their default values to the model."""
        pass

    @abstractmethod
    def _set_model_var(self):
        """A method for initializing model decision variables for the model."""
        pass

    @abstractmethod
    def instantiate_model(self):
        """A method for instantiating the model and assigning Optimizer attributes to model attributes."""
        pass

    @abstractmethod
    def populate_model(self):
        """A method for setting model parameters, variables, and an ExpressionsBlock object for defining objectives and constraints."""
        pass

    def solve_model(self):
        """Solves the model using the specified solver."""
        if self.solver == "neos":
            opt = SolverFactory("cbc")
            solver_manager = SolverManagerFactory("neos")
            results = solver_manager.solve(self.model, opt=opt)
        else:
            solver = self._create_solver()
            results = solver.solve(self.model, tee=False, keepfiles=False)

        assert results.solver.termination_condition == TerminationCondition.optimal

        self._process_results()

    @abstractmethod
    def _process_results(self):
        """A method for computing derived quantities of interest and creating the results DataFrame."""
        pass

    @abstractmethod
    def get_results(self):
        """A method for returning the results DataFrame plus any other quantities of interest."""
        pass

    def run(self):
        """Instantiates, creates, and solves the optimizer model based on supplied information. Use if no steps are needed between constructing the model and solving it."""
        self.instantiate_model()
        self.populate_model()

        if self.solver == "neos":
            opt = SolverFactory("cbc")
            solver_manager = SolverManagerFactory("neos")
            results = solver_manager.solve(self.model, opt=opt)
        else:
            solver = self._create_solver()

            try:
                solver.available()
            except ApplicationError as e:
                logging.error("Optimizer: {error}".format(error=e))
                raise
            else:
                results = solver.solve(self.model, tee=True, keepfiles=False)

        try:
            assert results.solver.termination_condition == TerminationCondition.optimal
        except AssertionError:
            logging.error(
                "Optimizer: An optimal solution could not be obtained. (solver termination condition: {0})".format(
                    results.solver.termination_condition
                )
            )
            raise (
                AssertionError(
                    "An optimal solution could not be obtained. (solver termination condition: {0})".format(
                        results.solver.termination_condition
                    )
                )
            )
        else:
            self._process_results()

        return self.get_results()

    def _create_solver(self):
        """Create a solver instance, preferring a bundled GLPK executable when present."""
        if self.solver != "glpk":
            return SolverFactory(self.solver)

        executable = self._find_glpk_executable()
        if executable:
            logging.info("Optimizer: Using GLPK executable at %s", executable)
            return SolverFactory(self.solver, executable=executable)

        return SolverFactory(self.solver)

    @staticmethod
    def _find_glpk_executable():
        """Locate glpsol in PATH or in the current environment's bundled GLPK folder."""
        exe_name = "glpsol.exe" if os.name == "nt" else "glpsol"
        from_path = shutil.which(exe_name) or shutil.which("glpsol")
        if from_path:
            return from_path

        env_root = os.path.dirname(os.path.dirname(sys.executable))
        candidates = [
            os.path.join(env_root, "glpk", "GLPK-4.65", "w64", exe_name),
            os.path.join(env_root, "glpk", "glpk-4.65", "w64", exe_name),
            os.path.join(env_root, "glpk", "winglpk-4.65", "w64", exe_name),
            os.path.join(env_root, "bin", exe_name),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        glpk_root = os.path.join(env_root, "glpk")
        if os.path.isdir(glpk_root):
            for root, _dirs, files in os.walk(glpk_root):
                if exe_name in files:
                    return os.path.join(root, exe_name)

        return None

    def set_model_parameters(self, **kwargs):
        """Sets model parameters in kwargs to their respective values."""
        for kw_key, kw_value in kwargs.items():
            logging.info(
                "Optimizer: Setting {param} to {value}".format(
                    param=kw_key, value=kw_value
                )
            )
            setattr(self.model, kw_key, kw_value)
