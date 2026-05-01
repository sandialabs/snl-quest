import os
import copy
from datetime import datetime
import numpy as np
from progress.mod_utilities import RAUtilities
from progress.mod_plot import RAPlotTools
from progress.paths import get_path

def mcs_run_samples_function(simulation_context):
    config = simulation_context['config']
    rasd = simulation_context['rasd']
    raut_data = simulation_context['raut_data']
    rmat = simulation_context['rmat']
    rsolar = simulation_context['rsolar']
    rwind = simulation_context['rwind']
    samples = simulation_context['samples']
    sim_hours = simulation_context['sim_hours']
    indices_rec = simulation_context['indices_rec']
    LOL_track = simulation_context['LOL_track']
    raut = RAUtilities()
    print('Simulation started')

    main_folder = get_path()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    results_subdir = os.path.join(main_folder, 'Results', timestamp)
    os.makedirs(results_subdir, exist_ok=True)

    def init_sample_state():
        var_s = {
            't_min': 0,
            'LLD': 0,
            'curtailment': np.zeros(sim_hours),
            'label_LOLF': np.zeros(sim_hours),
            'freq_LOLF': 0,
            'LOL_days': 0,
            'outage_day': np.zeros(365),
        }
        current_state = np.ones(rasd['ng'] + rasd['nl'] + rasd['ness'])
        current_w_class = None
        if rwind:
            current_w_class = np.floor(
                np.random.uniform(0, 1, rwind['w_sites']) * rwind['w_classes']
            ).astype(int)
        renewable_rec = {
            'wind_rec': np.zeros((rasd['nz'], sim_hours)),
            'solar_rec': np.zeros((rasd['nz'], sim_hours)),
            'congen_temp': 0,
            'rengen_temp': 0,
        }
        SOC_old = 0.5 * np.multiply(
            np.multiply(rasd['ess_pmax'], rasd['ess_duration']),
            rasd['ess_socmax'],
        ) / rasd['BMva']
        SOC_rec = np.zeros((rasd['ness'], sim_hours))
        curt_rec = np.zeros(sim_hours)
        part_netload = config['load_factor'] * rasd['load_all_regions']
        return var_s, current_state, current_w_class, renewable_rec, SOC_old, SOC_rec, curt_rec, part_netload

    def run_single_sample(sample_index):
        var_s, current_state, current_w_class, renewable_rec, SOC_old, SOC_rec, curt_rec, part_netload = init_sample_state()

        for n in range(sim_hours):
            next_state, current_cap, var_s['t_min'] = raut.NextState(
                var_s['t_min'],
                rasd['ng'],
                rasd['ness'],
                rasd['nl'],
                raut_data['lambda_tot'],
                raut_data['mu_tot'],
                current_state,
                raut_data['cap_max'],
                raut_data['cap_min'],
                rasd['ess_units'],
            )
            current_state = copy.deepcopy(next_state)
            ess_smax, ess_smin, SOC_old = raut.updateSOC(
                rasd['ng'],
                rasd['nl'],
                current_cap,
                rasd['ess_pmax'],
                rasd['ess_duration'],
                rasd['ess_socmax'],
                rasd['ess_socmin'],
                SOC_old,
            )
            gt_limits = {
                'g_lb': np.concatenate((
                    current_cap['min'][0:rasd['ng']] / rasd['BMva'],
                    current_cap['min'][rasd['ng'] + rasd['nl']:] / rasd['BMva'],
                )),
                'g_ub': np.concatenate((
                    current_cap['max'][0:rasd['ng']] / rasd['BMva'],
                    current_cap['max'][rasd['ng'] + rasd['nl']:] / rasd['BMva'],
                )),
                'tl': current_cap['max'][rasd['ng']:rasd['ng'] + rasd['nl']] / rasd['BMva'],
            }

            def fb_Pg(model, i):
                return (gt_limits['g_lb'][i], gt_limits['g_ub'][i])

            def fb_flow(model, i):
                return (-gt_limits['tl'][i], gt_limits['tl'][i])

            def fb_ess(model, i):
                return (
                    -current_cap['max'][rasd['ng'] + rasd['nl']:][i] / rasd['BMva'],
                    current_cap['min'][rasd['ng'] + rasd['nl']:][i] / rasd['BMva'],
                )

            def fb_soc(model, i):
                return (ess_smin[i] / rasd['BMva'], ess_smax[i] / rasd['BMva'])

            w_zones = None
            s_zones = None
            if rwind:
                w_zones, current_w_class = raut.WindPower(
                    rasd['nz'],
                    rwind['w_sites'],
                    rwind['zone_no'],
                    rwind['w_classes'],
                    rwind['r_cap'],
                    current_w_class,
                    rwind['tr_mats'],
                    rwind['p_class'],
                    rwind['w_turbines'],
                    rwind['out_curve2'],
                    rwind['out_curve3'],
                )
            if rsolar:
                s_zones = raut.SolarPower(
                    n,
                    rasd['nz'],
                    rsolar['s_zone_no'],
                    rsolar['solar_prob'],
                    rsolar['s_profiles'],
                    rsolar['s_sites'],
                    rsolar['s_max'],
                )

            if rwind:
                renewable_rec['wind_rec'][:, n] = w_zones
            if rsolar:
                s_zones_t = np.transpose(s_zones)
                renewable_rec['solar_rec'][:, n] = s_zones_t[:, n % 24]

            if rsolar and rwind:
                net_load = part_netload[n] - w_zones - s_zones[n % 24]
            elif (not rsolar) and rwind:
                net_load = part_netload[n] - w_zones
            elif rsolar and (not rwind):
                net_load = part_netload[n] - s_zones[n % 24]
            else:
                net_load = part_netload[n]

            if config['model'] == 'Zonal':
                load_curt, SOC_old = raut.OptDispatch(
                    rasd['ng'],
                    rasd['nz'],
                    rasd['nl'],
                    rasd['ness'],
                    fb_ess,
                    fb_soc,
                    rasd['BMva'],
                    fb_Pg,
                    fb_flow,
                    rmat['A_inc'],
                    rmat['gen_mat'],
                    rmat['curt_mat'],
                    rmat['ch_mat'],
                    rasd['gencost'],
                    net_load,
                    SOC_old,
                    rasd['ess_pmax'],
                    rasd['ess_eff'],
                    rasd['disch_cost'],
                    rasd['ch_cost'],
                )
            elif config['model'] == 'Copper Sheet':
                load_curt, SOC_old = raut.OptDispatchLite(
                    rasd['ng'],
                    rasd['nz'],
                    rasd['ness'],
                    fb_ess,
                    fb_soc,
                    rasd['BMva'],
                    fb_Pg,
                    rmat['A_inc'],
                    rasd['gencost'],
                    net_load,
                    SOC_old,
                    rasd['ess_pmax'],
                    rasd['ess_eff'],
                    rasd['disch_cost'],
                    rasd['ch_cost'],
                )
            else:
                raise ValueError(f"Unsupported model: {config['model']}")

            SOC_rec[:, n] = SOC_old * rasd['BMva']
            curt_rec[n] = load_curt * rasd['BMva']
            var_s, updated_lol_track = raut.TrackLOLStates(load_curt, rasd['BMva'], var_s, LOL_track, sample_index, n)
            LOL_track[:] = updated_lol_track
            if (n + 1) % 100 == 0:
                print(f'Hour {n + 1}')

        sample_subdir = os.path.join(results_subdir, f'Sample {sample_index + 1}')
        os.makedirs(sample_subdir, exist_ok=True)
        rapt = RAPlotTools(sample_subdir)
        rapt.PlotSolarGen(renewable_rec['solar_rec'], rasd['bus_name'], sample_index)
        rapt.PlotWindGen(renewable_rec['wind_rec'], rasd['bus_name'], sample_index)
        rapt.PlotSOC(SOC_rec, rasd['essname'], sample_index)
        rapt.PlotLoadCurt(curt_rec, sample_index)
        return var_s

    for s in range(samples):
        print(f'Sample: {s + 1}')
        var_s = run_single_sample(s)
        indices_rec = raut.UpdateIndexArrays(indices_rec, var_s, sim_hours, s)
        indices_rec['mLOLP_rec'][s] = np.mean(indices_rec['LOLP_rec'][0:s + 1])
        var_LOLP = np.var(indices_rec['LOLP_rec'][0:s + 1])
        if indices_rec['mLOLP_rec'][s] != 0:
            indices_rec['COV_rec'][s] = np.sqrt(var_LOLP) / indices_rec['mLOLP_rec'][s]
        else:
            indices_rec['COV_rec'][s] = 0

    return {
        'simulation_state': {
            'indices_rec': indices_rec,
            'results_subdir': results_subdir,
            'samples': samples,
            'sim_hours': sim_hours,
            'LOL_track': LOL_track,
        }
    }
