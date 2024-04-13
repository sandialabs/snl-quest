"""Wrappers over utility API routines."""

import ctypes

import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize._linprog_util import _LPProblem, _clean_inputs

from ._glpk_defines import GLPK


def _convert_bounds(processed_bounds):
    bounds = [None]*len(processed_bounds)
    for ii, (lb, ub) in enumerate(processed_bounds):
        if lb in {-np.inf, None} and ub in {np.inf, None}:
            # -inf < x < inf
            bounds[ii] = (GLPK.GLP_FR, 0, 0)
        elif lb in {-np.inf, None}:
            # -inf < x <= ub
            bounds[ii] = (GLPK.GLP_UP, 0, ub)
        elif ub in {np.inf, None}:
            # lb <= x < inf
            bounds[ii] = (GLPK.GLP_LO, lb, 0)
        elif lb < ub:
            # lb <= x <= ub
            bounds[ii] = (GLPK.GLP_DB, lb, ub)
        else:
            # lb == x == up
            bounds[ii] = (GLPK.GLP_FX, lb, ub)
    return bounds


def _fill_prob(c, A_ub, b_ub, A_eq, b_eq, bounds, integrality, binary, sense, prob_name: str):
    """Create and populate GLPK prob struct from linprog definition."""

    # Housekeeping
    lp = _clean_inputs(_LPProblem(
        c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
        bounds=bounds, x0=None, integrality=None))
    c, A_ub, b_ub, A_eq, b_eq, processed_bounds, _x0, _integrality = lp

    # handle GLPK integrality parameters apart from scipy's machinery
    # as we can have binary and integer valued variables
    if integrality is None or np.sum(integrality) == 0:
        integrality = None
    else:
        integrality = np.array(integrality, dtype=bool)
    if binary is None or np.sum(binary) == 0:
        binary = None
    else:
        binary = np.array(binary, dtype=bool)

    # coo for (i, j, val) format
    A = coo_matrix(np.concatenate((A_ub, A_eq), axis=0))

    # Convert linprog-style bounds to GLPK-style bounds
    bounds = _convert_bounds(processed_bounds)

    # Get the library
    _lib = GLPK()._lib

    # Create problem instance
    prob = _lib.glp_create_prob()

    # Give problem a name
    _lib.glp_set_prob_name(prob, prob_name.encode())

    # Set objective name
    _lib.glp_set_obj_name(prob, b'obj-name')

    # Set objective sense
    _lib.glp_set_obj_dir(prob, sense)

    # Set objective coefficients and column bounds
    first_col = _lib.glp_add_cols(prob, len(c))
    for ii, (c0, bnd) in enumerate(zip(c, bounds)):
        _lib.glp_set_obj_coef(prob, ii + first_col, c0)
        _lib.glp_set_col_name(prob, ii + first_col, b'c%d' % ii)  # name is c[idx], idx is 0-based index

        if bnd is not None:
            _lib.glp_set_col_bnds(prob, ii + first_col, bnd[0], bnd[1], bnd[2])
        # else: default is GLP_FX with lb=0, ub=0

        if integrality is not None and integrality[ii]:
            _lib.glp_set_col_kind(prob, ii + first_col, GLPK.GLP_IV)

        if binary is not None and binary[ii]:
            _lib.glp_set_col_kind(prob, ii + first_col, GLPK.GLP_BV)

    # Need to load both matrices at the same time
    first_row = _lib.glp_add_rows(prob, A.shape[0])

    # prepend an element and make 1-based index
    # b/c GLPK expects indices starting at 1
    nnz = A.nnz
    rows = np.concatenate(([-1], A.row + first_row)).astype(ctypes.c_int)
    cols = np.concatenate(([-1], A.col + first_col)).astype(ctypes.c_int)
    values = np.concatenate(([0], A.data)).astype(ctypes.c_double)
    _lib.glp_load_matrix(
        prob,
        nnz,
        rows,
        cols,
        values,
    )

    # Set row bounds
    # Upper bounds (b_ub):
    for ii, b0 in enumerate(b_ub):
        # lb is ignored for upper bounds
        _lib.glp_set_row_bnds(prob, ii + first_row, GLPK.GLP_UP, 0, b0)
    # Equalities (b_eq)
    for ii, b0 in enumerate(b_eq):
        _lib.glp_set_row_bnds(prob, ii + first_row + len(b_ub), GLPK.GLP_FX, b0, b0)

    return prob, c, A_ub, b_ub, A_eq, b_eq, processed_bounds, integrality, binary
