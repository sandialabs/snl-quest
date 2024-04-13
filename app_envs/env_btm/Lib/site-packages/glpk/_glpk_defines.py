
import ctypes
import importlib.util

from numpy.ctypeslib import ndpointer

# control structures


class glp_smcp(ctypes.Structure):
    _fields_ = [
        ('msg_lev', ctypes.c_int),
        ('meth', ctypes.c_int),
        ('pricing', ctypes.c_int),
        ('r_test', ctypes.c_int),
        ('tol_bnd', ctypes.c_double),
        ('tol_dj', ctypes.c_double),
        ('tol_piv', ctypes.c_double),
        ('obj_ll', ctypes.c_double),
        ('obj_ul', ctypes.c_double),
        ('it_lim', ctypes.c_int),
        ('tm_lim', ctypes.c_int),
        ('out_frq', ctypes.c_int),
        ('out_dly', ctypes.c_int),
        ('presolve', ctypes.c_int),
        ('excl', ctypes.c_int),
        ('shift', ctypes.c_int),
        ('aorn', ctypes.c_int),
        ('foobar', ctypes.c_double*33),
    ]


class glp_iptcp(ctypes.Structure):
    _fields_ = [
        ('msg_lev', ctypes.c_int),
        ('ord_alg', ctypes.c_int),
        ('foo_bar', ctypes.c_double*48),
    ]


class glp_mpscp(ctypes.Structure):
    _fields_ = []


class glp_bfcp(ctypes.Structure):
    _fields_ = [
        ('msg_lev', ctypes.c_int),        # (not used)
        ('type', ctypes.c_int),           # factorization type
        ('lu_size', ctypes.c_int),        # (not used)
        ('piv_tol', ctypes.c_double),     # sgf_piv_tol
        ('piv_lim', ctypes.c_int),        # sgf_piv_lim
        ('suhl', ctypes.c_int),           # sgf_suhl
        ('eps_tol', ctypes.c_double),     # sgf_eps_tol
        ('max_gro', ctypes.c_double),     # (not used)
        ('nfs_max', ctypes.c_int),        # fhvint.nfs_max
        ('upd_tol', ctypes.c_double),     # (not used)
        ('nrs_max', ctypes.c_int),        # scfint.nn_max
        ('rs_size', ctypes.c_int),        # (not used)
        ('foo_bar', ctypes.c_double*38),  # (reserved)
    ]

# integer optimizer control parameters


class glp_tree(ctypes.Structure):
    _fields_ = []


class glp_iocp(ctypes.Structure):
    _fields_ = [
        ('msg_lev', ctypes.c_int),        # message level (see glp_smcp)
        ('br_tech', ctypes.c_int),        # branching technique
        ('bt_tech', ctypes.c_int),        # backtracking technique:
        ('tol_int', ctypes.c_double),     # mip.tol_int
        ('tol_obj', ctypes.c_double),     # mip.tol_obj
        ('tm_lim', ctypes.c_int),         # mip.tm_lim (milliseconds)
        ('out_frq', ctypes.c_int),        # mip.out_frq (milliseconds)
        ('out_dly', ctypes.c_int),        # mip.out_dly (milliseconds)
        # void (*cb_func)(glp_tree *T, void *info);  # mip.cb_func
        ('cb_func', ctypes.CFUNCTYPE(None, ctypes.POINTER(glp_tree), ctypes.c_void_p)),
        ('cb_info', ctypes.c_void_p),     # mip.cb_info
        ('cb_size', ctypes.c_int),        # mip.cb_size
        ('pp_tech', ctypes.c_int),        # preprocessing technique:
        ('mip_gap', ctypes.c_double),     # relative MIP gap tolerance
        ('mir_cuts', ctypes.c_int),       # MIR cuts       (GLP_ON/GLP_OFF)
        ('gmi_cuts', ctypes.c_int),       # Gomory's cuts  (GLP_ON/GLP_OFF)
        ('cov_cuts', ctypes.c_int),       # cover cuts     (GLP_ON/GLP_OFF)
        ('clq_cuts', ctypes.c_int),       # clique cuts    (GLP_ON/GLP_OFF)
        ('presolve', ctypes.c_int),       # enable/disable using MIP presolver
        ('binarize', ctypes.c_int),       # try to binarize integer variables
        ('fp_heur', ctypes.c_int),        # feasibility pump heuristic
        ('ps_heur', ctypes.c_int),        # proximity search heuristic
        ('ps_tm_lim', ctypes.c_int),      # proxy time limit, milliseconds
        ('sr_heur', ctypes.c_int),        # simple rounding heuristic
        ('use_sol', ctypes.c_int),        # use existing solution
        ('save_sol', ctypes.c_char_p),    # filename to save every new solution
        ('alien', ctypes.c_int),          # use alien solver
        ('flip', ctypes.c_int),           # use long-step dual simplex; not documented--should not be used
        ('foo_bar', ctypes.c_double*23),  # (reserved)
    ]


# LP problem structure
class glp_prob(ctypes.Structure):
    class DMP(ctypes.Structure):
        _fields_ = []

    class glp_tree(ctypes.Structure):
        _fields_ = []

    class GLPROW(ctypes.Structure):
        _fields_ = []

    class GLPCOL(ctypes.Structure):
        _fields_ = []

    class AVL(ctypes.Structure):
        _fields_ = []

    class BFD(ctypes.Structure):
        _fields_ = []

    # shouldn't access these directly!
    _fields_ = [
        ('pool', ctypes.POINTER(DMP)),
        ('tree', ctypes.POINTER(glp_tree)),
        ('name', ctypes.c_char_p),
        ('obj', ctypes.c_char_p),
        ('dir', ctypes.c_int),
        ('c0', ctypes.c_double),
        ('m_max', ctypes.c_int),
        ('n_max', ctypes.c_int),
        ('m', ctypes.c_int),
        ('n', ctypes.c_int),
        ('nnz', ctypes.c_int),
        ('row', ctypes.POINTER(ctypes.POINTER(GLPROW))),
        ('col', ctypes.POINTER(ctypes.POINTER(GLPCOL))),
        ('r_tree', ctypes.POINTER(AVL)),
        ('c_tree', ctypes.POINTER(AVL)),
        ('valid', ctypes.c_int),
        ('head', ctypes.POINTER(ctypes.c_int)),
        ('bfd', ctypes.POINTER(BFD)),
        ('pbs_stat', ctypes.c_int),
        ('dbs_stat', ctypes.c_int),
        ('obj_val', ctypes.c_double),
        ('it_cnt', ctypes.c_int),
        ('some', ctypes.c_int),
        ('ipt_stat', ctypes.c_int),
        ('ipt_obj', ctypes.c_double),
        ('mip_stat', ctypes.c_int),
        ('mip_obj', ctypes.c_double),
    ]


class GLPK:

    # Where is GLPK? Find where the C extension module was installed:
    _glpk_lib_path = importlib.util.find_spec("glpk5_0").origin

    # FIXME: this looks like it has dubious portability
    INT_MAX = ctypes.c_uint(-1).value // 2
    GLP_ON = 1
    GLP_OFF = 0

    # solution status:
    GLP_UNDEF = 1   # solution is undefined
    GLP_FEAS = 2    # solution is feasible
    GLP_INFEAS = 3  # solution is infeasible
    GLP_NOFEAS = 4  # no feasible solution exists
    GLP_OPT = 5     # solution is optimal
    GLP_UNBND = 6   # solution is unbounded
    STATUS_CODES = {
        GLP_UNDEF: 'solution is undefined',
        GLP_FEAS: 'solution is feasible',
        GLP_INFEAS: 'solution is infeasible',
        GLP_NOFEAS: 'no feasible solution exists',
        GLP_OPT: 'solution is optimal',
        GLP_UNBND: 'solution is unbounded',
    }

    # Pricing techniques
    GLP_PT_STD = 17  # 0x11 # standard (Dantzig's rule)
    GLP_PT_PSE = 34  # 0x22 # projected steepest edge

    # Ratio test techniques
    GLP_RT_STD = 17  # 0x11
    GLP_RT_HAR = 34  # 0x22
    GLP_RT_FLIP = 51  # 0x33

    # Objective sense
    GLP_MIN = 1
    GLP_MAX = 2

    # Bound types
    GLP_FR = 1  # -inf < x < +inf
    GLP_LO = 2  # lb <= x < +inf
    GLP_UP = 3  # -inf < x <= ub
    GLP_DB = 4  # lb <= x <= ub
    GLP_FX = 5  # lb == x == ub

    # Scaling techniques
    GLP_SF_GM = 1      # 0x01   # geometric scaling
    GLP_SF_EQ = 16     # 0x10   # equilibration scaling
    GLP_SF_2N = 3      # 0x20   # round scale factors to nearest power of two
    GLP_SF_SKIP = 64   # 0x40 # skip scaling, if the problem is well scaled
    GLP_SF_AUTO = 128  # 0x80 # choose scaling options automatically

    # return codes for glp_simplex driver
    SUCCESS = 0
    GLP_EBADB = 1
    GLP_ESING = 2
    GLP_ECOND = 3
    GLP_EBOUND = 4
    GLP_EFAIL = 5
    GLP_EOBJLL = 6
    GLP_EOBJUL = 7
    GLP_EITLIM = 8
    GLP_ETMLIM = 9
    GLP_ENOPFS = 10
    GLP_ENODFS = 11
    GLP_EROOT = 12
    GLP_ESTOP = 13
    GLP_EMIPGAP = 14
    GLP_ENOFEAS = 15
    GLP_ENOCVG = 16
    GLP_EINSTAB = 17
    GLP_EDATA = 18
    GLP_ERANGE = 19

    RET_CODES = {
        SUCCESS: 'LP problem instance has been successfully solved',
        GLP_EBADB: 'invalid basis',
        GLP_ESING: 'singular matrix',
        GLP_ECOND: 'ill-conditioned matrix',
        GLP_EBOUND: 'invalid bounds',
        GLP_EFAIL: 'solver failed',
        GLP_EOBJLL: 'objective lower limit reached',
        GLP_EOBJUL: 'objective upper limit reached',
        GLP_EITLIM: 'iteration limit exceeded',
        GLP_ETMLIM: 'time limit exceeded',
        GLP_ENOPFS: 'no primal feasible solution',
        GLP_ENODFS: 'no dual feasible solution',
        GLP_EROOT: 'root LP optimum not provided',
        GLP_ESTOP: 'search terminated by application',
        GLP_EMIPGAP: 'relative mip gap tolerance reached',
        GLP_ENOFEAS: 'no primal/dual feasible solution',
        GLP_ENOCVG: 'no convergence',
        GLP_EINSTAB: 'numerical instability',
        GLP_EDATA: 'invalid data',
        GLP_ERANGE: 'result out of range',
    }

    # Message levels
    GLP_MSG_OFF = 0
    GLP_MSG_ERR = 1
    GLP_MSG_ON = 2
    GLP_MSG_ALL = 3
    GLP_MSG_DBG = 4

    # Simplex methods
    GLP_PRIMAL = 1
    GLP_DUALP = 2
    GLP_DUAL = 3

    # Ordering strategies
    GLP_ORD_NONE = 0
    GLP_ORD_QMD = 1
    GLP_ORD_AMD = 2
    GLP_ORD_SYMAMD = 3

    # MPS formats
    GLP_MPS_DECK = 1  # fixed (ancient)
    GLP_MPS_FILE = 2  # free (modern)

    # Factorization strategies
    GLP_BF_LUF = 0   # 0x00  # plain LU-factorization
    GLP_BF_BTF = 16  # 0x10  # block triangular LU-factorization
    GLP_BF_FT = 1    # 0x01  # Forrest-Tomlin (LUF only)
    GLP_BF_BG = 2    # 0x02  # Schur compl. + Bartels-Golub
    GLP_BF_GR = 3    # 0x03  # Schur compl. + Givens rotation

    # Branching techniques
    GLP_BR_FFV = 1  # first fractional variable
    GLP_BR_LFV = 2  # last fractional variable
    GLP_BR_MFV = 3  # most fractional variable
    GLP_BR_DTH = 4  # heuristic by Driebeck and Tomlin
    GLP_BR_PCH = 5  # hybrid pseudocost heuristic

    # Backtracking technique
    GLP_BT_DFS = 1  # depth first search
    GLP_BT_BFS = 2  # breadth first search
    GLP_BT_BLB = 3  # best local bound
    GLP_BT_BPH = 4  # best projection heuristic

    # MIP preprocessing
    GLP_PP_NONE = 0  # disable preprocessing
    GLP_PP_ROOT = 1  # preprocessing only on root level
    GLP_PP_ALL = 2   # preprocessing on all levels

    # Variable types
    GLP_CV = 1  # continuous variable
    GLP_IV = 2  # integer variable
    GLP_BV = 3  # binary variable

    def __init__(self):

        # Load the shared library;
        _lib = ctypes.cdll.LoadLibrary(self._glpk_lib_path)

        _lib.glp_version.restype = ctypes.c_char_p

        _lib.glp_create_prob.restype = ctypes.POINTER(glp_prob)

        # Setters
        _lib.glp_set_prob_name.restype = None
        _lib.glp_set_prob_name.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_char_p]

        _lib.glp_set_obj_name.restype = None
        _lib.glp_set_obj_name.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_char_p]

        _lib.glp_set_obj_dir.restype = None
        _lib.glp_set_obj_dir.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int]

        _lib.glp_add_cols.restype = ctypes.c_int
        _lib.glp_add_cols.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int]

        _lib.glp_set_obj_coef.restype = None
        _lib.glp_set_obj_coef.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int, ctypes.c_double]

        _lib.glp_set_col_name.restype = None
        _lib.glp_set_col_name.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int, ctypes.c_char_p]

        _lib.glp_set_col_bnds.restype = None
        _lib.glp_set_col_bnds.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,     # col index (1-based)
            ctypes.c_int,     # type
            ctypes.c_double,  # lb
            ctypes.c_double,  # up
        ]

        _lib.glp_add_rows.restype = ctypes.c_int
        _lib.glp_add_rows.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int]

        _lib.glp_load_matrix.restype = None
        _lib.glp_load_matrix.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,                                      # nnz
            ndpointer(ctypes.c_int, flags='C_CONTIGUOUS'),     # row indices
            ndpointer(ctypes.c_int, flags='C_CONTIGUOUS'),     # col indices
            ndpointer(ctypes.c_double, flags='C_CONTIGUOUS'),  # values
        ]

        _lib.glp_set_row_bnds.restype = None
        _lib.glp_set_row_bnds.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,     # row index (1-based)
            ctypes.c_int,     # type
            ctypes.c_double,  # lb
            ctypes.c_double,  # ub
        ]

        _lib.glp_scale_prob.restype = None
        _lib.glp_scale_prob.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int]

        _lib.glp_std_basis.restype = None
        _lib.glp_std_basis.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_adv_basis.restype = None
        _lib.glp_adv_basis.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int]

        _lib.glp_cpx_basis.restype = None
        _lib.glp_cpx_basis.argtypes = [ctypes.POINTER(glp_prob)]

        # Getters
        _lib.glp_get_prob_name.restype = ctypes.c_char_p
        _lib.glp_get_prob_name.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_get_obj_name.restype = ctypes.c_char_p
        _lib.glp_get_obj_name.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_get_obj_dir.restype = ctypes.c_int
        _lib.glp_get_obj_dir.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_get_obj_coef.restype = ctypes.c_double
        _lib.glp_get_obj_coef.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int]

        _lib.glp_get_num_cols.restype = ctypes.c_int
        _lib.glp_get_num_cols.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_get_col_name.restype = ctypes.c_char_p
        _lib.glp_get_col_name.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int]

        _lib.glp_get_row_name.restype = ctypes.c_char_p
        _lib.glp_get_row_name.argtypes = [ctypes.POINTER(glp_prob), ctypes.c_int]

        _lib.glp_get_num_rows.restype = ctypes.c_int
        _lib.glp_get_num_rows.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_get_num_nz.restype = ctypes.c_int
        _lib.glp_get_num_nz.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_get_mat_row.restype = ctypes.c_int  # len of col indices and values
        _lib.glp_get_mat_row.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # ith row
            ctypes.POINTER(ctypes.c_int),  # col indices
            ctypes.POINTER(ctypes.c_double),  # values
        ]

        _lib.glp_get_row_type.restype = ctypes.c_int
        _lib.glp_get_row_type.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # ith row
        ]

        _lib.glp_get_row_lb.restype = ctypes.c_double
        _lib.glp_get_row_lb.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # ith row
        ]

        _lib.glp_get_row_ub.restype = ctypes.c_double
        _lib.glp_get_row_ub.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # ith row
        ]

        _lib.glp_get_col_type.restype = ctypes.c_int
        _lib.glp_get_col_type.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # jth col
        ]

        _lib.glp_get_col_lb.restype = ctypes.c_double
        _lib.glp_get_col_lb.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # jth col
        ]

        _lib.glp_get_col_ub.restype = ctypes.c_double
        _lib.glp_get_col_ub.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # jth col
        ]

        _lib.glp_get_status.restype = ctypes.c_int
        _lib.glp_get_status.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_get_obj_val.restype = ctypes.c_double
        _lib.glp_get_obj_val.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_get_col_prim.restype = ctypes.c_double
        _lib.glp_get_col_prim.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # primal value of jth col
        ]

        _lib.glp_get_col_dual.restype = ctypes.c_double
        _lib.glp_get_col_dual.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # dual value of jth col
        ]

        _lib.glp_get_row_dual.restype = ctypes.c_double
        _lib.glp_get_row_dual.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # dual value of ith row
        ]
        
        # Interior point variants
        _lib.glp_ipt_status.restype = ctypes.c_int
        _lib.glp_ipt_status.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_ipt_obj_val.restype = ctypes.c_double
        _lib.glp_ipt_obj_val.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_ipt_col_prim.restype = ctypes.c_double
        _lib.glp_ipt_col_prim.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # primal value of jth col
        ]

        _lib.glp_ipt_col_dual.restype = ctypes.c_double
        _lib.glp_ipt_col_dual.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # dual value of jth col
        ]

        # MIP variants
        _lib.glp_mip_status.restype = ctypes.c_int
        _lib.glp_mip_status.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_mip_obj_val.restype = ctypes.c_double
        _lib.glp_mip_obj_val.argtypes = [ctypes.POINTER(glp_prob)]

        _lib.glp_mip_col_val.restype = ctypes.c_double
        _lib.glp_mip_col_val.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # jth col
        ]

        _lib.glp_get_col_kind.restype = ctypes.c_int
        _lib.glp_set_col_kind.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # jth col
        ]

        _lib.glp_set_col_kind.restype = None
        _lib.glp_set_col_kind.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,  # jth col
            ctypes.c_int,  # type
        ]

        # Initialize control structures
        _lib.glp_init_smcp.restype = ctypes.c_int
        _lib.glp_init_smcp.argtypes = [ctypes.POINTER(glp_smcp)]

        _lib.glp_init_iptcp.restype = ctypes.c_int
        _lib.glp_init_iptcp.argtypes = [ctypes.POINTER(glp_iptcp)]

        _lib.glp_init_iocp.restype = None
        _lib.glp_init_iocp.argtypes = [ctypes.POINTER(glp_iocp)]

        # Simplex drivers
        _lib.glp_simplex.restype = ctypes.c_int
        _lib.glp_simplex.argtypes = [ctypes.POINTER(glp_prob), ctypes.POINTER(glp_smcp)]

        _lib.glp_exact.restype = ctypes.c_int
        _lib.glp_exact.argtypes = [ctypes.POINTER(glp_prob), ctypes.POINTER(glp_smcp)]

        # Interior point drivers
        _lib.glp_interior.restype = ctypes.c_int
        _lib.glp_interior.argtypes = [ctypes.POINTER(glp_prob), ctypes.POINTER(glp_iptcp)]

        # MIP drivers
        _lib.glp_intopt.restype = ctypes.c_int
        _lib.glp_intopt.argtypes = [ctypes.POINTER(glp_prob), ctypes.POINTER(glp_iocp)]

        # Cleanup
        _lib.glp_delete_prob.restype = None
        _lib.glp_delete_prob.argtypes = [ctypes.POINTER(glp_prob)]

        # Utility
        _lib.glp_read_mps.restype = ctypes.c_int
        _lib.glp_read_mps.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,               # format (GLP_MPS_DECK or GLP_MPS_FILE)
            ctypes.POINTER(glp_mpscp),  # should be NULL
            ctypes.c_char_p,            # filename
        ]

        _lib.glp_write_mps.restype = ctypes.c_int
        _lib.glp_write_mps.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.c_int,               # format (GLP_MPS_DECK or GLP_MPS_FILE)
            ctypes.POINTER(glp_mpscp),  # should be NULL
            ctypes.c_char_p,            # filename
        ]

        _lib.glp_write_lp.restype = ctypes.c_int
        _lib.glp_write_lp.argtypes = [
            ctypes.POINTER(glp_prob),
            ctypes.POINTER(glp_mpscp),  # should be NULL
            ctypes.c_char_p,            # filename
        ]
        
        # LP Basis Factorization
        _lib.glp_get_bfcp.restype = None
        _lib.glp_get_bfcp.argtypes = [ctypes.POINTER(glp_prob), ctypes.POINTER(glp_bfcp)]

        _lib.glp_set_bfcp.restype = None
        _lib.glp_set_bfcp.argtypes = [ctypes.POINTER(glp_prob), ctypes.POINTER(glp_bfcp)]

        # Make accessible for front-end interface
        self._lib = _lib
