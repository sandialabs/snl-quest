import pandas as pd

class DataHandler():
    """Contains all data necessary for GUI/optimization"""
    def __init__(self) -> None:

        self.start_year = None
        self.end_year = None
        self.horizon = None
        self.rps_target_years = {}
        self.Ppv_init = None
        self.Pwind_init = None
        self.Pes_init = {}
        self.Eload_path = None  
        self.PV_inso_path = None  
        self.Wind_f_path = None  
        self.es_devices = {}
        self.Pgen = {}
        self.cap_factor = {}
        self.gen_type = {}
        self.Eload = []
        self.PV_inso = []
        self.Wind_f = []
        self.Cpv = None
        self.Cwind = None
        self.Cpcs = None
        self.Ces = {}
        self.wind_data_path = None
        self.inso_data_path = None
        self.load_data_path = None
        self.results = None
        self.year_range = None
        self.solver = 'glpk'

    def set_year_range(self, year_range):
        self.year_range = year_range
        self.start_year = year_range[0]

    def set_wind_data(self, values):
        self.wind_data_path = values

    def set_inso_path(self, values):
        self.inso_data_path = values

    def set_load_path(self, values):
        self.load_data_path = values

    def set_start_year(self, value):
        self.start_year = value

    def set_end_year(self, value):
        self.end_year = value

    def set_horizon(self, ls):
        self.horizon = ls
        self.process_data_paths()
    
    def process_data_paths(self):
        if self.Eload_path:
            self.process_Eload(self.Eload_path)
        if self.PV_inso_path:
            self.process_PV_inso(self.PV_inso_path)
        if self.Wind_f_path:
            self.process_Wind_f(self.Wind_f_path)
    
    def process_Eload(self, data_path):
        dataF = pd.read_csv(data_path)

        dataF = dataF.groupby(["year","month","day"])["system_wide"].sum()
        dataF = dataF.reset_index()
        for yr in range(self.horizon):
            load_data_df2 = dataF[dataF['year'] == self.start_year + yr]
            self.Eload.append(list(load_data_df2["system_wide"]))

    def process_PV_inso(self, data_path):
        dataF = pd.read_csv(data_path)
        print("processing")
        dataF = dataF.groupby(["month","day"])["insolation_pu"].sum()
        dataF = dataF.reset_index()
        for yr in range(self.horizon):
            self.PV_inso.append(list(dataF["insolation_pu"]))

    def process_Wind_f(self, data_path):
        dataF = pd.read_csv(data_path)

        dataF = dataF.groupby(["month","day"])["wind_power_pu"].sum()
        dataF = dataF.reset_index()
        for yr in range(self.horizon):
            self.Wind_f.append(list(dataF["wind_power_pu"]))


    def set_Eload(self, data_path):
        self.Eload_path = data_path

    def set_PV_inso(self, data_path):
        self.PV_inso_path = data_path

    def set_Wind_f(self, data_path):
        self.Wind_f_path = data_path

    def set_rps_target_year(self, year, target):
        self.rps_target_years[year] = target/100

    def set_Ppv_init(self, value):
        self.Ppv_init = value

    def set_Pwind_init(self, value):
        self.Pwind_init = value

    def set_es_device(self, name, rte, deg, eol, dur, cycle):
        """Add an energy storage device type to the dictionary"""
        self.es_devices[name] = {
            'rte': rte,
            'deg': deg,
            'eol': eol,
            'duration': dur,
            'cycle': cycle
        }

    def set_Pes_init(self, es_caps):
        """Set initial power capacities of all ES devices"""
        self.Pes_init = es_caps

    def set_cap_plan(self, gen, gen_type, cap_factor, ls):
        self.set_Pgen(gen, ls)
        self.set_cap_factor(gen, cap_factor)
        self.set_gen_type(gen, gen_type)

    def set_Pgen(self, gen, ls):
        assert len(ls) == self.horizon
        self.Pgen[gen] = ls

    def set_cap_factor(self, gen, cap_factor):
        self.cap_factor[gen] = cap_factor

    def set_gen_type(self, gen, gen_type):
        self.gen_type[gen] = (gen_type == "Clean")
        self.clean = {i: v for i, v in enumerate(self.gen_type) if self.gen_type[v]}
        self.dirty = {i: v for i, v in enumerate(self.gen_type) if not self.gen_type[v]}
        print(self.clean)
        print(self.dirty)

    def set_Cpv(self, cpv_input):

        self.Cpv = [cpv_input * (1 - i * 0.025) for i in range(self.horizon)]  # $/MW

    def set_Cwind(self, cwind_input):

        self.Cwind = [cwind_input * (1 - i * 0.025) for i in range(self.horizon)]  # $/MW

    def set_es_costs(self, es_costs):
        
        Ces = {}
        for device in es_costs:
            Ces[device] = [es_costs[device] * (1 - i * 0.025) for i in range(self.horizon)] # $/MWh

        self.Ces = Ces

    def set_Cpcs(self, cpcs_input):

        self.Cpcs = [cpcs_input * (1 - i * 0.025) for i in range(self.horizon)]  # $/MW

    def set_solver(self, solver):

        self.solver = solver
