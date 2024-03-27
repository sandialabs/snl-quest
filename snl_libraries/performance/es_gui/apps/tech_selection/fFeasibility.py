# import pandas as pd
from es_gui.apps.tech_selection import fAux


def isFeasibleTech_Location(techDB, selected_location):
    """
    Identify which ES techs are feasible for the current project based on the location where the ESS will be
    connected to the electric grid.

    Parameters
    ----------
    techDB: pandas dataframe
        Database containing detailed information for multiple ES techs
    selected_location: string
        Location where the ESS will be connected to the electric grid; valid values are 'Transmission/Central',
        'Distribution', 'BTM: Commercial/industrial', and 'BTM: residential'

    Returns
    -------
    List with a subset of ES techs that satisfy the grid location restriction
    """

    # Return the subset of ES techs that satisfy the grid location restriction
    return techDB.loc[fAux.pdSeriesIdxWhereTrue(techDB[f'Score for {selected_location}'] > 0)]['Storage technology (short name)'].values


def isFeasibleTech_Duration(techDB, selected_duration, remaining_feasible_techs=None):
    """
    Identify which ES techs are feasible for the current project based on the minimum discharge duration required
    for the selected application.

    Parameters
    ----------
    techDB: pandas dataframe
        Database containing detailed information for multiple ES techs
    selected_duration: float
        Minimum discharge duration required for the selected application
    remaining_feasible_techs: list, optional
        List of ES techs to be evaluated for feasibility; the default is None (use all ES techs in the database)

    Returns
    -------
    List with a subset of ES techs that satisfy the minimum discharge duration requirement
    """

    # If no subset of ES techs is provided, then evaluate all ES techs in the database
    if remaining_feasible_techs is None:
        remaining_feasible_techs = techDB.index

    # Return the subset of ES techs that satisfy the minimum discharge duration requirement
    return techDB.loc[fAux.pdSeriesIdxWhereTrue(techDB.loc[remaining_feasible_techs, 'Discharge duration (hours)'] >=
                                     selected_duration)]['Storage technology (short name)'].values


def isFeasibleTech_ResponseTime(techDB, selected_response_time, remaining_feasible_techs=None):
    """
    Identify which ES techs are feasible for the current project based on the minimum response time to full power
    required for the selected application.

    Parameters
    ----------
    techDB: pandas dataframe
        Database containing detailed information for multiple ES techs
    selected_response_time: string
        Minimum response time to full power required for the selected application; valid values are 'ms', 'sec', 'min', and'hrs'
    remaining_feasible_techs: list, optional
        List of ES techs to be evaluated for feasibility; the default is None (use all ES techs in the database)

    Returns
    -------
    List with a subset of ES techs that satisfy the minimum response time requirement
    """

    # If no subset of ES techs is provided, then evaluate all ES techs in the database
    if remaining_feasible_techs is None:
        remaining_feasible_techs = techDB.index

    # Ordering of response time values for comparison (ascending order)
    ordering_response_time = ['ms', 'sec', 'min', 'hrs']

    # Convert tech response times into an integer according to the ordering above (for easier comparison)
    tech_response_time_scale = techDB.loc[remaining_feasible_techs, 'Response time to full power'].\
        apply(lambda x: ordering_response_time.index(x))

    # Return the subset of ES techs that satisfy the minimum response time requirement
    return techDB.loc[fAux.pdSeriesIdxWhereTrue(tech_response_time_scale <= 
        ordering_response_time.index(selected_response_time))]['Storage technology (short name)'].values


def isFeasibleTech_ElectricOutput(techDB, requires_electric_output, remaining_feasible_techs=None):
    """
    Identify which ES techs are feasible for the current project based on the need of an output in electric
    form for the selected application.

    Parameters
    ----------
    techDB: pandas dataframe
        Database containing detailed information for multiple ES techs
    requires_electric_output: string
        Indicator of whether the selected application requires an electric output ('Yes' or 'No')
    remaining_feasible_techs: list, optional
        List of ES techs to be evaluated for feasibility; the default is None (use all ES techs)

    Returns
    -------
    List with a subset of ES techs that satisfy the electric output requirement
    """

    # If no subset of ES techs is provided, then evaluate all ES techs in the database
    if remaining_feasible_techs is None:
        remaining_feasible_techs = techDB.index

    # No electric output is required; thus, no ES tech is removed from the feasible subset
    if requires_electric_output == 'No':
        return techDB['Storage technology (short name)'].values
        # try:
            # return remaining_feasible_techs.tolist()
        # except:
            # return remaining_feasible_techs

    # Electric output is required; return the subset of ES techs that satisfy this requirement
    elif requires_electric_output == 'Yes':
        return techDB.loc[fAux.pdSeriesIdxWhereTrue(techDB.loc[remaining_feasible_techs, 'Output in electric form'] == 'Yes')]['Storage technology (short name)'].values