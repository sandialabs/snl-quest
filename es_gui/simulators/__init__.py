"""This package is for Simulators: objects composed of Optimizer-derived objects that can perform specific flavors of simulations that may span multiple optimization problems.

For example, a Simulator can perform simulation for one month of data by performing simulation for each individual day and combining the results. A Simulator should have similar data-access interfaces as its related Optimizer class.
"""