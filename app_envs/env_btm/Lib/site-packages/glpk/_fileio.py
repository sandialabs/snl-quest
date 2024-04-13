import ctypes
import pathlib

import numpy as np
from scipy.sparse import coo_matrix

from ._glpk_defines import GLPK
from ._utils import _fill_prob


def mpsread(filename: str, fmt=GLPK.GLP_MPS_FILE, ret_glp_prob: bool = False, read_additional_info: bool = False):
    """Read an MPS file.

    Parameters
    ----------
    filename : str
        Path to MPS file.
    fmt : { GLP_MPS_DECK, GLP_MPS_FILE }
        Type of MPS file (original or free-format). Default is
        free-format (``GLP_MPS_FILE``).
    ret_glp_prob : bool
        Return the ``glp_prob`` structure. If ``False``, `linprog` style
        matrices and bounds are returned, i.e., ``A_ub``, ``b_ub``, etc.
        Default is ``False``.
    read_additional_info : bool
        Return additional info dictionary, which contains:
            col_names - column names
            row_names - row names
            row_types - row types (GLP_FR, GLP_LO, GLP_UP, GLP_DB, GLP_FX)
            col_types - column types (GLP_FR, GLP_LO, GLP_UP, GLP_DB, GLP_FX)
            prob_name - problem name
            obj_name  - objective function name
            obj_dir   - optimization direction flag (GLP_MIN, GLP_MAX)
        All types constants (e.g. GLP_FR, GLP_MIN)  are contained in GLPK.{constant name}
        If ``True``, additional info is returned.
        Default is ``False``.
    """

    _lib = GLPK()._lib

    # Populate a glp_prob structure
    prob = _lib.glp_create_prob()
    filename = str(pathlib.Path(filename).expanduser().resolve())
    _lib.glp_read_mps(prob, fmt, None, filename.encode())

    # Return the GLPK object if requested
    if ret_glp_prob:
        return prob

    # Otherwise read the matrices
    n = _lib.glp_get_num_cols(prob)
    c = np.empty((n,))
    bounds = []
    for ii in range(1, n+1):
        c[ii-1] = _lib.glp_get_obj_coef(prob, ii)

        # get lb and ub; have to do it like this for some reason...
        tipe = _lib.glp_get_col_type(prob, ii)
        if tipe == GLPK.GLP_FR:
            bnd = (-np.inf, np.inf)
        elif tipe == GLPK.GLP_LO:
            bnd = (_lib.glp_get_col_lb(prob, ii), np.inf)
        elif tipe == GLPK.GLP_UP:
            bnd = (-np.inf, _lib.glp_get_col_ub(prob, ii))
        elif tipe == GLPK.GLP_DB:
            bnd = (_lib.glp_get_col_lb(prob, ii), _lib.glp_get_col_ub(prob, ii))
        else:
            bnd = (_lib.glp_get_col_lb(prob, ii), _lib.glp_get_col_lb(prob, ii))
        bounds.append(bnd)

    m = _lib.glp_get_num_rows(prob)
    nnz = _lib.glp_get_num_nz(prob)
    ub_cols, ub_rows, ub_vals = [], [], []
    eq_cols, eq_rows, eq_vals = [], [], []
    b_ub, b_eq = [], []
    indarr = ctypes.c_int*(n+1)
    valarr = ctypes.c_double*(n+1)
    col_ind = indarr()
    row_val = valarr()
    for ii in range(1, m+1):
        row_type = _lib.glp_get_row_type(prob, ii)
        l = _lib.glp_get_mat_row(prob, ii, col_ind, row_val)
        if l == 0:
            # if there are no elements in the row, skip,
            # otherwise we would add an extra element to RHS
            continue

        if row_type == GLPK.GLP_UP:
            b_ub.append(_lib.glp_get_row_ub(prob, ii))
            for jj in range(1, l+1):
                ub_cols.append(col_ind[jj] - 1)
                ub_rows.append(ii - 1)
                ub_vals.append(row_val[jj])
        elif row_type == GLPK.GLP_FX:
            b_eq.append(_lib.glp_get_row_lb(prob, ii))
            for jj in range(1, l+1):
                eq_cols.append(col_ind[jj] - 1)
                eq_rows.append(ii - 1)
                eq_vals.append(row_val[jj])
        elif row_type == GLPK.GLP_LO:
            b_ub.append(-1*_lib.glp_get_row_lb(prob, ii))
            for jj in range(1, l+1):
                ub_cols.append(col_ind[jj] - 1)
                ub_rows.append(ii - 1)
                ub_vals.append(-1*row_val[jj])
        else:
            raise NotImplementedError()

    if ub_vals:
        # Converting to csc_matrix gets rid of all-zero rows
        A_ub = coo_matrix((ub_vals, (ub_rows, ub_cols)), shape=(max(ub_rows)+1, n))
        A_ub = A_ub.tocsc()
        A_ub = A_ub[A_ub.getnnz(axis=1) > 0]
    else:
        A_ub = None
        b_ub = None

    if eq_vals:
        A_eq = coo_matrix((eq_vals, (eq_rows, eq_cols)), shape=(max(eq_rows)+1, n))
        A_eq = A_eq.tocsc()
        A_eq = A_eq[A_eq.getnnz(axis=1) > 0]
    else:
        A_eq = None
        b_eq = None

    # get integrality
    integrality = [{
        GLPK.GLP_CV: 0,
        GLPK.GLP_IV: 1,
        GLPK.GLP_BV: 1,
    }[_lib.glp_get_col_kind(prob, jj)] for jj in range(1, n+1)]

    # add additional constraints if binary
    for jj in range(1, n+1):
        if _lib.glp_get_col_kind(prob, jj) == GLPK.GLP_BV:
            bounds[jj-1] = (0, 1)

    if read_additional_info:
        additional_info = {'col_names': [_lib.glp_get_col_name(prob, ii).decode('utf-8') for ii in range(1, n + 1)],
                           'row_names': [_lib.glp_get_row_name(prob, ii).decode('utf-8') for ii in range(1, m + 1)],
                           'col_types': [_lib.glp_get_col_type(prob, ii) for ii in range(1, n + 1)],
                           'row_types': [_lib.glp_get_row_type(prob, ii) for ii in range(1, m + 1)],
                           'prob_name': _lib.glp_get_prob_name(prob), 'obj_name': _lib.glp_get_obj_name(prob),
                           'obj_dir': _lib.glp_get_obj_dir(prob)}

        return c, A_ub, b_ub, A_eq, b_eq, bounds, integrality, additional_info
    else:
        return c, A_ub, b_ub, A_eq, b_eq, bounds, integrality


def mpswrite(
        c,
        A_ub=None,
        b_ub=None,
        A_eq=None,
        b_eq=None,
        bounds=None,
        integrality=None,
        binary=None,
        sense=GLPK.GLP_MIN,
        filename: str = 'prob.mps',
        fmt=GLPK.GLP_MPS_FILE):
    """Write an MPS file."""

    filename = pathlib.Path(filename)
    prob, _lp = _fill_prob(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds,
                           integrality=integrality, binary=binary, sense=sense, prob_name=filename.stem)

    # Get the library
    _lib = GLPK()._lib

    # Call write
    res = _lib.glp_write_mps(prob, fmt, None, str(filename).encode())
    return res == 0


def lpwrite(c,
            A_ub=None,
            b_ub=None,
            A_eq=None,
            b_eq=None,
            bounds=None,
            integrality=None,
            binary=None,
            sense=GLPK.GLP_MIN,
            filename: str = 'prob.lp'):
    """Write a CPLEX LP file."""

    filename = pathlib.Path(filename)
    prob, _lp = _fill_prob(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds,
                           integrality=integrality, binary=binary, sense=sense, prob_name=filename.stem)

    # Get the library
    _lib = GLPK()._lib

    # Call write
    res = _lib.glp_write_lp(prob, None, str(filename).encode())
    return res == 0
