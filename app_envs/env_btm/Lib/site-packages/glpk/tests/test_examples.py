"""Simple examples for a sanity check."""

import pytest
import numpy as np
from scipy.optimize import linprog

from glpk import glpk, GLPK


@pytest.mark.parametrize("presolve", (True, False))
@pytest.mark.parametrize("solver", ("simplex", "interior"))
def test_widget_lp(presolve: bool, solver: str):
    """http://www.cs.toronto.edu/~jepson/csc373/lectures/linearProgIntro_4pp.pdf"""
    c = [1, 2]
    A = [[1, 1],
         [-1, 1],
         [-3, 10]]
    b = [4, 1, 15]
    res = glpk(c=c, A_ub=A, b_ub=b, solver=solver, sense=GLPK.GLP_MAX, simplex_options={"presolve": presolve})
    assert np.allclose(res["x"],  [25/13, 27/13])
    assert res["fun"] == res["x"] @ c


def test_against_scipy_simple():
    c = [-1, 8, 4, -6]
    A_ub = [[-7, -7, 6, 9],
            [1, -1, -3, 0],
            [10, -10, -7, 7],
            [6, -1, 3, 4]]
    b_ub = [-3, 6, -6, 6]
    A_eq = [[-10, 1, 1, -8]]
    b_eq = [-4]
    bnds = None
    glpk_res = glpk(
        c, A_ub, b_ub, A_eq, b_eq, bnds,
        message_level=GLPK.GLP_MSG_OFF,
        maxit=100,
        timeout=10,
        solver='simplex',
        basis_fac='btf+cbg',
        simplex_options={
            'init_basis': 'adv',
            'method': 'dual',
            'presolve': True,
            # 'exact': True,
        })
    scipy_res = linprog(c, A_ub, b_ub, A_eq, b_eq, bnds)

    assert np.allclose(glpk_res["x"], scipy_res["x"])
    assert np.allclose(glpk_res["fun"], scipy_res["fun"])


def test_simple_mip():
    """https://www.cs.upc.edu/~erodri/webpage/cps/theory/lp/milp/slides.pdf"""
    c = [1, 1]
    A = [[2, -2],
         [-8, 10]]
    b = [-1, 13]
    res = glpk(c=c, A_ub=A, b_ub=b, solver="mip", sense=GLPK.GLP_MAX,
               mip_options={"intcon": [0, 1]})
    assert np.allclose(res["x"], [1, 2])
    assert res["fun"] == 3

    res = glpk(c=c, A_ub=A, b_ub=b, solver="mip", sense=GLPK.GLP_MAX,
               mip_options={"intcon": [0, 1], "nomip": True})
    assert np.allclose(res["x"], [4, 4.5])
    assert res["fun"] == res["x"] @ c  # slides have the wrong answer!
