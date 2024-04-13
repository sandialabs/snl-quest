"""GLPK integration."""

import ctypes
from warnings import warn

import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import OptimizeWarning, OptimizeResult
from scipy.optimize._linprog_util import _LPProblem, _clean_inputs

from ._glpk_defines import GLPK, glp_smcp, glp_iptcp, glp_bfcp, glp_iocp
from ._utils import _fill_prob


def glpk(
        c,
        A_ub=None,
        b_ub=None,
        A_eq=None,
        b_eq=None,
        bounds=None,
        solver: str = 'simplex',
        sense=GLPK.GLP_MIN,
        scale: bool = True,
        maxit: int = GLPK.INT_MAX,
        timeout: int = GLPK.INT_MAX,
        basis_fac: str = 'luf+ft',
        message_level=GLPK.GLP_MSG_ERR,
        disp: bool = False,
        simplex_options=None,
        ip_options=None,
        mip_options=None,
):
    """GLPK ctypes interface.

    Parameters
    ----------
    c : 1-D array (n,)
        Array of objective coefficients.
    A_ub : 2-D array (m, n)
        scipy.sparse.coo_matrix
    b_ub : 1-D array (m,)
    A_eq : 2-D array (k, n)
        scipy.sparse.coo_matrix
    b_eq : 1-D array (k,)
    bounds : None or list (n,) of tuple (2,) or tuple (2,)
        The jth entry in the list corresponds to the jth objective coefficient.
        Each entry is made up of a tuple describing the bounds.
        Use None to indicate that there is no bound. By default, bounds are
        (0, None) (all decision variables are non-negative). If a single tuple
        (min, max) is provided, then min and max will serve as bounds for all
        decision variables.
    solver : { 'simplex', 'interior', 'mip' }
        Use simplex (LP/MIP) or interior point method (LP only).
        Default is ``simplex``.
    sense : { 'GLP_MIN', 'GLP_MAX' }
        Minimization or maximization problem.
        Default is ``GLP_MIN``.
    scale : bool
        Scale the problem. Default is ``True``.
    maxit : int
        Maximum number of iterations. Default is ``INT_MAX``.
    timeout : int
        Limit solution time to ``timeout`` seconds.
        Default is ``INT_MAX``.
    basis_fac : { 'luf+ft', 'luf+cbg', 'luf+cgr', 'btf+cbg', 'btf+cgr' }
        LP basis factorization strategy. Default is ``luf+ft``.
        These are combinations of the following strategies:

            - ``luf`` : plain LU-factorization
            - ``btf`` : block triangular LU-factorization
            - ``ft`` : Forrest-Tomlin update
            - ``cbg`` : Schur complement + Bartels-Golub update
            - ``cgr`` : Schur complement + Givens rotation update

    message_level : { GLP_MSG_OFF, GLP_MSG_ERR, GLP_MSG_ON, GLP_MSG_ON, GLP_MSG_ALL, GLP_MSG_DBG }
        Verbosity level of logging to stdout.
        Only applied when ``disp=True``. Default is ``GLP_MSG_ERR``.
        One of the following:

            ``GLP_MSG_OFF`` : no output
            ``GLP_MSG_ERR`` : warning and error messages only
            ``GLP_MSG_ON`` : normal output
            ``GLP_MSG_ALL`` : full output
            ``GLP_MSG_DBG`` : debug output

    disp : bool
        Display output to stdout. Default is ``False``.
    simplex_options : dict
        Options specific to simplex solver. The dictionary consists of
        the following fields:

            - primal : { 'primal', 'dual', 'dualp' }
                Primal or two-phase dual simplex.
                Default is ``primal``. One of the following:

                    - ``primal`` : use two-phase primal simplex
                    - ``dual`` : use two-phase dual simplex
                    - ``dualp`` : use two-phase dual simplex, and if it fails,
                        switch to the primal simplex

            - init_basis : { 'std', 'adv', 'bib' }
                Choice of initial basis.  Default is 'adv'.
                One of the following:

                    - ``std`` : standard initial basis of all slacks
                    - ``adv`` : advanced initial basis
                    - ``bib`` : Bixby's initial basis

            - steep : bool
                Use steepest edge technique or standard "textbook"
                pricing.  Default is ``True`` (steepest edge).

            - ratio : { 'relax', 'norelax', 'flip' }
                Ratio test strategy. Default is ``relax``.
                One of the following:

                    - ``relax`` : Harris' two-pass ratio test
                    - ``norelax`` : standard "textbook" ratio test
                    - ``flip`` : long-step ratio test

            - tol_bnd : double
                Tolerance used to check if the basic solution is primal
                feasible. (Default: 1e-7).

            - tol_dj : double
                Tolerance used to check if the basic solution is dual
                feasible. (Default: 1e-7).

            - tol_piv : double
                Tolerance used to choose eligble pivotal elements of
                the simplex table. (Default: 1e-10).

            - obj_ll : double
                Lower limit of the objective function. If the objective
                function reaches this limit and continues decreasing,
                the solver terminates the search. Used in the dual simplex
                only. (Default: -DBL_MAX -- the largest finite float64).

            - obj_ul : double
                Upper limit of the objective function. If the objective
                function reaches this limit and continues increasing,
                the solver terminates the search. Used in the dual simplex
                only. (Default: +DBL_MAX -- the largest finite float64).

            - presolve : bool
                Use presolver (assumes ``scale=True`` and
                ``init_basis='adv'``. Default is ``True``.

            - exact : bool
                Use simplex method based on exact arithmetic.
                Default is ``False``. If ``True``, all other
                ``simplex_option`` fields are ignored.

    ip_options : dict
        Options specific to interior-pooint solver.
        The dictionary consists of the following fields:

            - ordering : { 'nord', 'qmd', 'amd', 'symamd' }
                Ordering algorithm used before Cholesky factorizaiton.
                Default is ``amd``. One of the following:

                    - ``nord`` : natural (original) ordering
                    - ``qmd`` : quotient minimum degree ordering
                    - ``amd`` : approximate minimum degree ordering
                    - ``symamd`` : approximate minimum degree ordering
                        algorithm for Cholesky factorization of symmetric
                        matrices.

    mip_options : dict
        Options specific to MIP solver.
        The dictionary consists of the following fields:

            - intcon : 1-D array
                Array of integer contraints, specified as the 0-based
                indices of the solution. Default is an empty array.
            - bincon : 1-D array
                Array of binary constraints, specified as the 0-based
                indices of the solution. If any indices are duplicated
                between ``bincon`` and ``intcon``, they will be
                considered as binary constraints. Default is an empty
                array.
            - nomip : bool
                consider all integer variables as continuous
                (allows solving MIP as pure LP). Default is ``False``.
            - branch : { 'first', 'last', 'mostf', 'drtom', 'pcost' }
                Branching rule. Default is ``drtom``.
                One of the following:

                    - ``first`` : branch on first integer variable
                    - ``last`` : branch on last integer variable
                    - ``mostf`` : branch on most fractional variable
                    - ``drtom`` : branch using heuristic by Driebeck and Tomlin
                    - ``pcost`` : branch using hybrid pseudocost heuristic
                                  (may be useful for hard instances)

            - backtrack : { 'dfs', 'bfs', 'bestp', 'bestb' }
                Backtracking rule. Default is ``bestb``.
                One of the following:

                    - ``dfs`` : backtrack using depth first search
                    - ``bfs`` : backtrack using breadth first search
                    - ``bestp`` : backtrack using the best projection heuristic
                    - ``bestb`` : backtrack using node with best local bound

            - preprocess : { 'none', 'root', 'all' }
                Preprocessing technique. Default is ``GLP_PP_ALL``.
                One of the following:

                    - ``none`` : disable preprocessing
                    - ``root`` : perform preprocessing only on the root level
                    - ``all`` : perform preprocessing on all levels

            - round : bool
                Simple rounding heuristic. Default is ``True``.

            - presolve : bool
                Use MIP presolver. Default is ``True``.

            - binarize : bool
                replace general integer variables by binary ones
                (only used if ``presolve=True``). Default is ``False``.

            - fpump : bool
                Apply feasibility pump heuristic. Default is ``False``.

            - proxy : int
                Apply proximity search heuristic (in seconds). Default is 60.

            - cuts : list of { 'gomory', 'mir', 'cover', 'clique', 'all' }
                Cuts to generate. Default is no cuts. List of the following:

                    - ``gomory`` : Gomory's mixed integer cuts
                    - ``mir`` : MIR (mixed integer rounding) cuts
                    - ``cover`` : mixed cover cuts
                    - ``clique`` : clique cuts
                    - ``all`` : generate all cuts above

            - tol_int : float
                Absolute tolerance used to check if optimal solution to the
                current LP relaxation is integer feasible.
                (Default: 1e-5).
            - tol_obj : float
                Relative tolerance used to check if the objective value in
                optimal solution to the current LP relaxation is not better
                than in the best known integer feasible solution.
                (Default: 1e-7).
            - mip_gap : float
                Relative mip gap tolerance. If the relative mip gap for
                currently known best integer feasible solution falls below
                this tolerance, the solver terminates the search. This allows
                obtaining suboptimal integer feasible solutions if solving the
                problem to optimality takes too long time.
                (Default: 0.0).
            - bound : float
                add inequality obj <= bound (minimization) or
                obj >= bound (maximization) to integer feasibility
                problem (assumes ``minisat=True``).

    Notes
    -----
    In general, don't change tolerances without a detailed understanding
    of their purposes.
    """

    # Housekeeping
    if simplex_options is None:
        simplex_options = {}
    if ip_options is None:
        ip_options = {}
    if mip_options is None:
        mip_options = {}

    # Make variables integer- and binary-valued
    if not mip_options.get('nomip', False):
        intcon = mip_options.get('intcon', None)
        bincon = mip_options.get('bincon', None)
        if intcon:
            integrality = np.zeros(len(c), dtype=bool)
            integrality[intcon] = True
        else:
            integrality = None
        if bincon:
            binary = np.zeros(len(c), dtype=bool)
            binary[bincon] = True
        else:
            binary = None
    else:
        integrality = None
        binary = None

    # Create and fill the GLPK problem struct
    prob, c, A_ub, b_ub, A_eq, b_eq, processed_bounds, integrality, binary = _fill_prob(
        c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, sense=sense,
        integrality=integrality, binary=binary, prob_name='problem-name')

    # Get the library
    _lib = GLPK()._lib

    # Scale the problem
    no_need_explict_scale = (solver == "simplex" and 
                             simplex_options.get("presolve"))
    if not no_need_explict_scale and scale:
        _lib.glp_scale_prob(prob, GLPK.GLP_SF_AUTO)  # do auto-scale for now

    # Select basis factorization method
    bfcp = glp_bfcp()
    _lib.glp_get_bfcp(prob, ctypes.byref(bfcp))
    bfcp.type = {
        'luf+ft': GLPK.GLP_BF_LUF + GLPK.GLP_BF_FT,
        'luf+cbg': GLPK.GLP_BF_LUF + GLPK.GLP_BF_BG,
        'luf+cgr': GLPK.GLP_BF_LUF + GLPK.GLP_BF_GR,
        'btf+cbg': GLPK.GLP_BF_BTF + GLPK.GLP_BF_BG,
        'btf+cgr': GLPK.GLP_BF_BTF + GLPK.GLP_BF_GR,
    }[basis_fac]
    _lib.glp_set_bfcp(prob, ctypes.byref(bfcp))

    # Run the solver
    if solver == 'simplex':

        # Construct an initial basis
        basis = simplex_options.get('init_basis', 'adv')
        basis_fun = {
            'std': _lib.glp_std_basis,
            'adv': _lib.glp_adv_basis,
            'bib': _lib.glp_cpx_basis,
        }[basis]
        basis_args = [prob]
        if basis == 'adv':
            # adv must have 0 as flags argument
            basis_args.append(0)
        basis_fun(*basis_args)

        # Make control structure
        smcp = glp_smcp()
        _lib.glp_init_smcp(ctypes.byref(smcp))

        # Set options
        smcp.msg_lev = message_level*disp
        smcp.meth = {
            'primal': GLPK.GLP_PRIMAL,
            'dual': GLPK.GLP_DUAL,
            'dualp': GLPK.GLP_DUALP,
        }[simplex_options.get('method', 'primal')]
        smcp.pricing = {
            True: GLPK.GLP_PT_PSE,
            False: GLPK.GLP_PT_STD,
        }[simplex_options.get('steep', True)]
        smcp.r_test = {
            'relax': GLPK.GLP_RT_HAR,
            'norelax': GLPK.GLP_RT_STD,
            'flip': GLPK.GLP_RT_FLIP,
        }[simplex_options.get('ratio', 'relax')]
        smcp.tol_bnd = simplex_options.get('tol_bnd', 1e-7)
        smcp.tol_dj = simplex_options.get('tol_dj', 1e-7)
        smcp.tol_piv = simplex_options.get('tol_piv', 1e-10)
        if simplex_options.get('obj_ll', False):
            smcp.obj_ll = simplex_options['obj_ll']
        if simplex_options.get('obj_ul', False):
            smcp.obj_ul = simplex_options['obj_ul']
        smcp.it_lim = maxit
        smcp.tm_lim = timeout
        smcp.presolve = {
            True: GLPK.GLP_ON,
            False: GLPK.GLP_OFF,
        }[simplex_options.get('presolve', True)]

        # Simplex driver
        if simplex_options.get('exact', False):
            ret_code = _lib.glp_exact(prob, ctypes.byref(smcp))
        else:
            ret_code = _lib.glp_simplex(prob, ctypes.byref(smcp))
        if ret_code != GLPK.SUCCESS:
            warn('GLPK simplex not successful!', OptimizeWarning)
            return OptimizeResult({
                'message': GLPK.RET_CODES[ret_code],
            })

        # Figure out what happened
        status = _lib.glp_get_status(prob)
        message = GLPK.STATUS_CODES[status]
        res = OptimizeResult({
            'status': status,
            'message': message,
            'success': status == GLPK.GLP_OPT,
        })

        # We can read a solution:
        if status == GLPK.GLP_OPT:

            res.fun = _lib.glp_get_obj_val(prob)
            res.x = np.array([_lib.glp_get_col_prim(prob, ii) for ii in range(1, _lib.glp_get_num_cols(prob)+1)])
            res.dual = np.array([_lib.glp_get_row_dual(prob, ii) for ii in range(1, _lib.glp_get_num_rows(prob)+1)])

            # We don't get slack without doing sensitivity analysis since GLPK
            # uses auxiliary variables instead of slack!
            res.slack = b_ub - A_ub @ res.x
            res.con = b_eq - A_eq @ res.x

            # We shouldn't be reading this field... But we will anyways
            res.nit = prob.contents.it_cnt

    elif solver == 'interior':

        # Make a control structure
        iptcp = glp_iptcp()
        _lib.glp_init_iptcp(ctypes.byref(iptcp))

        # Set options
        iptcp.msg_lev = message_level*disp
        iptcp.ord_alg = {
            'nord': GLPK.GLP_ORD_NONE,
            'qmd': GLPK.GLP_ORD_QMD,
            'amd': GLPK.GLP_ORD_AMD,
            'symamd': GLPK.GLP_ORD_SYMAMD,
        }[ip_options.get('ordering', 'amd')]

        # Run the solver
        ret_code = _lib.glp_interior(prob, ctypes.byref(iptcp))
        if ret_code != GLPK.SUCCESS:
            warn('GLPK interior-point not successful!', OptimizeWarning)
            return OptimizeResult({
                'message': GLPK.RET_CODES[ret_code],
            })

        # Figure out what happened
        status = _lib.glp_ipt_status(prob)
        message = GLPK.STATUS_CODES[status]
        res = OptimizeResult({
            'status': status,
            'message': message,
            'success': status == GLPK.GLP_OPT,
        })

        # We can read a solution:
        if status == GLPK.GLP_OPT:

            res.fun = _lib.glp_ipt_obj_val(prob)
            res.x = np.array([_lib.glp_ipt_col_prim(prob, ii) for ii in range(1, _lib.glp_get_num_cols(prob)+1)])
            res.dual = np.array([_lib.glp_ipt_row_dual(prob, ii) for ii in range(1, _lib.glp_get_num_rows(prob)+1)])

            # We don't get slack without doing sensitivity analysis since GLPK uses
            # auxiliary variables instead of slack!
            res.slack = b_ub - A_ub @ res.x
            res.con = b_eq - A_eq @ res.x

            # We shouldn't be reading this field... But we will anyways
            res.nit = prob.contents.it_cnt

    elif solver == 'mip':

        # Make a control structure
        iocp = glp_iocp()
        _lib.glp_init_iocp(ctypes.byref(iocp))

        # Set options
        iocp.msg_lev = message_level*disp
        iocp.br_tech = {
            'first': GLPK.GLP_BR_FFV,
            'last': GLPK.GLP_BR_LFV,
            'mostf': GLPK.GLP_BR_MFV,
            'drtom': GLPK.GLP_BR_DTH,
            'pcost': GLPK.GLP_BR_PCH,
        }[mip_options.get('branch', 'drtom')]
        iocp.bt_tech = {
            'dfs': GLPK.GLP_BT_DFS,
            'bfs': GLPK.GLP_BT_BFS,
            'bestp': GLPK.GLP_BT_BPH,
            'bestb': GLPK.GLP_BT_BLB,
        }[mip_options.get('backtrack', 'bestb')]
        iocp.pp_teck = {
            'none': GLPK.GLP_PP_NONE,
            'root': GLPK.GLP_PP_ROOT,
            'all': GLPK.GLP_PP_ALL,
        }[mip_options.get('preprocess', 'all')]
        iocp.sr_heur = {
            True: GLPK.GLP_ON,
            False: GLPK.GLP_OFF,
        }[mip_options.get('round', True)]
        iocp.fp_heur = {
            True: GLPK.GLP_ON,
            False: GLPK.GLP_OFF,
        }[mip_options.get('fpump', False)]

        ps_tm_lim = mip_options.get('proxy', 60)
        if ps_tm_lim:
            iocp.ps_heur = GLPK.GLP_ON
            iocp.ps_tm_lim = ps_tm_lim*1000
        else:
            iocp.ps_heur = GLPK.GLP_OFF
            iocp.ps_tm_lim = 0

        cuts = set(list(mip_options.get('cuts', [])))
        if 'all' in cuts:
            cuts = {'gomory', 'mir', 'cover', 'clique'}
        if 'gomory' in cuts:
            iocp.gmi_cuts = GLPK.GLP_ON
        if 'mir' in cuts:
            iocp.mir_cuts = GLPK.GLP_ON
        if 'cover' in cuts:
            iocp.cov_cuts = GLPK.GLP_ON
        if 'clique' in cuts:
            iocp.clq_cuts = GLPK.GLP_ON

        iocp.tol_int = mip_options.get('tol_int', 1e-5)
        iocp.tol_obj = mip_options.get('tol_obj', 1e-7)
        iocp.mip_gap = mip_options.get('mip_gap', 0.0)
        iocp.tm_lim = timeout
        iocp.presolve = {
            True: GLPK.GLP_ON,
            False: GLPK.GLP_OFF,
        }[mip_options.get('presolve', True)]
        iocp.binarize = {
            True: GLPK.GLP_ON,
            False: GLPK.GLP_OFF,
        }[mip_options.get('binarize', False)]

        # Run the solver
        ret_code = _lib.glp_intopt(prob, ctypes.byref(iocp))
        if ret_code != GLPK.SUCCESS:
            warn('GLPK interior-point not successful!', OptimizeWarning)
            return OptimizeResult({
                'message': GLPK.RET_CODES[ret_code],
            })

        # Figure out what happened
        status = _lib.glp_mip_status(prob)
        message = GLPK.STATUS_CODES[status]
        res = OptimizeResult({
            'status': status,
            'message': message,
            'success': status in [GLPK.GLP_OPT, GLPK.GLP_FEAS],
        })

        # We can read a solution:
        if res.success:
            res.fun = _lib.glp_mip_obj_val(prob)
            res.x = np.array([_lib.glp_mip_col_val(prob, ii) for ii in range(1, len(c)+1)])

    else:
        raise ValueError('"%s" is not a recognized solver.' % solver)

    # We're done, cleanup!
    _lib.glp_delete_prob(prob)

    # Map status codes to scipy:
    # res.status = {
    #     GLPK.GLP_OPT: 0,
    # }[res.status]

    return res
