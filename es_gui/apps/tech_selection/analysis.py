import os
import re
import numpy as np
import pandas as pd
from es_gui.apps.tech_selection import fFeasibility, fPlots, fAux

from kivy.app import App

# Define some auxiliary functions
normalize_by_max = lambda x: x/x.max()
normalize_by_target = lambda x, tc: tc/(x+tc)


def perform_tech_selection(selections, target_cost_kWh, target_cost_kW):
    """Perform energy storage technology selection based on the user inputs."""

    data_manager = App.get_running_app().data_manager
    app_data = data_manager.get_applications_db()

    # Unpack user selections (input parameters)
    grid_location = selections['location']
    application = selections['application']
    system_size = selections['system_size']
    discharge_duration = float('.'.join(re.findall(r'\d+', selections['discharge_duration'])))
    app_type = selections['app_type']
    target_cost = target_cost_kW if app_type == 'Power' else target_cost_kWh

    # Read databases
    tech_data = data_manager.get_techs_db()

    tech_data.rename(columns={'Feas. score for residential': 'Score for BTM: residential',
                              'Feas. score for industrial': 'Score for BTM: commercial/industrial',
                              'Feas. score for distribution': 'Score for Distribution',
                              'Feas. score for transmission': 'Score for Transmission/central'}, inplace=True)

    # 1st filter: compatibility between grid location and ES techs
    feas_location = list(set(fFeasibility.isFeasibleTech_Location(tech_data, grid_location)))

    # 2nd filter: minimum application requirements
    feas_duration = list(set(fFeasibility.isFeasibleTech_Duration(tech_data, discharge_duration)))
    feas_response_time = list(set(fFeasibility.isFeasibleTech_ResponseTime(
        tech_data, app_data.loc[application, 'Minimum required response time'])))
    feas_electric_output = list(set(fFeasibility.isFeasibleTech_ElectricOutput(
        tech_data, app_data.loc[application, 'Requires electric output'])))

    # Combine feasibility results from all filters (each entry is the boolean True or False)
    all_feasibility = pd.DataFrame(index=np.unique(tech_data['Storage technology (short name)'].values))
    all_feasibility['Grid location'] = [value in feas_location for value in all_feasibility.index]
    all_feasibility['Application requirements'] = [
        value in feas_duration and value in feas_response_time and value in feas_electric_output
        for value in all_feasibility.index]
    all_feasibility['Feasible?'] = all_feasibility.all(axis='columns')

    # For each feasible technology, consider only the entry with the lowest discharge duration that satisfies the requirements
    aa = pd.DataFrame(tech_data.loc[tech_data['Discharge duration (hours)']>=discharge_duration]).groupby(by='Short abbreviation')
    feas_techs_lowest_duration = []
    for _, grp in aa:
        feas_techs_lowest_duration.append(grp.index.tolist()[0])

    # Subset the technology database to contain only the feasible technologies
    tech_data_lowest_duration = pd.DataFrame(tech_data.loc[feas_techs_lowest_duration])
    tech_data_lowest_duration.reset_index(inplace=True, drop=True)
    tech_data_lowest_duration.set_index('Storage technology (short name)', inplace=True)

    # Compute 'Application score' for all feasible technologies (based on discharge duration, cycle life, and efficiency)
    all_app_scores = pd.DataFrame(index=all_feasibility.index)
    all_app_scores['Score for duration'] = tech_data_lowest_duration[['Discharge duration (hours)']].apply(normalize_by_max)
    all_app_scores['Score for cycle life'] = tech_data_lowest_duration[['Cycle life (# of cycles)']].apply(normalize_by_max)
    all_app_scores['Score for efficiency'] = tech_data_lowest_duration[['Round-trip efficiency (%)']].apply(normalize_by_max)
    all_app_scores.fillna(value=0, inplace=True)
    all_app_scores['Application score'] = fAux.geom_mean(all_app_scores)

    # Compute 'Total score' for all feasible technologies (based on application, location, cost, and maturity)
    all_final_scores = pd.DataFrame(index=all_feasibility.index)
    all_final_scores['Application score'] = all_app_scores['Application score']
    all_final_scores['Location score'] = tech_data_lowest_duration[f'Score for {grid_location}']
    all_final_scores['Cost score'] = compute_cost_scores(tech_data_lowest_duration, system_size, app_type, target_cost)
    all_final_scores['Maturity score'] = tech_data_lowest_duration['Tech readiness score']
    all_final_scores.fillna(value=0, inplace=True)
    all_final_scores['Total score'] = all_final_scores['Maturity score'] *\
        fAux.geom_mean(all_final_scores[['Application score', 'Location score', 'Cost score']])
    all_final_scores.sort_values(by=['Total score', 'Application score', 'Location score', 'Cost score', 'Maturity score'],
                                 inplace=True)

    # Plot: feasibility heatmap
    fig = fPlots.plot_table_feasibility(all_feasibility, figsize=(1.4, 1),
                                        xticklabels=['Grid location', 'Application\nrequirements', 'Feasible?'])
    fig.savefig(os.path.join('results', 'tech_selection', 'plot_feasibility.png'))

    # Plot: final feasibility scores
    fig = fPlots.plot_ranking_techs(all_final_scores)
    fig.savefig(os.path.join('results', 'tech_selection', 'plot_ranking.png'))

    return all_feasibility, all_final_scores


def compute_cost_scores(techDB, system_size, app_type, target_cost):
    """Compute cost score for each technology."""
    if app_type == 'Power':
        cost_scores = techDB[f'Cost at {system_size} ($/kW)'].apply(normalize_by_target, tc=target_cost).fillna(value=0)
    elif app_type == 'Energy':
        kWh_costs = techDB[f'Cost at {system_size} ($/kW)']/techDB['Discharge duration (hours)']
        cost_scores = kWh_costs.apply(normalize_by_target, tc=target_cost).fillna(value=0)

    return cost_scores